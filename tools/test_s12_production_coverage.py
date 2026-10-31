"""Production shared-map/CLI EOF regressions. All recordings are synthetic."""
from array import array
from dataclasses import replace
from fractions import Fraction as F
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
import xml.etree.ElementTree as ET

from interview_auto_editor.application import Application
from interview_auto_editor.adapters.kdenlive import props
from interview_auto_editor.contracts import Analysis, Event, Override, dumps, loads
from interview_auto_editor.intake import inspect
from interview_auto_editor.planner import PlannerRequest, GapApproval, analysis_digest, plan_pauses
from interview_auto_editor.timing import ceil
from s12_coverage_fixture import generate
from test_s12_coverage import example

ROOT = Path(__file__).resolve().parents[1]
FFPROBE = os.environ.get('IAE_FFPROBE') or shutil.which('ffprobe')


class ProductionPolicyTests(unittest.TestCase):
    def test_equal_and_either_source_first_preserve_unknowns(self):
        for delta in (F(0), F(4,375), -F(4,375), -F(2)):
            a = example()
            a = replace(a, sources=(a.sources[0],) + tuple(replace(s,
                sample_count=int((F(12)+delta)*s.sample_rate), duration=F(12)+delta)
                for s in a.sources[1:]))
            before = dumps(a)
            r = plan_pauses(a, PlannerRequest(2, analysis_digest(a), 'tight', (), ()))
            self.assertEqual(r.plan.time_map.source_frames, ceil(max(s.duration for s in a.sources)*a.fps))
            self.assertEqual(r.plan.time_map.output_frames, r.plan.time_map.source_frames)
            self.assertEqual(dumps(a), before)
            self.assertTrue(all(s.verified_offset is None for s in r.plan.analysis.sources[1:]))
            for s in a.sources:
                self.assertEqual(r.plan.time_map.map_time(s.duration), s.duration)
            with self.assertRaisesRegex(ValueError, 'origin'):
                plan_pauses(a, PlannerRequest(1, analysis_digest(a), 'tight', (), ()))

    def test_approved_shared_cut_and_audible_restore_with_unequal_ends(self):
        a = example()
        a = replace(a, events=tuple(Event(str(i), 'p0', 'speech', start*192000,
            end*192000, F(start), F(end), F(1), 'construction', '', ('a',))
            for i, (start,end) in enumerate(((1,2),(6,7)))))
        req = PlannerRequest(2, analysis_digest(a), 'tight',
            (GapApproval('gap', F(3), F(5), 'construction_label', 'synthetic'),), ())
        r = plan_pauses(a, req)
        self.assertEqual(r.plan.time_map.output_frames, 251)
        for s in a.sources:
            self.assertEqual(r.plan.time_map.map_time(s.duration), s.duration-2)
        restored = plan_pauses(a, replace(req, overrides=(Override('p0', F(3), F(5), 'audible'),)))
        self.assertEqual(restored.plan.time_map.output_frames, 301)
        with self.assertRaises(ValueError):
            plan_pauses(replace(a, sources=(replace(a.sources[0], sha256='d'*64), *a.sources[1:])), req)


