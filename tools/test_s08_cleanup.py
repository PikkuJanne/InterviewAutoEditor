"""Independent S08 permission/protection, acoustic and export regressions."""
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
from unittest.mock import patch

from interview_auto_editor.cleanup import (CleanupRequest, CleanupResult, IdleApproval,
    build_cleanup, db_at, native_keys, planning_digest, validate_cleanup)
from interview_auto_editor.contracts import GainPoint, Override, dumps, loads
from interview_auto_editor.planner import plan_pauses
from interview_auto_editor.adapters.export import export_project
from interview_auto_editor.peaks import measure_peaks, pcm_values
from interview_auto_editor.probe import fingerprint
from interview_auto_editor.timing import ceil
from test_s06_planner import fixture, event, request

ROOT=Path(__file__).resolve().parents[1]
FFPROBE=os.environ.get('IAE_FFPROBE') or shutil.which('ffprobe')


def scenario(fps=F(25), rates=(48000,44100), labels=None, overrides=()):
    a=fixture(fps=fps,seconds=F(3003) if fps!=25 else F(12),rates=rates,labels=labels)
    a=replace(a,events=(event(a,'early','p0',1,2),event(a,'other','p1',3,9),
                       event(a,'late','p0',10,11)))
    r=plan_pauses(a,request(a,approvals=(),overrides=overrides))
    req=CleanupRequest(1,planning_digest(r),(IdleApproval('idle','p0',F(0),a.sources[0].duration,
            'construction_label','Adversarial blanket construction permission; protection must win'),))
    return r,req


