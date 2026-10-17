"""Exact timing properties and strict canonical contract safety checks."""
from dataclasses import replace
from fractions import Fraction as F
import json
import unittest

from interview_auto_editor.contracts import (Analysis, EditPlan, Event, GainPoint, Header,
                                            Override, Review, ShotCandidate, Source, dumps, loads, to_data)
from interview_auto_editor.timing import (FrameRange, SharedTimeMap, ceil, floor, frame_time,
                                         protected_frames, removable_frames, sample_bounds)


def analysis(fps=F(25), frames=300):
    duration = frame_time(frames, fps)
    rate = 48000
    samples = duration * rate
    assert samples.denominator == 1
    header = Header(1, 'synthetic', '0' * 64, '0.3.0', 'experimental', (), ())
    sources = (Source('video', '1' * 64, 'video', 0, 0, duration, F(0), F(0), 'verified', ()),
               Source('audio', '2' * 64, 'participant_audio', rate, int(samples), duration,
                      F(0), F(0), 'verified', ('participant',)))
    return Analysis(header, fps, sources, (), (), ())


def plan():
    return EditPlan(analysis(), SharedTimeMap(F(25), 300, (FrameRange(0, 100), FrameRange(125, 300))),
                    ('manual synthetic gap',), (), (0, 100, 275), (), (), 'exact_coverage')


class TimingTests(unittest.TestCase):
    def test_absolute_fractional_and_mixed_sample_grids_hundreds_of_cuts(self):
        for fps in (F(25), F(24), F(30000, 1001), F(24000, 1001), F(60000, 1001)):
            kept = tuple(FrameRange(i * 10, i * 10 + (10 if i == 499 else 7)) for i in range(500))
            mapping = SharedTimeMap(fps, 5000, kept)
            self.assertEqual(mapping.output_frames, 3503)
            for source, output in mapping.segments():
                t = mapping.map_time(frame_time(source.start, fps))
                self.assertEqual(t, frame_time(output.start, fps))
                for rate in (16000, 44100, 48000, 96000, 192000):
                    a, b = sample_bounds(frame_time(source.start, fps), frame_time(source.end, fps), rate)
                    self.assertLessEqual(F(a, rate), frame_time(source.start, fps))
                    self.assertGreaterEqual(F(b, rate), frame_time(source.end, fps))
                    self.assertLess(frame_time(output.start, fps) - F(floor(t * rate), rate), F(1, rate))
            self.assertEqual(mapping.map_time(frame_time(5000, fps)), frame_time(3503, fps))
            self.assertIsNone(mapping.map_time(frame_time(8, fps)))

    def test_protection_rounds_out_and_removals_in(self):
        for fps in (F(25), F(30000, 1001)):
            start, end = F(10001, 10000), F(22003, 10000)
            a, b = protected_frames(start, end, fps)
            self.assertLessEqual(frame_time(a, fps), start)
            self.assertGreaterEqual(frame_time(b, fps), end)
            a, b = removable_frames(start, end, fps)
            self.assertGreaterEqual(frame_time(a, fps), start)
            self.assertLessEqual(frame_time(b, fps), end)
        self.assertEqual(floor(F(-1, 3)), -1)
        self.assertEqual(ceil(F(-1, 3)), 0)

    def test_map_rejects_lost_handles_reorder_overlap_and_empty(self):
        for intervals in ((), (FrameRange(1, 300),), (FrameRange(0, 299),),
                          (FrameRange(0, 101), FrameRange(100, 300)),
                          (FrameRange(0, 100), FrameRange(100, 300))):
            with self.subTest(intervals=intervals), self.assertRaises(ValueError):
                SharedTimeMap(F(25), 300, intervals)
        for values in ((True, 10), (1.0, 10), (0, 0), (-1, 4)):
            with self.assertRaises(ValueError):
                FrameRange(*values)


