#!/usr/bin/env python3
"""Observe local picture boundaries; optionally write a separate refined plan.

Preliminary S09 interface; the integrated recoverable CLI belongs to S10.
"""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.contracts import Analysis, dumps, loads
from interview_auto_editor.picture import PictureAnalysis, PictureRequest, analyze_picture, refine_picture_seams
from interview_auto_editor.planner import PlanningResult
from interview_auto_editor.speech import atomic_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    analyze = sub.add_parser('analyze')
    for name in ('analysis', 'request', 'video', 'ffmpeg', 'ffprobe', 'output'):
        analyze.add_argument('--'+name, type=Path, required=True)
    refine = sub.add_parser('refine')
    for name in ('result', 'picture', 'output'):
        refine.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise FileExistsError('New output required.')
        if args.command == 'analyze':
            analysis = loads(Analysis, args.analysis.read_text(encoding='utf-8'))
            request = loads(PictureRequest, args.request.read_text(encoding='utf-8'))
            value = analyze_picture(analysis, request, args.video, args.ffmpeg, args.ffprobe)
        else:
            base = loads(PlanningResult, args.result.read_text(encoding='utf-8'))
            picture = loads(PictureAnalysis, args.picture.read_text(encoding='utf-8'))
            value = refine_picture_seams(base, picture)
        atomic_new(args.output, dumps(value))
    except KeyboardInterrupt:
        return 130
    except (OSError, ValueError, TypeError, KeyError, StopIteration):
        parser.exit(1, 'S09 refused; inspect input bindings, layout, frame budget and new destination locally.\n')
    print('S09 result written; recorded picture identity/delay requires review. Keep real records private.')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
