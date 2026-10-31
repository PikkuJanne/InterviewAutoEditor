"""Capability/build states, future safety, export and preserved plan migration.

All XML mutations below are hand-authored, never future-version GUI evidence.
"""
from copy import deepcopy
from dataclasses import replace
import json
import platform
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from interview_auto_editor.adapters.compatibility import assess, TESTED_BUILDS
from interview_auto_editor.adapters.export import export_project, put, native_layout
from interview_auto_editor.adapters.kdenlive import IntakeError, read_starter
from interview_auto_editor.application import Application, RunOptions
from interview_auto_editor.contracts import Analysis, dumps, loads
from interview_auto_editor.desktop_workflow import DesktopJob
from interview_auto_editor.planner import plan_pauses
from interview_auto_editor.probe import fingerprint
from test_s07_export import FIX, synthetic_result, FFPROBE, FFMPEG
from test_s06_planner import fixture, request


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.root = ET.parse(FIX / 'starter-2.kdenlive').getroot()
        self.root.set('root', str(FIX))

    def project(self, version='26.08.2', mutation=lambda r: None):
        root = deepcopy(self.root)
        put(root.find("playlist[@id='main_bin']"), 'kdenlive:docproperties.kdenliveversion', version)
        mutation(root)
        path = self.folder / 'hand-authored.kdenlive'
        ET.ElementTree(root).write(path, encoding='utf-8')
        return path

    def test_writer_version_never_certifies_installed_target(self):
        for version in ('26.08.2', '26.08.3', '26.11.70', '27.04.0'):
            with self.subTest(version=version):
                p = self.project(version); original = p.read_bytes()
                r = Application().compatibility_probe(p)
                self.assertEqual(r['compatibility'], 'EXPERIMENTAL')
                self.assertEqual(r['writer_version'], version)
                self.assertFalse(r['installed_build_verified'])
                self.assertTrue(r['experimental_opt_in_required'])
                self.assertEqual(p.read_bytes(), original)

    def test_exact_binary_platform_writer_identity_and_unknown_target(self):
        s = read_starter(self.project()); b = TESTED_BUILDS[0]
        with patch('interview_auto_editor.probe.fingerprint', return_value=b.executable_sha256), \
                patch('interview_auto_editor.adapters.compatibility.platform.system', return_value=b.system), \
                patch('interview_auto_editor.adapters.compatibility.platform.release', return_value=b.release), \
                patch('interview_auto_editor.adapters.compatibility.platform.machine', return_value=b.machine), \
                patch('interview_auto_editor.adapters.compatibility.platform.version', return_value=b.nt_version):
            r = assess(s, self.folder/'mock.exe')
            self.assertEqual(r['compatibility'], 'TESTED')
            self.assertFalse(r['actual_application_test_performed'])
            self.assertFalse(r['experimental_opt_in_required'])
            self.assertEqual(assess(replace(s, writer_version='27.04.0'), 'mock')['compatibility'], 'EXPERIMENTAL')
            with patch('interview_auto_editor.adapters.compatibility.platform.machine', return_value='ARM64'):
                self.assertEqual(assess(s, 'mock')['compatibility'], 'EXPERIMENTAL')
            with patch('interview_auto_editor.probe.fingerprint', return_value='0'*64):
                self.assertEqual(assess(s, 'mock')['compatibility'], 'EXPERIMENTAL')
        self.assertEqual(assess(s, self.folder/'absent')['reason'], 'TARGET_BUILD_UNREADABLE')

    def test_unsafe_future_structure_refuses_export_but_plan_analysis_survives(self):
        changes = [lambda r: r.find('tractor/track').set('offset', '1'),
            lambda r: r.find('playlist/entry').set('speed', '2'),
            lambda r: ET.SubElement(r.find('chain'), 'filter'),
            lambda r: put(r.find('chain'), 'mlt_service', 'timewarp'),
            lambda r: put(r.find('chain'), 'force_fps', '30'),
            lambda r: put(r.find('chain'), 'audio_delay', '0.4'),
            lambda r: r.find('tractor/track').set('in', '1'),
            lambda r: r.find('tractor/track').set('out', '100'),
            lambda r: put(r.find("playlist[@id='main_bin']"), 'kdenlive:docproperties.version', '9.0')]
        a = fixture(); before = dumps(a)
        for change in changes:
            p = self.project('27.04.0', change)
            report = Application().compatibility_probe(p)
            self.assertEqual(report['compatibility'], 'UNSUPPORTED')
            self.assertFalse(report['export_allowed'])
            with self.assertRaises(IntakeError):
                export_project(None, p, {}, {}, self.folder/'never.kdenlive', None, experimental=True)
            self.assertFalse((self.folder/'never.kdenlive').exists())
            self.assertEqual(plan_pauses(loads(Analysis, before), request(a)).plan.analysis, a)
        self.assertEqual(dumps(a), before)

    def test_probe_cli_codes_safe_diagnostics_and_no_overwrite(self):
        p = self.project('27.04.0')
        for name, extra, code in [('experimental', [], 2),
                ('unreadable', ['--target-kdenlive', str(self.folder/'missing.exe')], 1)]:
            out = self.folder/(name+'.json')
            cmd = [sys.executable, '-B', '-m', 'interview_auto_editor', 'compatibility-probe',
                '--project', str(p), '--output', str(out), *extra]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(proc.returncode, code, proc.stderr)
            self.assertNotIn(str(self.folder), proc.stdout+proc.stderr)
            before = out.read_bytes()
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 1)
            self.assertEqual(out.read_bytes(), before)
        r = Application().compatibility_probe(self.project(mutation=lambda r: r.find('tractor/track').set('offset', '1')))
        self.assertEqual(r['reason'], 'UNKNOWN_XML_ATTRIBUTE')

    def test_legacy_jobs_and_wire_records_require_no_implicit_migration(self):
        o = RunOptions('edit', self.folder/'starter', self.folder/'mapping', self.folder/'probe', self.folder/'output')
        job = DesktopJob.from_options(o)
        for removed in ((), ('mutes',), ('target_kdenlive',), ('mutes', 'target_kdenlive')):
            old = replace(job, options=tuple((k,v) for k,v in job.options if k not in removed))
            self.assertEqual(old.run_options(), o)
        with self.assertRaises(ValueError):
            loads(Analysis, dumps(fixture()).replace('"schema_version": 1', '"schema_version": 999', 1))

    @unittest.skipUnless(FFPROBE, 'Local media probe required')
    def test_tested_target_exports_without_opt_in_and_unknown_target_needs_it(self):
        p = self.project(); result, paths, names = synthetic_result(p)
        target = self.folder/'identity-only.exe'; target.write_bytes(b'never executed')
        b = replace(TESTED_BUILDS[0], executable_sha256=fingerprint(target),
            system=platform.system(), release=platform.release(), machine=platform.machine(), nt_version=platform.version())
        with patch('interview_auto_editor.adapters.compatibility.TESTED_BUILDS', (b,)):
            report = export_project(result, p, paths, names, self.folder/'tested.kdenlive', FFPROBE, target_kdenlive=target)
            self.assertEqual(report['compatibility'], 'TESTED')
            target.write_bytes(b'changed build')
            with self.assertRaisesRegex(IntakeError, 'EXPERIMENTAL_EXPORT_REQUIRES_OPT_IN'):
                export_project(result, p, paths, names, self.folder/'unknown.kdenlive', FFPROBE, target_kdenlive=target)
            target.write_bytes(b'never executed')
            def changed_during_export(result):
                target.write_bytes(b'changed while exporting')
                return native_layout(result)
            with patch('interview_auto_editor.adapters.export.native_layout', side_effect=changed_during_export), \
                    self.assertRaisesRegex(IntakeError, 'TARGET_CHANGED_DURING_EXPORT'):
                export_project(result, p, paths, names, self.folder/'changed.kdenlive', FFPROBE, target_kdenlive=target)
            self.assertFalse((self.folder/'changed.kdenlive').exists())

    @unittest.skipUnless(FFPROBE, 'Local media probe required')
    def test_future_export_opt_in_retains_version_and_current_timeline(self):
        for version in ('26.08.3', '27.04.0'):
            p = self.project(version)
            result, paths, names = synthetic_result(p)
            out = self.folder/(version+'.kdenlive')
            with self.assertRaisesRegex(IntakeError, 'EXPERIMENTAL_EXPORT_REQUIRES_OPT_IN'):
                export_project(result, p, paths, names, out, FFPROBE)
            report = export_project(result, p, paths, names, out, FFPROBE, experimental=True)
            self.assertEqual(report['compatibility'], 'EXPERIMENTAL')
            bp = ET.parse(out).find("playlist[@id='main_bin']")
            self.assertEqual(bp.find("property[@name='kdenlive:docproperties.kdenliveversion']").text, version)
            self.assertEqual(report['participants'], 2)


