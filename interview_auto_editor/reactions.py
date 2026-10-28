"""S05 additive local event evidence. Negative results never authorize editing.

YAMNet windows and empirical signal floor support review, not source separation,
speaker identity, alignment certification or a disposable-silence decision.
"""
from dataclasses import dataclass, replace
from fractions import Fraction
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
from typing import Literal

from .contracts import Analysis, Event, Review, dumps, loads, to_data
from .probe import fingerprint, probe_wav, tool_version
from .speech import (NUMPY_VERSION, RATE, SpeechError, atomic_new, cancelled,
                     decode_channel)
from .timing import ceil as ceil_fraction, floor as floor_fraction


ALGORITHM = 's05-additive-events-1'
MODEL_SHA256 = '10c95ea3eb9a7bb4cb8bddf6feb023250381008177ac162ce169694d05c317de'
MODEL_BYTES = 4126810
LITERT_VERSION = '2.3.0'
WINDOW = 15600  # 96 STFT frames: 25 ms window, 10 ms hop, 975 ms waveform
HOP = 7680     # 480 ms; retain full overlapping receptive fields
LAUGHTER = tuple(range(13, 19))
VOCAL = (*range(46), *range(49, 55), *range(61, 67))
MAX_SIGNAL_RUNS = 200000


@dataclass(frozen=True)
class Settings:
    reaction_threshold: Fraction = Fraction(1, 10)
    vocal_uncertainty: Fraction = Fraction(3, 100)
    signal_minimum: Fraction = Fraction(1, 1000000)
    floor_ratio: Fraction = Fraction(4)
    onset: Fraction = Fraction(3, 25)
    tail: Fraction = Fraction(1, 5)

    def __post_init__(self):
        values = (self.reaction_threshold, self.vocal_uncertainty, self.signal_minimum,
                  self.floor_ratio, self.onset, self.tail)
        if any(type(v) is not Fraction for v in values):
            raise SpeechError('REACTION_SETTINGS_REQUIRE_RATIONALS')
        if not 0 < self.vocal_uncertainty <= self.reaction_threshold <= 1:
            raise SpeechError('INVALID_REACTION_THRESHOLDS')
        if not 0 < self.signal_minimum <= 1 or not 1 <= self.floor_ratio <= 100:
            raise SpeechError('INVALID_SIGNAL_REVIEW_SETTINGS')
        if not 0 <= self.onset <= 2 or not 0 <= self.tail <= 2:
            raise SpeechError('INVALID_REACTION_PROTECTION')


class YamnetCPU:
    """Official unchanged TFLite; one-thread CPU with default CPU XNNPACK.

    No external/GPU/NPU delegate is supplied. Pinned LiteRT's Interpreter uses
    its packaged CPU backend; hardware accelerator SDKs are not installed.
    """
    def __init__(self, path):
        path = Path(path)
        if not path.is_file():
            raise SpeechError('REACTION_MODEL_MISSING_RUN_EXPLICIT_SETUP')
        if path.stat().st_size != MODEL_BYTES or fingerprint(path) != MODEL_SHA256:
            raise SpeechError('REACTION_MODEL_HASH_MISMATCH')
        try:
            import numpy as np
            from ai_edge_litert.interpreter import Interpreter, OpResolverType
            version = importlib.metadata.version('ai-edge-litert')
        except ImportError:
            raise SpeechError('PINNED_REACTION_CPU_RUNTIME_MISSING') from None
        if np.__version__ != NUMPY_VERSION or version != LITERT_VERSION:
            raise SpeechError('PINNED_REACTION_RUNTIME_VERSION_MISMATCH')
        self.np = np
        try:
            self.session = Interpreter(model_content=path.read_bytes(), num_threads=1,
                experimental_op_resolver_type=OpResolverType.BUILTIN)
            self.session.allocate_tensors()
            inputs, outputs = self.session.get_input_details(), self.session.get_output_details()
            if (len(inputs) != 1 or len(outputs) != 1 or tuple(inputs[0]['shape']) != (WINDOW,)
                    or tuple(outputs[0]['shape']) != (1, 521)
                    or inputs[0]['dtype'] != np.float32 or outputs[0]['dtype'] != np.float32):
                raise ValueError('Interface mismatch')
            self.input, self.output = inputs[0]['index'], outputs[0]['index']
        except Exception:
            raise SpeechError('REACTION_MODEL_LOAD_OR_INTERFACE_FAILED') from None

    def scores(self, samples):
        np = self.np
        try:
            self.session.set_tensor(self.input, np.asarray(samples, dtype='float32'))
            self.session.invoke()
            scores = self.session.get_tensor(self.output)[0]
        except Exception:
            raise SpeechError('REACTION_CPU_INFERENCE_FAILED') from None
        if scores.shape != (521,) or not np.isfinite(scores).all() or (scores < 0).any() or (scores > 1).any():
            raise SpeechError('INVALID_REACTION_MODEL_OUTPUT')
        return scores


