#!/usr/bin/env python3
"""Prepare copies of synthetic S01 captures; requires manual publication review."""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from s01_fixture_media import sha256
from s01_project_census import MAX_BYTES, census, RESOURCE_KEYS

REMOVE_PROPERTIES = frozenset((
    'kdenlive:docproperties.browserurl', 'kdenlive:docproperties.profile',
    'kdenlive:docproperties.layout', 'kdenlive:documentnotes',
))


def sanitize(project, manifest_path, output):
    project, manifest_path, output = Path(project), Path(manifest_path), Path(output)
    census(project)  # bounded UTF-8, DTD-free XML; no GUI or provenance verdict
    if manifest_path.stat().st_size > MAX_BYTES:
        raise ValueError('Synthetic manifest is too large.')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('provenance') != 'generated_synthetic_media_no_recorded_people':
        raise ValueError('Only generated S01 synthetic media is accepted.')
    media_root = manifest_path.parent.resolve()
    allowed = {}
    for item in manifest['files']:
        relative = Path(item['path'])
        if relative.is_absolute() or len(relative.parts) != 1 or relative.name in ('.', '..'):
            raise ValueError('Manifest media names must be simple local basenames.')
        media = (media_root / relative).resolve()
        if not media.is_relative_to(media_root) or sha256(media) != item['sha256']:
            raise ValueError('Synthetic source does not match its manifest.')
        allowed[media] = item
    raw = project.read_bytes()
    root = ET.fromstring(raw.decode('utf-8-sig'))
    if root.get('root') not in ('.', str(project.parent.resolve()).replace('\\', '/'), str(project.parent.resolve())):
        raise ValueError('Capture root differs from the captured project location.')
    removed = []
    for parent in root.iter():
        for child in list(parent):
            if child.tag == 'property' and child.get('name') in REMOVE_PROPERTIES:
                removed.append(child.get('name'))
                parent.remove(child)
    resources = 0
    for prop in root.iter('property'):
        if prop.get('name') not in RESOURCE_KEYS or not prop.text or prop.text in ('black', '-', '0'):
            continue
        value = prop.text
        if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', value) and not re.match(r'^[A-Za-z]:[/\\]', value):
            raise ValueError('URL/service resources cannot be published by this capture tool.')
        source = (project.parent / value).resolve()
        if source not in allowed:
            raise ValueError('Project references media outside the verified synthetic manifest.')
        # The public package has one sibling media-2 directory, never private media.
        target = output.parent / 'media-2' / source.name
        if target.is_symlink() or sha256(target) != allowed[source]['sha256']:
            raise ValueError('Public media copy is missing or changed.')
        prop.text = 'media-2/' + source.name
        resources += 1
    if not resources:
        raise ValueError('No synthetic file resources were found.')
    # In this build '.' resolves against the process cwd, not the project folder.
    # An absent root lets Kdenlive use the opened project's directory.
    root.attrib.pop('root', None)
    sanitized = ET.tostring(root, encoding='unicode', xml_declaration=True)
    if re.search(r'[A-Za-z]:[/\\]|\\\\|(?:https?|file)://', sanitized):
        raise ValueError('Unreviewed absolute path or URL remains; inspect privately.')
    with output.open('x', encoding='utf-8', newline='\n') as destination:
        destination.write(sanitized + '\n')
    return {'raw_capture_sha256': sha256(project), 'sanitized_sha256': sha256(output),
            'resource_references': resources, 'removed_properties': sorted(set(removed)),
            'root_attribute_removed': True, 'manual_publication_review': 'REQUIRED',
            'gui_reopen_of_sanitized_copy': 'NOT RUN'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--media-manifest', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = sanitize(args.project, args.media_manifest, args.output)
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError):
        parser.exit(1, 'Sanitization refused; source unchanged. Review capture and synthetic media privately.\n')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
