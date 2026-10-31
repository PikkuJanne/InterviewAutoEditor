#!/usr/bin/env python3
"""Experimental S02 proof adapter, limited to the observed 26.08.2 starter.

This is deliberately not the S03 timing contract or an automatic editor.
Input/output boundaries are integer project frames, with one manual removal.
"""
import argparse
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET

MAX_BYTES = 8 * 1024 * 1024
BUILD = '26.08.2'


class Unsupported(ValueError):
    """Input cannot safely be exported by this bounded proof adapter."""


def props(node):
    return {p.get('name'): p.text or '' for p in node.findall('property')}


def put(node, name, value):
    found = node.findall(f"property[@name='{name}']")
    if len(found) > 1:
        raise Unsupported('Duplicate property.')
    prop = found[0] if found else ET.SubElement(node, 'property', name=name)
    prop.text = str(value)


def frames(value, fps):
    if re.fullmatch(r'\d+', value):
        return int(value)
    if not re.fullmatch(r'\d+:\d{2}:\d{2}\.\d{3}', value):
        raise Unsupported('Unsupported time representation.')
    h, m, s = map(Fraction, value.split(':'))
    count = (h * 3600 + m * 60 + s) * fps
    if count.denominator != 1:
        raise Unsupported('Time is not on the project frame grid.')
    return int(count)


def local_resource(value, base):
    if not value or re.match(r'^[A-Za-z][\w+.-]*:', value) and not re.match(r'^[A-Za-z]:[/\\]', value):
        raise Unsupported('Only existing local media is accepted.')
    path = Path(value)
    path = path if path.is_absolute() else base / path
    path = path.resolve()
    if not path.is_file():
        raise Unsupported('Media reference does not resolve locally.')
    return path


@dataclass
class Track:
    node: ET.Element
    playlist: ET.Element
    chain: ET.Element
    audio: bool
    resource: Path
    end: int