@unittest.skipUnless(FFPROBE, 'ffprobe required')
class ProductionCommandTests(unittest.TestCase):
    def test_normal_export_command_preserves_last_samples_frames_and_blanks(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'fixture'
            generate(folder, FFPROBE)
            from interview_auto_editor.application import read_record
            from interview_auto_editor.intake import MappingManifest
            mapping = read_record(MappingManifest, folder/'mapping.json')
            for label, counts in (('equal', (2304000,2304000)),
                                  ('audio-long', (2306048,2301952)),
                                  ('picture-long', (1920000,2112000))):
                with self.subTest(label=label):
                    for i, count in enumerate(counts,1):
                        with wave.open(str(folder/f'media/participant-{i:02}.wav'), 'wb') as w:
                            w.setparams((1,2,192000,0,'NONE','not compressed'))
                            pcm = array('h', [0])*count
                            pcm[-1] = 1200+i  # last real sample must be addressable
                            w.writeframes(pcm.tobytes())
                    a = inspect(folder/'constructed-starter.kdenlive', mapping, FFPROBE, mapping_base=folder).analysis
                    a = replace(a,events=tuple(Event(str(i),identity,'speech',start*192000,end*192000,
                        F(start),F(end),F(1),'synthetic construction','',(f'participant{i+1}',))
                        for i,(identity,start,end) in enumerate((('p1',1,2),('p2',6,7)))))
                    analysis = folder/f'{label}-analysis.json'; analysis.write_text(dumps(a))
                    request = folder/f'{label}-request.json'
                    request.write_text(dumps(PlannerRequest(2, analysis_digest(a), 'tight', (), ())))
                    out = folder/label
                    command = [sys.executable, '-B', '-m', 'interview_auto_editor', 'export',
                        '--project', str(folder/'constructed-starter.kdenlive'), '--mapping', str(folder/'mapping.json'),
                        '--analysis', str(analysis), '--request', str(request), '--ffprobe', str(FFPROBE),
                        '--output', str(out), '--experimental']
                    p = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
                    self.assertEqual(p.returncode, 2, p.stdout+p.stderr)
                    self.assertEqual(Application.report(out).state, 'complete')
                    report=json.loads((out/'report.json').read_text())
                    self.assertEqual(report['export']['master_linear_bound'], .95/2)
                    exported = ET.parse(out/'project.kdenlive').getroot()
                    nodes = {n.get('id'):n for n in exported if n.get('id')}
                    seq = next(n for n in exported.findall('tractor') if 'kdenlive:sequenceproperties.groups' in props(n))
                    expected_end = ceil(max(s.duration for s in a.sources)*a.fps)
                    self.assertEqual(int(seq.get('out'))+1, expected_end)
                    master=next(f for f in seq.findall('filter') if props(f).get('mlt_service')=='volume')
                    self.assertEqual(props(master)['disable'],'0')
                    self.assertTrue(props(master)['level'].startswith('0=-'))
                    self.assertEqual(sum(c.get('id','').startswith('s07chain') for c in exported.findall('chain')),3)
                    self.assertGreater(len(json.loads(props(seq)['kdenlive:sequenceproperties.groups'])),1)
                    self.assertLessEqual(len(json.loads(props(seq)['kdenlive:sequenceproperties.guides'])),3)
                    self.assertTrue(report['turn_cues'])
                    self.assertGreater(report['export']['diagnostic_cues_in_private_report'],0)
                    for ref in seq.findall('track')[1:]:
                        track = nodes[ref.get('producer')]
                        pl = nodes[track.find('track').get('producer')]
                        entries = pl.findall('entry');e=entries[0]; chain = nodes[e.get('producer')]
                        resource = props(chain)['resource']
                        s = next(s for s in a.sources if (s.kind=='video') == resource.endswith('.mp4') and
                            (s.kind=='video' or resource.endswith(f'participant-0{int(s.source_id[-1])}.wav')))
                        stop = ceil(s.duration*a.fps)
                        self.assertEqual((int(entries[0].get('in')),int(entries[-1].get('out'))+1),(0,stop))
                        self.assertTrue(all(int(left.get('out'))+1==int(right.get('in')) for left,right in zip(entries,entries[1:])))
                        self.assertEqual(len({e.get('producer') for e in entries}),1)
                        self.assertEqual(props(chain)['eof'], 'continue')
                        self.assertEqual(sum(int(b.get('length')) for b in pl.findall('blank')), expected_end-stop)
                        if s.kind=='participant_audio':
                            self.assertLessEqual(F(s.sample_count,s.sample_rate), F(stop,1)/a.fps)
                            with wave.open(str(folder/'media'/Path(resource).name),'rb') as w:
                                w.setpos(w.getnframes()-1)
                                self.assertNotEqual(w.readframes(1), b'\0\0')
                    if label=='audio-long':
                        self.assertIn('MISSING RECORDED PICTURE', props(seq)['kdenlive:sequenceproperties.guides'])


if __name__ == '__main__':
    unittest.main()