class NativeEvidenceTests(unittest.TestCase):
    def test_genuine_capture_hashes_and_native_edit_semantics(self):
        from s02_validate_render import semantic
        folder = FIX.parent/'s13-compatibility-26.08.2'
        provenance = json.loads((folder/'PROVENANCE.json').read_text())
        self.assertEqual(provenance['application']['executable_sha256'], TESTED_BUILDS[0].executable_sha256)
        for item in provenance['files']:
            self.assertEqual(fingerprint(folder/item['path']), item['sha256'])
        expected = semantic(folder/'picture-cleaned.kdenlive')
        self.assertEqual(semantic(folder/'native-roundtrip.kdenlive'), expected)
        self.assertEqual(semantic(folder/'native-undone.kdenlive'), expected)
        moved = semantic(folder/'group-moved.kdenlive')
        for t, u in zip(expected['tracks'], moved['tracks']):
            self.assertEqual(u['entries'], [dict(e, position=e['position']+(25 if i==5 else 0)) for i,e in enumerate(t['entries'])])

    @unittest.skipUnless(FFMPEG, 'Local decoder required')
    def test_current_measurement_of_actual_gui_render(self):
        from s09_validate_render import validate
        folder = FIX.parent/'s13-compatibility-26.08.2'
        measured = validate(folder, FFMPEG, FIX.parent/'s09-picture-26.08.2/media')
        self.assertTrue(measured['passed'], measured['checks'])
        recorded = json.loads((folder/'render-validation.json').read_text())
        self.assertEqual(measured, recorded)


if __name__ == '__main__':
    unittest.main()