class Kdenlive260802:
    """Observed two-playlist tracks; unknown timing features fail closed."""
    compatibility = 'EXPERIMENTAL'

    def __init__(self, project):
        self.path = Path(project).resolve()
        with self.path.open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES or re.search(br'<!\s*(?:DOCTYPE|ENTITY)\b', raw, re.I):
            raise Unsupported('Oversize XML or DTD/entity declarations.')
        self.root = ET.fromstring(raw)
        if self.root.tag != 'mlt':
            raise Unsupported('Expected MLT document.')
        ids = [n.get('id') for n in self.root.iter() if n.get('id')]
        if len(ids) != len(set(ids)):
            raise Unsupported('Duplicate XML IDs.')
        for parent in self.root.iter():
            names = [p.get('name') for p in parent.findall('property')]
            if len(names) != len(set(names)):
                raise Unsupported('Duplicate XML properties.')
        self.nodes = {n.get('id'): n for n in self.root if n.get('id')}
        for n in self.root.iter():
            if n.tag in ('track', 'entry') and n.get('producer') not in self.nodes:
                raise Unsupported('Unresolved producer reference.')
        bins = [n for n in self.root.findall('playlist') if n.get('id') == 'main_bin']
        if len(bins) != 1:
            raise Unsupported('Expected one main bin.')
        self.bin = bins[0]
        bp = props(self.bin)
        if bp.get('kdenlive:docproperties.kdenliveversion') != BUILD or bp.get('kdenlive:docproperties.version') != '1.1':
            raise Unsupported('No registered proof adapter for this build/structure.')
        seqs = [n for n in self.root.findall('tractor') if 'kdenlive:sequenceproperties.groups' in props(n)]
        if len(seqs) != 1:
            raise Unsupported('Expected one sequence; nested timelines are unsupported.')
        self.sequence = seqs[0]
        sequence_tracks = self.sequence.findall('track')
        if not sequence_tracks or props(self.nodes[sequence_tracks[0].get('producer')]).get('resource') != 'black' or props(self.nodes[sequence_tracks[0].get('producer')]).get('mlt_service') != 'color':
            raise Unsupported('Expected the native internal black background track.')
        for f in self.sequence.findall('filter'):
            if props(f).get('internal_added') != '237' or props(f).get('disable') != '1':
                raise Unsupported('Sequence effects are unsupported in starters.')
        for transition in self.sequence.findall('transition'):
            p = props(transition)
            if p.get('internal_added') != '237' or p.get('mlt_service') not in ('mix', 'qtblend'):
                raise Unsupported('Custom transitions are unsupported in starters.')
        if self.root.findall('consumer') or self.root.findall('link') or self.root.findall('filter'):
            raise Unsupported('Unexpected processing nodes in starter.')
        if any(n.tag not in ('profile', 'producer', 'chain', 'playlist', 'tractor') for n in self.root):
            raise Unsupported('Unknown top-level structure.')
        profile = self.root.find('profile')
        if profile is None:
            raise Unsupported('Missing profile.')
        self.fps = Fraction(int(profile.get('frame_rate_num')), int(profile.get('frame_rate_den')))
        # S02 does not claim fractional-rate XML timing support before its GUI proof.
        if self.fps.denominator != 1 or self.fps <= 0:
            raise Unsupported('S02 proof currently requires integer FPS.')
        base = Path(self.root.get('root', self.path.parent))
        if not base.is_absolute():
            raise Unsupported('Ambiguous relative project root; open/save natively first.')
        self.tracks = []
        self.excluded = []
        for ref in self.sequence.findall('track')[1:]:
            node = self.nodes[ref.get('producer')]
            tp = props(node)
            children = node.findall('track')
            if node.tag != 'tractor' or len(children) != 2 or any(self.nodes[c.get('producer')].tag != 'playlist' for c in children):
                raise Unsupported('Expected native dual-playlist tracks.')
            audio = tp.get('kdenlive:audio_track') == '1'
            if any(c.get('hide') != ('video' if audio else 'audio') for c in children):
                raise Unsupported('Unknown track stream routing.')
            for f in node.findall('filter'):
                if props(f).get('internal_added') != '237' or props(f).get('disable') != '1':
                    raise Unsupported('Active track effects are unsupported in starters.')
            playlists = [self.nodes[c.get('producer')] for c in children]
            items = [(pl, e) for pl in playlists for e in pl if e.tag != 'property']
            if not items:
                continue
            if len(items) != 1 or items[0][1].tag != 'entry':
                raise Unsupported('Starter must have one unedited clip at zero on each used track.')
            playlist, entry = items[0]
            chain = self.nodes[entry.get('producer')]
            cp = props(chain)
            if chain.tag != 'chain' or cp.get('mlt_service') not in ('avformat', 'avformat-novalidate') or chain.findall('filter'):
                raise Unsupported('Effects, speed changes and nested sources are unsupported.')
            if frames(entry.get('in'), self.fps) != 0:
                raise Unsupported('Starter source origin must be zero.')
            if entry.findall('filter') or entry.findall('transition'):
                raise Unsupported('Edited entry effects are unsupported in starters.')
            if audio and (cp.get('audio_index') in ('-1', None) or cp.get('set.test_audio') != '0'):
                raise Unsupported('Participant/linked audio must use an enabled source audio stream.')
            if not audio and (cp.get('video_index') in ('-1', None) or cp.get('set.test_image') != '0'):
                raise Unsupported('Video must use an enabled source picture stream.')
            end = frames(entry.get('out'), self.fps) + 1
            resource = local_resource(cp.get('resource'), base)
            track = Track(node, playlist, chain, audio, resource, end)
            if audio and resource.suffix.lower() == '.mp4':
                self.excluded.append(track)
            else:
                if resource.suffix.lower() != ('.wav' if audio else '.mp4'):
                    raise Unsupported('S02 proof accepts MP4 video and cleaned WAV participants.')
                self.tracks.append(track)
        videos = [t for t in self.tracks if not t.audio]
        audios = [t for t in self.tracks if t.audio]
        if len(videos) != 1 or not audios or len({t.resource for t in self.tracks}) != len(self.tracks):
            raise Unsupported('Require one MP4 and distinct participant WAV tracks.')
        if any(t.resource != videos[0].resource for t in self.excluded):
            raise Unsupported('Unexpected second MP4 audio source.')
        self.end = videos[0].end
        if any(t.end != self.end for t in self.tracks + self.excluded):
            raise Unsupported('Clip-grid extents differ; no silent tail trimming is allowed.')
        self.sequence_extent = frames(self.sequence.get('out'), self.fps) + 1
        if self.sequence_extent not in (self.end, self.end + 1):
            raise Unsupported('Unexplained sequence extent differs from clip coverage.')
        # Preserve this observation in the proof result, never shift the media.
        self.extent_delta = self.sequence_extent - self.end

    def export(self, output, cut_start, cut_end, names, gain_edges=False, experimental=False):
        output = Path(output).resolve()
        if not experimental:
            raise Unsupported('S02 export requires explicit experimental opt-in.')
        if not all(type(v) is int for v in (cut_start, cut_end)) or not 0 < cut_start < cut_end < self.end:
            raise Unsupported('One nonempty strictly interior integer-frame cut is required.')
        audios = [t for t in self.tracks if t.audio]
        expected = {t.resource for t in audios}
        mapping = {Path(k).resolve(): v for k, v in names.items()}
        if set(mapping) != expected or any(not isinstance(v, str) or not v.strip() for v in mapping.values()) or len(set(mapping.values())) != len(mapping):
            raise Unsupported('Supply one unique nonempty name per participant WAV.')
        if gain_edges and cut_start < 70:
            raise Unsupported('Gain proof needs at least 70 frames in the first retained unit.')
        root = deepcopy(self.root)
        nodes = {n.get('id'): n for n in root if n.get('id')}
        seq, main_bin = nodes[self.sequence.get('id')], nodes['main_bin']
        # Resolve resources before removing root; output may live in another folder.
        base = Path(self.root.get('root', self.path.parent))
        for chain in root.findall('chain'):
            cp = props(chain)
            if cp.get('resource'):
                source = local_resource(cp['resource'], base)
                try:
                    target = os.path.relpath(source, output.parent).replace('\\', '/')
                except ValueError:  # different Windows drive
                    target = str(source).replace('\\', '/')
                put(chain, 'resource', target)
                if source.suffix.lower() == '.mp4':
                    put(chain, 'set.test_audio', 1)
                    put(chain, 'audio_index', -1)
                    put(chain, 'astream', -1)
        for parent in root.iter():
            for prop in list(parent.findall('property')):
                if prop.get('name') in ('kdenlive:docproperties.browserurl', 'kdenlive:docproperties.profile', 'kdenlive:docproperties.layout', 'kdenlive:documentnotes'):
                    parent.remove(prop)
        root.attrib.pop('root', None)
        kept = sorted(self.tracks, key=lambda t: not t.audio)
        for ref in list(seq.findall('track'))[1:]:
            seq.remove(ref)
        for transition in list(seq.findall('transition')):
            seq.remove(transition)
        groups = [[], []]
        new_end = self.end - (cut_end - cut_start)
        used_ids = {n.get('id') for n in root.iter() if n.get('id')}
        def unique(prefix):
            i = 0
            while f'{prefix}{i}' in used_ids:
                i += 1
            value = f'{prefix}{i}'
            used_ids.add(value)
            return value
        for index, track in enumerate(kept):
            node = nodes[track.node.get('id')]
            for ref in node.findall('track'):
                playlist = nodes[ref.get('producer')]
                for item in list(playlist):
                    if item.tag != 'property':
                        playlist.remove(item)
            playlist = nodes[track.playlist.get('id')]
            if track.audio:
                put(node, 'kdenlive:track_name', mapping[track.resource])
            node.set('out', str(new_end - 1))
            for unit, (start, end) in enumerate(((0, cut_start), (cut_end, self.end))):
                chain = deepcopy(nodes[track.chain.get('id')])
                chain_id = unique('s02chain')
                chain.set('id', chain_id)
                root.insert(list(root).index(playlist), chain)
                entry = ET.SubElement(playlist, 'entry', producer=chain_id, **{'in': str(start), 'out': str(end - 1)})
                put(entry, 'kdenlive:id', props(chain)['kdenlive:id'])
                if track.audio and gain_edges and unit == 0 and track == min(audios, key=lambda t: str(t.resource)):
                    put(entry, 'kdenlive:activeeffect', 0)
                    f = ET.SubElement(entry, 'filter', {'id': unique('s02filter')})
                    for k, v in {'window': 75, 'max_gain': '20dB', 'channel_mask': -1, 'mlt_service': 'volume', 'kdenlive_id': 'volume', 'kdenlive:collapsed': '0', 'level': f'0=0;35=0;45=-60;55=-60;65=0;{end-start-1}=0'}.items():
                        put(f, k, v)
                groups[unit].append({'data': f'{index}:{0 if unit == 0 else cut_start}:-1', 'leaf': 'clip', 'type': 'Leaf'})
            # All track elements precede filters/transitions in native saves.
            last_track = seq.findall('track')[-1]
            seq.insert(list(seq).index(last_track) + 1, ET.Element('track', producer=node.get('id')))
            transition = ET.SubElement(seq, 'transition', id=unique('s02transition'))
            values = {'a_track': 0, 'b_track': index + 1, 'mlt_service': 'mix' if track.audio else 'qtblend', 'kdenlive_id': 'mix' if track.audio else 'qtblend', 'internal_added': 237, 'always_active': 1}
            values.update({'sum': 1, 'accepts_blanks': 1} if track.audio else {'compositing': 0, 'distort': 0, 'rotate_center': 0})
            for k, v in values.items():
                put(transition, k, v)
        # Disconnected linked/default tracks must not survive as hidden audible paths.
        kept_ids = {t.node.get('id') for t in kept}
        for t in self.sequence.findall('track')[1:]:
            if t.get('producer') not in kept_ids:
                old = nodes[t.get('producer')]
                for p in old.findall('track'):
                    root.remove(nodes[p.get('producer')])
                root.remove(old)
        guide = [{'comment': f'Manual shared cut [{cut_start},{cut_end}) source frames', 'duration': 0, 'pos': cut_start, 'type': 0}]
        for k, v in {'groups': json.dumps([{'children': g, 'type': 'Normal'} for g in groups]), 'guides': json.dumps(guide), 'tracksCount': len(kept), 'zonein': 0, 'zoneout': new_end, 'position': 0, 'activeTrack': 0, 'audioTarget': 0, 'videoTarget': len(kept)-1}.items():
            put(seq, 'kdenlive:sequenceproperties.' + k, v)
        put(seq, 'kdenlive:markers', json.dumps(guide))
        put(seq, 'kdenlive:duration', str(new_end))
        put(seq, 'kdenlive:maxduration', new_end)
        seq.set('out', str(new_end - 1))
        for tractor in root.findall('tractor'):
            if props(tractor).get('kdenlive:projectTractor') == '1':
                tractor.set('out', str(new_end - 1))
                for t in tractor.findall('track'):
                    t.set('out', str(new_end - 1))
        ET.indent(root, space=' ')
        with output.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(ET.tostring(root, encoding='unicode', xml_declaration=True) + '\n')
        return {'adapter': BUILD, 'compatibility': self.compatibility, 'manual_cut_source_frames': [cut_start, cut_end], 'retained_source_frames': [[0, cut_start], [cut_end, self.end]], 'output_frames': new_end, 'input_clip_frames': self.end, 'input_sequence_extent_delta_frames': self.extent_delta, 'participants': len(audios), 'excluded_mp4_audio_tracks': len(self.excluded), 'gain_edges': gain_edges, 'source_timing_certified': False}


def read(project):
    """Registry boundary; unknown builds/structures are not silently downgraded."""
    return Kdenlive260802(project)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--cut', nargs=2, required=True, type=int, metavar=('START', 'END'))
    parser.add_argument('--names', required=True, type=Path, help='Local JSON mapping WAV paths to display names.')
    parser.add_argument('--experimental', action='store_true')
    parser.add_argument('--gain-edge-proof', action='store_true')
    args = parser.parse_args()
    try:
        names = json.loads(args.names.read_text(encoding='utf-8'))
        result = read(args.project).export(args.output, *args.cut, names, args.gain_edge_proof, args.experimental)
    except Unsupported as exc:
        parser.exit(1, f'S02 export refused: {exc}\n')
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError):
        parser.exit(1, 'S02 export refused; inspect the simple starter, local mapping and new output path privately.\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
