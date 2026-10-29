"""Independent S09 preservation, picture and restore-only seam regressions."""
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
from unittest.mock import patch

from interview_auto_editor.contracts import Override, dumps, loads
from interview_auto_editor.picture import (ALGORITHM, PIXELS, Boundary, PictureAnalysis,
    PictureRequest, PictureWindow, analyze_picture, confidence, digest, inspect_frames,
    refine_picture_seams, validate_picture, window_ranges)
from interview_auto_editor.planner import analysis_digest, plan_pauses
from interview_auto_editor.probe import fingerprint
from interview_auto_editor.timing import ceil, frame_time
from test_s06_planner import fixture, event, request, two_events

ROOT = Path(__file__).resolve().parents[1]
FFMPEG = os.environ.get('IAE_FFMPEG') or shutil.which('ffmpeg')
FFPROBE = os.environ.get('IAE_FFPROBE') or shutil.which('ffprobe')


def observations(a, switches=(), layout='speaker_view'):
    req = PictureRequest(1, analysis_digest(a), layout, 'construction_label', 'Independent synthetic layout label')
    windows = []
    for t, r in window_ranges(a):
        images = [bytes([40+150*(sum(f >= k for k in switches) % 2)])*PIXELS for f in range(r.start, r.end)]
        windows.append(PictureWindow(t, r, inspect_frames(images, r.start)))
    from interview_auto_editor import picture
    return PictureAnalysis(1, ALGORITHM, req, a.sources[0].sha256, fingerprint(picture.__file__),
                           '0'*64, 'synthetic-test-decoder', tuple(windows))


