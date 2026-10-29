"""S06 exact planning regressions; construction labels are not human acceptance."""
from dataclasses import replace
from fractions import Fraction as F
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from interview_auto_editor.contracts import (Analysis, Event, Header, Override, Review,
                                            Source, dumps, loads, to_data)
from interview_auto_editor.planner import (GapApproval, PlannerRequest, PlanningResult,
                                          analysis_digest, explain, plan_pauses)
from interview_auto_editor.timing import frame_time, sample_bounds


ROOT = Path(__file__).resolve().parents[1]


def fixture(fps=F(25), seconds=F(12), rates=(48000, 44100), labels=None):
    assert (seconds * fps).denominator == 1
    sources = [Source('video', '1' * 64, 'video', 0, 0, seconds, F(0), F(0), 'verified', ())]
    for i, rate in enumerate(rates):
        assert (seconds * rate).denominator == 1
        sources.append(Source(f'p{i}', str(i + 2) * 64, 'participant_audio', rate,
                              int(seconds * rate), seconds, F(0), F(0), 'verified',
                              labels[i] if labels else (f'participant{i}',)))
    return Analysis(Header(1, 'S06-construction', '0' * 64, '0.6.0', 'experimental', (), ()),
                    fps, tuple(sources), (), (), ())


def event(a, identity, source, start, end, kind='speech', guards=(F(3, 25), F(1, 5)), confidence=F(1)):
    s = next(s for s in a.sources if s.source_id == source)
    start, end = F(start), F(end)
    assert (start * s.sample_rate).denominator == (end * s.sample_rate).denominator == 1
    return Event(identity, source, kind, int(start * s.sample_rate), int(end * s.sample_rate),
                 max(F(0), start - guards[0]), min(s.duration, end + guards[1]), confidence,
                 'constructed source-time label', 'preserve uncertain sound' if kind == 'uncertainty' else '',
                 s.channel_labels)


def request(a, preset='tight', approvals=None, overrides=()):
    if approvals is None:
        approvals = (GapApproval('construction', F(0), a.sources[0].duration,
                                 'construction_label', 'Known synthetic gap labels; all tracks'),)
    return PlannerRequest(1, analysis_digest(a), preset, approvals, overrides)


def two_events(same=False, fps=F(25), **kwargs):
    a = fixture(fps=fps, **kwargs)
    return replace(a, events=(event(a, 'first', 'p0', 2, 3),
                              event(a, 'second', 'p0' if same else 'p1', 6, 7)))


