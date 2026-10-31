"""Desktop workflow gates using shareable synthetic sources and real service."""
from dataclasses import replace
from fractions import Fraction as F
import gc
import os
from pathlib import Path
import shutil
import tempfile
import time
import tkinter as tk
import unittest
from unittest.mock import patch

from interview_auto_editor.application import Application, RunError, RunOptions, read_record
from interview_auto_editor.cancellation import Cancelled
from interview_auto_editor.contracts import Analysis, dumps, loads
from interview_auto_editor.desktop import Desktop, review_seconds
from interview_auto_editor.desktop_workflow import (DesktopJob, STAGES, Worker, absolute_mapping,
    discover_mapping, error_message, open_edit_copy, prepare_job, restored_request, review_run)
from interview_auto_editor.intake import MappingManifest
from interview_auto_editor.planner import PlannerRequest
from interview_auto_editor.probe import fingerprint

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/s09-picture-26.08.2'
FFPROBE = os.environ.get('IAE_FFPROBE') or shutil.which('ffprobe')
FFMPEG = os.environ.get('IAE_FFMPEG') or shutil.which('ffmpeg')


class DesktopUnitTests(unittest.TestCase):
    def test_mapping_suggestions_are_neutral_and_retain_every_audio_source(self):
        mapping = discover_mapping(FIXTURE / 'before.kdenlive')
        self.assertEqual(len(mapping.participants), 2)
        self.assertEqual([p.display_name for p in mapping.participants], ['Participant 01', 'Participant 02'])
        self.assertTrue(all(Path(p.resource).is_absolute() for p in mapping.participants))
        explicit = absolute_mapping(FIXTURE / 'mapping.json')
        self.assertEqual([p.source_id for p in explicit.participants], ['p0', 'p1'])

    def test_picture_review_formats_exact_seconds_without_serialization_details(self):
        self.assertEqual(review_seconds({'numerator':138, 'denominator':25}), '138/25')
        self.assertEqual(review_seconds(None), 'removed / no output time')

    def test_job_requires_strict_complete_absolute_option_snapshot(self):
        o = RunOptions('run', ROOT/'starter', ROOT/'mapping', ROOT/'probe', ROOT/'new', experimental=True)
        job = DesktopJob.from_options(o)
        self.assertEqual(loads(DesktopJob, dumps(job)).run_options(), o)
        for raw in (dumps(job).replace('"schema_version": 1', '"schema_version": 2'),
                    dumps(job).replace('"run"', '"unknown"'),
                    dumps(job).replace('"experimental"', '"unknown_field"')):
            with self.assertRaises(ValueError): loads(DesktopJob, raw)
        with self.assertRaisesRegex(RunError, 'ABSOLUTE'):
            DesktopJob.from_options(replace(o, project=Path('relative'))).run_options()

    def test_exact_source_override_never_creates_new_approval_or_changes_binding(self):
        a = read_record(Analysis, FIXTURE/'analysis.json')
        request = read_record(PlannerRequest, ROOT/'tests/fixtures/s10-cli-26.08.2/planner-request.json')
        restored = restored_request(a, request, 'p0', '4.5', '11/2', 'audible')
        self.assertEqual(restored.overrides[0].start, F(9, 2))
        self.assertEqual(restored.approvals, request.approvals)
        self.assertEqual(restored.analysis_sha256, request.analysis_sha256)
        base = Application().plan(a, request)[1].plan.time_map
        new = Application().plan(a, restored)[1].plan.time_map
        self.assertGreater(new.output_frames, base.output_frames)
        for start, end in (('-1', '2'), ('5', '4'), ('0', '100'), ('NaN', '2'), ('1/0', '2')):
            with self.assertRaises(RunError): restored_request(a, request, 'p0', start, end, 'keep')

    def test_unverified_origin_cannot_be_certified_by_restore(self):
        a = read_record(Analysis, FIXTURE/'analysis.json')
        source = replace(a.sources[1], origin_status='unverified', verified_offset=None)
        a = replace(a, sources=(a.sources[0], source, *a.sources[2:]))
        from interview_auto_editor.planner import analysis_digest
        request = PlannerRequest(1, analysis_digest(a), 'tight', (), ())
        with self.assertRaises(RunError): restored_request(a, request, 'p0', '4', '7', 'keep')

    def test_worker_masks_private_error_content_and_rejects_concurrency(self):
        from threading import Event
        event = Event(); w = Worker()
        w.start(lambda app: event.wait(3))
        with self.assertRaisesRegex(RunError, 'BUSY'): w.start(lambda app: None)
        event.set(); w.thread.join(5); self.assertEqual(w.events.get()[0], 'done')
        w.start(lambda app: (_ for _ in ()).throw(ValueError('private name/path/hash')))
        w.thread.join(5)
        kind, value = w.events.get()
        self.assertEqual(kind, 'error'); self.assertNotIn('private name/path/hash', value)
        self.assertNotIn('private name/path/hash', error_message(RunError('private name/path/hash')))

    def test_worker_cancellation_is_a_distinct_recoverable_state(self):
        w = Worker()
        def stop(app):
            w.cancel.set()
            from interview_auto_editor.cancellation import checkpoint, scope
            with scope(app.cancel): checkpoint()
        w.start(stop); w.thread.join(5)
        self.assertEqual(w.events.get()[0], 'cancelled')