class SeamTests(unittest.TestCase):
    def test_12_speech_12_45_picture_preserves_entire_opening_exact_20fps(self):
        a = fixture(fps=F(20), seconds=F(20), rates=(48000, 44100))
        a = replace(a, events=(event(a, 'left', 'p0', 8, 10), event(a, 'opening', 'p1', 12, 15)))
        base = plan_pauses(a, request(a))
        refined = refine_picture_seams(base, observations(a, (249,)))
        m = refined.result.plan.time_map
        self.assertTrue(m.contains(F(12), F(15)))
        # Original picture latency remains exactly .45 s on BOTH clocks.
        self.assertEqual(m.map_time(F(249,20))-m.map_time(F(12)), F(9,20))
        for s in a.sources[1:]:
            for n in range(12*s.sample_rate, 15*s.sample_rate):
                self.assertIsNotNone(m.map_time(F(n,s.sample_rate)))
        self.assertTrue(any(m.kind == 'probable_picture_boundary' and m.source_time == F(249,20) for m in refined.markers))

    def test_stable_switch_inside_silence_restores_only_shared_time(self):
        a = two_events()
        base = plan_pauses(a, request(a))
        refined = refine_picture_seams(base, observations(a, (110,)))
        self.assertEqual(refined.result.decisions[0].removed[0].start, 80)
        self.assertEqual(refined.result.decisions[0].removed[0].end, 110)
        self.assertEqual(refined.result.plan.time_map.output_frames, 270)
        self.assertEqual(refined.result.plan.analysis, a)
        self.assertEqual(refined.result.plan.overrides, base.plan.overrides)
        self.assertEqual(refined.result, plan_pauses(a, refined.result.request))
        self.assertIsNotNone(refined.result.plan.time_map.map_time(F(110,25)))

    def test_all_unsafe_layouts_restore_handover_deletion(self):
        a = two_events()
        base = plan_pauses(a, request(a))
        for layout in ('gallery', 'pinned', 'camera_off', 'uncertain'):
            r = refine_picture_seams(base, observations(a, (110,), layout))
            self.assertEqual(r.result.plan.time_map.output_frames, 300)
            self.assertTrue(all(m.confidence < F(9,10) for m in r.markers))

    def test_short_flash_or_edge_fragment_restores_instead_of_truncating_shot(self):
        a = two_events()
        base = plan_pauses(a, request(a))
        for switches in ((110,112), (75,), (150,), (110,130)):
            r = refine_picture_seams(base, observations(a, switches))
            self.assertEqual(r.result.plan.time_map.output_frames,300)

    def test_already_aligned_or_static_picture_does_not_change_s06(self):
        a = two_events()
        base = plan_pauses(a, request(a))
        for switches in ((), (147,)):
            self.assertEqual(refine_picture_seams(base, observations(a,switches)).result,base)

    def test_no_approval_no_activity_and_shared_mic_have_no_new_authority(self):
        for a in (two_events(), fixture(), two_events(labels=(('a','b'),('c',)))):
            base = plan_pauses(a, request(a, approvals=()))
            r = refine_picture_seams(base, observations(a,(110,)))
            self.assertEqual(r.result, base)

    def test_protected_kinds_overlap_off_frame_and_overrides_survive(self):
        for kind in ('speech','reaction','uncertainty','overlap','turn'):
            a = two_events()
            a = replace(a,events=a.events+(event(a,'quiet','p0',F(4001,1000),F(4501,1000),kind),))
            for action in ('keep','audible'):
                overrides=(Override('p1',F(47,10),F(49,10),action),)
                base=plan_pauses(a,request(a,overrides=overrides))
                r=refine_picture_seams(base,observations(a,(110,)))
                for e in a.events:
                    self.assertTrue(r.result.plan.time_map.contains(e.protected_start,e.protected_end))
                self.assertTrue(r.result.plan.time_map.contains(F(47,10),F(49,10)))

    def test_short_acknowledgement_creates_marker_without_fragmentation(self):
        a=two_events()
        a=replace(a,events=a.events+(event(a,'brief','p1',F(9),F(91,10)),))
        base=plan_pauses(a,request(a,approvals=()))
        r=refine_picture_seams(base,observations(a,(225,)))
        self.assertEqual(r.result,base)
        self.assertTrue(any(m.kind=='picture_activity_kept' and m.source_time==9 for m in r.markers))

    def test_stale_tampered_unknown_and_incomplete_records_refuse(self):
        a=two_events(); base=plan_pauses(a,request(a)); p=observations(a,(110,))
        self.assertEqual(loads(PictureAnalysis,dumps(p)),p)
        for bad in (replace(p,video_sha256='0'*64), replace(p,windows=()),
                    replace(p,request=replace(p.request,analysis_sha256='0'*64)),
                    replace(p,implementation_sha256='0'*64)):
            with self.assertRaises(ValueError):refine_picture_seams(base,bad)
        with self.assertRaises(ValueError):loads(PictureAnalysis,dumps(p).replace('"schema_version": 1','"schema_version": 2',1))
        with self.assertRaises(ValueError):loads(PictureAnalysis,dumps(p).replace('"windows": [','"unknown": 1, "windows": [',1))
        with self.assertRaises(ValueError):replace(p.request,layout='face_identified')

    def test_origin_and_exact_tail_refusals_remain_before_refinement(self):
        a=two_events()
        for source in (replace(a.sources[1],origin_status='unverified',verified_offset=None),
                       replace(a.sources[1],sample_count=576001,duration=F(576001,48000))):
            b=replace(a,sources=(a.sources[0],source,a.sources[2]))
            with self.assertRaises(ValueError):plan_pauses(b,request(b))

    def test_fractional_fps_and_variable_track_counts_restore_monotonically(self):
        for n in (2,3,6,8):
            a=fixture(fps=F(30000,1001),seconds=F(1001,100),rates=(48000,)*n)
            a=replace(a,events=(event(a,'a','p0',1,2),event(a,'b','p1',5,7)))
            base=plan_pauses(a,request(a));r=refine_picture_seams(base,observations(a,(100,)))
            self.assertEqual(r.result.decisions[0].removed[0].end,100)
            for interval in base.plan.time_map.retained:
                self.assertTrue(r.result.plan.time_map.contains(frame_time(interval.start,a.fps),frame_time(interval.end,a.fps)))
            for s in a.sources[1:]:
                self.assertTrue(r.result.plan.time_map.contains(F(5),F(7)))

    def test_broad_cut_motion_flash_and_incomplete_frame_measurements(self):
        frames=[bytes([40])*PIXELS]*20+[bytes([190])*PIXELS]*20
        b=inspect_frames(frames,100)[0]
        self.assertEqual(b.source_frame,120)
        self.assertEqual((b.stable_before,b.stable_after),(20,20))
        self.assertEqual(confidence(b,F(25),'speaker_view'),F(9,10))
        self.assertFalse(inspect_frames([bytes([i])*PIXELS for i in range(40)],0))
        b=inspect_frames(frames[:20]+frames[20:22]+frames[:20],0)[0]
        self.assertEqual(confidence(b,F(25),'speaker_view'),F(1,2))
        with self.assertRaises(ValueError):inspect_frames([b'partial'],0)

    def test_budget_failure_and_incomplete_coverage_fail_closed(self):
        a=two_events();p=observations(a,(110,))
        with patch('interview_auto_editor.picture.MAX_FRAMES',1):
            with self.assertRaisesRegex(ValueError,'budget'):validate_picture(a,p)
        w=p.windows[0]
        bad=replace(w,boundaries=(replace(w.boundaries[0],stable_before=99999),))
        with self.assertRaisesRegex(ValueError,'stability'):validate_picture(a,replace(p,windows=(bad,)))