class RuleTests(unittest.TestCase):
    def test_different_speaker_protection_overrides_quarter_second_residual(self):
        a = two_events()
        result = plan_pauses(a, request(a))
        mapping = result.plan.time_map
        cut = result.decisions[0].removed[0]
        self.assertEqual((cut.start, cut.end), (80, 147))
        self.assertEqual(result.decisions[0].residual_target, F(8, 25))
        self.assertEqual(mapping.output_frames, 233)
        self.assertGreaterEqual(F(3) - frame_time(cut.length, a.fps), F(8, 25))
        self.assertEqual(mapping.retained[0].start, 0)
        self.assertEqual(mapping.retained[-1].end, 300)
        self.assertTrue(mapping.contains(F(0), F(2)))
        self.assertTrue(mapping.contains(F(7), F(12)))

    def test_same_speaker_half_second_and_gentle_preserves_more_time(self):
        for same in (False, True):
            a = two_events(same)
            tight = plan_pauses(a, request(a))
            gentle = plan_pauses(a, request(a, 'gentle'))
            self.assertEqual(tight.decisions[0].rule, 'same' if same else 'different')
            self.assertGreater(gentle.plan.time_map.output_frames, tight.plan.time_map.output_frames)
            target = F(1, 2) if same else F(8, 25)
            self.assertGreaterEqual(F(3) - sum(frame_time(r.length, a.fps) for r in tight.decisions[0].removed), target)

    def test_strict_threshold_and_unknown_or_shared_speaker_preserved(self):
        a = fixture()
        for same, threshold in ((False, F(4, 5)), (True, F(3, 2))):
            for delta, expected in ((F(0), False), (F(1, 25), True)):
                events = (event(a, 'a', 'p0', 2, 3), event(a, 'b', 'p0' if same else 'p1', 3 + threshold + delta, 6))
                result = plan_pauses(replace(a, events=events), request(replace(a, events=events)))
                self.assertEqual(bool(result.decisions[0].removed), expected)
        a = two_events()
        for bad in (replace(a.events[0], confidence=F(89, 100)), replace(a.events[0], kind='reaction')):
            b = replace(a, events=(bad, a.events[1]))
            self.assertEqual(plan_pauses(b, request(b)).plan.time_map.output_frames, 300)
        shared = two_events(labels=(('one', 'two'), ('three',)))
        self.assertEqual(plan_pauses(shared, request(shared)).decisions[0].rule, 'uncertain')

    def test_no_activity_no_approvals_or_continuous_activity_keeps_all(self):
        for a in (fixture(), replace(fixture(), events=(event(fixture(), 'all', 'p0', 0, 12),))):
            result = plan_pauses(a, request(a))
            self.assertEqual(result.plan.time_map.output_frames, 300)
            self.assertEqual(result.decisions, ())
        a = two_events()
        self.assertEqual(plan_pauses(a, request(a, approvals=())).plan.time_map.output_frames, 300)

    def test_every_event_kind_union_and_overlapping_boundaries_protect_all_tracks(self):
        a = two_events()
        for kind in ('speech', 'reaction', 'uncertainty', 'overlap', 'turn'):
            b = replace(a, events=(*a.events, event(a, 'middle', 'p0', 4, 5, kind)))
            result = plan_pauses(b, request(b))
            self.assertTrue(result.plan.time_map.contains(F(4) - F(3, 25), F(5) + F(1, 5)))
            for e in b.events:
                self.assertTrue(result.plan.time_map.contains(e.protected_start, e.protected_end))
        b = replace(a, events=(*a.events, event(a, 'simultaneous', 'p1', 2, 3)))
        self.assertEqual(plan_pauses(b, request(b)).decisions[0].rule, 'uncertain')

    def test_existing_longer_protection_is_never_shrunk(self):
        a = two_events()
        a = replace(a, events=(replace(a.events[0], protected_end=F(5)), a.events[1]))
        r = plan_pauses(a, request(a))
        self.assertEqual(r.decisions[0].residual_target, F(53, 25))
        self.assertTrue(r.plan.time_map.contains(F(2) - F(3, 25), F(5)))
        a = replace(a, events=(replace(a.events[0], protected_end=F(6)), a.events[1]))
        self.assertEqual(plan_pauses(a, request(a)).plan.time_map.output_frames, 300)

    def test_keep_audible_overrides_and_approval_bounds_round_inward(self):
        a = two_events(fps=F(30000, 1001), seconds=F(1001, 100))
        approvals = (GapApproval('narrow', F(32001, 10000), F(58799, 10000), 'human_review', 'Approved entire-track gap'),)
        overrides = (Override('p0', F(4), F(17, 4), 'keep'), Override('p1', F(21, 5), F(9, 2), 'audible'))
        r = plan_pauses(a, request(a, approvals=approvals, overrides=overrides))
        for o in overrides:
            self.assertTrue(r.plan.time_map.contains(o.start, o.end))
        self.assertEqual(len(r.decisions[0].removed), 2)
        for cut in r.decisions[0].removed:
            self.assertGreaterEqual(frame_time(cut.start, a.fps), approvals[0].start)
            self.assertLessEqual(frame_time(cut.end, a.fps), approvals[0].end)
        restored = plan_pauses(a, request(a, overrides=(Override('p0', F(3), F(6), 'keep'),)))
        self.assertEqual(restored.plan.time_map.output_frames, int(a.sources[0].duration * a.fps))

    def test_picture_candidates_cannot_change_plan_or_retained_timing(self):
        from interview_auto_editor.contracts import ShotCandidate
        a = two_events()
        original = plan_pauses(a, request(a))
        b = replace(a, shots=(ShotCandidate('video', 160, F(1), 'late picture switch during speech', ''),))
        self.assertEqual(original.plan.time_map, plan_pauses(b, request(b)).plan.time_map)
        self.assertTrue(original.plan.time_map.contains(F(6), F(7)))


