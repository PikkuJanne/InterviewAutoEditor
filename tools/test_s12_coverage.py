"""EOF preview tests: exact retention, stale review and unchanged v1 refusal."""
from dataclasses import replace
from fractions import Fraction as F
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.contracts import Analysis, EditPlan, Header, Source, dumps, loads
from s12_coverage import CoveragePreview, CoverageReview, preview_coverage
from interview_auto_editor.planner import PlannerRequest, analysis_digest, plan_pauses
from interview_auto_editor.timing import FrameRange, SharedTimeMap
from interview_auto_editor.probe import fingerprint, probe_wav


def example(fps=F(25), rates=(192000, 48000)):
    end = F(12)
    sources = (Source('video', 'a'*64, 'video', 0, 0, end, F(0), F(0), 'verified', ()),)
    for i, (rate, delta) in enumerate(zip(rates, (F(4,375), -F(4,375)))):
        samples = int((end + delta) * rate)
        sources += (Source(f'p{i}', str(i+1)*64, 'participant_audio', rate, samples,
            F(samples, rate), F(0), None, 'unverified', ('shared-a', 'shared-b') if i else ('a',)),)
    return Analysis(Header(1, 'coverage-test', 'b'*64, 'test', 'kdenlive-26.08.2-experimental', (), ()), fps, sources, (), (), ())


def review(analysis):
    return CoverageReview(2, analysis_digest(analysis), 'preserve_samples_mark_empty_eof',
        'construction reviewer', 'Synthetic sample counts; only empty EOF representation accepted', True)