class PolicyTests(unittest.TestCase):
    def test_default_no_approval_identity_and_no_activity_unity(self):
        r,req=scenario()
        self.assertFalse(build_cleanup(r,replace(req,approvals=())).spans)
        a=replace(r.plan.analysis,events=())
        r=plan_pauses(a,request(a,approvals=()))
        c=build_cleanup(r,replace(req,planning_sha256=planning_digest(r)))
        self.assertFalse(c.spans)

    def test_independent_protected_kind_and_off_frame_sample_sweep(self):
        for kind in ('speech','reaction','uncertainty','overlap','turn'):
            r,req=scenario()
            a=r.plan.analysis
            extra=event(a,'quiet','p0',F(4001,1000),F(4501,1000),kind)
            a=replace(a,events=a.events+(extra,))
            r=plan_pauses(a,request(a,approvals=()))
            c=build_cleanup(r,replace(req,planning_sha256=planning_digest(r)))
            self.assertTrue(c.spans)
            # Independently examine the full supports (including ramps), not
            # just policy key points or raw event interiors.
            for span in c.spans:
                lo,hi=F(span.start_frame,25),F(span.end_frame+1,25)
                for e in a.events:
                    if e.source_id=='p0' or e.kind=='overlap':
                        self.assertTrue(hi<=e.protected_start or lo>=e.protected_end)
                self.assertGreaterEqual(lo,min(e.protected_start for e in a.events))
                self.assertLessEqual(hi,max(e.protected_end for e in a.events))
            for n in range(int(extra.protected_start*48000),ceil(extra.protected_end*48000)):
                self.assertEqual(db_at(c.spans,'p0',F(n,48000)*25),0)

    def test_overlap_protects_every_mic_and_shared_mic_never_gated(self):
        r,req=scenario(labels=(('a','b'),('c',)))
        self.assertFalse(build_cleanup(r,req).spans)
        r,req=scenario()
        a=replace(r.plan.analysis,events=r.plan.analysis.events+(event(r.plan.analysis,'overlap','p1',4,7,'overlap'),))
        r=plan_pauses(a,request(a,approvals=()))
        c=build_cleanup(r,replace(req,planning_sha256=planning_digest(r)))
        self.assertTrue(all(s.end_frame<=97 or s.start_frame>=180 for s in c.spans))

    def test_overrides_restore_interval_on_all_tracks(self):
        for action in ('keep','audible'):
            r,req=scenario(overrides=(Override('p1',F(4),F(7),action),))
            c=build_cleanup(r,req)
            self.assertTrue(c.spans)
            for f in range(100,175):
                self.assertEqual(db_at(c.spans,'p0',F(f)),0)

    def test_source_approvals_do_not_authorize_shared_removal(self):
        r,req=scenario()
        c=build_cleanup(r,req)
        self.assertEqual(r.plan.time_map.output_frames,300)
        self.assertEqual(r.plan.gains,())
        with self.assertRaisesRegex(ValueError,'Protected-source'):
            replace(r.plan,gains=(GainPoint('p0',0,F(1,2)),))
        self.assertEqual(loads(CleanupResult,dumps(c)),c)

    def test_native_group_seams_and_fractional_fps_round_inward(self):
        for fps in (F(25),F(30000,1001)):
            r,req=scenario(fps=fps)
            c=build_cleanup(r,req)
            self.assertTrue(c.spans)
            for s in c.spans:
                self.assertGreaterEqual(s.down_frame-s.start_frame,ceil(fps/5))
                self.assertGreaterEqual(s.end_frame-s.up_frame,ceil(fps/5))
                self.assertEqual(db_at(c.spans,s.source_id,F(s.start_frame)),0)
                self.assertEqual(db_at(c.spans,s.source_id,F(s.end_frame)),0)

    def test_stale_tampered_unknown_and_non_idle_approvals_refused(self):
        r,req=scenario()
        c=build_cleanup(r,req)
        with self.assertRaisesRegex(ValueError,'different'):
            build_cleanup(r,replace(req,planning_sha256='0'*64))
        with self.assertRaisesRegex(ValueError,'reproduce'):
            validate_cleanup(r,replace(c,spans=()))
        for approval in (replace(req.approvals[0],source_id='unknown'),replace(req.approvals[0],end=F(13))):
            with self.assertRaises(ValueError):build_cleanup(r,replace(req,approvals=(approval,)))
        with self.assertRaises(ValueError):replace(req.approvals[0],basis='model_negative')
        with self.assertRaises(ValueError):loads(CleanupResult,dumps(c).replace('"schema_version": 1','"schema_version": 2',1))

    def test_existing_origin_and_tail_refusals_still_apply(self):
        r,req=scenario()
        a=r.plan.analysis
        for s in (replace(a.sources[1],origin_status='unverified',verified_offset=None),
                  replace(a.sources[1],sample_count=576001,duration=F(576001,48000))):
            b=replace(a,sources=(a.sources[0],s,a.sources[2]))
            with self.assertRaises(ValueError):plan_pauses(b,request(b,approvals=()))

    def test_pcm_widths_and_opposite_polarity_channels(self):
        self.assertEqual(pcm_values(bytes((0,128,255)),1),[-1,0,127/128])
        for width in (2,3,4):
            scale=2**(8*width-1)
            raw=b''.join(x.to_bytes(width,'little',signed=True) for x in (-scale,0,scale-1))
            self.assertEqual(pcm_values(raw,width),[-1,0,(scale-1)/scale])

    def test_variable_track_counts_preserve_simultaneous_sources(self):
        for n in (1,2,3,6,8):
            a=fixture(rates=(48000,)*n)
            a=replace(a,events=tuple(event(a,f's{i}',f'p{i}',3,9) for i in range(n))+
                      (event(a,'start','p0',1,2),event(a,'end','p0',10,11)))
            r=plan_pauses(a,request(a,approvals=()))
            approvals=tuple(IdleApproval(f'a{i}',f'p{i}',F(0),F(12),'construction_label','Adversarial permission') for i in range(n))
            c=build_cleanup(r,CleanupRequest(1,planning_digest(r),approvals))
            for i in range(n):
                for f in range(72,230):
                    self.assertEqual(db_at(c.spans,f'p{i}',F(f)),0)
            self.assertEqual(r.plan.time_map.output_frames,300)

    def test_five_hundred_gain_intervals_do_not_change_fractional_map(self):
        r,req=scenario(fps=F(30000,1001))
        approvals=tuple(IdleApproval(f'a{i}','p0',F(i*5+12),F(i*5+14),'construction_label','Fixed constructed idle interval') for i in range(500))
        a=replace(r.plan.analysis,events=(event(r.plan.analysis,'first','p0',1,2),event(r.plan.analysis,'last','p0',2900,2901)))
        r=plan_pauses(a,request(a,approvals=()))
        c=build_cleanup(r,CleanupRequest(1,planning_digest(r),approvals))
        self.assertEqual(len(c.spans),500)
        self.assertEqual(r.plan.time_map.source_frames,r.plan.time_map.output_frames)
        for approval,span in zip(approvals,c.spans):
            self.assertGreater(F(span.start_frame,1)/a.fps,approval.start)
            self.assertLess(F(span.end_frame+1,1)/a.fps,approval.end)