class ExactRegressionTests(unittest.TestCase):
    def test_version_one_construction_snapshots_recompute_and_keep_labelled_content(self):
        for preset, expected, cuts in (('tight', 591, [(80, 147), (430, 522)]),
                                       ('gentle', 603, [(83, 144), (433, 519)])):
            path = ROOT / f'tests/fixtures/planner-v1/construction-{preset}.json'
            snapshot = loads(PlanningResult, path.read_text(encoding='utf-8'))
            self.assertEqual(plan_pauses(snapshot.plan.analysis, snapshot.request), snapshot)
            self.assertEqual(snapshot.plan.time_map.output_frames, expected)
            self.assertEqual([(c.start, c.end) for d in snapshot.decisions for c in d.removed], cuts)
            self.assertEqual(len(snapshot.plan.analysis.events), 7)
            for e in snapshot.plan.analysis.events:
                self.assertTrue(snapshot.plan.time_map.contains(e.protected_start, e.protected_end))
            self.assertTrue(snapshot.plan.time_map.contains(F(0), F(2)))
            self.assertTrue(snapshot.plan.time_map.contains(F(111, 5), F(30)))

    def test_hundreds_of_planned_cuts_fractional_fps_mixed_rates_no_drift(self):
        # 501 one-second activity labels, 500 approved gaps. Absolute mapping
        # checked at every seam/sample grid, independent of gap recurrence.
        for fps in (F(25), F(30000, 1001)):
            duration = F(1505) if fps == 25 else F(8008, 5)
            a = fixture(fps, duration, (16000, 44100, 48000, 96000, 192000))
            a = replace(a, events=tuple(event(a, f'e{i}', f'p{i % 5}', 1 + i * 3, 2 + i * 3) for i in range(501)))
            r = plan_pauses(a, request(a))
            self.assertEqual(len(r.plan.time_map.retained), 501)
            mapping = r.plan.time_map
            removed_frames = sum(c.length for d in r.decisions for c in d.removed)
            self.assertEqual(mapping.source_frames, mapping.output_frames + removed_frames)
            for source, output in mapping.segments():
                self.assertEqual(mapping.map_time(frame_time(source.start, fps)), frame_time(output.start, fps))
                for rate in (16000, 44100, 48000, 96000, 192000):
                    n, _ = sample_bounds(frame_time(output.start, fps), frame_time(output.end, fps), rate)
                    self.assertLess(frame_time(output.start, fps) - F(n, rate), F(1, rate))
            self.assertEqual(mapping.map_time(duration), frame_time(mapping.output_frames, fps))
            for e in a.events:
                self.assertTrue(mapping.contains(e.protected_start, e.protected_end))

    def test_seeded_off_frame_gap_labels_only_authorize_approved_interior(self):
        rng = random.Random(6006)
        for i in range(50):
            a = fixture()
            start = F(rng.randrange(4 * 44100 + 1, 5 * 44100), 44100)
            a = replace(a, events=(event(a, 'a', 'p0', 2, 3), event(a, 'b', 'p1', start, 7)))
            approval = GapApproval('label', F(31, 10), start - F(1, 10), 'construction_label', 'Label independent of model')
            r = plan_pauses(a, request(a, approvals=(approval,)))
            for d in r.decisions:
                for c in d.removed:
                    self.assertGreaterEqual(frame_time(c.start, a.fps), approval.start)
                    self.assertLessEqual(frame_time(c.end, a.fps), approval.end)
            for e in a.events:
                self.assertTrue(r.plan.time_map.contains(e.protected_start, e.protected_end))

    def test_explanation_reviews_null_removed_time_and_inverse_recovery(self):
        a = two_events()
        a = replace(a, reviews=(Review('p0', F(4), None, 'inside approved gap'),
                                Review('p1', F(6), None, 'retained speech'),
                                Review('video', F(12), None, 'endpoint')))
        r = plan_pauses(a, request(a))
        report = explain(r)
        self.assertIsNone(r.plan.reviews[0].output_time)
        self.assertEqual(r.plan.reviews[1].output_time, F(6) - F(67, 25))
        self.assertEqual(report['gaps'][0]['removed'][0]['output_seam'], '16/5')
        self.assertEqual(report['segments'][1]['source_frames'], [147, 300])
        # Original source references/time ranges remain recoverable in plan.
        self.assertEqual(r.plan.analysis, a)
        self.assertEqual(loads(PlanningResult, dumps(r)), r)

    def test_synthetic_pcm_all_track_sample_retention_and_restore(self):
        # Construction-labelled integer PCM, not speech or a Kdenlive render.
        # Every retained sample and labelled activity region survives exactly.
        from array import array
        a = two_events()
        a = replace(a, events=(*a.events, event(a, 'laugh', 'p1', F(21, 5), F(23, 5), 'reaction'),
                              event(a, 'overlap', 'p0', F(13, 2), F(69, 10), 'overlap'),
                              event(a, 'third', 'p0', 9, 10)))
        result = plan_pauses(a, request(a))
        self.assertLess(result.plan.time_map.output_frames, 300)
        for source in a.sources[1:]:
            pcm = array('h', (i % 32767 for i in range(source.sample_count)))
            output = array('h')
            for original, mapped in result.plan.time_map.segments():
                start, end = frame_time(original.start, a.fps) * source.sample_rate, frame_time(original.end, a.fps) * source.sample_rate
                target = frame_time(mapped.start, a.fps) * source.sample_rate
                self.assertEqual(len(output), target)
                output.extend(pcm[int(start):int(end)])
            for e in a.events:
                if e.source_id == source.source_id:
                    target = result.plan.time_map.map_time(F(e.start_sample, source.sample_rate)) * source.sample_rate
                    self.assertEqual(output[int(target):int(target) + e.end_sample - e.start_sample], pcm[e.start_sample:e.end_sample])
            self.assertEqual(len(pcm), source.sample_count)
        restored = plan_pauses(a, request(a, overrides=(Override('p0', F(0), F(12), 'keep'),)))
        self.assertEqual(restored.plan.time_map.output_frames, 300)


