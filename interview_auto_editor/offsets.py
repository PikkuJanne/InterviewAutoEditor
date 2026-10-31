"""Bounded diagnostic correlation, never an automatic correction estimate.

Positive lag means the participant waveform occurs later than the reference.
Evidence uses explicit source-time windows; silence, repeated tones and changing
lags fail closed. Downsampled diagnostic buffers are not replacement media.
"""
from array import array
from dataclasses import dataclass
from fractions import Fraction
import math
import sys

from .adapters.kdenlive import IntakeError
from .probe import run_bounded
from .timing import integer, rational


@dataclass(frozen=True)
class Anchor:
    source_time: Fraction
    lag_samples: int | None
    sample_rate: int
    score: Fraction
    status: str

    def __post_init__(self):
        rational(self.source_time)
        integer(self.sample_rate, 1)
        if self.source_time < 0 or not -1 <= rational(self.score) <= 1:
            raise IntakeError('INVALID_OFFSET_ANCHOR')
        if self.lag_samples is not None and type(self.lag_samples) is not int:
            raise IntakeError('INVALID_OFFSET_ANCHOR')
        if self.status not in ('RELIABLE_ANCHOR', 'SILENT_OR_INACTIVE', 'AMBIGUOUS_OR_LOW_CONFIDENCE') or (self.status == 'RELIABLE_ANCHOR') != (self.lag_samples is not None):
            raise IntakeError('INVALID_OFFSET_ANCHOR')


@dataclass(frozen=True)
class OriginDiagnostic:
    status: str
    anchors: tuple[Anchor, ...]
    suggested_correction: None = None


def correlate(reference, candidate, rate=2000, max_lag=200):
    integer(rate, 1)
    integer(max_lag, 1)
    if len(reference) != len(candidate) or not 4 * max_lag < len(reference) <= 20000 or max_lag > 1000:
        raise IntakeError('CORRELATION_BUFFER_BOUNDS')
    if not all(math.isfinite(x) for x in (*reference, *candidate)):
        raise IntakeError('NONFINITE_DIAGNOSTIC_AUDIO')
    # Fixed central reference window gives every lag identical support. Energy
    # is normalized per candidate position; no duration-based alignment inference.
    a = list(reference[max_lag:-max_lag])
    mean = sum(a) / len(a)
    a = [x - mean for x in a]
    ea = sum(x * x for x in a)
    if ea / len(a) < 1e-10:
        return None, Fraction(0), 'SILENT_OR_INACTIVE'
    scores = []
    n = len(a)
    for lag in range(-max_lag, max_lag + 1):
        b = candidate[max_lag + lag:max_lag + lag + n]
        mb = sum(b) / n
        eb = sum((x - mb) ** 2 for x in b)
        score = sum(x * (y - mb) for x, y in zip(a, b)) / math.sqrt(ea * eb) if eb > 1e-10 * n else 0
        scores.append((score, lag))
    best, lag = max(scores)
    # Nearby peaks describe one broad peak; distinct repeated peaks are unsafe.
    second = max((s for s, k in scores if abs(k - lag) > max(2, rate // 200)), default=best)
    score = Fraction(round(best * 1000000), 1000000)
    if best < 0.65 or best - second < 0.08 or abs(lag) == max_lag:
        return None, score, 'AMBIGUOUS_OR_LOW_CONFIDENCE'
    return lag, score, 'RELIABLE_ANCHOR'


def diagnose(anchors, duration):
    rational(duration, positive=True)
    anchors = tuple(anchors)
    if any(a.source_time < 0 or a.source_time >= duration for a in anchors):
        raise IntakeError('ANCHOR_OUTSIDE_SOURCE')
    good = [a for a in anchors if a.status == 'RELIABLE_ANCHOR' and a.lag_samples is not None]
    if len(good) < 3 or len({a.source_time for a in good}) < 3 or max(a.source_time for a in good) - min(a.source_time for a in good) < duration / 2:
        return OriginDiagnostic('UNVERIFIED_INSUFFICIENT_ANCHORS', anchors)
    lags = [Fraction(a.lag_samples, a.sample_rate) for a in good]
    tolerance = max(Fraction(1, a.sample_rate) for a in good)
    if max(lags) - min(lags) > 2 * tolerance:
        return OriginDiagnostic('INCONSISTENT_LAGS_REVIEW_OFFSET_OR_DRIFT', anchors)
    if any(abs(lag) > tolerance for lag in lags):
        return OriginDiagnostic('OFFSET_DETECTED', anchors)
    if len(good) != len(anchors):
        return OriginDiagnostic('UNVERIFIED_AMBIGUOUS_WINDOWS', anchors)
    return OriginDiagnostic('ZERO_LAG_WITHIN_DIAGNOSTIC_RESOLUTION', anchors)


def decode_window(path, ffmpeg, start, stream_index, rate=2000, seconds=4):
    rational(start)
    integer(stream_index)
    if start < 0 or not 1 <= seconds <= 8 or not 500 <= rate <= 2000:
        raise IntakeError('DIAGNOSTIC_WINDOW_BOUNDS')
    # FFmpeg accepts decimal seconds; this is a bounded diagnostic seek only.
    position = f'{float(start):.9f}'
    raw = run_bounded([ffmpeg, '-nostdin', '-v', 'error', '-protocol_whitelist', 'file,pipe',
                       '-ss', position, '-i', path, '-t', str(seconds), '-map', f'0:{stream_index}',
                       '-ac', '1', '-ar', str(rate), '-f', 'f32le', 'pipe:1'], timeout=45, limit=rate * seconds * 4)
    data = array('f')
    data.frombytes(raw)
    if sys.byteorder != 'little':
        data.byteswap()
    if len(data) != rate * seconds:
        raise IntakeError('TRUNCATED_DIAGNOSTIC_WINDOW')
    return data


def diagnostic_windows(video, audio, ffmpeg, starts, duration, reference_stream=1, participant_stream=0):
    anchors = []
    for start in starts:
        if start + 4 > duration:
            raise IntakeError('ANCHOR_OUTSIDE_SOURCE')
        ref = decode_window(video, ffmpeg, start, reference_stream)
        candidate = decode_window(audio, ffmpeg, start, participant_stream)
        lag, score, status = correlate(ref, candidate)
        anchors.append(Anchor(start, lag, 2000, score, status))
    return diagnose(anchors, duration)
