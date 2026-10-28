"""S04 local per-PCM-channel speech evidence. Never authorizes edits.

No network access, normalization, denoising, channel mixing or source writes.
The pinned upstream ONNX interface uses 512 samples plus 64 context samples.
"""
from dataclasses import dataclass, replace
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import queue
import subprocess
import tempfile
import threading
import time
from typing import Literal

from .contracts import Analysis, Event, Review, dumps, loads, to_data
from .probe import fingerprint, probe_wav, tool_version
from .timing import ceil as ceil_fraction, floor as floor_fraction


RATE = 16000
WINDOW = 512
ALGORITHM = 's04-speech-1'
MODEL_SHA256 = '2623a2953f6ff3d2c1e61740c6cdb7168133479b267dfef114a4a3cc5bdd788f'
ORT_VERSION = '1.20.1'
NUMPY_VERSION = '2.1.3'


class SpeechError(ValueError):
    """Fixed, private-safe diagnostic code; never include media/tool paths."""


@dataclass(frozen=True)
class Settings:
    speech_threshold: Fraction = Fraction(1, 2)
    uncertain_threshold: Fraction = Fraction(3, 20)
    signal_peak: Fraction = Fraction(1, 10000)
    onset: Fraction = Fraction(3, 25)
    tail: Fraction = Fraction(1, 5)
    merge_samples: int = 1600

    def __post_init__(self):
        if not 0 < self.uncertain_threshold < self.speech_threshold <= 1 or not 0 < self.signal_peak <= 1:
            raise SpeechError('INVALID_SPEECH_THRESHOLDS')
        if not 0 <= self.onset <= 2 or not 0 <= self.tail <= 2 or type(self.merge_samples) is not int or not 0 <= self.merge_samples <= RATE:
            raise SpeechError('INVALID_PROTECTION_SETTINGS')


def cancelled(check):
    if check():
        raise SpeechError('ANALYSIS_CANCELLED')


class SileroCPU:
    def __init__(self, model):
        model = Path(model)
        if not model.is_file():
            raise SpeechError('MODEL_MISSING_RUN_EXPLICIT_SETUP')
        if model.stat().st_size != 2327524 or fingerprint(model) != MODEL_SHA256:
            raise SpeechError('MODEL_HASH_MISMATCH')
        try:
            import numpy as np
            import onnxruntime as ort
        except ImportError:
            raise SpeechError('PINNED_CPU_RUNTIME_MISSING') from None
        if np.__version__ != NUMPY_VERSION or ort.__version__ != ORT_VERSION:
            raise SpeechError('PINNED_CPU_RUNTIME_VERSION_MISMATCH')
        ort.disable_telemetry_events()
        self.np = np
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = opts.inter_op_num_threads = 1
        opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        opts.log_severity_level = 4
        try:
            self.session = ort.InferenceSession(model.read_bytes(), sess_options=opts,
                                                providers=['CPUExecutionProvider'])
            if self.session.get_providers() != ['CPUExecutionProvider']:
                raise SpeechError('CPU_PROVIDER_REQUIRED')
        except Exception:
            raise SpeechError('MODEL_LOAD_FAILED') from None
        self.reset()

    def reset(self):
        self.state = self.np.zeros((2, 1, 128), dtype='float32')
        self.context = self.np.zeros((1, 64), dtype='float32')

    def probability(self, samples):
        x = self.np.asarray(samples, dtype='float32').reshape(1, WINDOW)
        x = self.np.concatenate((self.context, x), axis=1)
        try:
            out, state = self.session.run(None, {'input': x, 'state': self.state,
                                                 'sr': self.np.array(RATE, dtype='int64')})
        except Exception:
            raise SpeechError('CPU_INFERENCE_FAILED') from None
        probability = float(out[0, 0])
        if not math.isfinite(probability) or not 0 <= probability <= 1 or not self.np.isfinite(state).all():
            raise SpeechError('NONFINITE_OR_INVALID_MODEL_OUTPUT')
        self.state, self.context = state, x[:, -64:]
        return probability