class BoundaryTests(unittest.TestCase):
    def test_unverified_shifted_and_unequal_tails_still_refused(self):
        a = two_events()
        source = a.sources[1]
        for bad in (replace(source, origin_status='unverified', verified_offset=None),
                    replace(source, origin=F(1, 100)), replace(source, verified_offset=F(1, 100)),
                    replace(source, duration=source.duration + F(1, source.sample_rate), sample_count=source.sample_count + 1)):
            b = replace(a, sources=(a.sources[0], bad, a.sources[2]))
            with self.assertRaises(ValueError):
                plan_pauses(b, request(b))

    def test_stale_approval_unknown_versions_types_and_out_of_domain_refused(self):
        a = two_events()
        req = request(a)
        with self.assertRaisesRegex(ValueError, 'different analysis'):
            plan_pauses(replace(a, events=a.events[:1]), req)
        for change in ({'schema_version': 2}, {'preset': 'aggressive'}, {'schema_version': True}):
            data = to_data(req)
            data.update(change)
            with self.assertRaises(ValueError):
                loads(PlannerRequest, json.dumps(data))
        with self.assertRaises(ValueError):
            plan_pauses(a, request(a, approvals=(replace(req.approvals[0], end=F(13)),)))
        with self.assertRaises(ValueError):
            plan_pauses(a, replace(req, overrides=(Override('missing', F(4), F(5), 'keep'),)))
        with self.assertRaises(ValueError):
            replace(req.approvals[0], basis='negative_vad')
        with self.assertRaises(ValueError):
            loads(PlannerRequest, dumps(req).replace('"preset": "tight"', '"preset": "tight", "extra": 1'))
        r = plan_pauses(a, req)
        with self.assertRaises(ValueError):
            replace(r, request=replace(req, approvals=()))

    def test_permutation_determinism_and_input_immutable(self):
        a = two_events()
        before = dumps(a)
        first = plan_pauses(a, request(a))
        b = replace(a, events=tuple(reversed(a.events)))
        second = plan_pauses(b, request(b))
        self.assertEqual(first.plan.time_map, second.plan.time_map)
        self.assertEqual(first.decisions, second.decisions)
        self.assertEqual(dumps(a), before)

    def test_cli_atomic_no_overwrite_invalid_input_no_private_error_leak(self):
        a = two_events()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, req, out = (root / name for name in ('analysis.json', 'request.json', 'new.json'))
            source.write_text(dumps(a), encoding='utf-8')
            req.write_text(dumps(request(a)), encoding='utf-8')
            args = [sys.executable, '-B', str(ROOT / 'tools/s06_plan.py'), '--analysis', str(source),
                    '--request', str(req), '--output', str(out)]
            run = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(loads(PlanningResult, out.read_text()).plan.analysis, a)
            original = out.read_bytes()
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 1)
            self.assertEqual(out.read_bytes(), original)
            req.write_text('{"private-detail": "bad"}', encoding='utf-8')
            run = subprocess.run(args[:-1] + [str(root / 'failed.json')], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertNotIn(folder, run.stderr)
            self.assertNotIn('private-detail', run.stderr)
            self.assertFalse((root / 'failed.json').exists())
            self.assertEqual(source.read_text(), dumps(a))


if __name__ == '__main__':
    unittest.main()
