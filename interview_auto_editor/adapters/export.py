"""Experimental 26.08.2 grouped export from a reproducible approved S06 result."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

from .kdenlive import MAX_XML, IntakeError, props, read_starter, resolve_resource
from ..probe import fingerprint, probe_video, probe_wav
from ..turns import build_turns, pieces


def put(node, name, value):
    prop = node.find(f"property[@name='{name}']")
    if prop is None:
        prop = ET.SubElement(node, 'property', name=name)
    prop.text = str(value)


def export_project(result, project, bindings, names, output, ffprobe, *, experimental=False, cleanup=None):
    """Bindings map every canonical source ID to its explicit local resource.

    Validate strict contracts, reproducibility, starter/media fingerprints and
    actual complete media grids before writing a new file atomically. Optional
    S08 cleanup is separately reproduced; the canonical v1 plan stays unchanged.
    """
    if not experimental:
        raise IntakeError('EXPERIMENTAL_EXPORT_REQUIRES_OPT_IN')
    layout = build_turns(result)
    plan = layout.plan
    peak_report = None
    if cleanup is not None:
        from ..cleanup import validate_cleanup, native_keys
        from ..peaks import measure_peaks
        cleanup = validate_cleanup(result, cleanup)
    project, output = Path(project).resolve(), Path(output).resolve()
    starter = read_starter(project)
    if fingerprint(project) != plan.analysis.header.project_sha256:
        raise IntakeError('PLAN_PROJECT_FINGERPRINT_MISMATCH')
    if plan.analysis.header.adapter_target != 'kdenlive-26.08.2-experimental' or starter.fps != plan.time_map.fps or starter.clip_frames != plan.time_map.source_frames:
        raise IntakeError('PLAN_ADAPTER_OR_GRID_MISMATCH')
    sources = {s.source_id: s for s in plan.analysis.sources}
    paths = {k: Path(v).resolve() for k, v in bindings.items()}
    audios = {s.source_id for s in sources.values() if s.kind == 'participant_audio'}
    if set(paths) != set(sources) or len(set(paths.values())) != len(paths) or set(paths.values()) != {t.resource for t in starter.tracks}:
        raise IntakeError('EXPLICIT_SOURCE_BINDING_MISMATCH')
    if set(names) != audios or any(not isinstance(n, str) or not n.strip() for n in names.values()) or len({n.strip().casefold() for n in names.values()}) != len(names):
        raise IntakeError('PARTICIPANT_NAMES_REQUIRED')
    tracks = {t.resource: t for t in starter.tracks}
    for identity, path in paths.items():
        source, track = sources[identity], tracks[path]
        if track.audio != (source.kind == 'participant_audio') or fingerprint(path) != source.sha256:
            raise IntakeError('PLAN_MEDIA_FINGERPRINT_OR_KIND_MISMATCH')
        if track.audio:
            probe = probe_wav(path)
            if (probe.sample_rate, probe.sample_count) != (source.sample_rate, source.sample_count):
                raise IntakeError('PLAN_AUDIO_GRID_MISMATCH')
        else:
            probe = probe_video(path, ffprobe, track.stream_index)
            if probe.fps != starter.fps or probe.duration != source.duration or probe.start != 0 or probe.cadence != 'CFR_AUDITED':
                raise IntakeError('PLAN_VIDEO_GRID_MISMATCH')
    if output == project or output in paths.values() or output.exists():
        raise FileExistsError('Export requires a new destination.')
    if cleanup is not None:
        peak_report = measure_peaks(result, cleanup, paths)
        if not peak_report['export_safe']:
            raise IntakeError('MIX_HEADROOM_REVIEW_REQUIRED_NO_AUTOMATIC_NORMALIZATION')
    with project.open('rb') as stream:
        raw = stream.read(MAX_XML + 1)
    if len(raw) > MAX_XML or hashlib.sha256(raw).hexdigest() != plan.analysis.header.project_sha256:
        raise IntakeError('SOURCE_CHANGED_DURING_EXPORT')
    root = ET.fromstring(raw.decode('utf-8-sig'))
    nodes = {n.get('id'): n for n in root if n.get('id')}
    seq = next(n for n in root.findall('tractor') if 'kdenlive:sequenceproperties.groups' in props(n))
    base = Path(root.get('root', project.parent))
    path_by_chain = {}
    for chain in root.findall('chain'):
        value = props(chain).get('resource')
        if value:
            path = resolve_resource(value, base)
            path_by_chain[chain.get('id')] = path
            try:
                relative = os.path.relpath(path, output.parent)
            except ValueError:
                relative = str(path)
            put(chain, 'resource', relative.replace('\\', '/'))
            if path.suffix.lower() == '.mp4':
                for key, value in (('audio_index', -1), ('astream', -1), ('set.test_audio', 1)):
                    put(chain, key, value)
    for parent in root.iter():
        for prop in list(parent.findall('property')):
            if prop.get('name') in ('kdenlive:docproperties.browserurl', 'kdenlive:docproperties.profile', 'kdenlive:docproperties.layout', 'kdenlive:documentnotes'):
                parent.remove(prop)
    root.attrib.pop('root', None)
    old_tracks = [nodes[t.get('producer')] for t in seq.findall('track')[1:]]
    kept = []
    for node in old_tracks:
        entries = [(nodes[t.get('producer')], e) for t in node.findall('track') for e in nodes[t.get('producer')].findall('entry')]
        if entries and path_by_chain[entries[0][1].get('producer')] in paths.values() and not (props(node).get('kdenlive:audio_track') == '1' and path_by_chain[entries[0][1].get('producer')].suffix.lower() == '.mp4'):
            kept.append((node, *entries[0]))
        else:
            for t in node.findall('track'):
                root.remove(nodes[t.get('producer')])
            root.remove(node)
    kept.sort(key=lambda row: props(row[0]).get('kdenlive:audio_track') != '1')
    main_bin = nodes['main_bin']
    recoverable = {path_by_chain.get(e.get('producer')) for e in main_bin.findall('entry')}
    for _, _, entry in kept:
        path = path_by_chain[entry.get('producer')]
        if path not in recoverable:
            main_bin.append(deepcopy(entry))
            recoverable.add(path)
    for ref in list(seq.findall('track'))[1:]:
        seq.remove(ref)
    for transition in list(seq.findall('transition')):
        seq.remove(transition)
    units = tuple(pieces(plan))
    groups = [[] for _ in units]
    used = {n.get('id') for n in root.iter() if n.get('id')}
    def unique(prefix):
        i = 0
        while f'{prefix}{i}' in used:
            i += 1
        value = f'{prefix}{i}'
        used.add(value)
        return value
    end = plan.time_map.output_frames
    for index, (node, playlist, original) in enumerate(kept):
        chain = nodes[original.get('producer')]
        identity = next(k for k, p in paths.items() if p == path_by_chain[chain.get('id')])
        audio = sources[identity].kind == 'participant_audio'
        if audio:
            put(node, 'kdenlive:track_name', names[identity])
        for ref in node.findall('track'):
            pl = nodes[ref.get('producer')]
            for item in list(pl):
                if item.tag != 'property':
                    pl.remove(item)
        for unit, (a, b, position) in enumerate(units):
            copy = deepcopy(chain)
            copy.set('id', unique('s07chain'))
            root.insert(list(root).index(playlist), copy)
            entry = ET.SubElement(playlist, 'entry', producer=copy.get('id'), **{'in': str(a), 'out': str(b - 1)})
            put(entry, 'kdenlive:id', props(copy)['kdenlive:id'])
            if audio and cleanup is not None:
                keys = native_keys(cleanup, identity, a, b)
                if keys:
                    put(entry, 'kdenlive:activeeffect', 0)
                    effect = ET.SubElement(entry, 'filter', id=unique('s08filter'))
                    for key, value in {'window': 75, 'max_gain': '20dB', 'channel_mask': -1,
                                       'mlt_service': 'volume', 'kdenlive_id': 'volume',
                                       'kdenlive:collapsed': 0,
                                       'level': ';'.join(f'{frame}={float(db):.9g}' for frame, db in keys)}.items():
                        put(effect, key, value)
            groups[unit].append({'data': f'{index}:{position}:-1', 'leaf': 'clip', 'type': 'Leaf'})
        node.set('out', str(end - 1))
        last = seq.findall('track')[-1]
        seq.insert(list(seq).index(last) + 1, ET.Element('track', producer=node.get('id')))
        transition = ET.SubElement(seq, 'transition', id=unique('s07transition'))
        values = {'a_track': 0, 'b_track': index + 1, 'mlt_service': 'mix' if audio else 'qtblend', 'kdenlive_id': 'mix' if audio else 'qtblend', 'internal_added': 237, 'always_active': 1}
        values.update({'sum': 1, 'accepts_blanks': 1} if audio else {'compositing': 0, 'distort': 0, 'rotate_center': 0})
        for key, value in values.items():
            put(transition, key, value)
    # Multiple cues sharing a frame become one native guide, with exact source
    # coordinates in its text. Local source IDs/names are intentionally private.
    guides = {}
    for cue in layout.cues:
        pos = min(end - 1, int(cue.output_start * starter.fps))
        guides.setdefault(pos, []).append(f'{cue.kind}: {", ".join(cue.source_ids)}; source [{cue.source_start},{cue.source_end}) s')
    for _, out in list(plan.time_map.segments())[1:]:
        guides.setdefault(out.start, []).append('Approved shared pause seam')
    guide = [{'comment': ' | '.join(comments), 'duration': 0, 'pos': pos, 'type': 0} for pos, comments in sorted(guides.items())]
    for key, value in {'groups': json.dumps([{'children': g, 'type': 'Normal'} for g in groups]), 'guides': json.dumps(guide), 'tracksCount': len(kept), 'zonein': 0, 'zoneout': end, 'position': 0, 'activeTrack': 0, 'audioTarget': 0, 'videoTarget': len(kept)-1}.items():
        put(seq, 'kdenlive:sequenceproperties.' + key, value)
    put(seq, 'kdenlive:markers', json.dumps(guide))
    put(seq, 'kdenlive:duration', end)
    put(seq, 'kdenlive:maxduration', end)
    seq.set('out', str(end - 1))
    for tractor in root.findall('tractor'):
        if props(tractor).get('kdenlive:projectTractor') == '1':
            tractor.set('out', str(end - 1))
            for ref in tractor.findall('track'):
                ref.set('out', str(end - 1))
    ET.indent(root, space=' ')
    if fingerprint(project) != plan.analysis.header.project_sha256 or any(fingerprint(paths[s.source_id]) != s.sha256 for s in sources.values()):
        raise IntakeError('SOURCE_CHANGED_DURING_EXPORT')
    serialized = ET.tostring(root, encoding='unicode', xml_declaration=True) + '\n'
    if len(serialized.encode('utf-8')) > MAX_XML:
        raise IntakeError('EXPORTED_XML_EXCEEDS_BOUNDED_SIZE')
    from ..speech import atomic_new
    atomic_new(output, serialized)
    return {'compatibility': 'EXPERIMENTAL', 'adapter': '26.08.2', 'turn_algorithm': layout.algorithm,
            'participants': len(audios), 'groups': len(groups), 'output_frames': end,
            'edit_units': list(plan.edit_units), 'input_sequence_extent_delta_frames': starter.sequence_frames - starter.clip_frames,
            'excluded_mp4_audio_tracks': starter.excluded_mp4_audio,
            **({'cleanup_algorithm': cleanup.algorithm, 'gain_spans': len(cleanup.spans), 'peak_report': peak_report} if cleanup is not None else {})}