@dataclass(frozen=True)
class Floor:
    pcm_channel: int
    rms_lower_decibel_bin: int
    blocks: int

    def __post_init__(self):
        if (type(self.pcm_channel) is not int or self.pcm_channel < 0 or type(self.blocks) is not int
                or self.blocks < 1 or type(self.rms_lower_decibel_bin) is not int
                or not -240 <= self.rms_lower_decibel_bin <= 24):
            raise ValueError('Invalid empirical floor.')


def infer_channel(blocks, model, settings=Settings(), cancel=lambda: False):
    """Bounded audio, overlapping model fields, EOF once per final hop.

    Signal metadata is capped. A 10th-percentile RMS histogram is only an empirical
    floor: continuous speech, denoising and digital silence can bias it. Contrast
    may add uncertainty; it can never remove existing evidence.
    """
    np = model.np
    pending = bytearray()
    signal_pending = bytearray()
    regions = {'reaction': [], 'uncertainty': []}
    histogram = [0] * 265
    candidates = []
    offset = signal_offset = blocks_count = 0
    last_model_end = 0

    def append(kind, a, b, score):
        p = Fraction(round(float(score) * 1000000), 1000000)
        runs = regions[kind]
        if runs and a <= runs[-1][1]:
            start, end, prev = runs[-1]
            runs[-1] = (start, max(end, b), max(prev, p))
        else:
            runs.append((a, b, p))
        if sum(map(len, regions.values())) > MAX_SIGNAL_RUNS:
            raise SpeechError('REACTION_METADATA_LIMIT')

    def signal(raw):
        nonlocal signal_offset, blocks_count
        samples = np.frombuffer(raw, dtype='<f4').astype('float64')
        rms = float(np.sqrt(np.mean(samples * samples)))
        db = max(-240, min(24, math.floor(20 * math.log10(max(rms, 1e-12)))))
        histogram[db + 240] += 1
        blocks_count += 1
        peak = float(np.abs(samples).max())
        end = signal_offset + len(samples)
        # Quantized energy runs bound metadata without storing audio. The lower
        # bin edge is conservative for the positive contrast safeguard.
        if peak >= settings.signal_minimum:
            band = db // 3 * 3
            if candidates and candidates[-1][1] == signal_offset and candidates[-1][2] == band:
                candidates[-1] = (candidates[-1][0], end, band)
            else:
                candidates.append((signal_offset, end, band))
            if len(candidates) > MAX_SIGNAL_RUNS:
                raise SpeechError('REACTION_METADATA_LIMIT')
        signal_offset = end

    def window(raw, a):
        nonlocal last_model_end
        cancelled(cancel)
        x = np.frombuffer(raw, dtype='<f4')
        b = a + len(x)
        if len(x) < WINDOW:
            x = np.pad(x, (0, WINDOW-len(x)))
        scores = model.scores(x)
        laugh = float(max(scores[i] for i in LAUGHTER))
        vocal = float(max(scores[i] for i in VOCAL))
        if laugh >= settings.reaction_threshold:
            append('reaction', a, b, laugh)
        elif vocal >= settings.vocal_uncertainty:
            append('uncertainty', a, b, vocal)
        last_model_end = b

    for block in blocks:
        cancelled(cancel)
        if len(block) % 4 or len(block) > 65536 * 4:
            raise SpeechError('REACTION_DECODE_BLOCK_BOUNDS')
        if not np.isfinite(np.frombuffer(block, dtype='<f4')).all():
            raise SpeechError('NONFINITE_DECODED_AUDIO')
        pending.extend(block)
        signal_pending.extend(block)
        while len(signal_pending) >= 512 * 4:
            signal(bytes(signal_pending[:512*4]))
            del signal_pending[:512*4]
        while len(pending) >= WINDOW * 4:
            window(bytes(pending[:WINDOW*4]), offset)
            del pending[:HOP*4]
            offset += HOP
    if signal_pending:
        signal(bytes(signal_pending))
    # Avoid a redundant all-old trailing window; do infer new final samples.
    if pending and offset + len(pending)//4 > last_model_end:
        window(bytes(pending), offset)
    if not blocks_count:
        raise SpeechError('EMPTY_REACTION_INPUT')
    target = ceil_fraction(Fraction(blocks_count, 10))
    cumulative = 0
    for i, count in enumerate(histogram):
        cumulative += count
        if cumulative >= target:
            floor_db = i - 240
            break
    threshold = max(float(settings.signal_minimum), 10 ** ((floor_db+1)/20) * float(settings.floor_ratio))
    for a, b, db in candidates:
        if 10 ** (db/20) >= threshold:
            # Score zero explicitly means signal contrast, not vocal confidence.
            regions['uncertainty'].append((a,b,Fraction(0)))
            if len(regions['uncertainty']) > MAX_SIGNAL_RUNS:
                raise SpeechError('REACTION_METADATA_LIMIT')
    # Model and contrast evidence may arrive in different orders; union each kind.
    for kind, runs in regions.items():
        merged = []
        for a, b, p in sorted(runs):
            if merged and a <= merged[-1][1]:
                x, y, q = merged[-1]
                merged[-1] = (x, max(y,b), max(p,q))
            else:
                merged.append((a,b,p))
        regions[kind] = merged
    return regions, signal_offset, (floor_db, blocks_count)


