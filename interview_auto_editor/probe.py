"""Local bounded ffprobe and exact PCM WAV inspection. No media writes."""
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import os
import re
from pathlib import Path
import struct
import subprocess
import tempfile
import time
import wave

from .adapters.kdenlive import IntakeError


def fingerprint(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def run_bounded(args, timeout=120, limit=64 * 1024 * 1024):
    """Argument arrays, disk-spooled bounded output, fixed private-safe errors."""
    try:
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            process = subprocess.Popen([str(a) for a in args], stdout=out, stderr=err,
                                       stdin=subprocess.DEVNULL, shell=False)
            try:
                deadline = time.monotonic() + timeout
                while process.poll() is None:
                    if time.monotonic() > deadline or os.fstat(out.fileno()).st_size > limit or os.fstat(err.fileno()).st_size > limit:
                        raise IntakeError('PROBE_TIME_OR_OUTPUT_LIMIT')
                    time.sleep(0.02)
                if process.returncode or os.fstat(out.fileno()).st_size > limit or os.fstat(err.fileno()).st_size > limit:
                    raise IntakeError('DECODER_OR_PROBE_FAILED')
                if os.fstat(err.fileno()).st_size:
                    raise IntakeError('DECODER_REPORTED_ERRORS')
                out.seek(0)
                return out.read(limit + 1)
            finally:
                if process.poll() is None:
                    process.kill()
                process.wait()
    except OSError as exc:
        raise IntakeError('LOCAL_TOOL_UNAVAILABLE') from exc


def tool_version(executable):
    first = run_bounded([executable, '-version'], timeout=10, limit=65536).decode('utf-8', errors='replace').splitlines()[0]
    # Build configuration may contain developer paths; only the version token.
    parts = first.split()
    return parts[2] if len(parts) >= 3 and parts[1] == 'version' and re.fullmatch(r'[A-Za-z0-9+._-]{1,100}', parts[2]) else 'UNKNOWN'


@dataclass(frozen=True)
class AudioProbe:
    sample_rate: int
    sample_count: int
    channels: int
    sample_width: int

    @property
    def duration(self):
        return Fraction(self.sample_count, self.sample_rate)


def probe_wav(path):
    """PCM/WAVE_EXTENSIBLE supported by Python >=3.12; RF64 not guessed.

    Inspect RIFF chunk boundaries against physical size before trusting a WAV
    header. Data is never decoded, downmixed or resampled by this operation.
    """
    path = Path(path)
    try:
        size = path.stat().st_size
        with path.open('rb') as stream:
            header = stream.read(12)
            if len(header) != 12 or header[:4] != b'RIFF' or header[8:] != b'WAVE':
                raise IntakeError('UNSUPPORTED_WAV_CONTAINER')
            declared = struct.unpack('<I', header[4:8])[0] + 8
            if declared != size:
                raise IntakeError('TRUNCATED_OR_INCONSISTENT_WAV')
            data_size = None
            while stream.tell() < declared:
                chunk = stream.read(8)
                if len(chunk) != 8:
                    raise IntakeError('TRUNCATED_WAV_CHUNK')
                tag, length = chunk[:4], struct.unpack('<I', chunk[4:])[0]
                if stream.tell() + length + length % 2 > declared:
                    raise IntakeError('TRUNCATED_WAV_CHUNK')
                if tag == b'data':
                    if data_size is not None:
                        raise IntakeError('MULTIPLE_WAV_DATA_CHUNKS')
                    data_size = length
                stream.seek(length + length % 2, 1)
        with wave.open(str(path), 'rb') as wav:
            result = AudioProbe(wav.getframerate(), wav.getnframes(), wav.getnchannels(), wav.getsampwidth())
            if wav.getcomptype() != 'NONE' or min(result.sample_rate, result.sample_count, result.channels, result.sample_width) <= 0 or data_size != result.sample_count * result.channels * result.sample_width:
                raise IntakeError('INCONSISTENT_PCM_SAMPLE_COUNT')
        return result
    except (OSError, wave.Error, EOFError, struct.error) as exc:
        raise IntakeError('WAV_PROBE_FAILED') from exc


@dataclass(frozen=True)
class VideoProbe:
    fps: Fraction
    time_base: Fraction
    start: Fraction
    duration: Fraction
    metadata_duration: Fraction | None
    decoded_frames: int
    cadence: str
    embedded_audio_streams: int


def probe_video(path, ffprobe, stream_index=0):
    common = [ffprobe, '-v', 'error', '-protocol_whitelist', 'file,pipe', '-i', Path(path).resolve()]
    try:
        metadata = json.loads(run_bounded(common + ['-show_streams', '-of', 'json']))
        streams = metadata['streams']
        selected = next(s for s in streams if s['index'] == stream_index)
        if selected['codec_type'] != 'video':
            raise IntakeError('SELECTED_STREAM_IS_NOT_VIDEO')
        fps = Fraction(selected['r_frame_rate'])
        tb = Fraction(selected['time_base'])
        if fps <= 0 or tb <= 0:
            raise ValueError()
        audit = json.loads(run_bounded(common + ['-select_streams', str(stream_index), '-show_frames',
                          '-show_entries', 'frame=best_effort_timestamp', '-of', 'json']))['frames']
        pts = [int(f['best_effort_timestamp']) for f in audit]
        if len(pts) < 2:
            raise IntakeError('INSUFFICIENT_FRAME_TIMESTAMPS')
        period = 1 / fps
        # Compare absolute positions, not just adjacent steps, so rounded ticks
        # cannot conceal a different rate or cumulative drift.
        cfr = all(abs((p - pts[0]) * tb - i * period) <= tb for i, p in enumerate(pts))
        cfr = cfr and all(b > a for a, b in zip(pts, pts[1:]))
        reported = selected.get('nb_frames')
        if reported not in (None, 'N/A') and int(reported) != len(pts):
            raise IntakeError('TRUNCATED_VIDEO_FRAME_COUNT')
        duration = (pts[-1] - pts[0]) * tb + period
        md = int(selected['duration_ts']) * tb if 'duration_ts' in selected else None
        if md is not None and abs(md - duration) > max(period, tb):
            raise IntakeError('INCONSISTENT_VIDEO_DURATION')
        return VideoProbe(fps, tb, pts[0] * tb, duration, md, len(pts),
                          'CFR_AUDITED' if cfr else 'VFR_OR_DISCONTINUOUS',
                          sum(s['codec_type'] == 'audio' for s in streams))
    except (KeyError, TypeError, ValueError, StopIteration, ZeroDivisionError) as exc:
        if isinstance(exc, IntakeError):
            raise
        raise IntakeError('INVALID_OR_MISSING_PROBE_TIMING') from exc