@unittest.skipUnless(FFMPEG and FFPROBE,'Set local IAE_FFMPEG and IAE_FFPROBE for picture decode/export.')
class ActualDecodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from s09_fixture import generate
        cls.temp=tempfile.TemporaryDirectory()
        cls.folder=Path(cls.temp.name)/'picture'
        generate(cls.folder,FFMPEG,FFPROBE)
        from interview_auto_editor.planner import PlanningResult
        cls.base=loads(PlanningResult,(cls.folder/'planning-result.json').read_text())
        cls.picture=loads(PictureAnalysis,(cls.folder/'picture-analysis.json').read_text())

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_actual_absolute_frames_boundary_and_reproduction(self):
        a=self.base.plan.analysis
        result=analyze_picture(a,self.picture.request,self.folder/'media/zoom-source.mp4',FFMPEG,FFPROBE)
        self.assertEqual(result,self.picture)
        self.assertTrue(any(b.source_frame==138 for w in result.windows for b in w.boundaries))
        self.assertEqual(refine_picture_seams(self.base,result).result.plan.time_map.output_frames,267)

    def test_refined_cleanup_rebind_stale_refusal_and_no_overwrite(self):
        from interview_auto_editor.cleanup import CleanupResult, build_cleanup, planning_digest, validate_cleanup
        old=loads(CleanupResult,(self.folder/'base-cleanup.json').read_text())
        refined=refine_picture_seams(self.base,self.picture).result
        with self.assertRaises(ValueError):validate_cleanup(refined,old)
        new=build_cleanup(refined,replace(old.request,planning_sha256=planning_digest(refined)))
        self.assertTrue(new.spans)
        from interview_auto_editor.adapters.export import export_project
        bindings={'video':self.folder/'media/zoom-source.mp4',**{f'p{i}':self.folder/f'media/participant-{i+1:02}.wav' for i in range(2)}}
        out=self.folder/'refusal.kdenlive'
        with self.assertRaises(ValueError):export_project(self.base,self.folder/'before.kdenlive',bindings,{'p0':'A','p1':'B'},out,FFPROBE,experimental=True,picture=self.picture,cleanup=old)
        self.assertFalse(out.exists())

    def test_cli_exclusive_private_safe_results_and_export_review_exit(self):
        output=self.folder/'cli-picture.json'
        cmd=[sys.executable,str(ROOT/'tools/s09_picture.py'),'analyze','--analysis',str(self.folder/'analysis.json'),'--request',str(self.folder/'picture-request.json'),'--video',str(self.folder/'media/zoom-source.mp4'),'--ffmpeg',FFMPEG,'--ffprobe',FFPROBE,'--output',str(output)]
        first=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(first.returncode,2,first.stderr)
        self.assertEqual(loads(PictureAnalysis,output.read_text()),self.picture)
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,1)
        self.assertNotIn(str(self.folder),first.stdout+first.stderr)

    def test_decoder_failure_cancellation_and_changed_source_publish_nothing(self):
        a=self.base.plan.analysis
        for failure in (ValueError('test decode failure'),KeyboardInterrupt()):
            with patch('interview_auto_editor.picture.run_bounded',side_effect=failure):
                with self.assertRaises(type(failure)):
                    analyze_picture(a,self.picture.request,self.folder/'media/zoom-source.mp4',FFMPEG,FFPROBE)
        with self.assertRaises(ValueError):analyze_picture(a,self.picture.request,self.folder/'media/participant-01.wav',FFMPEG,FFPROBE)

    def test_actual_20fps_12_45_switch_decode_keeps_opening_and_latency(self):
        from interview_auto_editor.probe import run_bounded
        video=self.folder/'delay-20fps.mp4'
        run_bounded([FFMPEG,'-v','error','-nostdin','-n','-f','lavfi','-i',
            "nullsrc=s=96x54:r=20:d=20,geq=lum='if(lt(N,249),40,190)':cb=128:cr=128",
            '-an','-c:v','libx264','-pix_fmt','yuv420p',video])
        a=fixture(fps=F(20),seconds=F(20))
        a=replace(a,sources=(replace(a.sources[0],sha256=fingerprint(video)),*a.sources[1:]),
            events=(event(a,'first','p0',8,10),event(a,'opening','p1',12,15)))
        p=analyze_picture(a,observations(a).request,video,FFMPEG,FFPROBE)
        self.assertEqual([b.source_frame for w in p.windows for b in w.boundaries],[249])
        r=refine_picture_seams(plan_pauses(a,request(a)),p)
        self.assertTrue(r.result.plan.time_map.contains(F(12),F(15)))
        self.assertEqual(r.result.plan.time_map.map_time(F(249,20))-r.result.plan.time_map.map_time(F(12)),F(9,20))

    def test_moved_package_reuses_observations_cleanup_without_inference(self):
        from interview_auto_editor.adapters.export import export_project
        from interview_auto_editor.cleanup import CleanupResult
        moved=self.folder.parent/'moved space \u00e4'
        shutil.copytree(self.folder,moved)
        bindings={'video':moved/'media/zoom-source.mp4',**{f'p{i}':moved/f'media/participant-{i+1:02}.wav' for i in range(2)}}
        cleanup=loads(CleanupResult,(moved/'cleanup-result.json').read_text())
        with patch('interview_auto_editor.picture.analyze_picture',side_effect=AssertionError('No new inference')):
            export_project(self.base,moved/'before.kdenlive',bindings,{'p0':'Participant 01','p1':'Participant 02'},
                moved/'reproduced.kdenlive',FFPROBE,experimental=True,picture=self.picture,cleanup=cleanup)
        self.assertEqual((moved/'reproduced.kdenlive').read_bytes(),(moved/'picture-cleaned.kdenlive').read_bytes())


@unittest.skipUnless(FFMPEG,'Set local IAE_FFMPEG for actual GUI artifact remeasurement.')
class CapturedArtifactTests(unittest.TestCase):
    def test_actual_gui_artifact_hashes_and_render_measurements(self):
        bundle=ROOT/'tests/fixtures/s09-picture-26.08.2'
        from s09_validate_render import validate
        report=validate(bundle,FFMPEG)
        recorded=json.loads((bundle/'render-validation.json').read_text())
        self.assertEqual(report,recorded)
        self.assertTrue(report['passed'])


if __name__=='__main__':unittest.main()
