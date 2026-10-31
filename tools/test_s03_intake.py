"""Synthetic invalid inputs and real-tool probes; mutations are hand-authored."""
from array import array
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
import json
import os
from pathlib import Path
import random
import shutil
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave
import xml.etree.ElementTree as ET

from interview_auto_editor.adapters.kdenlive import IntakeError, read_starter, resolve_resource, xml_frames
from interview_auto_editor.contracts import dumps, loads
from interview_auto_editor.intake import FileMapping, MappingManifest, inspect
from interview_auto_editor.offsets import Anchor, correlate, diagnose, diagnostic_windows
from interview_auto_editor.probe import probe_video, probe_wav, run_bounded

FIXTURES = Path(__file__).resolve().parents[1] / 'tests/fixtures/kdenlive-26.08.2'
FFPROBE = os.environ.get('IAE_FFPROBE') or shutil.which('ffprobe')
FFMPEG = os.environ.get('IAE_FFMPEG') or shutil.which('ffmpeg')


def write_wav(path, rate=48000, count=576000, channels=1):
    with wave.open(str(path), 'wb') as wav:
        wav.setparams((channels, 2, rate, 0, 'NONE', 'not compressed'))
        wav.writeframes(b'\0\0' * count * channels)


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.root = ET.parse(FIXTURES / 'starter-2.kdenlive').getroot()
        self.root.set('root', str(FIXTURES))

    def mutation(self, change=lambda r: None):
        root = deepcopy(self.root)
        change(root)
        path = self.folder / 'hand-authored ä.kdenlive'
        ET.ElementTree(root).write(path, encoding='utf-8')
        return path

    def test_native_starter_sequence_extent_and_no_modification(self):
        for name in ('starter-2.kdenlive',):
            path = FIXTURES / name
            before = path.read_bytes()
            result = read_starter(path)
            self.assertEqual(result.fps, F(25))
            self.assertEqual(result.clip_frames, 300)
            self.assertIn(result.sequence_frames - result.clip_frames, (0, 1))
            self.assertEqual(path.read_bytes(), before)
        # Genuine linked-input fixture contains only MP4 tracks, no cleaned WAV
        # participants. Its native provenance does not make it a supported input.
        with self.assertRaisesRegex(IntakeError, 'EXPECTED_ONE_VIDEO_AND_PARTICIPANTS'):
            read_starter(FIXTURES / 'linked-input.kdenlive')

    def test_fractional_millisecond_serialization_is_bounded(self):
        for fps in (F(25), F(30000, 1001), F(24000, 1001)):
            for frame in (0, 1, 300, 1000000):
                milliseconds = round(F(frame * 1000, 1) / fps)
                h, rem = divmod(milliseconds, 3600000)
                m, rem = divmod(rem, 60000)
                s, ms = divmod(rem, 1000)
                self.assertEqual(xml_frames(f'{h:02}:{m:02}:{s:02}.{ms:03}', fps), frame)
        with self.assertRaises(IntakeError):
            xml_frames('00:00:01.001', F(25))
        def fractional(root):
            root.find('profile').set('frame_rate_num', '30000')
            root.find('profile').set('frame_rate_den', '1001')
            for node in root.iter():
                for key in ('in', 'out'):
                    if key in node.attrib:
                        node.set(key, '0' if key == 'in' else '299')
        self.assertEqual(read_starter(self.mutation(fractional)).fps, F(30000, 1001))

    def test_invalid_structures_and_paths_fail_before_probing(self):
        changes = [lambda r: r.find('playlist/entry').set('in', '1'),
                   lambda r: ET.SubElement(r.find('playlist'), 'blank', length='1'),
                   lambda r: ET.SubElement(r.find('playlist/entry'), 'filter'),
                   lambda r: r.find('chain/property[@name="mlt_service"]').__setattr__('text', 'timewarp'),
                   lambda r: r.find('chain/property[@name="resource"]').__setattr__('text', 'https://invalid/private'),
                   lambda r: r.find('chain/property[@name="resource"]').__setattr__('text', 'missing.wav'),
                   lambda r: r.find('chain').set('id', 'producer0'),
                   lambda r: r.find('playlist/entry').set('producer', 'missing'),
                   lambda r: r.find('profile').set('frame_rate_den', '0'),
                   lambda r: r.find('tractor').set('in', '1'),
                   lambda r: r.find('chain').set('in', '1'),
                   lambda r: ET.SubElement(r.find('chain'), 'transition'),
                   lambda r: r.findall('tractor')[-1].set('out', '1000'),
                   lambda r: ET.SubElement(r, 'consumer'),
                   lambda r: ET.SubElement(r.find('chain'), 'property', name='resource'),
                   lambda r: ET.SubElement(r.find('chain'), 'property', name='warp_speed').__setattr__('text', '1'),
                   lambda r: ET.SubElement(r.find('chain'), 'property', name='kdenlive:proxy').__setattr__('text', 'proxy.mp4')]
        for i, change in enumerate(changes):
            with self.subTest(case=i), self.assertRaises(IntakeError):
                read_starter(self.mutation(change))

    def test_unsafe_xml_encodings_entities_and_size(self):
        path = self.folder / 'unsafe.xml'
        for raw in (b'<!DOCTYPE mlt [<!ENTITY x "bad">]><mlt/>', '<!DOCTYPE mlt><mlt/>'.encode('utf-16'), b'<mlt>' + b' ' * (8 * 1024 * 1024)):
            path.write_bytes(raw)
            with self.assertRaises(IntakeError):
                read_starter(path)

    def test_explicit_relocation_unicode_moved_media_and_unc_opt_in(self):
        media = self.folder / 'relocated participant ä.wav'
        write_wav(media, count=10)
        self.assertEqual(resolve_resource('missing.wav', self.folder, {'missing.wav': str(media)}), media.resolve())
        self.assertEqual(resolve_resource(media.name, self.folder), media.resolve())
        for value in ('https://invalid/media', 'file:///private.wav', 'D:relative.wav', '//server/share/private.wav'):
            with self.assertRaises(IntakeError):
                resolve_resource(value, self.folder)

    def test_exact_stereo_mixed_rate_wav_and_physical_truncation(self):
        for rate in (16000, 44100, 48000, 192000):
            path = self.folder / f'{rate}.wav'
            write_wav(path, rate, rate + 1, channels=2)
            before = path.read_bytes()
            result = probe_wav(path)
            self.assertEqual(result.sample_count, rate + 1)
            self.assertEqual(result.duration, F(rate + 1, rate))
            self.assertEqual(result.channels, 2)
            self.assertEqual(path.read_bytes(), before)
            path.write_bytes(before[:-1])
            with self.assertRaises(IntakeError):
                probe_wav(path)

    def test_mapping_contract_rejects_guessing_duplicates_missing_extra(self):
        mapping = MappingManifest(1, (FileMapping('a.wav', 'a', 'Participant A', ('A',)),), ())
        self.assertEqual(loads(MappingManifest, dumps(mapping)), mapping)
        with self.assertRaises(IntakeError):
            replace(mapping, participants=mapping.participants * 2)
        with self.assertRaises(IntakeError):
            replace(mapping, schema_version=2)
        # Missing/extra mappings fail before launching a tool.
        with self.assertRaises(IntakeError):
            inspect(FIXTURES / 'starter-2.kdenlive', mapping, 'not-launched', mapping_base=self.folder)

    @unittest.skipUnless(FFPROBE, 'Set IAE_FFPROBE for real ffprobe integration')
    def test_full_probe_reports_native_timing_and_uncertified_origins(self):
        mapping = MappingManifest(1, tuple(FileMapping(str(FIXTURES / f'media-2/participant-{i:02}.wav'), f'p{i}', f'Participant {i}', (f'p{i}',)) for i in (1, 2)), ())
        result = inspect(FIXTURES / 'starter-2.kdenlive', mapping, FFPROBE)
        self.assertEqual(result.clip_frames, 300)
        self.assertEqual(result.tails, (('video', F(0)), ('p2', F(0)), ('p1', F(0))))
        self.assertFalse(result.ready)
        report = json.dumps(result.summary())
        self.assertNotIn(str(FIXTURES), report)
        self.assertNotIn('Participant', report)
        self.assertNotIn(result.analysis.sources[0].sha256, report)

    @unittest.skipUnless(FFPROBE, 'Set IAE_FFPROBE for real ffprobe integration')
    def test_tail_inventory_distinguishes_subframe_tail_and_truncation(self):
        for difference, expected in ((1, 'SOURCE_TAIL_RECONCILIATION_REQUIRED'), (-1, 'SOURCE_TAIL_RECONCILIATION_REQUIRED'), (-4800, 'SOURCE_TRUNCATED_BEFORE_CLIP_END')):
            path = self.folder / 'participant ä.wav'
            write_wav(path, count=576000 + difference)
            root = deepcopy(self.root)
            for prop in root.findall('chain/property[@name="resource"]'):
                if prop.text.endswith('participant-01.wav'):
                    prop.text = str(path)
            project = self.folder / 'tail.kdenlive'
            ET.ElementTree(root).write(project, encoding='utf-8')
            mapping = MappingManifest(1, (FileMapping(str(path), 'a', 'A', ('A',)), FileMapping(str(FIXTURES / 'media-2/participant-02.wav'), 'b', 'B', ('B',))), ())
            result = inspect(project, mapping, FFPROBE)
            self.assertEqual(dict(result.tails)['a'], F(difference, 48000))
            self.assertIn(expected, [d.code for d in result.diagnostics if d.source_id == 'a'])

    @unittest.skipUnless(FFPROBE and FFMPEG, 'Set IAE_FFPROBE/IAE_FFMPEG for VFR integration')
    def test_actual_vfr_frame_audit_even_with_plausible_metadata(self):
        target = self.folder / 'vfr.mp4'
        run_bounded([FFMPEG, '-nostdin', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=size=64x64:rate=25:duration=2',
                     '-vf', r'select=not(eq(n\,20))', '-fps_mode', 'vfr', '-an', '-c:v', 'mpeg4', target])
        result = probe_video(target, FFPROBE)
        self.assertEqual(result.cadence, 'VFR_OR_DISCONTINUOUS')

    def test_bounded_subprocess_failure_is_private_safe(self):
        with self.assertRaises(IntakeError) as failure:
            run_bounded(['missing-private-executable-name'])
        self.assertEqual(str(failure.exception), 'LOCAL_TOOL_UNAVAILABLE')
        with self.assertRaises(IntakeError):
            run_bounded([sys.executable, '-c', 'import time; time.sleep(10)'], timeout=0.05)
        with self.assertRaises(IntakeError):
            run_bounded([sys.executable, '-c', 'print("x"*10000)'], limit=100)
        with self.assertRaisesRegex(IntakeError, 'DECODER_REPORTED_ERRORS'):
            run_bounded([sys.executable, '-c', 'import sys; sys.stderr.write("private decoder error")'])


