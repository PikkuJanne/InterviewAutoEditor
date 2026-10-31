#!/usr/bin/env python3
"""Build a shareable synthetic S07 before/after package, never GUI evidence."""
from dataclasses import replace
from fractions import Fraction as F
import argparse
import json
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.adapters.export import export_project, put
from interview_auto_editor.adapters.kdenlive import props
from interview_auto_editor.contracts import Event, dumps
from interview_auto_editor.intake import FileMapping, MappingManifest, inspect
from interview_auto_editor.planner import GapApproval, PlannerRequest, analysis_digest, plan_pauses
from interview_auto_editor.probe import fingerprint
from s01_fixture_media import write_tone


def generate(output, ffprobe):
    original = Path(__file__).resolve().parents[1] / 'tests/fixtures/kdenlive-26.08.2'
    folder = Path(output).resolve()
    folder.mkdir(parents=True, exist_ok=False)
    media = folder / 'media'
    media.mkdir()
    windows = (((1, 3), (7, 9)), ((2, 4), (8, 10)))
    for i, intervals in enumerate(windows):
        write_tone(media / f'participant-{i+1:02}.wav', 576000, 330+i*110,
                   [(a*48000, b*48000) for a, b in intervals])
    shutil.copyfile(original / 'media-2/zoom-source.mp4', media / 'zoom-source.mp4')
    root = ET.parse(original / 'starter-2.kdenlive').getroot()
    root.attrib.pop('root', None)
    for chain in root.findall('chain'):
        resource = props(chain).get('resource')
        if resource:
            put(chain, 'resource', 'media/' + Path(resource).name)
            # These are newly constructed sources, not the S01 WAV bytes.
            # Drop native cached hashes so Kdenlive computes its own metadata.
            # Canonical source binding below still uses actual SHA256 probes.
            for prop in list(chain.findall('property')):
                if prop.get('name') in ('kdenlive:file_hash', 'kdenlive:file_size'):
                    chain.remove(prop)
    before = folder / 'before.kdenlive'
    ET.indent(root, space=' ')
    before.write_text(ET.tostring(root, encoding='unicode', xml_declaration=True)+'\n', encoding='utf-8', newline='\n')
    mapping = MappingManifest(1, tuple(FileMapping(f'media/participant-{i+1:02}.wav',
        f'p{i}', f'Participant {i+1:02}', (f'participant{i}',)) for i in range(2)), ())
    analysis = inspect(before, mapping, ffprobe, mapping_base=folder).analysis
    # Known construction clock applies only to this generated equal-length media.
    analysis = replace(analysis, sources=tuple(replace(s, origin_status='verified', verified_offset=F(0)) for s in analysis.sources))
    events = []
    for i, intervals in enumerate(windows):
        for j, (a, b) in enumerate(intervals):
            events.append(Event(f'p{i}-{j}', f'p{i}', 'speech', a*48000, b*48000,
                F(a)-F(3,25), F(b)+F(1,5), F(1), 'Constructed tone activity, not human speech', '', (f'participant{i}',)))
    analysis = replace(analysis, events=tuple(events))
    approval = GapApproval('construction-gap', F(4), F(7), 'construction_label',
                           'Independent digital silence on both generated participant tracks')
    result = plan_pauses(analysis, PlannerRequest(1, analysis_digest(analysis), 'tight', (approval,), ()))
    bindings = {'video': media/'zoom-source.mp4', **{p.source_id: folder/p.resource for p in mapping.participants}}
    report = export_project(result, before, bindings, {p.source_id: p.display_name for p in mapping.participants}, folder/'after.kdenlive', ffprobe, experimental=True)
    (folder/'planning-result.json').write_text(dumps(result), encoding='utf-8', newline='\n')
    (folder/'mapping.json').write_text(dumps(mapping), encoding='utf-8', newline='\n')
    manifest = {'schema_version': 1, 'provenance': 'generated_synthetic_media_no_recorded_people',
        'before_project': 'Hand-relinked copy of native S01 starter; not a new Kdenlive save',
        'after_project': 'S07 production adapter output; not Kdenlive-authored',
        'gui_evidence': 'NOT_RUN', 'source_windows_seconds': windows, 'global_gap_seconds': [4,7],
        'source_frames': 300, 'export': report,
        'files': [{'path': str(p.relative_to(folder)).replace('\\','/'), 'sha256': fingerprint(p)}
                  for p in sorted(folder.rglob('*')) if p.is_file()]}
    (folder/'construction.json').write_text(json.dumps(manifest,indent=2)+'\n', encoding='utf-8', newline='\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--ffprobe', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(generate(args.output, args.ffprobe), indent=2))
