"""Capture-tool safety and genuine saved-fixture structure, not GUI tests."""
from array import array
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import shutil
import unittest
from unittest.mock import patch
import wave
import xml.etree.ElementTree as ET

from s01_fixture_media import generate, media_settings, sha256, write_tone
from s01_project_census import census, MAX_BYTES, resource_kind
from s01_sanitize_fixture import sanitize
from s01_validate_render import frame_number, semantic_capture, tone_amplitude

FIXTURES = Path(__file__).resolve().parents[1] / 'tests/fixtures/kdenlive-26.08.2'


def properties(node):
    return {child.get('name'): child.text or '' for child in node.findall('property')}


def frames(timecode):
    hours, minutes, seconds = map(Fraction, timecode.split(':'))
    value = (hours * 3600 + minutes * 60 + seconds) * 25
    if value.denominator != 1:
        raise AssertionError('Non-frame-representable time in the 25 FPS capture.')
    return int(value)


class CaptureToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def xml(self, text):
        # Deliberately hand-authored parser input; never a genuine fixture.
        source = self.folder / 'hand-authored-parser-input.xml'
        source.write_text(text, encoding='utf-8')
        return source

    def test_whole_samples_for_fractional_fps(self):
        rate, duration, samples = media_settings(8, 300, '30000/1001')
        self.assertEqual(rate, Fraction(30000, 1001))
        self.assertEqual(duration, Fraction(1001, 100))
        self.assertEqual(samples, 480480)

    def test_25fps_sample_duration(self):
        self.assertEqual(media_settings(2, 300, '25/1')[1:], (Fraction(12), 576000))

    def test_invalid_counts_rates_and_duration(self):
        for arguments in [(0, 300, '25/1'), (33, 300, '25/1'), (2, 0, '25/1'),
                          (2, 1, '30000/1001'), (2, 3001, '25/1'), (2, 300, '24/1')]:
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                media_settings(*arguments)

    def test_pcm_has_exact_duration_and_silent_handles(self):
        target = self.folder / 'tone.wav'
        write_tone(target, 48000, 440, [(4800, 12000), (24000, 36000)])
        with wave.open(str(target), 'rb') as source:
            self.assertEqual((source.getnframes(), source.getframerate(), source.getnchannels(), source.getsampwidth()),
                             (48000, 48000, 1, 2))
            pcm = array('h', source.readframes(48000))
        self.assertFalse(any(pcm[:4800]))
        self.assertFalse(any(pcm[36000:]))
        self.assertGreater(max(pcm), 7000)
        self.assertEqual(pcm[4800], 0)
        self.assertEqual(pcm[11999], 0)

    def test_generation_refuses_existing_output(self):
        target = self.folder / 'existing'
        target.mkdir()
        sentinel = target / 'preserve.txt'
        sentinel.write_text('keep', encoding='utf-8')
        with patch('s01_fixture_media.subprocess.run') as run:
            run.return_value.stdout = 'ffmpeg version unit-test\n'
            with self.assertRaises(FileExistsError):
                generate(target, 'not-executed-ffmpeg')
        self.assertEqual(sentinel.read_text(encoding='utf-8'), 'keep')
        self.assertEqual(list(target.iterdir()), [sentinel])

    def test_census_rejects_dtd_and_entities(self):
        source = self.xml('<!DOCTYPE mlt [<!ENTITY private "secret">]><mlt>&private;</mlt>')
        with self.assertRaises(ValueError):
            census(source)

    def test_census_is_bounded(self):
        source = self.folder / 'oversize.xml'
        source.write_bytes(b' ' * (MAX_BYTES + 1))
        with self.assertRaises(ValueError):
            census(source)

    def test_census_does_not_echo_paths_names_or_notes(self):
        source = self.xml('<mlt root="C:/private/person"><chain><property name="resource">C:/private/person.wav</property>'
                          '<property name="kdenlive:docproperties.version">1 person secret</property>'
                          '<property name="kdenlive:documentnotes">private transcript</property></chain></mlt>')
        before = sha256(source)
        result = census(source)
        serialized = json.dumps(result)
        for private in ('C:/', 'person', 'secret', 'private transcript'):
            self.assertNotIn(private, serialized)
        self.assertEqual(result['document_versions']['kdenlive:docproperties.version'], 'REDACTED')
        self.assertEqual(result['gui_open_save'], 'NOT RUN')
        self.assertEqual(sha256(source), before)

    def test_census_does_not_accept_other_xml_as_a_project(self):
        with self.assertRaises(ValueError):
            census(self.xml('<document/>'))

    def test_resource_classes_do_not_fetch_urls(self):
        expected = {'C:/media/a.wav': 'absolute_path', r'\\server\share\a.wav': 'absolute_path',
                    'https://example.invalid/a.wav': 'url_or_service', 'media/a.wav': 'relative_or_unclassified',
                    'black': 'empty_or_internal'}
        for value, kind in expected.items():
            self.assertEqual(resource_kind(value), kind)

    def test_sanitizer_rejects_non_synthetic_manifest(self):
        manifest = self.folder / 'manifest.json'
        manifest.write_text('{"provenance":"private_interview"}', encoding='utf-8')
        source = self.xml('<mlt/>')
        with self.assertRaises(ValueError):
            sanitize(source, manifest, self.folder / 'out.kdenlive')
        self.assertFalse((self.folder / 'out.kdenlive').exists())

    def test_sanitizer_never_overwrites_source_or_existing_output(self):
        # Isolate the real synthetic package; this copy is only a sanitizer test.
        shutil.copytree(FIXTURES / 'media-2', self.folder / 'media-2')
        source = FIXTURES / 'grouped-gain.kdenlive'
        manifest = self.folder / 'media-2/synthetic-media.json'
        copied = self.folder / 'source.kdenlive'
        copied.write_bytes(source.read_bytes())
        text = copied.read_text(encoding='utf-8').replace('version="7.43.0"', 'version="7.43.0" root="."', 1)
        copied.write_text(text, encoding='utf-8')
        before = sha256(copied)
        with self.assertRaises(FileExistsError):
            sanitize(copied, manifest, copied)
        self.assertEqual(sha256(copied), before)
        target = self.folder / 'existing.kdenlive'
        target.write_text('preserve existing result', encoding='utf-8')
        with self.assertRaises(FileExistsError):
            sanitize(copied, manifest, target)
        self.assertEqual(target.read_text(encoding='utf-8'), 'preserve existing result')

    def test_sanitizer_rejects_changed_media(self):
        shutil.copytree(FIXTURES / 'media-2', self.folder / 'media-2')
        (self.folder / 'media-2/participant-01.wav').write_bytes(b'changed')
        source = self.xml('<mlt root="."/>')
        with self.assertRaises(ValueError):
            sanitize(source, self.folder / 'media-2/synthetic-media.json', self.folder / 'out.kdenlive')
        self.assertFalse((self.folder / 'out.kdenlive').exists())

    def test_sanitizer_rejects_traversal_in_manifest(self):
        manifest = self.folder / 'manifest.json'
        manifest.write_text(json.dumps({'provenance': 'generated_synthetic_media_no_recorded_people',
                                        'files': [{'path': '../outside.wav', 'sha256': '0' * 64}]}), encoding='utf-8')
        with self.assertRaises(ValueError):
            sanitize(self.xml('<mlt root="."/>'), manifest, self.folder / 'out.kdenlive')

    def test_exact_capture_frame_conversion(self):
        self.assertEqual(frame_number('00:00:03.960'), 99)
        self.assertEqual(frame_number('00:00:04.000'), 100)
        with self.assertRaises(ValueError):
            frame_number('00:00:04.001')

    def test_marker_measurement_distinguishes_contamination_from_participant(self):
        import math
        participant = array('h', (round(8000 * math.sin(2 * math.pi * 330 * i / 48000)) for i in range(48000)))
        contaminated = array('h', (value + round(3000 * math.sin(2 * math.pi * 997 * i / 48000)) for i, value in enumerate(participant)))
        self.assertLess(tone_amplitude(participant, 997, 0), 0.1)
        self.assertAlmostEqual(tone_amplitude(contaminated, 997, 0), 3000, delta=1)
        self.assertAlmostEqual(tone_amplitude(contaminated, 330, 0), 8000, delta=1)

    def test_missing_probe_audio_is_a_failure(self):
        with self.assertRaises(ValueError):
            tone_amplitude(array('h', [0]), 997, 0)