class OriginTests(unittest.TestCase):
    def signal(self):
        rng = random.Random(42)
        return array('f', (rng.uniform(-0.5, 0.5) for _ in range(2000)))

    def test_equal_duration_positive_negative_shift_and_zero_detected(self):
        reference = self.signal()
        for lag in (-20, 0, 31):
            candidate = array('f', [0] * len(reference))
            for i in range(len(reference)):
                if 0 <= i - lag < len(reference):
                    candidate[i] = reference[i - lag]
            measured, score, status = correlate(reference, candidate, rate=1000, max_lag=80)
            self.assertEqual(measured, lag)
            self.assertGreater(score, F(99, 100))
            anchors = tuple(Anchor(F(t), measured, 1000, score, status) for t in (1, 5, 9))
            result = diagnose(anchors, F(12))
            self.assertEqual(result.status, 'OFFSET_DETECTED' if lag else 'ZERO_LAG_WITHIN_DIAGNOSTIC_RESOLUTION')
            self.assertIsNone(result.suggested_correction)

    def test_inactive_periodic_ambiguous_and_inconsistent_anchors(self):
        zeros = array('f', [0] * 2000)
        self.assertEqual(correlate(zeros, zeros, rate=1000, max_lag=80)[2], 'SILENT_OR_INACTIVE')
        periodic = array('f', [0.4, -0.4] * 1000)
        self.assertIsNone(correlate(periodic, periodic, rate=1000, max_lag=80)[0])
        anchors = tuple(Anchor(F(t), lag, 1000, F(1), 'RELIABLE_ANCHOR') for t, lag in ((1, 0), (5, 10), (9, -30)))
        self.assertEqual(diagnose(anchors, F(12)).status, 'INCONSISTENT_LAGS_REVIEW_OFFSET_OR_DRIFT')
        self.assertEqual(diagnose(anchors[:1], F(12)).status, 'UNVERIFIED_INSUFFICIENT_ANCHORS')

    @unittest.skipUnless(FFPROBE and FFMPEG, 'Set IAE_FFPROBE/IAE_FFMPEG for decoded-file offset checks')
    def test_equal_duration_files_decode_to_zero_and_shifted_diagnostics(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            rng = random.Random(200)
            samples = array('h', (rng.randrange(-14000, 14000) for _ in range(8000 * 12)))
            reference = folder / 'reference.wav'
            shifted = folder / 'shifted.wav'
            for path, data in ((reference, samples), (shifted, array('h', [0] * 160) + samples[:-160])):
                with wave.open(str(path), 'wb') as wav:
                    wav.setparams((1, 2, 8000, 0, 'NONE', 'not compressed'))
                    wav.writeframes(data.tobytes())
            video = folder / 'reference.mp4'
            run_bounded([FFMPEG, '-nostdin', '-v', 'error', '-f', 'lavfi', '-i', 'color=size=64x64:rate=25:duration=12',
                         '-i', reference, '-c:v', 'mpeg4', '-c:a', 'aac', '-ar', '48000', '-shortest', video])
            before = (reference.read_bytes(), shifted.read_bytes())
            for path, expected in ((reference, 'ZERO_LAG_WITHIN_DIAGNOSTIC_RESOLUTION'), (shifted, 'OFFSET_DETECTED')):
                result = diagnostic_windows(video, path, FFMPEG, (F(0), F(4), F(8)), F(12))
                self.assertEqual(result.status, expected)
            self.assertEqual(probe_wav(reference).sample_count, probe_wav(shifted).sample_count)
            self.assertEqual(before, (reference.read_bytes(), shifted.read_bytes()))


if __name__ == '__main__':
    unittest.main()