@dataclass(frozen=True)
class CachedTrack:
    schema_version: Literal[1]
    key: str
    events: tuple[Event, ...]
    floors: tuple[Floor, ...]
    decoded_samples: int
    channels: int


def identity(source, settings, decoder, channels):
    data = {'algorithm': ALGORITHM, 'implementation_sha256': fingerprint(__file__),
        'decoder_implementation_sha256': fingerprint(Path(__file__).with_name('speech.py')),
        'source': to_data(source), 'settings': to_data(settings), 'decoder': decoder,
        'channels': channels, 'model': MODEL_SHA256, 'litert': LITERT_VERSION,
        'numpy': NUMPY_VERSION, 'python': platform.python_version(), 'platform': platform.platform(),
        'window': WINDOW, 'hop': HOP, 'cpu_backend': 'litert-builtin-default-cpu-xnnpack-one-thread',
        'laughter_indices': LAUGHTER, 'vocal_indices': VOCAL,
        'decode': 's04-continuous-separate-channel-swr16000', 'floor': '10pct-32ms-rms-db-histogram-v1'}
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _event(source, channel, kind, i, a, b, count, confidence, settings):
    start = floor_fraction(Fraction(a * source.sample_rate, RATE))
    end = source.sample_count if b == count else min(source.sample_count, ceil_fraction(Fraction(b * source.sample_rate, RATE)))
    return Event(f'{source.source_id}:s05:pcm{channel}:{kind}:{i}', source.source_id, kind,
        start, end, max(Fraction(0), Fraction(start, source.sample_rate)-settings.onset),
        min(source.duration, Fraction(end, source.sample_rate)+settings.tail), confidence,
        f'{ALGORITHM};pcm_channel={channel};yamnet_521_or_empirical_signal_contrast;uncalibrated_score',
        'VOCAL_MODEL_OR_SIGNAL_CONTRAST_KEEP_FOR_REVIEW' if kind == 'uncertainty' else '', source.channel_labels)


