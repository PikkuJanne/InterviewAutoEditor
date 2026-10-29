"""Bounded original-grid PCM audit. Conservative sum bound, never normalization."""
from contextlib import ExitStack
from fractions import Fraction as F
import math
import wave

from .cleanup import db_at, validate_cleanup
from .probe import fingerprint, probe_wav
from .timing import ceil


def pcm_values(raw, width):
    if width not in (1, 2, 3, 4) or len(raw) % width:
        raise ValueError('Unsupported/incomplete integer PCM.')
    scale = 2 ** (8*width-1)
    return [(v-128)/128 for v in raw] if width == 1 else [
        int.from_bytes(raw[i:i+width], 'little', signed=True)/scale for i in range(0, len(raw), width)]


def measure_peaks(result, cleanup, bindings):
    """Audit every retained frame without resampling or summing phase cancellation.

    Sum each source's maximum physical-channel absolute sample. This upper bound
    also covers mono duplication/stereo routing and any attenuation in [0,1].
    A 0.95 ceiling reserves headroom, but is NOT an intersample/codec peak proof.
    Mixed rates use independent absolute rational sample boundaries. Bleed-like
    correlation is diagnostic only and cannot authorize suppression.
    """
    cleanup = validate_cleanup(result, cleanup)
    plan = result.plan
    sources = [s for s in plan.analysis.sources if s.kind == 'participant_audio']
    before = after = max_correlation = 0.0
    measured_frames = correlation_frames = 0
    with ExitStack() as stack:
        rows = []
        for s in sources:
            p = probe_wav(bindings[s.source_id])
            if fingerprint(bindings[s.source_id]) != s.sha256 or (p.sample_rate, p.sample_count) != (s.sample_rate, s.sample_count):
                raise ValueError('Peak audit source identity/grid mismatch.')
            if p.sample_rate > 384000 or p.channels > 8 or plan.time_map.fps < 1:
                raise ValueError('Peak audit buffer bounds exceeded.')
            rows.append((s, p, stack.enter_context(wave.open(str(bindings[s.source_id]), 'rb'))))
        for retained in plan.time_map.retained:
            for f in range(retained.start, retained.end):
                bounds, signals = [], []
                for s, p, wav in rows:
                    lo, hi = ceil(F(f, 1)/plan.time_map.fps*p.sample_rate), ceil(F(f+1, 1)/plan.time_map.fps*p.sample_rate)
                    wav.setpos(lo)
                    raw = wav.readframes(hi-lo)
                    if len(raw) != (hi-lo)*p.channels*p.sample_width:
                        raise ValueError('Incomplete peak audit PCM.')
                    values = pcm_values(raw, p.sample_width)
                    bounds.append(max(map(abs, values), default=0.0))
                    signals.append(values[::p.channels])
                original = math.fsum(bounds)
                # Full original bound deliberately ignores cancellations/gains:
                # attenuation can expose phase cancellation and increase mix peak.
                before = max(before, original)
                after = max(after, math.fsum(v*10**(float(max(db_at(cleanup.spans,s.source_id,F(f)), db_at(cleanup.spans,s.source_id,F(f+1))))/20)
                                               for (s,_,_),v in zip(rows,bounds)))
                measured_frames += 1
                for i, left in enumerate(signals):
                    for j, right in enumerate(signals[i+1:], i+1):
                        if rows[i][1].sample_rate != rows[j][1].sample_rate or len(left) != len(right) or not left:
                            continue
                        xx, yy = math.fsum(x*x for x in left), math.fsum(y*y for y in right)
                        if min(xx, yy) > 1e-12:
                            correlation_frames += 1
                            max_correlation = max(max_correlation, abs(math.fsum(x*y for x,y in zip(left,right))/math.sqrt(xx*yy)))
        if any(fingerprint(bindings[s.source_id]) != s.sha256 for s in sources):
            raise ValueError('Source changed during peak audit.')
    return {'schema_version': 1, 'method': 'retained-frame sum of physical-channel maxima; no cancellation credit',
            'retained_frames_audited': measured_frames, 'original_sum_bound': before,
            'attenuated_sum_bound': after, 'export_safe': before < .95,
            'safety_ceiling': .95, 'gain_reduction_applied': False,
            'correlation_frame_pairs': correlation_frames, 'max_absolute_correlation': max_correlation,
            'bleed_diagnosis': 'Possible correlation only; never a speaker/idle label or suppression authority',
            'intersample_and_encoded_peak_proof': False}