class CoverageTests(unittest.TestCase):
    def test_mixed_grid_retention_and_exact_empty_coverage(self):
        a = example()
        before = dumps(a)
        p = preview_coverage(a, review(a))
        self.assertEqual(p.time_map.source_frames, 301)
        self.assertEqual(p.sources[0].clip_end_frame, 300)
        self.assertEqual(p.sources[1].retained_samples, 2306048)
        self.assertEqual(p.sources[1].empty_until - p.sources[1].source_end, F(11,375))
        self.assertEqual(p.sources[2].empty_until - p.sources[2].source_end, F(19,375))
        self.assertEqual(dumps(a), before)
        self.assertEqual(loads(CoveragePreview, dumps(p)), p)
        self.assertEqual(a.sources[1].verified_offset, None)
        self.assertEqual(a.sources[1].origin_status, 'unverified')

    def test_old_origin_and_exact_tail_refusals_survive(self):
        a = example()
        preview_coverage(a, review(a))
        with self.assertRaisesRegex(ValueError, 'origin'):
            plan_pauses(a, PlannerRequest(1, analysis_digest(a), 'tight', (), ()))
        verified = replace(a, sources=tuple(replace(s, origin_status='verified', verified_offset=F(0)) for s in a.sources))
        with self.assertRaisesRegex(ValueError, 'tails'):
            plan_pauses(verified, PlannerRequest(1, analysis_digest(verified), 'tight', (), ()))
        with self.assertRaises(ValueError):
            loads(EditPlan, dumps(preview_coverage(a, review(a))))

    def test_stale_rejected_or_malformed_review(self):
        a = example()
        for r in (replace(review(a), accepted=False), replace(review(a), analysis_sha256='c'*64)):
            with self.assertRaises(ValueError):
                preview_coverage(a, r)
        raw = json.loads(dumps(review(a)))
        for key, value in (('schema_version', 1), ('accepted', 1), ('policy', 'exact_coverage'), ('unexpected', True)):
            changed = {**raw, key: value}
            with self.assertRaises(ValueError):
                loads(CoverageReview, json.dumps(changed))
        for s in (replace(a.sources[1], sha256='d'*64), replace(a.sources[1], origin=F(1,1000))):
            changed = replace(a, sources=(a.sources[0], s, a.sources[2]))
            with self.assertRaises(ValueError):
                preview_coverage(changed, review(a))

    def test_modified_preview_map_samples_and_source_order_refuse(self):
        a = example()
        p = preview_coverage(a, review(a))
        for changes in ({'time_map': SharedTimeMap(F(25), 301, (FrameRange(0, 100), FrameRange(101,301)))},
                        {'sources': tuple(reversed(p.sources))},
                        {'sources': (p.sources[0], replace(p.sources[1], retained_samples=1), p.sources[2])}):
            with self.assertRaises(ValueError):
                replace(p, **changes)

    def test_fractional_fps_absolute_sample_end(self):
        a = example(F(30000,1001))
        video_end = F(360)*1001/30000
        sources = (replace(a.sources[0], duration=video_end),) + tuple(replace(s,
            sample_count=int(video_end*s.sample_rate) + sign,
            duration=F(int(video_end*s.sample_rate)+sign, s.sample_rate))
            for s, sign in zip(a.sources[1:], (1,-1)))
        a = replace(a, sources=sources)
        p = preview_coverage(a, review(a))
        self.assertEqual(p.time_map.source_frames, 361)
        for s, c in zip(a.sources, p.sources):
            self.assertEqual(s.duration, c.source_end)
            self.assertEqual(s.sample_count, c.retained_samples)
        for delta in (F(1,25), -F(1,25)):
            a = example()
            s = a.sources[1]
            count = int((F(12)+delta)*s.sample_rate)
            changed = replace(a, sources=(a.sources[0], replace(s, sample_count=count, duration=F(count,s.sample_rate)), a.sources[2]))
            with self.assertRaisesRegex(ValueError, 'complete picture frame'):
                preview_coverage(changed, review(changed))

    @unittest.skipUnless(os.environ.get('IAE_FFPROBE'), 'Explicit local ffprobe required')
    def test_generated_native_representation_does_not_certify_sources(self):
        import xml.etree.ElementTree as ET
        from s12_coverage_fixture import generate
        from interview_auto_editor.adapters.kdenlive import props
        with tempfile.TemporaryDirectory(prefix='iae-eof-') as temporary:
            folder = Path(temporary)/'generated'
            report = generate(folder, os.environ['IAE_FFPROBE'])
            self.assertEqual(report['coverage_frames'], 301)
            self.assertFalse(report['production_export'])
            a = loads(Analysis, (folder/'analysis.json').read_text(encoding='utf-8'))
            self.assertTrue(all(s.origin_status=='unverified' and s.verified_offset is None for s in a.sources if s.kind=='participant_audio'))
            self.assertEqual([probe_wav(folder/f'media/participant-{i:02}.wav').sample_count for i in (1,2)], [2306048,2301952])
            root = ET.parse(folder/'constructed-coverage.kdenlive').getroot()
            nodes = {n.get('id'): n for n in root if n.get('id')}
            entries = [(props(nodes[e.get('producer')])['resource'], e.get('out')) for pl in root.findall('playlist') if pl.get('id')!='main_bin' for e in pl.findall('entry')]
            self.assertEqual(sorted((Path(r).name,end) for r,end in entries), [('participant-01.wav','300'),('participant-02.wav','299'),('zoom-source.mp4','299')])
            for chain in root.findall('chain'):
                if props(chain).get('resource','').endswith('.mp4'):
                    self.assertEqual(props(chain)['audio_index'], '-1')
            # The shorter audio and recorded picture each end one frame early.
            self.assertEqual(sum(int(b.get('length')) for pl in root.findall('playlist') for b in pl.findall('blank')), 2)
            manifest = json.loads((folder/'construction.json').read_text(encoding='utf-8'))
            self.assertTrue(all(fingerprint(folder/p['path'])==p['sha256'] for p in manifest['files']))
            with self.assertRaises(FileExistsError):
                generate(folder, os.environ['IAE_FFPROBE'])


if __name__ == '__main__':
    unittest.main()
