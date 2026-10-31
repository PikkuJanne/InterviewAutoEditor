#!/usr/bin/env python3
"""S04 offline speech evidence command, not the S10 product CLI. No edits."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.adapters.kdenlive import IntakeError, resolve_resource
from interview_auto_editor.contracts import dumps, loads
from interview_auto_editor.intake import MappingManifest, inspect
from interview_auto_editor.speech import SpeechError, SileroCPU, analyze, atomic_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--mapping', type=Path, required=True)
    parser.add_argument('--ffprobe', type=Path, required=True)
    parser.add_argument('--ffmpeg', type=Path, required=True)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--cache', type=Path, required=True, help='Private local cache directory.')
    parser.add_argument('--report', type=Path, required=True, help='New sanitized report; still review before publishing.')
    parser.add_argument('--analysis', type=Path, help='Optional new PRIVATE strict contract with source hashes/IDs.')
    parser.add_argument('--anchor', type=Fraction, action='append', default=[])
    parser.add_argument('--chunk-samples', type=int, default=8192)
    parser.add_argument('--allow-unc', action='store_true')
    args = parser.parse_args()
    try:
        # Fail visibly and before media probing; no energy-only fallback.
        SileroCPU(args.model)
        if args.report.exists() or (args.analysis and args.analysis.exists()):
            raise SpeechError('OUTPUT_ALREADY_EXISTS')
        if args.analysis and args.analysis.resolve() == args.report.resolve():
            raise SpeechError('OUTPUT_PATHS_MUST_DIFFER')
        with args.mapping.open(encoding='utf-8-sig') as stream:
            mapping = loads(MappingManifest, stream.read(8 * 1024 * 1024 + 1))
        intake = inspect(args.project, mapping, args.ffprobe, mapping_base=args.mapping.parent,
                         ffmpeg=args.ffmpeg if args.anchor else None,
                         anchor_starts=args.anchor, allow_unc=args.allow_unc)
        paths = {p.source_id: resolve_resource(p.resource, args.mapping.parent, allow_unc=args.allow_unc)
                 for p in mapping.participants}
        result = analyze(intake, paths, args.model, args.ffmpeg, args.cache,
                         chunk_samples=args.chunk_samples)
        if args.analysis:
            atomic_new(args.analysis, dumps(result.analysis))
        atomic_new(args.report, json.dumps(result.summary(), indent=2) + '\n')
    except (SpeechError, IntakeError) as exc:
        parser.exit(1, f'S04 analysis refused: {exc}\n')
    except KeyboardInterrupt:
        parser.exit(130, 'S04 analysis cancelled. Completed track caches may be reused; sources unchanged.\n')
    except (OSError, ValueError, TypeError, KeyError, OverflowError):
        parser.exit(1, 'S04 analysis failed; check local inputs, tools and cache privately. Sources unchanged.\n')
    print('Offline speech evidence written. Review required; analysis does not authorize cuts or certify alignment.')
    return 2  # Analysis-only; no ready-for-editing claim.


if __name__ == '__main__':
    raise SystemExit(main())
