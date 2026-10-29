"""S10 application integration: no invented media provenance or origin approval."""
from dataclasses import replace
from fractions import Fraction as F
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from interview_auto_editor.application import (Application, Journal, RunError, RunManifest,
    RunOptions, _rename_new, _run_lock, _validate_reused_summary, read_record)
from interview_auto_editor.cancellation import Cancelled, scope
from interview_auto_editor.cleanup import CleanupRequest, planning_digest
from interview_auto_editor.contracts import Analysis, Override, dumps
from interview_auto_editor.planner import PlanningResult
from interview_auto_editor.probe import fingerprint, run_bounded

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/s09-picture-26.08.2'
FFPROBE = os.environ.get('IAE_FFPROBE') or shutil.which('ffprobe')
FFMPEG = os.environ.get('IAE_FFMPEG') or shutil.which('ffmpeg')
SPEECH = os.environ.get('IAE_S04_MODEL')
REACTION = os.environ.get('IAE_S05_MODEL')


class AtomicTests(unittest.TestCase):
    def test_directory_publish_never_replaces_even_empty_destination(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); source = root/'source'; target = root/'target'
            source.mkdir(); target.mkdir()
            (source/'data').write_text('preserve')
            with self.assertRaises(OSError): _rename_new(source, target)
            self.assertEqual((source/'data').read_text(), 'preserve')
            self.assertEqual(list(target.iterdir()), [])

    def test_lock_never_modifies_existing_user_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'lock'; p.write_bytes(b'user owned')
            with self.assertRaisesRegex(RunError, 'LOCK_CONFLICT'):
                with _run_lock(p): pass
            self.assertEqual(p.read_bytes(), b'user owned')

    def test_os_lock_survives_marker_and_recovers_after_process_death(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'lock'
            with _run_lock(p):
                script='from pathlib import Path; from interview_auto_editor.application import _run_lock; import sys;\nwith _run_lock(Path(sys.argv[1])): print("owned", flush=True)'
                denied=subprocess.run([sys.executable,'-c',script,str(p)],capture_output=True)
                self.assertNotEqual(denied.returncode,0)
            proc=subprocess.Popen([sys.executable,'-c',script.replace('print("owned", flush=True)','print("owned", flush=True); __import__("time").sleep(30)'),str(p)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                self.assertEqual(proc.stdout.readline().strip(),b'owned')
                proc.kill(); proc.wait(timeout=5)
            finally:
                proc.kill() if proc.poll() is None else None
                proc.communicate(timeout=5)
            with _run_lock(p): pass

    def test_bounded_child_is_killed_and_reaped_on_cooperative_cancel(self):
        event=threading.Event(); timer=threading.Timer(.15,event.set)
        timer.start(); before=time.monotonic()
        try:
            with scope(event.is_set), self.assertRaises(Cancelled):
                run_bounded([sys.executable,'-c','import time; time.sleep(30)'])
        finally: timer.cancel()
        self.assertLess(time.monotonic()-before,5)

    def test_journal_adopts_only_exact_orphan_and_refuses_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'partial'; j=Journal(root,'inspect','0'*64,False)
            (root/'intake.json').write_text('same\n',encoding='utf-8',newline='\n')
            j.write('intake.json','same\n')
            j.write('intake.json','same\n')
            with self.assertRaisesRegex(RunError,'CONFLICT'):j.write('intake.json','different\n')
            (root/'intake.json').write_text('corrupt')
            with self.assertRaisesRegex(RunError,'CHANGED'):Journal(root,'inspect','0'*64,True)

    def test_unknown_manifest_version_and_missing_complete_artifact_refuse(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); j=Journal(root/'stage','run','0'*64,False)
            j.save(state='complete')
            with self.assertRaisesRegex(RunError,'INCOMPLETE'):Application.report(root/'stage')
            raw=j.path.read_text().replace('"schema_version": 1','"schema_version": 2')
            j.path.write_text(raw)
            with self.assertRaises(ValueError):read_record(RunManifest,j.path)

    def test_orphan_analysis_summary_accepts_only_valid_changed_cache_counts(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'summary.json'
            current={'speech':{'cache_hits':1,'tracks':[{'event':'kept'}]}}
            p.write_text(json.dumps({'speech':{'cache_hits':0,'tracks':[{'event':'kept'}]}}))
            _validate_reused_summary(p,current)
            for raw in ('{}','{"speech":{"cache_hits":true,"tracks":[{"event":"kept"}]}}',
                        '{"speech":{"cache_hits":0,"tracks":[{"event":"lost"}]}}',
                        '{"speech":{},"speech":{}}'):
                p.write_text(raw)
                with self.assertRaises(ValueError):_validate_reused_summary(p,current)


@unittest.skipUnless(FFPROBE, 'Set local IAE_FFPROBE for actual input/export gates.')
class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.fixture=self.root/'fixture space \u00e4'
        shutil.copytree(FIXTURE,self.fixture)
        self.base=read_record(PlanningResult,self.fixture/'planning-result.json')
        self.request=self.root/'request.json'
        self.request.write_text(dumps(self.base.request),encoding='utf-8')
        self.originals={p:fingerprint(p) for p in (self.fixture/'before.kdenlive',*sorted((self.fixture/'media').iterdir()))}
        self.o=RunOptions('run',self.fixture/'before.kdenlive',self.fixture/'mapping.json',
            Path(FFPROBE),self.root/'run',analysis=self.fixture/'analysis.json',
            request=self.request,picture=self.fixture/'picture-analysis.json',
            cleanup_request=self.fixture/'cleanup-request.json',experimental=True)

    def tearDown(self):
        self.assertEqual({p:fingerprint(p) for p in self.originals},self.originals)
        self.temp.cleanup()

    def partial(self, o=None):
        p=(o or self.o).output
        return p.with_name('.'+p.name+'.incomplete')

    def test_end_to_end_refined_cleanup_export_matches_existing_adapter_bytes(self):
        manifest=Application().run(self.o)
        self.assertEqual(manifest.state,'complete')
        self.assertFalse(self.partial().exists())
        report=json.loads((self.o.output/'report.json').read_text())
        self.assertEqual(report['export']['output_frames'],267)
        self.assertEqual(report['export']['groups'],6)
        self.assertEqual(report['export']['gain_spans'],4)
        cleanup=read_record(CleanupRequest,self.fixture/'cleanup-request.json')
        refined=read_record(PlanningResult,self.o.output/'refined-planning-result.json')
        self.assertEqual(cleanup.planning_sha256,planning_digest(refined))
        from interview_auto_editor.adapters.export import export_project
        from interview_auto_editor.cleanup import CleanupResult
        from interview_auto_editor.picture import PictureAnalysis
        bindings={'video':self.fixture/'media/zoom-source.mp4',**{f'p{i}':self.fixture/f'media/participant-{i+1:02}.wav' for i in range(2)}}
        expected=self.o.output/'expected.kdenlive'
        export_project(self.base,self.o.project,bindings,{'p0':'Participant 01','p1':'Participant 02'},expected,FFPROBE,experimental=True,
            picture=read_record(PictureAnalysis,self.o.picture),cleanup=read_record(CleanupResult,self.fixture/'cleanup-result.json'))
        self.assertEqual(expected.read_bytes(),(self.o.output/'project.kdenlive').read_bytes())
        expected.unlink()
        self.assertEqual(Application.report(self.o.output),manifest)

    def test_failure_after_project_publication_resumes_without_partial_final(self):
        def fail(stage):
            if stage=='reporting':raise OSError('private exception must not escape CLI')
        with self.assertRaises(OSError):Application(progress=fail).run(self.o)
        self.assertFalse(self.o.output.exists())
        self.assertTrue((self.partial()/'project.kdenlive').exists())
        self.assertEqual(Application.report(self.partial()).state,'failed')
        before=fingerprint(self.partial()/'project.kdenlive')
        result=Application().run(self.o,resume=True)
        self.assertEqual(result.attempt,2)
        self.assertEqual(fingerprint(self.o.output/'project.kdenlive'),before)

    def test_abrupt_process_exit_before_rename_recovers_complete_staged_journal(self):
        script='import os; import interview_auto_editor.application as a; a._rename_new=lambda *args:os._exit(88); from interview_auto_editor.cli import main; raise SystemExit(main())'
        cmd=[sys.executable,'-c',script,'run','--project',str(self.o.project),'--mapping',str(self.o.mapping),
            '--analysis',str(self.o.analysis),'--request',str(self.request),'--picture',str(self.o.picture),
            '--cleanup-request',str(self.o.cleanup_request),'--ffprobe',FFPROBE,'--output',str(self.o.output),'--experimental']
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,88)
        self.assertFalse(self.o.output.exists())
        self.assertEqual(Application.report(self.partial()).state,'building')
        self.assertEqual(Application().run(self.o,resume=True).state,'complete')

    @unittest.skipUnless(FFMPEG,'Set local decoder for picture request reuse.')
    def test_picture_observations_reused_after_cancel_with_decoder_binding(self):
        o=replace(self.o,picture=None,picture_request=self.fixture/'picture-request.json',ffmpeg=Path(FFMPEG))
        def stop(stage):
            if stage=='reporting':raise Cancelled()
        with self.assertRaises(Cancelled):Application(progress=stop).run(o)
        with patch('interview_auto_editor.application.analyze_picture',side_effect=AssertionError('picture decode repeated')):
            self.assertEqual(Application().run(o,resume=True).state,'complete')

    def test_cancellation_at_each_stage_never_publishes_final_and_resumes(self):
        for target in ('inspecting','analyzing','planning','exporting','reporting','finalizing'):
            o=replace(self.o,output=self.root/target)
            state={'cancel':False}
            app=Application(cancel=lambda:state['cancel'],progress=lambda s:state.update(cancel=s==target))
            with self.assertRaises(Cancelled):app.run(o)
            self.assertFalse(o.output.exists())
            self.assertEqual(Application.report(self.partial(o)).state,'cancelled')
            self.assertEqual(Application().run(o,resume=True).state,'complete')

    def test_repeat_run_refuses_without_touching_complete_or_inputs(self):
        Application().run(self.o)
        before={p.name:fingerprint(p) for p in self.o.output.iterdir()}
        for resume in (False,True):
            with self.assertRaisesRegex(RunError,'ALREADY_EXISTS'):Application().run(self.o,resume=resume)
        self.assertEqual({p.name:fingerprint(p) for p in self.o.output.iterdir()},before)

    def test_resume_is_explicit_and_changed_settings_refuse(self):
        with self.assertRaises(KeyboardInterrupt):
            Application(progress=lambda s:(_ for _ in ()).throw(KeyboardInterrupt())).run(self.o)
        with self.assertRaisesRegex(RunError,'RESUME'):Application().run(self.o)
        with self.assertRaisesRegex(RunError,'INPUTS_CHANGED'):Application().run(replace(self.o,preset='gentle'),resume=True)
        self.assertEqual(Application().run(self.o,resume=True).state,'complete')

    def test_tampered_stage_refuses_and_leaves_evidence(self):
        def cancel(s):
            if s=='planning':raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):Application(progress=cancel).run(self.o)
        p=self.partial()/'analysis.json'; p.write_text('tampered')
        with self.assertRaisesRegex(RunError,'CHANGED'):Application().run(self.o,resume=True)
        self.assertEqual(p.read_text(),'tampered'); self.assertFalse(self.o.output.exists())

    def test_missing_asset_or_model_never_creates_success(self):
        (self.fixture/'media/zoom-source.mp4').rename(self.fixture/'media/absent.mp4')
        try:
            with self.assertRaises(ValueError):Application().run(self.o)
            self.assertFalse(self.o.output.exists())
        finally:(self.fixture/'media/absent.mp4').rename(self.fixture/'media/zoom-source.mp4')
        with self.assertRaises(OSError):Application().run(replace(self.o,analysis=None,speech_model=self.root/'missing.onnx'))
        self.assertFalse(self.o.output.exists())

    def test_stale_cleanup_bound_to_base_is_refused(self):
        bad=self.root/'stale-cleanup.json'
        old=read_record(CleanupRequest,self.o.cleanup_request)
        bad.write_text(dumps(replace(old,planning_sha256=planning_digest(self.base))),encoding='utf-8')
        with self.assertRaises(ValueError):Application().run(replace(self.o,cleanup_request=bad))
        self.assertFalse(self.o.output.exists())

    def test_cancel_inside_export_removes_candidate_and_resume_revalidates(self):
        app=Application(); original=app.export
        def stop(*args,**kwargs):
            original(*args,**kwargs)
            raise Cancelled()
        with patch.object(app,'export',side_effect=stop),self.assertRaises(Cancelled):app.run(self.o)
        self.assertFalse(self.o.output.exists())
        self.assertFalse(list(self.root.glob('.iae-export-*')))
        self.assertEqual(Application().run(self.o,resume=True).state,'complete')

    def test_change_during_run_refuses_final_and_can_recover_original_inputs(self):
        raw=self.o.mapping.read_bytes()
        def change(stage):
            if stage=='finalizing':self.o.mapping.write_bytes(raw+b'\n')
        try:
            with self.assertRaisesRegex(RunError,'INPUT_CHANGED'):Application(progress=change).run(self.o)
            self.assertFalse(self.o.output.exists())
        finally:self.o.mapping.write_bytes(raw)
        self.assertEqual(Application().run(self.o,resume=True).state,'complete')

    def test_moved_package_references_resolve_and_regenerates_without_inference(self):
        Application().run(self.o)
        moved=self.root/'moved space \u00f6';moved.mkdir()
        fixture=moved/self.fixture.name
        shutil.copytree(self.fixture,fixture)
        shutil.copytree(self.o.output,moved/'run')
        import xml.etree.ElementTree as ET
        from interview_auto_editor.adapters.kdenlive import props,resolve_resource
        project=moved/'run/project.kdenlive'
        for chain in ET.parse(project).getroot().findall('chain'):
            if resource:=props(chain).get('resource'):
                self.assertTrue(resolve_resource(resource,project.parent).is_file())
        o=replace(self.o,project=fixture/'before.kdenlive',mapping=fixture/'mapping.json',
            analysis=fixture/'analysis.json',picture=fixture/'picture-analysis.json',
            cleanup_request=fixture/'cleanup-request.json',output=moved/'regenerated')
        with patch('interview_auto_editor.application.speech_analyze',side_effect=AssertionError('inference')):
            Application().run(o)
        self.assertEqual(project.read_bytes(),(o.output/'project.kdenlive').read_bytes())

    def test_source_time_override_restores_all_tracks_without_inference(self):
        req=replace(self.base.request,overrides=(Override('p1',F(4),F(7),'audible'),))
        self.request.write_text(dumps(req),encoding='utf-8')
        o=replace(self.o,picture=None,cleanup_request=None)
        with patch('interview_auto_editor.application.speech_analyze',side_effect=AssertionError('inference')):
            Application().run(o)
        result=read_record(PlanningResult,o.output/'planning-result.json')
        self.assertEqual(result.plan.time_map.output_frames,300)
        self.assertEqual(result.request.overrides,req.overrides)

    def test_original_unverified_origins_and_unequal_tails_still_refuse(self):
        a=read_record(Analysis,self.o.analysis)
        for name,source in (('origins',replace(a.sources[1],origin_status='unverified',verified_offset=None)),
                            ('tails',replace(a.sources[1],duration=F(576001,48000),sample_count=576001))):
            analysis=replace(a,sources=(a.sources[0],source,*a.sources[2:]))
            p=self.root/(name+'.json');p.write_text(dumps(analysis),encoding='utf-8')
            with self.assertRaises(ValueError):Application().run(replace(self.o,analysis=p,output=self.root/name))
            self.assertFalse((self.root/name).exists())

    def test_inspect_plan_export_and_compatibility_are_callable_cli_paths(self):
        for command in ('inspect','plan','export'):
            o=replace(self.o,command=command,output=self.root/command)
            self.assertEqual(Application().run(o).state,'complete')
            self.assertEqual((o.output/'project.kdenlive').exists(),command=='export')
        self.assertEqual(Application().compatibility_probe(self.o.project)['compatibility'],'EXPERIMENTAL')
        self.assertEqual(Application().compatibility_probe(self.root/'absent')['compatibility'],'UNSUPPORTED')

    def test_cli_private_safe_review_repeat_report_probe_and_cancel_codes(self):
        cmd=[sys.executable,'-B','-m','interview_auto_editor','run','--project',str(self.o.project),
             '--mapping',str(self.o.mapping),'--analysis',str(self.o.analysis),'--request',str(self.request),
             '--ffprobe',FFPROBE,'--output',str(self.o.output),'--experimental']
        result=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertNotIn(str(self.root),result.stdout+result.stderr)
        self.assertNotIn(self.originals[self.o.project],result.stdout+result.stderr)
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,1)
        self.assertEqual(subprocess.run([sys.executable,'-m','interview_auto_editor','report','--run',str(self.o.output)],capture_output=True).returncode,2)
        flag=self.root/'cancel';flag.touch()
        cancelled=subprocess.run(cmd[:-3]+['--output',str(self.root/'cancelled'),'--experimental','--cancel-file',str(flag)],capture_output=True)
        self.assertEqual(cancelled.returncode,130,cancelled.stderr)
        probe=subprocess.run([sys.executable,'-m','interview_auto_editor','compatibility-probe','--project',str(self.o.project),'--output',str(self.root/'probe.json')],capture_output=True)
        self.assertEqual(probe.returncode,2,probe.stderr)

    @unittest.skipUnless(FFMPEG and SPEECH and REACTION,'Set existing local pinned CPU models and decoder.')
    def test_actual_analysis_cache_hits_resume_and_changed_pacing_needs_no_inference(self):
        o=replace(self.o,command='analyze',analysis=None,request=None,picture=None,cleanup_request=None,
            ffmpeg=Path(FFMPEG),speech_model=Path(SPEECH),reaction_model=Path(REACTION),cache=self.root/'cache')
        Application().run(o)
        first=read_record(Analysis,o.output/'analysis.json')
        self.assertTrue(all(s.origin_status=='unverified' for s in first.sources if s.kind=='participant_audio'))
        from interview_auto_editor.speech import SileroCPU
        from interview_auto_editor.reactions import YamnetCPU
        second=replace(o,output=self.root/'analyze-hit',preset='gentle')
        with patch.object(SileroCPU,'probability',side_effect=AssertionError('speech inference on hit')), patch.object(YamnetCPU,'scores',side_effect=AssertionError('reaction inference on hit')):
            Application().run(second)
        self.assertEqual(first,read_record(Analysis,second.output/'analysis.json'))
        summary=json.loads((second.output/'analysis-report.json').read_text())
        self.assertEqual(summary['speech']['cache_hits'],2)
        self.assertEqual(summary['reactions']['cache_hits'],2)
        # A changed preset cannot certify the original intake's origins.
        with self.assertRaises(ValueError):Application().run(replace(second,command='run',output=self.root/'unverified-run'))
        self.assertFalse((self.root/'unverified-run').exists())

    @unittest.skipUnless(FFMPEG and SPEECH and REACTION,'Set existing local pinned CPU models and decoder.')
    def test_cancel_between_models_retains_speech_cache_and_resume_reuses_it(self):
        o=replace(self.o,command='analyze',analysis=None,request=None,picture=None,cleanup_request=None,
            ffmpeg=Path(FFMPEG),speech_model=Path(SPEECH),reaction_model=Path(REACTION),cache=self.root/'cache')
        with patch('interview_auto_editor.application.reaction_analyze',side_effect=Cancelled()),self.assertRaises(Cancelled):
            Application().run(o)
        self.assertFalse(o.output.exists())
        self.assertEqual(len(list((o.cache/'speech').glob('*.json'))),2)
        from interview_auto_editor.speech import SileroCPU
        with patch.object(SileroCPU,'probability',side_effect=AssertionError('speech rerun')):
            Application().run(o,resume=True)
        summary=json.loads((o.output/'analysis-report.json').read_text())
        self.assertEqual(summary['speech']['cache_hits'],2)
        self.assertEqual(summary['reactions']['cache_hits'],0)
        # A missing model and corrupt cache still refuse after successful hits.
        with self.assertRaises(OSError):Application().run(replace(o,output=self.root/'missing-model',speech_model=self.root/'absent.onnx'))
        cached=next((o.cache/'reactions').glob('*.json'));cached.write_text('corrupt')
        with self.assertRaisesRegex(ValueError,'CACHE_CORRUPT'):Application().run(replace(o,output=self.root/'corrupt-cache'))
        self.assertFalse((self.root/'corrupt-cache').exists())


if __name__=='__main__':unittest.main()
