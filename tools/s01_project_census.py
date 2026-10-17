#!/usr/bin/env python3
"""Read-only XML census for fixture capture; no import or compatibility verdict."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

MAX_BYTES = 8 * 1024 * 1024
VERSION_KEYS = ('kdenlive:docproperties.version', 'kdenlive:docproperties.kdenliveversion')
RESOURCE_KEYS = ('resource', 'kdenlive:originalurl', 'kdenlive:proxy')


def resource_kind(value):
    value = value.strip()
    if value in ('', '-', '0', 'black'):
        return 'empty_or_internal'
    if re.match(r'^[A-Za-z]:[\\/]', value) or value.startswith(('\\\\', '/')):
        return 'absolute_path'
    if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', value):
        return 'url_or_service'
    return 'relative_or_unclassified'


def census(project):
    with Path(project).open('rb') as source:
        raw = source.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Project exceeds the capture census size limit.')
    text = raw.decode('utf-8-sig')
    if re.search(r'<!\s*(DOCTYPE|ENTITY)\b', text, re.IGNORECASE):
        raise ValueError('DTD/entity declarations are not accepted.')
    root = ET.fromstring(text)
    if root.tag != 'mlt':
        raise ValueError('Expected an MLT XML root, not a supported-project verdict.')
    elements = Counter(node.tag for node in root.iter())
    resources = Counter()
    versions = {}
    for prop in root.iter('property'):
        name, value = prop.get('name'), prop.text or ''
        if name in RESOURCE_KEYS:
            resources[resource_kind(value)] += 1
        if name in VERSION_KEYS:
            # Never echo arbitrary document text into a potentially public report.
            versions[name] = value if re.fullmatch(r'[0-9]+(?:\.[0-9]+){0,3}', value) else 'REDACTED'
    return {'schema_version': 1, 'source_sha256': hashlib.sha256(raw).hexdigest(),
            'source_bytes': len(raw), 'document_versions': versions,
            'element_counts': {name: elements[name] for name in
                               ('producer', 'chain', 'playlist', 'tractor', 'track', 'entry', 'filter', 'transition')},
            'resource_kinds': dict(sorted(resources.items())),
            'root_has_absolute_path': any(resource_kind(value) == 'absolute_path' for value in root.attrib.values()),
            'provenance': 'unverified_requires_capture_record',
            'compatibility': 'NOT ASSESSED', 'gui_open_save': 'NOT RUN',
            'publication_review': 'REQUIRED; counts do not sanitize or certify the source XML'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path, help='New JSON report; never overwrite.')
    args = parser.parse_args()
    try:
        result = census(args.project)
        if args.report.resolve() == args.project.resolve():
            raise ValueError('Report cannot replace source.')
        with args.report.open('x', encoding='utf-8', newline='\n') as report:
            report.write(json.dumps(result, indent=2) + '\n')
    except (OSError, ValueError, ET.ParseError):
        parser.exit(1, 'Census failed; source unchanged. Inspect input/report locations privately.\n')
    print('Census written. GUI evidence, provenance and publication review remain required.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