def overlap_events(analysis):
    """Potential cross-source activity, never identity/bleed or alignment proof.

    Physical channels of a source are unioned before pairing, so shared mics
    remain one group. Compare raw activity, not padded protection intervals.
    """
    sources = [s for s in analysis.sources if s.kind == 'participant_audio']
    bounds = {}
    for s in sources:
        runs = sorted((Fraction(e.start_sample,s.sample_rate)+s.origin,
                       Fraction(e.end_sample,s.sample_rate)+s.origin)
                      for e in analysis.events if e.source_id == s.source_id and e.kind in ('speech','reaction','uncertainty'))
        merged = []
        for a,b in runs:
            if merged and a <= merged[-1][1]:
                merged[-1] = (merged[-1][0],max(b,merged[-1][1]))
            else:
                merged.append((a,b))
        bounds[s.source_id] = merged
    out = []
    for k, left in enumerate(sources):
        for right in sources[k+1:]:
            x,y = bounds[left.source_id],bounds[right.source_id]
            i=j=0
            while i<len(x) and j<len(y):
                a,b=max(x[i][0],y[j][0]),min(x[i][1],y[j][1])
                if a < b:
                    for s in (left,right):
                        start = max(0,floor_fraction((a-s.origin)*s.sample_rate))
                        end = min(s.sample_count,ceil_fraction((b-s.origin)*s.sample_rate))
                        out.append(Event(f'{s.source_id}:s05:overlap:{len(out)}',s.source_id,'overlap',start,end,
                            Fraction(start,s.sample_rate),Fraction(end,s.sample_rate),Fraction(0),
                            'potential_cross_source_activity;declared_origins;no_bleed_or_speaker_decision',
                            'SIMULTANEITY_AND_IDENTITY_UNCERTIFIED',s.channel_labels))
                if x[i][1] <= y[j][1]:
                    i+=1
                else:
                    j+=1
    return tuple(out)


@dataclass(frozen=True)
class FusedResult:
    speech: object
    analysis: Analysis
    tracks: tuple[CachedTrack, ...]
    cache_hits: int

    def summary(self):
        data = self.speech.summary()
        source_ids = [s.source_id for s in self.analysis.sources if s.kind=='participant_audio']
        data['reactions'] = {'algorithm': ALGORITHM, 'model_sha256': MODEL_SHA256,
            'runtime': LITERT_VERSION, 'cpu_only': True, 'cache_hits': self.cache_hits,
            'negative_model_certifies_silence': False, 'automatic_cuts': False,
            'noise_floor_is_supporting_only': True, 'private_labelled_g04_acceptance': 'NOT_ESTABLISHED',
            'tracks': [{'id': f'participant_{i+1:02d}', 'channels': t.channels,
                'decoded_samples_per_channel': t.decoded_samples,
                'floors': [to_data(f) for f in t.floors],
                'reaction_events': sum(e.kind=='reaction' for e in t.events),
                'additional_uncertainty_events': sum(e.kind=='uncertainty' for e in t.events),
                'events': [{'kind': e.kind, 'start_sample': e.start_sample, 'end_sample': e.end_sample,
                    'protected_start': to_data(e.protected_start), 'protected_end': to_data(e.protected_end),
                    'confidence': to_data(e.confidence), 'evidence': e.evidence,
                    'uncertainty_reason': e.uncertainty_reason} for e in t.events],
                'potential_overlap_bounds': [[e.start_sample,e.end_sample] for e in self.analysis.events
                    if e.kind=='overlap' and e.source_id==source_ids[i]]}
                for i,t in enumerate(self.tracks)],
            'potential_overlap_events': sum(e.kind=='overlap' for e in self.analysis.events)}
        return data


