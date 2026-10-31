"""Ordinary generation, precise scoped edits, and recoverable old jobs."""
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import replace
from fractions import Fraction as F
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import wave
import xml.etree.ElementTree as ET

from interview_auto_editor.application import Application, RunOptions, read_record
from interview_auto_editor.cli import main
from interview_auto_editor.contracts import Analysis, Event, Override, dumps
from interview_auto_editor.desktop_workflow import DesktopJob, review_run
from interview_auto_editor.editing import Mute, ordinary_request, starter_mapping, mute_keys, validate_mutes
from interview_auto_editor.adapters.kdenlive import props, read_starter
from interview_auto_editor.intake import inspect
from interview_auto_editor.planner import PlannerRequest, analysis_digest, plan_pauses
from interview_auto_editor.planner import GapApproval
from interview_auto_editor.adapters.export import native_layout
from interview_auto_editor.turns import build_turns
from s12_coverage_fixture import generate
from test_s12_coverage import example

FFPROBE = os.environ.get('IAE_FFPROBE') or shutil.which('ffprobe')


class EditorChoiceTests(unittest.TestCase):
    def test_explicit_mute_cannot_bypass_any_tracks_keep_or_audible_safeguard(self):
        for action in ('keep','audible'):
            with self.assertRaisesRegex(ValueError,'preservation'):
                validate_mutes(example(),(Mute('p0',F(3),F(5)),),
                    (Override('p1',F(4),F(6),action),))
        validate_mutes(example(),(Mute('p0',F(3),F(5)),),
            (Override('p1',F(5),F(6),'audible'),))

    def test_native_fragmentation_coalesces_optional_units_without_touching_shared_cuts_or_cues(self):
        a = example()
        a = replace(a, sources=tuple(replace(s, duration=F(1200),
            sample_count=1200*s.sample_rate,
            channel_labels=(s.source_id,) if s.kind=='participant_audio' else ()) for s in a.sources))
        sources={s.source_id:s for s in a.sources}
        a = replace(a, events=tuple(Event(str(i),'p'+str(i%2),'speech',
            (i*3+1)*sources['p'+str(i%2)].sample_rate,
            (i*3+2)*sources['p'+str(i%2)].sample_rate,F(i*3+1),F(i*3+2),F(1),
            'independent synthetic construction','',sources['p'+str(i%2)].channel_labels) for i in range(300)))
        request = PlannerRequest(2,analysis_digest(a),'tight',(),())
        result = plan_pauses(a, request)
        original = build_turns(result)
        layout, info = native_layout(result)
        self.assertGreater(len(original.plan.edit_units)-1,128)
        self.assertEqual(len(layout.plan.edit_units)-1,128)
        self.assertEqual(layout.cues,original.cues)
        self.assertEqual(layout.plan.time_map,original.plan.time_map)
        self.assertEqual(layout.plan.analysis,a)
        self.assertEqual(Application().plan(a,request)[-1],layout)
        # Mandatory pause seams may exceed the soft structural budget. Never
        # restore approved removals or merge media across a real shared seam.
        approvals=tuple(GapApproval(str(i),F(i*3)+F(11,5),
            F(i*3)+F(19,5),'construction_label','known synthetic silence') for i in range(180))
        cut_result=plan_pauses(a,replace(request,approvals=approvals))
        cut_layout,_=native_layout(cut_result)
        mandatory={0,*(out.end for _,out in cut_result.plan.time_map.segments())}
        self.assertGreater(len(mandatory),129)
        self.assertTrue(mandatory <= set(cut_layout.plan.edit_units))
        self.assertEqual(cut_layout.plan.time_map,cut_result.plan.time_map)

    def test_mutes_keep_original_coordinates_across_clip_seams(self):
        mutes = (Mute('p0', F(3), F(5)),)
        validate_mutes(example(), mutes)
        self.assertEqual(mute_keys(mutes, 'p1', 0, 300, F(25)), ())
        self.assertEqual(dict(mute_keys(mutes, 'p0', 90, 110, F(25))), {90:-1000,109:-1000})
        self.assertEqual(dict(mute_keys(mutes, 'p0', 70, 130, F(25))),
                         {70:0,75:0,76:-1000,123:-1000,124:0,129:0})
        for bad in ((Mute('video', F(3), F(5)),), (Mute('p0',F(3),F(301,100)),),
                    (Mute('p0',F(3),F(5)),Mute('p0',F(4),F(6)))):
            with self.assertRaises(ValueError): validate_mutes(example(), bad)

    def test_old_job_roundtrip_does_not_add_owner_exercise(self):
        o = RunOptions('run',Path('D:/p'),Path('D:/m'),Path('D:/f'),Path('D:/out'))
        job = DesktopJob.from_options(o)
        historical = replace(job, options=tuple((k,v) for k,v in job.options if k != 'mutes'))
        self.assertEqual(historical.run_options(), o)
        corrected = replace(o, mutes=(Mute('p0',F(3),F(5)),))
        self.assertEqual(DesktopJob.from_options(corrected).run_options(), corrected)

    def test_only_measured_all_channel_digital_silence_can_approve(self):
        a = example()
        # Independent synthetic speech/overlap construction; no labels inferred
        # from the planner or its predictions.
        a = replace(a, events=tuple(Event(str(i),'p0','speech',start*192000,end*192000,
            F(start),F(end),F(1),'known construction','',('a',))
            for i,(start,end) in enumerate(((1,2),(8,9)))))
        with tempfile.TemporaryDirectory() as temp:
            paths = {}
            for source in a.sources[1:]:
                p = Path(temp)/(source.source_id+'.wav');paths[source.source_id]=p
                with wave.open(str(p),'wb') as w:
                    w.setparams((1,2,192000,0,'NONE','not compressed'))
                    for second in range(13):
                        # Both silent only inside [3,7). One PCM bit in either
                        # source is enough to preserve that 100ms interval.
                        data = bytearray(192000*2)
                        if not 3 <= second < 7: data[0]=1
                        w.writeframes(data)
            req = ordinary_request(a, paths)
            self.assertTrue(all(x.basis=='digital_silence' for x in req.approvals))
            result = plan_pauses(a, req)
            self.assertLess(result.plan.time_map.output_frames,result.plan.time_map.source_frames)
            self.assertEqual(result.plan.time_map.map_time(F(1)),F(1))
            self.assertIsNotNone(result.plan.time_map.map_time(F(9)))
            self.assertTrue(all(s.verified_offset is None for s in result.plan.analysis.sources[1:]))