def decode_channel(path, channel, ffmpeg, expected, *, chunk_samples=8192, cancel=lambda: False, idle_timeout=30):
    """One continuous resampler per channel; bounded queue and cooperative stop.

    Reader thread unblocks pipe IO on Windows; the main thread enforces timeout,
    output count, stderr size and cancellation, including a stalled decoder.
    Only the last model window is padded, by the inference consumer, at EOF.
    """
    if type(chunk_samples) is not int or not 1 <= chunk_samples <= 65536:
        raise SpeechError('DECODE_CHUNK_BOUNDS')
    args = [ffmpeg, '-nostdin', '-hide_banner', '-v', 'error', '-xerror',
            '-protocol_whitelist', 'file,pipe', '-i', path, '-map', '0:a:0',
            '-af', f'pan=mono|c0=c{channel},aresample={RATE}:resampler=swr:filter_size=32:phase_shift=10:exact_rational=1:dither_method=none',
            '-threads', '1', '-f', 'f32le', '-acodec', 'pcm_f32le', 'pipe:1']
    stop = threading.Event()
    blocks = queue.Queue(maxsize=2)
    def put(value):
        while not stop.is_set():
            try:
                blocks.put(value, timeout=0.05)
                return
            except queue.Full:
                pass
    with tempfile.TemporaryFile() as err:
        try:
            process = subprocess.Popen([str(v) for v in args], stdin=subprocess.DEVNULL,
                                       stdout=subprocess.PIPE, stderr=err, shell=False)
        except OSError:
            raise SpeechError('LOCAL_DECODER_UNAVAILABLE') from None
        def read():
            try:
                while not stop.is_set():
                    block = process.stdout.read(chunk_samples * 4)
                    if not block:
                        break
                    put(block)
            except OSError:
                pass
            finally:
                put(None)
        worker = threading.Thread(target=read, daemon=True)
        worker.start()
        total = 0
        deadline = time.monotonic() + max(120, expected / RATE * 2)
        last = time.monotonic()
        try:
            while True:
                cancelled(cancel)
                if time.monotonic() > deadline or time.monotonic() - last > idle_timeout or os.fstat(err.fileno()).st_size > 65536:
                    raise SpeechError('DECODER_TIME_OR_ERROR_LIMIT')
                try:
                    block = blocks.get(timeout=0.05)
                except queue.Empty:
                    continue
                last = time.monotonic()
                if block is None:
                    break
                if len(block) % 4:
                    raise SpeechError('DECODED_PCM_ALIGNMENT')
                total += len(block) // 4
                if total > expected + 1:
                    raise SpeechError('DECODED_SAMPLE_COUNT_MISMATCH')
                yield block
            try:
                process.wait(timeout=idle_timeout)
            except subprocess.TimeoutExpired:
                raise SpeechError('DECODER_TIME_OR_ERROR_LIMIT') from None
            if process.returncode or os.fstat(err.fileno()).st_size:
                raise SpeechError('DECODER_FAILED_OR_REPORTED_ERRORS')
            if abs(total - expected) > 1 or not total:
                raise SpeechError('DECODED_SAMPLE_COUNT_MISMATCH')
        finally:
            stop.set()
            if process.poll() is None:
                process.kill()
            process.wait()
            worker.join(timeout=2)
            process.stdout.close()


