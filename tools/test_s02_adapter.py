"""S02 safety/semantic regression tests; generated mutations are not GUI fixtures."""
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest
import shutil
import xml.etree.ElementTree as ET

from s01_fixture_media import sha256
from s02_kdenlive_adapter import read, frames, props, put, Unsupported
from s02_validate_render import semantic

FIXTURES = Path(__file__).resolve().parents[1] / 'tests/fixtures/kdenlive-26.08.2'


def semantics(project):
    root = ET.parse(project).getroot()
    nodes = {n.get('id'): n for n in root if n.get('id')}
    seq = next(n for n in root.findall('tractor') if 'kdenlive:sequenceproperties.groups' in props(n))
    result = []
    for ref in seq.findall('track')[1:]:
        t = nodes[ref.get('producer')]
        entries = []
        for child in t.findall('track'):
            position = 0
            for e in nodes[child.get('producer')]:
                if e.tag == 'blank':
                    position += frames(e.get('length'), Fraction(25))
                if e.tag == 'entry':
                    a, b = frames(e.get('in'), Fraction(25)), frames(e.get('out'), Fraction(25)) + 1
                    chain = nodes[e.get('producer')]
                    p = props(chain)
                    entries.append((position, a, b, Path(p['resource']).name, p.get('set.test_audio'), p.get('audio_index'), tuple(props(f).get('level') for f in e.findall('filter'))))
                    position += b - a
        result.append((props(t).get('kdenlive:track_name', ''), sorted(entries)))
    return result, json.loads(props(seq)['kdenlive:sequenceproperties.groups']), json.loads(props(seq)['kdenlive:sequenceproperties.guides'])


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.adapter = read(FIXTURES / 'starter-2.kdenlive')
        self.names = {t.resource: t.resource.stem.replace('participant-', 'Participant ') for t in self.adapter.tracks if t.audio}

    def export(self, **kw):
        return self.adapter.export(self.folder / 'new.kdenlive', 100, 125, self.names, experimental=True, **kw)

    def mutation(self, change):
        root = deepcopy(self.adapter.root)
        # Mutation keeps media resolved; never mistaken for native provenance.
        root.set('root', str(FIXTURES))
        change(root)
        path = self.folder / 'hand-authored-negative-test.kdenlive'
        ET.ElementTree(root).write(path, encoding='utf-8')
        return path

    def test_shared_cut_and_recovery_sources(self):
        before = sha256(self.adapter.path)
        report = self.export()
        tracks, groups, guides = semantics(self.folder / 'new.kdenlive')
        self.assertEqual(report['output_frames'], 275)
        self.assertEqual(len(tracks), 3)
        for _, entries in tracks:
            self.assertEqual([e[:3] for e in entries], [(0, 0, 100), (100, 125, 300)])
        self.assertEqual({x[0] for x in tracks}, {'Participant 01', 'Participant 02', ''})
        self.assertEqual([len(g['children']) for g in groups], [3, 3])
        self.assertEqual(guides[0]['pos'], 100)
        root = ET.parse(self.folder / 'new.kdenlive').getroot()
        bins = root.find("playlist[@id='main_bin']")
        self.assertEqual(len(bins.findall('entry')), 4)
        for p in root.findall("chain/property[@name='resource']"):
            self.assertTrue((self.folder / p.text).resolve().is_file())
        self.assertEqual(sha256(self.adapter.path), before)

    def test_mp4_disabled_in_every_chain_and_video_track(self):
        self.export()
        root = ET.parse(self.folder / 'new.kdenlive').getroot()
        for chain in root.findall('chain'):
            p = props(chain)
            if p.get('resource', '').endswith('.mp4'):
                self.assertEqual((p['audio_index'], p['astream'], p['set.test_audio']), ('-1', '-1', '1'))
        self.assertEqual(semantics(self.folder / 'new.kdenlive')[0][-1][1][0][4:6], ('1', '-1'))

    def test_no_overwrite_and_opt_in(self):
        self.export()
        with self.assertRaises(FileExistsError):
            self.export()
        with self.assertRaises(Unsupported):
            self.adapter.export(self.folder / 'other.kdenlive', 100, 125, self.names)
        with self.assertRaises(FileExistsError):
            self.adapter.export(self.adapter.path, 100, 125, self.names, experimental=True)

    def test_interior_bounds_and_unique_mapping(self):
        for a, b in [(0, 1), (5, 5), (20, 300), (125, 100), (1.5, 20), (True, 20)]:
            with self.subTest(a=a, b=b), self.assertRaises(Unsupported):
                self.adapter.export(self.folder / 'invalid.kdenlive', a, b, self.names, experimental=True)
        for mapping in ({}, {k: 'same' for k in self.names}, {k: '' for k in self.names}):
            with self.assertRaises(Unsupported):
                self.adapter.export(self.folder / 'invalid.kdenlive', 100, 125, mapping, experimental=True)

    def test_gain_is_native_and_only_one_proof_unit(self):
        self.export(gain_edges=True)
        root = ET.parse(self.folder / 'new.kdenlive').getroot()
        gain = [props(f) for f in root.findall('playlist/entry/filter')]
        self.assertEqual(len(gain), 1)
        self.assertEqual(gain[0]['mlt_service'], 'volume')
        self.assertIn('45=-60;55=-60;65=0', gain[0]['level'])
        self.assertFalse(list(self.folder.glob('*.wav')))
        self.assertEqual(semantic(self.folder / 'new.kdenlive'), semantic(FIXTURES / 's02-manual-cut.kdenlive'))

    def test_known_one_frame_extent_is_reported(self):
        path = self.mutation(lambda r: next(n for n in r.findall('tractor') if 'kdenlive:sequenceproperties.groups' in props(n)).set('out', '300'))
        self.assertEqual(read(path).extent_delta, 1)

    def test_unsafe_and_edited_structures_rejected(self):
        mutations = [
            lambda r: put(r.find("playlist[@id='main_bin']"), 'kdenlive:docproperties.kdenliveversion', '27.0.0'),
            lambda r: r.find('playlist/entry').set('in', '1'),
            lambda r: r.find('playlist/entry').set('out', '298'),
            lambda r: ET.SubElement(r.find('chain'), 'filter'),
            lambda r: ET.SubElement(r.find('playlist/entry'), 'filter'),
            lambda r: put(r.find('chain'), 'mlt_service', 'timewarp'),
            lambda r: put(r.find('chain'), 'set.test_audio', '1'),
            lambda r: r.find('chain').set('id', 'producer0'),
            lambda r: r.find('playlist/entry').set('producer', 'missing'),
            lambda r: put(r.find('chain'), 'resource', 'https://example.invalid/private.wav'),
            lambda r: r.find('profile').set('frame_rate_den', '1001'),
            lambda r: r.find('playlist').append(ET.Element('blank', length='10')),
            lambda r: put(r.find('tractor/filter'), 'disable', '0'),
            lambda r: ET.SubElement(r, 'consumer'),
        ]
        for change in mutations:
            with self.subTest(change=mutations.index(change)), self.assertRaises((Unsupported, ValueError)):
                read(self.mutation(change))

    def test_dtd_bounded_read(self):
        path = self.folder / 'entity.xml'
        path.write_text('<!DOCTYPE mlt [<!ENTITY x "bad">]><mlt/>')
        with self.assertRaises(Unsupported):
            read(path)

    def test_variable_tracks_linked_audio_and_empty_tracks(self):
        def change(r):
            nodes = {n.get('id'): n for n in r if n.get('id')}
            seq = next(n for n in r.findall('tractor') if 'kdenlive:sequenceproperties.groups' in props(n))
            # Reuse native linked-input track serialization as a deliberate mutation.
            linked = ET.parse(FIXTURES / 'linked-input.kdenlive').getroot()
            t = deepcopy(linked.find("tractor[@id='tractor1']"))
            t.set('id', 'linkedtrack')
            for i, f in enumerate(t.findall('filter')):
                f.set('id', f'linkedfilter{i}')
            for i, ref in enumerate(t.findall('track')):
                p = deepcopy(linked.find(f"playlist[@id='{ref.get('producer')}']"))
                p.set('id', f'linkedplaylist{i}')
                for e in p.findall('entry'):
                    e.set('producer', 'linkedaudiochain')
                ref.set('producer', p.get('id'))
                r.insert(0, p)
            r.insert(list(r).index(seq), t)
            chain = deepcopy(nodes['chain2'])
            chain.set('id', 'linkedaudiochain')
            put(chain, 'set.test_audio', 0)
            put(chain, 'audio_index', 1)
            r.insert(0, chain)
            seq.insert(list(seq).index(seq.findall('track')[-1]), ET.Element('track', producer='linkedtrack'))
        a = read(self.mutation(change))
        self.assertEqual(len(a.excluded), 1)
        a.export(self.folder / 'new.kdenlive', 100, 125, self.names, experimental=True)
        self.assertEqual(len(semantics(self.folder / 'new.kdenlive')[0]), 3)

    def test_variable_participant_counts_use_one_shared_map(self):
        for count in (1, 3, 6, 8):
            with self.subTest(count=count):
                root = deepcopy(self.adapter.root)
                root.set('root', str(FIXTURES))
                nodes = {n.get('id'): n for n in root if n.get('id')}
                seq = next(n for n in root.findall('tractor') if 'kdenlive:sequenceproperties.groups' in props(n))
                for ref in list(seq.findall('track'))[1:]:
                    seq.remove(ref)
                mapping = {}
                for i in range(count):
                    media = self.folder / f'channel {count}-{i} ä.wav'
                    shutil.copyfile(FIXTURES / 'media-2/participant-01.wav', media)
                    mapping[media] = f'Channel {i+1}'
                    chain = deepcopy(nodes['chain0'])
                    chain.set('id', f'countchain{i}')
                    put(chain, 'resource', str(media))
                    put(chain, 'kdenlive:id', 100+i)
                    root.insert(0, chain)
                    track = deepcopy(nodes['tractor0'])
                    track.set('id', f'counttrack{i}')
                    for j, f in enumerate(track.findall('filter')):
                        f.set('id', f'countfilter{i}-{j}')
                    for j, ref in enumerate(track.findall('track')):
                        playlist = deepcopy(nodes[ref.get('producer')])
                        playlist.set('id', f'countplaylist{i}-{j}')
                        ref.set('producer', playlist.get('id'))
                        for e in playlist.findall('entry'):
                            e.set('producer', chain.get('id'))
                            put(e, 'kdenlive:id', 100+i)
                        root.insert(0, playlist)
                    root.insert(list(root).index(seq), track)
                    seq.insert(list(seq).index(seq.findall('track')[-1])+1, ET.Element('track', producer=track.get('id')))
                seq.insert(list(seq).index(seq.findall('track')[-1])+1, ET.Element('track', producer='tractor2'))
                source = self.folder / f'hand-authored-count-{count}.kdenlive'
                ET.ElementTree(root).write(source, encoding='utf-8')
                target = self.folder / f'count-{count}-export.kdenlive'
                read(source).export(target, 100, 125, mapping, experimental=True)
                tracks, groups, _ = semantics(target)
                self.assertEqual(len(tracks), count+1)
                self.assertTrue(all(len(g['children']) == count+1 for g in groups))
                self.assertTrue(all([e[:3] for e in t[1]] == [(0,0,100),(100,125,300)] for t in tracks))

    def test_genuine_roundtrip_retains_timeline_and_records_extent(self):
        generated = semantic(FIXTURES / 's02-manual-cut.kdenlive')
        native = semantic(FIXTURES / 's02-native-roundtrip.kdenlive')
        self.assertEqual(native['sequence_extent_frames'] - generated['sequence_extent_frames'], 1)
        for key in generated:
            if key != 'sequence_extent_frames':
                self.assertEqual(native[key], generated[key])
        evidence = json.loads((FIXTURES / 's02-render-validation.json').read_text())
        self.assertTrue(evidence['passed'])
        self.assertFalse(evidence['whole_project_semantic_equal'])
        self.assertEqual(evidence['project_sha256'], sha256(FIXTURES / 's02-manual-cut.kdenlive'))
        self.assertEqual(evidence['native_roundtrip_sha256'], sha256(FIXTURES / 's02-native-roundtrip.kdenlive'))
        self.assertEqual(evidence['gui_render_sha256'], sha256(FIXTURES / 's02-gui-render.mp4'))


if __name__ == '__main__':
    unittest.main()