@unittest.skipUnless(FFPROBE and FFMPEG, 'Set local FFmpeg/ffprobe for current synthetic picture observations.')
class DesktopPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from interview_auto_editor.picture import PictureAnalysis, analyze_picture
        old=read_record(PictureAnalysis,FIXTURE/'picture-analysis.json')
        cls.current_picture=analyze_picture(read_record(Analysis,FIXTURE/'analysis.json'),
            old.request,FIXTURE/'media/zoom-source.mp4',FFMPEG,FFPROBE)
        assert replace(cls.current_picture,implementation_sha256=old.implementation_sha256)==old

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fixture = self.root/'fixture space \u00e4'
        shutil.copytree(FIXTURE, self.fixture)
        (self.fixture/'picture-analysis.json').write_text(dumps(self.current_picture),encoding='utf-8')
        self.mapping = absolute_mapping(self.fixture/'mapping.json')
        self.o = RunOptions('run', self.fixture/'before.kdenlive', self.fixture/'mapping.json', Path(FFPROBE), self.root/'new run',
            analysis=self.fixture/'analysis.json', request=ROOT/'tests/fixtures/s10-cli-26.08.2/planner-request.json',
            picture=self.fixture/'picture-analysis.json', cleanup_request=self.fixture/'cleanup-request.json', experimental=True)
        self.originals = {p: fingerprint(p) for p in (self.o.project, *sorted((self.fixture/'media').iterdir()))}

    def tearDown(self):
        self.assertEqual({p: fingerprint(p) for p in self.originals}, self.originals)
        self.temp.cleanup()

    def run_job(self, options=None, request=None):
        path, job = prepare_job(options or self.o, self.mapping, request)
        restored = read_record(DesktopJob, path).run_options()
        Application().run(restored)
        return path, restored

    def test_fresh_desktop_job_shared_service_full_export_and_review(self):
        path, options = self.run_job()
        manifest, report, analysis, request = review_run(options.output)
        self.assertEqual(manifest.state, 'complete')
        self.assertEqual(report['export']['output_frames'], 267)
        self.assertEqual(report['export']['groups'], 6)
        self.assertEqual(report['export']['gain_spans'], 4)
        self.assertEqual(analysis, read_record(Analysis, self.o.analysis))
        self.assertEqual(request, read_record(PlannerRequest, self.o.request))
        self.assertNotIn(path.name, [p.name for p in options.output.iterdir()])
        from test_s02_adapter import semantics
        tracks, groups, guides = semantics(options.output/'project.kdenlive')
        self.assertEqual(len(tracks), 3)
        self.assertTrue(all([e[:3] for e in t[1]] == [e[:3] for e in tracks[0][1]] for t in tracks))

    def test_actual_tk_start_worker_completion_and_safe_review(self):
        root = tk.Tk(); root.withdraw(); ui = Desktop(root)
        try:
            ui.project.set(str(self.o.project)); ui.mapping = self.mapping; ui.show_mapping()
            ui.confirmed.set(True); ui.experimental.set(True); ui.output.set(str(self.o.output))
            ui.assets['ffprobe'].set(str(FFPROBE))
            for key in ui.records:
                ui.records[key].set(str(getattr(self.o, key)) if getattr(self.o, key) else '')
            ui.start()
            deadline = time.monotonic()+15
            while time.monotonic() < deadline:
                root.update()
                if not ui.worker.busy and ui.status.get().startswith('Run complete'): break
                time.sleep(.02)
            ui.worker.thread.join(1); root.update_idletasks()
            self.assertFalse(ui.worker.busy)
            self.assertIn('Run complete', ui.status.get())
            self.assertEqual(str(ui.open_button.cget('state')), 'normal')
            rows = [ui.review_tree.item(row, 'values') for row in ui.review_tree.get_children()]
            pictures = [r for r in rows if r[0] == 'picture']
            self.assertTrue(pictures)
            self.assertTrue(all('numerator' not in r[1] for r in pictures))
        finally:
            if ui.worker.busy:
                ui.worker.cancel.set(); ui.worker.thread.join(10)
            ui.close()
            del ui, root
            gc.collect()  # Tcl objects must be reclaimed on their owning thread.

    def test_every_stage_cancel_preserves_explicit_unchanged_resume(self):
        for stage in STAGES:
            o = replace(self.o, output=self.root/stage)
            path, job = prepare_job(o, self.mapping)
            options = read_record(DesktopJob, path).run_options()
            w = Worker()
            def run(app):
                progress = app.progress
                def cancel_here(value):
                    progress(value)
                    if value == stage: w.cancel.set()
                app.progress = cancel_here
                return app.run(options)
            w.start(run); w.thread.join(15)
            self.assertFalse(w.busy)
            messages = list(w.events.queue)
            self.assertEqual(messages[-1][0], 'cancelled')
            self.assertFalse(o.output.exists())
            self.assertEqual(Application().run(options, resume=True).attempt, 2)

    def test_changed_resume_input_and_repeated_run_refuse(self):
        path, job = prepare_job(self.o, self.mapping)
        options = job.run_options()
        def stop(stage): raise Cancelled()
        with self.assertRaises(Cancelled): Application(progress=stop).run(options)
        original_bytes = options.mapping.read_bytes()
        changed = read_record(MappingManifest, options.mapping)
        options.mapping.write_text(dumps(replace(changed, participants=tuple(replace(p, display_name=p.display_name+' renamed') for p in changed.participants))), encoding='utf-8')
        with self.assertRaisesRegex(RunError, 'INPUTS_CHANGED'): Application().run(options, resume=True)
        options.mapping.write_bytes(original_bytes)
        Application().run(options, resume=True)
        with self.assertRaisesRegex(RunError, 'ALREADY_EXISTS'): Application().run(options, resume=True)
        with self.assertRaisesRegex(RunError, 'ALREADY_EXISTS'): prepare_job(self.o, self.mapping)

    def test_restore_stale_cleanup_refuses_then_explicit_unity_succeeds(self):
        _, options = self.run_job()
        manifest, report, a, request = review_run(options.output)
        updated = restored_request(a, request, 'p0', '4', '7', 'audible')
        path, job = prepare_job(replace(self.o, output=self.root/'stale'), self.mapping, updated)
        with self.assertRaisesRegex(ValueError, 'different planning result'): Application().run(job.run_options())
        self.assertFalse((self.root/'stale').exists())
        _, restored = self.run_job(replace(self.o, output=self.root/'restored', cleanup_request=None), updated)
        _, result, _, _ = review_run(restored.output)
        self.assertEqual(result['export']['output_frames'], 300)
        self.assertEqual(result['export'].get('gain_spans', 0), 0)

    def test_corrupt_report_prevents_review_and_kdenlive_launch(self):
        _, options = self.run_job()
        (options.output/'report.json').write_text('{}')
        with self.assertRaisesRegex(RunError, 'CHANGED'): review_run(options.output)
        with patch('interview_auto_editor.desktop_workflow.subprocess.Popen') as popen:
            with self.assertRaises(RunError): open_edit_copy(options.output, Path(FFPROBE))
            popen.assert_not_called()

    def test_edit_copy_preserves_relative_depth_and_immutable_run(self):
        _, options = self.run_job()
        before = {p.name: fingerprint(p) for p in options.output.iterdir()}
        with patch('interview_auto_editor.desktop_workflow.subprocess.Popen') as popen:
            project = open_edit_copy(options.output, Path(FFPROBE))
            self.assertEqual(project.parent.parent, options.output.parent)
            self.assertEqual(project.read_bytes(), (options.output/'project.kdenlive').read_bytes())
            self.assertFalse(popen.call_args.kwargs['shell'])
            self.assertEqual(popen.call_args.args[0], [str(Path(FFPROBE).resolve()), str(project)])
        self.assertEqual(before, {p.name: fingerprint(p) for p in options.output.iterdir()})
        from xml.etree import ElementTree as ET
        for prop in ET.parse(project).findall(".//chain/property[@name='resource']"):
            self.assertTrue((project.parent/prop.text).resolve().is_file())

    def test_missing_and_invalid_inputs_have_actionable_private_safe_errors(self):
        for o in (replace(self.o, analysis=self.root/'missing'), replace(self.o, project=self.root/'missing')):
            path, job = prepare_job(replace(o, output=self.root/('missing-'+o.analysis.name+'-'+o.project.name)), self.mapping)
            w = Worker(); w.start(lambda app: app.run(job.run_options())); w.thread.join(10)
            kind, text = list(w.events.queue)[-1]
            self.assertEqual(kind, 'error'); self.assertNotIn(str(self.root), text)
            self.assertIn('missing', text)
        invalid = self.root/'invalid.kdenlive'; invalid.write_text('<not-a-project/>')
        with self.assertRaises(ValueError): discover_mapping(invalid)


class TkSmokeTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk(); self.root.withdraw()
        self.ui = Desktop(self.root)
        self.root.update_idletasks()

    def tearDown(self):
        self.ui.close()
        self.ui = self.root = None
        gc.collect()

    def test_fresh_ui_requires_explicit_mapping_and_clears_stale_open(self):
        self.ui.mapping = discover_mapping(FIXTURE/'before.kdenlive')
        self.ui.show_mapping(); self.ui.start()
        self.assertIn('confirm', self.ui.status.get())
        self.assertFalse(self.ui.worker.busy)
        self.assertEqual(str(self.ui.open_button.cget('state')), 'disabled')

    def test_eight_and_64_participant_rows_remain_scrollable_and_editable(self):
        mapping = discover_mapping(FIXTURE/'before.kdenlive')
        for count in (8, 64):
            self.ui.mapping = replace(mapping, participants=tuple(replace(mapping.participants[0], source_id=f'p{i}', display_name=f'Participant {i}') for i in range(count)))
            self.ui.show_mapping(); self.root.update_idletasks()
            self.assertEqual(len(self.ui.mapping_tree.get_children()), count)
            self.ui.mapping_tree.see(str(count-1)); self.ui.mapping_tree.selection_set(str(count-1))
            self.ui.edit_participant(); self.root.update_idletasks()
            dialogs = [w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)]
            self.assertEqual(len(dialogs), 1); dialogs[0].destroy()

    def test_busy_disables_form_retains_cancel_and_prevents_close_during_worker(self):
        from threading import Event
        event = Event(); self.ui.launch(lambda app: event.wait(3), lambda value: None)
        try:
            self.assertEqual(str(self.ui.cancel_button.cget('state')), 'normal')
            self.assertEqual(str(self.ui.open_button.cget('state')), 'disabled')
            self.ui.close(); self.assertTrue(self.ui.worker.cancel.is_set())
            self.assertTrue(self.root.winfo_exists())
        finally: event.set(); self.ui.worker.thread.join(5)


if __name__ == '__main__':
    unittest.main()
