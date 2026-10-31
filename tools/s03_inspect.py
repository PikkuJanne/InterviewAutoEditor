#!/usr/bin/env python3
"""S03 read-only setup/timing diagnostics; not the S10 product CLI."""
import argparse
import json
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.adapters.kdenlive import IntakeError
from interview_auto_editor.contracts import loads
from interview_auto_editor.intake import MappingManifest, inspect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--mapping', type=Path, required=True)
    parser.add_argument('--ffprobe', type=Path, required=True)
    parser.add_argument('--ffmpeg', type=Path)
    parser.add_argument('--anchor', action='append', type=Fraction, default=[], help='Source seconds for an optional 4s diagnostic window; repeat at start/middle/end.')
    parser.add_argument('--report', type=Path, required=True, help='New sanitized JSON report. Existing files are never overwritten.')
    parser.add_argument('--allow-unc', action='store_true', help='Explicit untested UNC read opt-in.')
    args = parser.parse_args()
    try:
        if args.report.exists():
            raise IntakeError('REPORT_ALREADY_EXISTS')
        with args.mapping.open('r', encoding='utf-8-sig') as stream:
            mapping = loads(MappingManifest, stream.read(8 * 1024 * 1024 + 1))
        if bool(args.anchor) != bool(args.ffmpeg):
            raise IntakeError('DIAGNOSTIC_REQUIRES_FFMPEG_AND_ANCHORS')
        result = inspect(args.project, mapping, args.ffprobe, mapping_base=args.mapping.parent,
                         ffmpeg=args.ffmpeg, anchor_starts=args.anchor, allow_unc=args.allow_unc)
        with args.report.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(result.summary(), stream, indent=2)
            stream.write('\n')
    except IntakeError as exc:
        parser.exit(1, f'S03 inspection refused: {exc}\n')
    except (OSError, ValueError, TypeError, KeyError, OverflowError):
        parser.exit(1, 'S03 inspection failed; check local inputs, tools and mapping privately. Sources unchanged.\n')
    print('Read-only inspection report written. Review timing/origin diagnostics before planning.')
    return 0 if result.ready else 2


if __name__ == '__main__':
    raise SystemExit(main())
