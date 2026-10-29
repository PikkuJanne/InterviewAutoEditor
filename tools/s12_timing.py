"""Two-hour S12 contract/timing stress, without decoding or fabricated GUI evidence."""
from dataclasses import replace
from fractions import Fraction as F
import argparse
import ctypes
import hashlib
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from interview_auto_editor.contracts import Analysis, Event, Header, Source, dumps, loads
from interview_auto_editor.planner import GapApproval, PlannerRequest, PlanningResult, analysis_digest, plan_pauses
from interview_auto_editor.speech import atomic_new
from interview_auto_editor.timing import ceil, frame_time, sample_bounds
from interview_auto_editor.turns import build_turns


def fixture(fps):
    rates = (16000, 44100, 48000, 96000, 192000, 44100, 48000, 192000)
    # Round UP to a common exact frame/sample endpoint. At fractional FPS this
    # exceeds two hours; never assert 7200 seconds is an integral frame domain.
    period = math.lcm(*((F(rate, 1) / fps).denominator for rate in rates))
    frames = ceil(F(7200) * fps / period) * period
    duration = frame_time(frames, fps)
    def sha(identity):
        return hashlib.sha256(identity.encode()).hexdigest()
    sources = (Source('video', sha('S12-generated-video'), 'video', 0, 0, duration,
                      F(0), F(0), 'verified', ()),)
    sources += tuple(Source(f'p{i}', sha(f'S12-generated-audio-{i}'), 'participant_audio',
                            rate, int(duration * rate), duration, F(0), F(0), 'verified', (f'p{i}',))
                     for i, rate in enumerate(rates))
    events = []
    for i in range(600):
        s = sources[1 + i % len(rates)]
        start, end = F(1 + 12 * i), F(2 + 12 * i)
        events.append(Event(f'e{i}', s.source_id, 'speech', int(start * s.sample_rate),
                            int(end * s.sample_rate), start - F(3, 25), end + F(1, 5),
                            F(1), 'Generated interval, not human speech.', '', s.channel_labels))
    a = Analysis(Header(1, 'S12-long-construction', sha('S12-generated-project'), '0.12.0',
                        'experimental', (), ()), fps, sources, tuple(events), (), ())
    approvals = tuple(GapApproval(f'g{i}', F(2 + 12 * i), F(13 + 12 * i),
                                 'construction_label', 'Generated all-source empty interval.')
                      for i in range(599))
    return a, PlannerRequest(1, analysis_digest(a), 'tight', approvals, ())


def peak_working_set():
    if sys.platform != 'win32':
        return None
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize',
            'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
            'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise OSError('Process memory measurement failed.')
    return counters.PeakWorkingSetSize


def measure(fps):
    start = time.perf_counter()
    a, request = fixture(fps)
    result = plan_pauses(a, request)
    planned = time.perf_counter()
    raw = dumps(result)
    assert loads(PlanningResult, raw) == result
    structured = build_turns(result)
    m = structured.plan.time_map
    removed = sum(c.length for d in result.decisions for c in d.removed)
    assert len(result.decisions) == 599 and all(d.removed for d in result.decisions)
    assert m.source_frames == m.output_frames + removed
    assert all(m.contains(e.protected_start, e.protected_end) for e in a.events)
    assert m.contains(F(0), a.events[0].protected_start)
    assert m.contains(a.events[-1].protected_end, a.sources[0].duration)
    anchors = 0
    max_error = F(0)
    for source, output in m.segments():
        # Segment boundaries come directly from one exact map, with every
        # participant's sample grid checked at both endpoints independently.
        for frame in (output.start, output.end):
            t = frame_time(frame, fps)
            for s in a.sources[1:]:
                lo, hi = sample_bounds(t, t + F(1, s.sample_rate), s.sample_rate)
                error = t - F(lo, s.sample_rate)
                assert F(0) <= error < F(1, s.sample_rate)
                max_error = max(max_error, error)
                anchors += 1
        assert output.length == source.length
    assert m.map_time(a.sources[0].duration) == frame_time(m.output_frames, fps)
    # Serialization must not upgrade incomplete originals in order to pass.
    refusals = 0
    source = a.sources[1]
    for bad in (replace(source, origin_status='unverified', verified_offset=None),
                replace(source, duration=source.duration + F(1, source.sample_rate),
                        sample_count=source.sample_count + 1)):
        b = replace(a, sources=(a.sources[0], bad, *a.sources[2:]))
        try:
            plan_pauses(b, replace(request, analysis_sha256=analysis_digest(b)))
        except ValueError:
            refusals += 1
        else:
            raise AssertionError('Long fixture bypassed origin/tail refusal.')
    elapsed = time.perf_counter() - start
    return {'status': 'passed', 'scope': 'generated_contract_timing_only_no_media_decode_export_or_GUI',
            'fps': str(fps), 'duration_seconds': str(a.sources[0].duration),
            'audio_sources': 8, 'sample_rates': [s.sample_rate for s in a.sources[1:]],
            'source_frames': m.source_frames, 'output_frames': m.output_frames,
            'removed_frames': removed, 'cuts': len(m.retained) - 1,
            'protected_labels_retained': 600, 'protected_label_denominator': 600,
            'sample_grid_endpoint_checks': anchors, 'maximum_output_grid_rounding_seconds': str(max_error),
            'cumulative_map_drift_frames': 0, 'origin_tail_refusals': refusals,
            'planning_seconds': round(planned - start, 6), 'total_seconds': round(elapsed, 6),
            'peak_process_working_set_bytes': peak_working_set(),
            'serialized_planning_bytes': len(raw.encode('utf-8')),
            'actual_render_sync': 'NOT_RUN', 'actual_native_editability': 'NOT_RUN',
            'full_interview_acceptance': 'NOT_RUN'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fps', choices=('25', '30000/1001'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    report = measure(F(args.fps))
    atomic_new(args.output, json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