class ContractTests(unittest.TestCase):
    def test_roundtrip_analysis_and_plan_are_typed(self):
        original = plan()
        self.assertEqual(loads(EditPlan, dumps(original)), original)
        self.assertEqual(loads(Analysis, dumps(original.analysis)), original.analysis)
        # Mixed rates share one rational extent at fractional FPS.
        a = analysis(F(30000, 1001), 300)
        duration = a.sources[1].duration
        extra = replace(a.sources[1], source_id='second', sha256='3' * 64, sample_rate=44100,
                        sample_count=int(duration * 44100))
        a = replace(a, sources=(*a.sources, extra), shots=(ShotCandidate('video', 10, F(1), 'synthetic picture change', ''),))
        mapping = SharedTimeMap(a.fps, 300, (FrameRange(0, 100), FrameRange(125, 300)))
        p = EditPlan(a, mapping, ('synthetic gap',), (), (0, 275), (), (), 'exact_coverage')
        self.assertEqual(loads(EditPlan, dumps(p)), p)

    def test_schema_unknown_keys_missing_fields_floats_and_duplicates_rejected(self):
        raw = to_data(plan())
        mutations = [
            lambda d: d['analysis']['header'].update(schema_version=2),
            lambda d: d['analysis']['header'].update(schema_version=True),
            lambda d: d.update(new_policy='guess'),
            lambda d: d.pop('tail_policy'),
            lambda d: d['time_map'].update(fps=29.97),
            lambda d: d['time_map'].update(fps={'numerator': 50, 'denominator': 2}),
            lambda d: d['time_map'].update(source_frames=True),
            lambda d: d['analysis']['sources'][0].update(kind='invented'),
        ]
        for mutation in mutations:
            d = json.loads(json.dumps(raw))
            mutation(d)
            with self.subTest(mutation=mutations.index(mutation)), self.assertRaises(ValueError):
                loads(EditPlan, json.dumps(d))
        with self.assertRaises(ValueError):
            loads(Header, '{"schema_version":1,"schema_version":1}')

    def test_unverified_shifted_origin_and_unresolved_tail_cannot_export(self):
        p = plan()
        audio = p.analysis.sources[1]
        for source in (replace(audio, origin_status='unverified', verified_offset=None),
                       replace(audio, verified_offset=F(1, 100)),
                       replace(audio, origin=F(1, 100)),
                       replace(audio, sample_count=audio.sample_count + 1, duration=audio.duration + F(1, audio.sample_rate))):
            with self.assertRaises(ValueError):
                replace(p, analysis=replace(p.analysis, sources=(p.analysis.sources[0], source)))

    def test_protected_speech_reaction_uncertainty_overlap_units_and_keep_override(self):
        p = plan()
        for kind in ('speech', 'reaction', 'uncertainty', 'overlap'):
            event = Event(kind, 'audio', kind, 4 * 48000, 5 * 48000, F(4), F(5), F(9, 10),
                          'synthetic annotation', 'uncertain vocal sound', ('participant',))
            with self.assertRaises(ValueError):
                replace(p, analysis=replace(p.analysis, events=(event,)))
        # Genuine overlap can span an edit-unit boundary when time is retained.
        event = Event('overlap', 'audio', 'overlap', 48000, 3 * 48000, F(1), F(3), F(1),
                      'synthetic annotation', '', ('participant',))
        self.assertEqual(replace(p, analysis=replace(p.analysis, events=(event,)), edit_units=(0, 50, 275)).time_map, p.time_map)
        with self.assertRaises(ValueError):
            replace(p, overrides=(Override('audio', F(4), F(5), 'keep'),))

    def test_references_bounds_gain_and_review_locations(self):
        p = plan()
        for reviews in ((Review('audio', F(6), F(6), 'wrong mapped time'),),
                        (Review('missing', F(1), F(1), 'unresolved'),)):
            with self.assertRaises(ValueError):
                replace(p, reviews=reviews)
        self.assertEqual(replace(p, reviews=(Review('audio', F(6), F(5), 'mapped'),)).reviews[0].output_time, F(5))
        for gains in ((GainPoint('missing', 0, F(1)),), (GainPoint('audio', 576001, F(1)),),
                      (GainPoint('audio', 2, F(1)), GainPoint('audio', 1, F(1)))):
            with self.assertRaises(ValueError):
                replace(p, gains=gains)
        with self.assertRaises(ValueError):
            GainPoint('audio', 0, F(2))
        for units in ((0, 275, 274), (1, 275), (0, 274)):
            with self.assertRaises(ValueError):
                replace(p, edit_units=units)


if __name__ == '__main__':
    unittest.main()