class GenuineCaptureStructureTests(unittest.TestCase):
    """Assertions inspect actual GUI captures; cannot replace an application round trip."""
    def test_every_public_media_file_matches_its_manifest(self):
        manifest = json.loads((FIXTURES / 'media-2/synthetic-media.json').read_text(encoding='utf-8'))
        self.assertFalse(manifest['kdenlive_project_created'])
        self.assertEqual(manifest['participants'], 2)
        for record in manifest['files']:
            self.assertEqual(sha256(FIXTURES / 'media-2' / record['path']), record['sha256'])

    def test_captured_versions_are_independent_fields(self):
        for path in FIXTURES.glob('*.kdenlive'):
            root = ET.parse(path).getroot()
            props = {prop.get('name'): prop.text for prop in root.iter('property')}
            self.assertEqual(root.get('version'), '7.43.0')
            self.assertEqual(props['kdenlive:docproperties.version'], '1.1')
            self.assertEqual(props['kdenlive:docproperties.kdenliveversion'], '26.08.2')

    def test_sanitized_resources_resolve_without_a_machine_root(self):
        for path in FIXTURES.glob('*.kdenlive'):
            root = ET.parse(path).getroot()
            self.assertNotIn('root', root.attrib)
            for prop in root.iter('property'):
                if prop.get('name') == 'resource' and prop.text != 'black':
                    resource = prop.text
                    self.assertTrue(resource.startswith('media-2/'))
                    self.assertTrue((path.parent / resource).is_file())
            report = census(path)
            self.assertFalse(report['root_has_absolute_path'])
            self.assertNotIn('absolute_path', report['resource_kinds'])

    def test_grouped_cuts_preserve_all_300_frames_on_every_track(self):
        root = ET.parse(FIXTURES / 'grouped-gain.kdenlive').getroot()
        timelines = [node for node in root.findall('playlist') if node.get('id') != 'main_bin' and node.findall('entry')]
        self.assertEqual(len(timelines), 3)
        for timeline in timelines:
            self.assertFalse(timeline.findall('blank'))
            intervals = [(frames(entry.get('in')), frames(entry.get('out')) + 1) for entry in timeline.findall('entry')]
            self.assertEqual(intervals, [(0, 100), (100, 200), (200, 300)])

    def test_three_native_groups_reference_all_three_tracks(self):
        root = ET.parse(FIXTURES / 'grouped-gain.kdenlive').getroot()
        prop = next(p for p in root.iter('property') if p.get('name') == 'kdenlive:sequenceproperties.groups')
        groups = json.loads(prop.text)
        self.assertEqual(len(groups), 3)
        actual = []
        for group in groups:
            self.assertEqual(group['type'], 'Normal')
            actual.append({child['data'] for child in group['children']})
        expected = [{f'{track}:{start}:-1' for track in range(3)} for start in (0, 100, 200)]
        self.assertCountEqual(actual, expected)

    def test_native_gain_guide_and_names_are_present(self):
        root = ET.parse(FIXTURES / 'grouped-gain.kdenlive').getroot()
        props = [properties(node) for node in root.iter()]
        track_names = [item['kdenlive:track_name'] for item in props if 'kdenlive:track_name' in item]
        self.assertCountEqual(track_names, ['Participant 01', 'Participant 02'])
        gains = [float(item['level']) for item in props if item.get('mlt_service') == 'volume' and 'level' in item]
        self.assertEqual(len(gains), 1)
        self.assertAlmostEqual(gains[0], -6, delta=0.01)
        guide = next(p for p in root.iter('property') if p.get('name') == 'kdenlive:sequenceproperties.guides')
        self.assertEqual(json.loads(guide.text)[0]['pos'], 100)

    def test_mp4_timeline_is_video_only_in_grouped_fixture(self):
        root = ET.parse(FIXTURES / 'grouped-gain.kdenlive').getroot()
        chains = {node.get('id'): properties(node) for node in root.findall('chain')}
        referenced = {e.get('producer') for p in root.findall('playlist') if p.get('id') != 'main_bin' for e in p.findall('entry')}
        video = [chains[item] for item in referenced if chains[item].get('resource', '').endswith('.mp4')]
        self.assertEqual(len(video), 1)
        self.assertEqual(video[0]['set.test_audio'], '1')
        self.assertEqual(video[0]['set.test_image'], '0')
        # The bin original still has its audio available for recovery/analysis.
        self.assertTrue(any(p.get('resource', '').endswith('.mp4') and p.get('set.test_audio') != '1' for p in chains.values()))

    def test_semantic_comparison_ignores_machine_root_but_detects_timing_change(self):
        source = FIXTURES / 'grouped-gain.kdenlive'
        expected = semantic_capture(source)
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / 'comparison-copy.xml'
            root = ET.parse(source).getroot()
            root.set('root', 'C:/synthetic/relocated')
            ET.ElementTree(root).write(copy, encoding='utf-8', xml_declaration=True)
            self.assertEqual(semantic_capture(copy), expected)
            root.find('playlist/entry').set('out', '00:00:03.920')
            ET.ElementTree(root).write(copy, encoding='utf-8', xml_declaration=True)
            self.assertNotEqual(semantic_capture(copy), expected)


if __name__ == '__main__':
    unittest.main()