@unittest.skipUnless(FFPROBE,'Set IAE_FFPROBE for actual S08 media/export checks.')
class AcousticExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from s08_fixture import generate
        cls.temp=tempfile.TemporaryDirectory()
        cls.folder=Path(cls.temp.name)/'fixture'
        generate(cls.folder,FFPROBE)
        from interview_auto_editor.planner import PlanningResult
        cls.result=loads(PlanningResult,(cls.folder/'planning-result.json').read_text())
        cls.cleanup=loads(CleanupResult,(cls.folder/'cleanup-result.json').read_text())
        cls.bindings={'video':cls.folder/'media/zoom-source.mp4',**{f'p{i}':cls.folder/f'media/participant-{i+1:02}.wav' for i in range(2)}}

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_actual_source_hashes_full_bin_and_native_keys_after_removed_gap(self):
        root=ET.parse(self.folder/'cleaned.kdenlive').getroot()
        effects=[f for f in root.iter('filter') if f.find("property[@name='kdenlive_id']") is not None]
        self.assertEqual(len(effects),4)
        self.assertTrue(any(int(f.find("property[@name='level']").text.split('=')[0])>=172 for f in effects))
        self.assertTrue(all(f.find("property[@name='mlt_service']").text=='volume' for f in effects))
        for s in self.result.plan.analysis.sources:
            self.assertEqual(fingerprint(self.bindings[s.source_id]),s.sha256)
        self.assertEqual(len(root.find("playlist[@id='main_bin']").findall('entry')),4)

    def test_recovery_removes_all_effects_with_identical_timing_groups(self):
        from test_s02_adapter import semantics
        self.assertEqual(semantics(self.folder/'baseline.kdenlive'),semantics(self.folder/'restored.kdenlive'))
        self.assertEqual((self.folder/'baseline.kdenlive').read_bytes(),(self.folder/'restored.kdenlive').read_bytes())

    def test_no_cancellation_credit_and_no_new_normalization(self):
        report=measure_peaks(self.result,self.cleanup,self.bindings)
        self.assertTrue(report['export_safe'])
        self.assertEqual(report['retained_frames_audited'],233)
        self.assertLess(report['original_sum_bound'],.5)
        self.assertFalse(report['gain_reduction_applied'])

    def test_mixed_pcm_grids_widths_and_fractional_frame_peak_audit(self):
        a=fixture(fps=F(30000,1001),seconds=F(1001,100),rates=(44100,48000))
        with tempfile.TemporaryDirectory() as temp:
            bindings={}
            for i,s in enumerate(a.sources[1:]):
                width=i+2
                path=Path(temp)/f'grid{i}.wav'
                value=2**(8*width-4)  # exactly 1/8 of PCM full scale
                with wave.open(str(path),'wb') as w:
                    w.setparams((1,width,s.sample_rate,0,'NONE','not compressed'))
                    w.writeframes(value.to_bytes(width,'little',signed=True)*s.sample_count)
                bindings[s.source_id]=path
            a=replace(a,sources=tuple(replace(s,sha256=fingerprint(bindings[s.source_id])) if s.source_id in bindings else s for s in a.sources))
            r=plan_pauses(a,request(a,approvals=()))
            c=build_cleanup(r,CleanupRequest(1,planning_digest(r),()))
            report=measure_peaks(r,c,bindings)
            self.assertEqual(report['retained_frames_audited'],300)
            self.assertEqual(report['original_sum_bound'],.25)
            self.assertEqual(report['correlation_frame_pairs'],0)
            self.assertTrue(report['export_safe'])

    def test_correlated_opposite_phase_mix_cannot_hide_overload(self):
        from array import array
        with tempfile.TemporaryDirectory() as temp:
            paths={}
            for i in range(2):
                path=Path(temp)/f'phase{i}.wav'
                with wave.open(str(path),'wb') as w:
                    w.setparams((2,2,48000,0,'NONE','not compressed'))
                    # Opposite-polarity stereo must not disappear by averaging.
                    w.writeframes(array('h',(24576,-24576) if i==0 else (-24576,24576)).tobytes()*576000)
                paths[f'p{i}']=path
            a=replace(self.result.plan.analysis,sources=tuple(replace(s,sha256=fingerprint(paths[s.source_id]))
                      if s.source_id in paths else s for s in self.result.plan.analysis.sources))
            r=plan_pauses(a,request(a,approvals=()))
            c=build_cleanup(r,CleanupRequest(1,planning_digest(r),()))
            report=measure_peaks(r,c,paths)
            self.assertEqual(report['original_sum_bound'],1.5)
            self.assertGreater(report['max_absolute_correlation'],.999)
            self.assertFalse(report['export_safe'])
            self.assertFalse(c.spans)  # diagnostic correlation grants no approval

    def test_peak_refusal_and_cancellation_publish_nothing(self):
        for failure in (ValueError('bad PCM'),KeyboardInterrupt()):
            output=self.folder/('cancelled' if isinstance(failure,KeyboardInterrupt) else 'bad-pcm')
            with patch('interview_auto_editor.peaks.measure_peaks',side_effect=failure):
                with self.assertRaises(type(failure)):
                    export_project(self.result,self.folder/'before.kdenlive',self.bindings,
                        {'p0':'One','p1':'Two'},output,FFPROBE,experimental=True,cleanup=self.cleanup)
            self.assertFalse(output.exists())
        with patch('interview_auto_editor.peaks.measure_peaks',return_value={'export_safe':False}):
            output=self.folder/'overload'
            with self.assertRaisesRegex(ValueError,'MIX_HEADROOM'):
                export_project(self.result,self.folder/'before.kdenlive',self.bindings,
                    {'p0':'One','p1':'Two'},output,FFPROBE,experimental=True,cleanup=self.cleanup)
            self.assertFalse(output.exists())

    def test_cli_no_overwrite_and_safe_failure(self):
        output=self.folder/'cli-cleanup.json'
        args=[sys.executable,'-B',str(ROOT/'tools/s08_cleanup.py'),'--result',str(self.folder/'planning-result.json'),
              '--request',str(self.folder/'cleanup-request.json'),'--output',str(output)]
        first=subprocess.run(args,capture_output=True,text=True)
        self.assertIn(first.returncode,(0,2),first.stderr)
        self.assertEqual(loads(CleanupResult,output.read_text()),self.cleanup)
        before=output.read_bytes()
        second=subprocess.run(args,capture_output=True,text=True)
        self.assertEqual(second.returncode,1)
        self.assertEqual(output.read_bytes(),before)
        self.assertNotIn(str(self.folder),second.stderr)

    def test_public_bundle_hashes_and_actual_render_remeasurement(self):
        folder=ROOT/'tests/fixtures/s08-cleanup-26.08.2'
        manifest=json.loads((folder/'construction.json').read_text())
        for row in manifest['files']:
            self.assertEqual(fingerprint(folder/row['path']),row['sha256'])
        provenance=json.loads((folder/'PROVENANCE.json').read_text())
        for row in provenance['artifacts']:
            self.assertEqual(fingerprint(folder/row['path']),row['sha256'])
        ffmpeg=os.environ.get('IAE_FFMPEG') or shutil.which('ffmpeg')
        if not ffmpeg:self.skipTest('Set IAE_FFMPEG to remeasure the actual GUI artifact.')
        from s08_validate_render import validate
        report=validate(folder,folder/'native-roundtrip.kdenlive',folder/'group-moved.kdenlive',folder/'gui-render.mp4',ffmpeg)
        self.assertTrue(report['passed'],report['checks'])
        from s08_validate_render import validate_restoration
        restoration=validate_restoration(folder,ffmpeg)
        self.assertTrue(restoration['passed'],restoration['checks'])

    def test_public_bundle_moves_and_reproduces_gain_without_inference(self):
        folder=ROOT/'tests/fixtures/s08-cleanup-26.08.2'
        with tempfile.TemporaryDirectory() as temp:
            moved=Path(temp)/'moved folder ä'
            shutil.copytree(folder,moved)
            from interview_auto_editor.planner import PlanningResult
            r=loads(PlanningResult,(moved/'planning-result.json').read_text())
            c=loads(CleanupResult,(moved/'cleanup-result.json').read_text())
            bindings={'video':moved/'media/zoom-source.mp4',**{f'p{i}':moved/f'media/participant-{i+1:02}.wav' for i in range(2)}}
            export_project(r,moved/'before.kdenlive',bindings,{'p0':'Participant 01','p1':'Participant 02'},
                           moved/'reproduced.kdenlive',FFPROBE,experimental=True,cleanup=c)
            self.assertEqual((moved/'cleaned.kdenlive').read_bytes(),(moved/'reproduced.kdenlive').read_bytes())


if __name__=='__main__':unittest.main()
