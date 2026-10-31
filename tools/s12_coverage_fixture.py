#!/usr/bin/env python3
"""Build ONLY a generated EOF experiment, never an export path for interviews.

The project below is hand-relinked/constructed. Native saves/render need actual
Kdenlive provenance separately. No Application/desktop policy is changed.
"""
from array import array
from fractions import Fraction as F
import argparse
import json
from pathlib import Path
import random
import shutil
import sys
import wave
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.adapters.export import put
from interview_auto_editor.adapters.kdenlive import props
from interview_auto_editor.contracts import dumps
from s12_coverage import CoverageReview, preview_coverage
from interview_auto_editor.intake import FileMapping, MappingManifest, inspect
from interview_auto_editor.planner import analysis_digest
from interview_auto_editor.probe import fingerprint


def generate(output, ffprobe):
    original = Path(__file__).resolve().parents[1] / 'tests/fixtures/kdenlive-26.08.2'
    folder = Path(output).resolve()
    folder.mkdir(parents=True, exist_ok=False)
    media = folder / 'media'
    media.mkdir()
    rate = 192000
    for i, delta in enumerate((2048, -2048), 1):
        count = 12*rate + delta
        rng = random.Random(1200+i)
        # Aperiodic nonzero PCM across the entire file, including final sample.
        samples = array('h', (rng.choice((-1, 1))*rng.randint(100, 1000) for _ in range(count)))
        with wave.open(str(media / f'participant-{i:02}.wav'), 'wb') as w:
            w.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
            w.writeframes(samples.tobytes())
    shutil.copyfile(original / 'media-2/zoom-source.mp4', media / 'zoom-source.mp4')
    root = ET.parse(original / 'starter-2.kdenlive').getroot()
    root.attrib.pop('root', None)
    for chain in root.findall('chain'):
        resource = props(chain).get('resource')
        if resource:
            put(chain, 'resource', 'media/' + Path(resource).name)
            for prop in list(chain.findall('property')):
                if prop.get('name', '').startswith(('meta.', 'kdenlive:meta.')) or prop.get('name') in ('kdenlive:file_hash', 'kdenlive:file_size'):
                    chain.remove(prop)
            if resource.endswith('.mp4'):
                for key, value in (('audio_index', -1), ('astream', -1), ('set.test_audio', 1)):
                    put(chain, key, value)
    def save(path):
        ET.indent(root, space=' ')
        with path.open('x', encoding='utf-8', newline='\n') as out:
            out.write(ET.tostring(root, encoding='unicode', xml_declaration=True)+'\n')
    before = folder / 'constructed-starter.kdenlive'
    save(before)
    mapping = MappingManifest(1, tuple(FileMapping(f'media/participant-{i:02}.wav',
        f'p{i}', f'Participant {i:02}', (f'participant{i}',)) for i in (1,2)), ())
    analysis = inspect(before, mapping, ffprobe, mapping_base=folder).analysis
    # Intentionally retain intake's unverified/null audio origins. This tool
    # builds an explicit synthetic representation, NOT an authorized EditPlan.
    review = CoverageReview(2, analysis_digest(analysis), 'preserve_samples_mark_empty_eof',
        'synthetic construction', 'Generated EOF counts; preview only, no source-clock approval', True)
    preview = preview_coverage(analysis, review)
    nodes = {n.get('id'): n for n in root if n.get('id')}
    seq = next(n for n in root.findall('tractor') if 'kdenlive:sequenceproperties.groups' in props(n))
    end = preview.time_map.output_frames
    common = {c.source_id: c for c in preview.sources}
    identities = {'zoom-source.mp4': 'video', 'participant-01.wav': 'p1', 'participant-02.wav': 'p2'}
    for chain in root.findall('chain'):
        resource = props(chain).get('resource')
        if not resource:
            continue
        coverage = common[identities[Path(resource).name]]
        chain.set('out', str(coverage.clip_end_frame-1))
        put(chain, 'length', coverage.clip_end_frame)
        # EOF absence is decoded silence/blank; never pause/repeat the source.
        put(chain, 'eof', 'continue')
    groups = []
    for index, ref in enumerate(seq.findall('track')[1:]):
        tractor = nodes[ref.get('producer')]
        tractor.set('out', str(end-1))
        for plref in tractor.findall('track'):
            pl = nodes[plref.get('producer')]
            for entry in pl.findall('entry'):
                chain = nodes[entry.get('producer')]
                coverage = common[identities[Path(props(chain)['resource']).name]]
                entry.set('in', '0')
                entry.set('out', str(coverage.clip_end_frame-1))
                if coverage.clip_end_frame < end:
                    ET.SubElement(pl, 'blank', length=str(end-coverage.clip_end_frame))
                groups.append({'data': f'{index}:0:-1', 'leaf': 'clip', 'type': 'Leaf'})
    guide = [{'comment': 'EMPTY PICTURE AFTER RECORDED EOF; original audio samples retained; no source shift',
              'duration': 0, 'pos': 300, 'type': 0}]
    for key, value in {'groups': json.dumps([{'children': groups, 'type': 'Normal'}]),
                       'guides': json.dumps(guide), 'zonein': 0, 'zoneout': end,
                       'position': 0}.items():
        put(seq, 'kdenlive:sequenceproperties.'+key, value)
    put(seq, 'kdenlive:markers', json.dumps(guide))
    for key in ('kdenlive:duration', 'kdenlive:maxduration'):
        put(seq, key, end)
    seq.set('out', str(end-1))
    for tractor in root.findall('tractor'):
        if props(tractor).get('kdenlive:projectTractor') == '1':
            tractor.set('out', str(end-1))
            for ref in tractor.findall('track'):
                ref.set('out', str(end-1))
    save(folder / 'constructed-coverage.kdenlive')
    (folder/'analysis.json').write_text(dumps(analysis), encoding='utf-8', newline='\n')
    (folder/'mapping.json').write_text(dumps(mapping), encoding='utf-8', newline='\n')
    (folder/'coverage-preview.json').write_text(dumps(preview), encoding='utf-8', newline='\n')
    manifest = {'schema_version': 1, 'provenance': 'generated_synthetic_media_no_recorded_people',
        'construction': 'Hand-relinked native S01 template; not Kdenlive-authored; not a production export',
        'gui_evidence': 'NOT_RUN', 'source_frames': 300, 'coverage_frames': end,
        'sample_rate': rate, 'audio_sample_counts': [2306048, 2301952],
        'files': [{'path': p.relative_to(folder).as_posix(), 'sha256': fingerprint(p)}
                  for p in sorted(folder.rglob('*')) if p.is_file()]}
    (folder/'construction.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8', newline='\n')
    return {'source_frames': 300, 'coverage_frames': end, 'production_export': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--ffprobe', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(generate(args.output, args.ffprobe), indent=2))
