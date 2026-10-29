#!/usr/bin/env python3
"""Write a new experimental grouped project from a private S06 planning result."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.adapters.export import export_project
from interview_auto_editor.adapters.kdenlive import read_starter, resolve_resource
from interview_auto_editor.contracts import loads
from interview_auto_editor.intake import MappingManifest
from interview_auto_editor.planner import PlanningResult


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('project','mapping','result','output','ffprobe'):
        parser.add_argument('--'+name,required=True,type=Path)
    parser.add_argument('--experimental',action='store_true')
    args=parser.parse_args()
    try:
        result=loads(PlanningResult,args.result.read_text(encoding='utf-8'))
        mapping=loads(MappingManifest,args.mapping.read_text(encoding='utf-8'))
        if mapping.relocations:
            raise ValueError('Explicit relocation export is not supported yet.')
        starter=read_starter(args.project)
        video=next(s.source_id for s in result.plan.analysis.sources if s.kind=='video')
        bindings={p.source_id:resolve_resource(p.resource,args.mapping.resolve().parent) for p in mapping.participants}
        bindings[video]=next(t.resource for t in starter.tracks if not t.audio)
        report=export_project(result,args.project,bindings,{p.source_id:p.display_name for p in mapping.participants},args.output,args.ffprobe,experimental=args.experimental)
    except KeyboardInterrupt:
        return 130
    except (OSError,ValueError,TypeError,KeyError,StopIteration):
        parser.exit(1,'S07 export refused; inspect the private plan, mapping, starter and new destination locally.\n')
    print(json.dumps(report,indent=2))
    return 2 if result.plan.reviews else 0


if __name__=='__main__':
    raise SystemExit(main())