def infer_regions(blocks, model, settings=Settings(), cancel=lambda: False):
    """Streaming coalescer; no minimum speech duration discards short responses."""
    np = model.np
    model.reset()
    pending = bytearray()
    offset = 0
    regions = {'speech': [], 'uncertainty': []}
    def window(raw, length):
        nonlocal offset
        cancelled(cancel)
        samples = np.frombuffer(raw, dtype='<f4')
        # Sinc interpolation of valid PCM can overshoot full scale. Do not
        # reject, clip or renormalize finite temporary analysis samples.
        if not np.isfinite(samples).all():
            raise SpeechError('NONFINITE_DECODED_AUDIO')
        peak = float(np.abs(samples).max())
        if length < WINDOW:
            samples = np.pad(samples, (0, WINDOW - length))
        probability = model.probability(samples)
        kind = ('speech' if probability >= settings.speech_threshold else
                'uncertainty' if probability >= settings.uncertain_threshold or peak >= settings.signal_peak else None)
        if kind:
            runs = regions[kind]
            confidence = Fraction(round(probability * 1000000), 1000000)
            if runs and offset - runs[-1][1] <= settings.merge_samples:
                a, _, p = runs[-1]
                runs[-1] = (a, offset + length, max(p, confidence))
            else:
                runs.append((offset, offset + length, confidence))
        offset += length
    for block in blocks:
        pending.extend(block)
        while len(pending) >= WINDOW * 4:
            raw = bytes(pending[:WINDOW * 4])
            del pending[:WINDOW * 4]
            window(raw, WINDOW)
    if pending:
        if len(pending) % 4:
            raise SpeechError('DECODED_PCM_ALIGNMENT')
        window(bytes(pending), len(pending) // 4)
    return regions, offset


@dataclass(frozen=True)
class CachedTrack:
    schema_version: Literal[1]
    key: str
    events: tuple[Event, ...]
    decoded_samples: int
    channels: int


def identity(source, settings, decoder, channels):
    data = {'algorithm': ALGORITHM, 'implementation_sha256': fingerprint(__file__),
            'source': to_data(source), 'settings': to_data(settings),
            'model': MODEL_SHA256, 'ort': ORT_VERSION, 'numpy': NUMPY_VERSION,
            'python': platform.python_version(), 'platform': platform.platform(),
            'decoder': decoder, 'channels': channels,
            'decode': 'f32le-separate-PCM-channels-swr16000-size32-phase10-exact-no-dither',
            'window': WINDOW, 'context': 64}
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def atomic_new(path, content):
    """Publish complete validated content exclusively, including on Windows."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                         dir=path.parent, delete=False) as out:
            temporary = Path(out.name)
            out.write(content)
            out.flush()
            os.fsync(out.fileno())
        os.link(temporary, path)  # atomic create-if-absent, no overwrite
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@dataclass(frozen=True)
class SpeechResult:
    intake: object
    analysis: Analysis
    tracks: tuple[CachedTrack, ...]
    cache_hits: int

    def summary(self):
        # Existing intake summary retains *all* original extent/origin evidence.
        result = self.intake.summary()
        result['analysis_only'] = True
        result['ready'] = False
        result['speech'] = {'algorithm': ALGORITHM, 'model_sha256': MODEL_SHA256,
                            'runtime': ORT_VERSION, 'numpy': NUMPY_VERSION,
                            'decoder_version': dict(self.analysis.header.settings)['speech_decoder_version'],
                            'runtime_telemetry_disabled': True,
                            'cache_hits': self.cache_hits, 'negative_vad_certifies_silence': False,
                            'laughter_protection_validated': False, 'tracks': []}
        for i, track in enumerate(self.tracks):
            result['speech']['tracks'].append({'id': f'participant_{i+1:02d}',
                'channels': track.channels, 'decoded_samples_per_channel': track.decoded_samples,
                'events': [{'kind': e.kind, 'start_sample': e.start_sample, 'end_sample': e.end_sample,
                            'protected_start': to_data(e.protected_start), 'protected_end': to_data(e.protected_end),
                            'confidence': to_data(e.confidence), 'evidence': e.evidence,
                            'uncertainty_reason': e.uncertainty_reason} for e in track.events]})
        return result


def analyze(intake, audio_paths, model_path, ffmpeg, cache_dir, *, settings=Settings(),
            chunk_samples=8192, cancel=lambda: False):
    """Analyze full measured WAV extents even when intake has unresolved reviews.

    Cache keys exclude IO chunk size (semantically irrelevant), project/pacing
    settings and local paths, but bind source, inference/decode and protection.
    Model and source validation still run on hits. Corrupt caches fail visibly.
    """
    settings = loads(Settings, dumps(settings))
    original = loads(Analysis, dumps(intake.analysis))
    if original.events:
        raise SpeechError('EXPECTED_INTAKE_WITHOUT_PRIOR_SPEECH_EVENTS')
    sources = [s for s in original.sources if s.kind == 'participant_audio']
    if set(audio_paths) != {s.source_id for s in sources}:
        raise SpeechError('AUDIO_MAPPING_MUST_MATCH_INTAKE')
    model = SileroCPU(model_path)  # Required even if every track is cached.
    decoder = (tool_version(ffmpeg), fingerprint(ffmpeg))
    cache_dir = Path(cache_dir)
    tracks, hits = [], 0
    reviews = list(original.reviews)
    # The analysis contract has no separate intake fields. Preserve the full
    # intake alongside it, and mirror each diagnostic as a canonical review.
    for diagnostic in intake.diagnostics:
        sid = diagnostic.source_id if diagnostic.source_id in {s.source_id for s in original.sources} else 'video'
        reviews.append(Review(sid, Fraction(0), None, diagnostic.code))
    for source in sources:
        cancelled(cancel)
        path = Path(audio_paths[source.source_id])
        ap = probe_wav(path)
        if fingerprint(path) != source.sha256 or (ap.sample_rate, ap.sample_count) != (source.sample_rate, source.sample_count):
            raise SpeechError('SOURCE_CHANGED_SINCE_INTAKE')
        expected = ceil_fraction(source.duration * RATE)
        key = identity(source, settings, decoder, ap.channels)
        cache_path = cache_dir / (key + '.json')
        if cache_path.exists():
            try:
                with cache_path.open(encoding='utf-8') as stream:
                    track = loads(CachedTrack, stream.read(8 * 1024 * 1024 + 1))
                if (track.key != key or track.channels != ap.channels or abs(track.decoded_samples - expected) > 1
                        or any(e.source_id != source.source_id or e.kind not in ('speech', 'uncertainty') for e in track.events)):
                    raise ValueError('Invalid cache identity/count.')
                loads(Analysis, dumps(replace(original, events=track.events)))
            except (OSError, ValueError, TypeError):
                raise SpeechError('CACHE_CORRUPT_REMOVE_LOCAL_ENTRY_AND_RETRY') from None
            hits += 1
        else:
            events = []
            counts = []
            for channel in range(ap.channels):
                blocks = decode_channel(path, channel, ffmpeg, expected,
                                        chunk_samples=chunk_samples, cancel=cancel)
                try:
                    regions, count = infer_regions(blocks, model, settings, cancel)
                finally:
                    blocks.close()
                counts.append(count)
                for kind, runs in regions.items():
                    for i, (a, b, confidence) in enumerate(runs):
                        start = floor_fraction(Fraction(a * source.sample_rate, RATE))
                        end = source.sample_count if b == count else min(source.sample_count, ceil_fraction(Fraction(b * source.sample_rate, RATE)))
                        if end <= start:
                            continue
                        events.append(Event(f'{source.source_id}:pcm{channel}:{kind}:{i}', source.source_id, kind,
                            start, end, max(Fraction(0), Fraction(start, source.sample_rate) - settings.onset),
                            min(source.duration, Fraction(end, source.sample_rate) + settings.tail), confidence,
                            f'{ALGORITHM};pcm_channel={channel};silero_v5.1.2;max_window_probability',
                            'LOW_VAD_OR_NON_SPEECH_SIGNAL_KEEP_FOR_REVIEW' if kind == 'uncertainty' else '', source.channel_labels))
            if len(set(counts)) != 1:
                raise SpeechError('CHANNEL_DECODE_LENGTH_MISMATCH')
            events.sort(key=lambda e: (e.start_sample, e.end_sample, e.event_id))
            track = CachedTrack(1, key, tuple(events), counts[0], ap.channels)
            loads(Analysis, dumps(replace(original, events=track.events)))
            if fingerprint(path) != source.sha256:
                raise SpeechError('SOURCE_CHANGED_DURING_ANALYSIS')
            cancelled(cancel)
            try:
                atomic_new(cache_path, dumps(track))
            except FileExistsError:
                if cache_path.read_text(encoding='utf-8') != dumps(track):
                    raise SpeechError('CACHE_CONCURRENT_CONTENT_MISMATCH') from None
        tracks.append(track)
        reviews.append(Review(source.source_id, Fraction(0), None, 'VAD_NEGATIVE_IS_NOT_SILENCE_CERTIFICATE_REACTION_ANALYSIS_PENDING'))
    events = tuple(e for track in tracks for e in track.events)
    header = replace(original.header, run_id='speech-analysis',
                     settings=original.header.settings + (('speech_settings', dumps(settings).strip()),
                         ('decoder_sha256', decoder[1]), ('speech_decoder_version', decoder[0]),
                         ('speech_python', platform.python_version()), ('speech_algorithm', ALGORITHM)),
                     model_versions=original.header.model_versions + (('silero_v5.1.2_sha256', MODEL_SHA256), ('onnxruntime_cpu', ORT_VERSION), ('numpy', NUMPY_VERSION)))
    analysis = loads(Analysis, dumps(replace(original, header=header, events=events, reviews=tuple(reviews))))
    return SpeechResult(intake, analysis, tuple(tracks), hits)