@unittest.skipUnless(FFPROBE, 'ffprobe required')
class EditorCommandTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get('IAE_S04_MODEL') and os.environ.get('IAE_S05_MODEL'), 'Pinned local CPU assets required')
    def test_new_interview_needs_no_mapping_analysis_or_approval_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture=root/'fixture';generate(fixture,FFPROBE)
            out=root/'new-interview'
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(['edit','--project',str(fixture/'constructed-starter.kdenlive'),
                    '--output',str(out),'--cache',str(root/'cache')]),0)
            self.assertEqual(Application.report(out).state,'complete')
            self.assertEqual(len(read_record(Analysis,out/'analysis.json').sources),3)
            self.assertEqual(json.loads((out/'analysis-report.json').read_text())['speech']['cache_hits'],0)

    def test_starter_only_generation_scoped_mute_retention_and_missing_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture=root/'fixture';generate(fixture,FFPROBE)
            project=fixture/'constructed-starter.kdenlive'
            mapping=starter_mapping(read_starter(project))
            a=inspect(project,mapping,FFPROBE).analysis
            a=replace(a, events=(Event('one','participant_01','speech',192000,384000,
                F(1),F(2),F(1),'construction','',('participant_01',)),))
            analysis=root/'analysis.json';analysis.write_text(dumps(a))
            out=root/'ordinary'
            command=['edit','--project',str(project),'--analysis',str(analysis),
                     '--ffprobe',str(FFPROBE),'--output',str(out),
                     '--mute','participant_02','3','5']
            stdout=io.StringIO()
            with redirect_stdout(stdout):self.assertEqual(main(command),0)
            self.assertIn(str(out/'project.kdenlive'),stdout.getvalue())
            self.assertEqual(Application.report(out).state,'complete')
            _,report,_,request=review_run(out)
            self.assertEqual(request.schema_version,2)
            self.assertEqual(report['editor_mutes'][0]['source_id'],'participant_02')
            xml=ET.parse(out/'project.kdenlive').getroot()
            effects=[props(f) for e in xml.iter('entry') for f in e.findall('filter')]
            self.assertTrue(any('-1000' in f.get('level','') for f in effects))
            for name in ('manual_seconds','assisted_seconds','usefulness_score'):
                self.assertNotIn(name,json.dumps(report))
            # A genuine missing source is still actionable; no final output.
            Path(mapping.participants[0].resource).rename(root/'temporarily-moved.wav')
            failure=root/'missing';command[command.index('--output')+1]=str(failure)
            stderr=io.StringIO()
            with redirect_stdout(io.StringIO()),redirect_stderr(stderr):
                self.assertEqual(main(command),1)
            self.assertIn('starter',stderr.getvalue())
            self.assertIn('Affected input:',stderr.getvalue())
            self.assertFalse(failure.exists())
            command[command.index('--mute')+2]='1/0'
            with redirect_stderr(io.StringIO()):self.assertEqual(main(command),1)