def analyze(speech_result, audio_paths, model_path, ffmpeg, cache_dir, *, settings=Settings(),
            chunk_samples=8192, cancel=lambda: False):
    settings = loads(Settings,dumps(settings))
    original = loads(Analysis,dumps(speech_result.analysis))
    if any(e.kind not in ('speech','uncertainty') for e in original.events):
        raise SpeechError('EXPECTED_S04_SPEECH_EVIDENCE')
    sources = [s for s in original.sources if s.kind=='participant_audio']
    if set(audio_paths) != {s.source_id for s in sources}:
        raise SpeechError('AUDIO_MAPPING_MUST_MATCH_INTAKE')
    model = YamnetCPU(model_path)  # Mandatory on hits too; no detector fallback.
    decoder = (tool_version(ffmpeg), fingerprint(ffmpeg))
    tracks,hits = [],0
    for source in sources:
        cancelled(cancel)
        path = Path(audio_paths[source.source_id])
        ap = probe_wav(path)
        if fingerprint(path)!=source.sha256 or (ap.sample_rate,ap.sample_count)!=(source.sample_rate,source.sample_count):
            raise SpeechError('SOURCE_CHANGED_SINCE_INTAKE')
        expected = ceil_fraction(source.duration*RATE)
        key = identity(source,settings,decoder,ap.channels)
        cache_path = Path(cache_dir)/(key+'.json')
        if cache_path.exists():
            try:
                with cache_path.open(encoding='utf-8') as stream:
                    track = loads(CachedTrack,stream.read(8*1024*1024+1))
                if (track.key!=key or track.channels!=ap.channels or abs(track.decoded_samples-expected)>1
                    or tuple(f.pcm_channel for f in track.floors)!=tuple(range(ap.channels))
                    or any(f.blocks!=ceil_fraction(Fraction(track.decoded_samples,512)) for f in track.floors)
                    or any(e.source_id!=source.source_id or e.kind not in ('reaction','uncertainty')
                        or e.channel_labels!=source.channel_labels
                        or not any(e.evidence.startswith(f'{ALGORITHM};pcm_channel={c};') for c in range(ap.channels))
                        for e in track.events)):
                    raise ValueError('Cache mismatch')
                loads(Analysis,dumps(replace(original,events=track.events)))
            except (ValueError,TypeError,OSError):
                raise SpeechError('REACTION_CACHE_CORRUPT_REMOVE_LOCAL_ENTRY_AND_RETRY') from None
            hits+=1
        else:
            events,floors,counts=[],[],[]
            for channel in range(ap.channels):
                blocks=decode_channel(path,channel,ffmpeg,expected,chunk_samples=chunk_samples,cancel=cancel)
                try:
                    regions,count,floor=infer_channel(blocks,model,settings,cancel)
                finally:
                    blocks.close()
                counts.append(count)
                floors.append(Floor(channel,*floor))
                for kind,runs in regions.items():
                    events.extend(_event(source,channel,kind,i,a,b,count,p,settings)
                                  for i,(a,b,p) in enumerate(runs))
            if len(set(counts))!=1:
                raise SpeechError('CHANNEL_DECODE_LENGTH_MISMATCH')
            track=CachedTrack(1,key,tuple(sorted(events,key=lambda e:(e.start_sample,e.end_sample,e.event_id))),tuple(floors),counts[0],ap.channels)
            loads(Analysis,dumps(replace(original,events=track.events)))
            if fingerprint(path)!=source.sha256:
                raise SpeechError('SOURCE_CHANGED_DURING_ANALYSIS')
            cancelled(cancel)
            try:
                atomic_new(cache_path,dumps(track))
            except FileExistsError:
                if cache_path.read_text(encoding='utf-8')!=dumps(track):
                    raise SpeechError('REACTION_CACHE_CONCURRENT_CONTENT_MISMATCH') from None
        tracks.append(track)
    events=original.events+tuple(e for t in tracks for e in t.events)
    provisional=replace(original,events=events)
    events+=overlap_events(provisional)
    header=replace(original.header,run_id='fused-protected-event-analysis',
        settings=original.header.settings+(('reaction_settings',dumps(settings).strip()),
            ('reaction_algorithm',ALGORITHM),('reaction_decoder_version',decoder[0]),('reaction_decoder_sha256',decoder[1])),
        model_versions=original.header.model_versions+(('yamnet_tflite_sha256',MODEL_SHA256),('litert_cpu',LITERT_VERSION)))
    reviews=original.reviews+tuple(Review(s.source_id,Fraction(0),None,
        'REACTION_NEGATIVE_AND_EMPIRICAL_FLOOR_ARE_NOT_SILENCE_OR_BLEED_CERTIFICATES') for s in sources)
    fused=loads(Analysis,dumps(replace(original,header=header,events=events,reviews=reviews)))
    return FusedResult(speech_result,fused,tuple(tracks),hits)
