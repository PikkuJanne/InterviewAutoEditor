#!/usr/bin/env python3
"""S05 local fused evidence command. Review required; no automatic editing."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.adapters.kdenlive import IntakeError, resolve_resource
from interview_auto_editor.contracts import dumps, loads
from interview_auto_editor.intake import MappingManifest, inspect
from interview_auto_editor.speech import SpeechError, SileroCPU, analyze as speech_analyze, atomic_new
from interview_auto_editor.reactions import YamnetCPU, analyze


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('project','mapping','ffprobe','ffmpeg','speech-model','reaction-model','cache','report'):
        parser.add_argument('--'+name,required=True,type=Path)
    parser.add_argument('--analysis',type=Path,help='New PRIVATE fused v1 contract, containing source hashes/labels.')
    parser.add_argument('--anchor',type=Fraction,action='append',default=[])
    parser.add_argument('--chunk-samples',type=int,default=8192)
    parser.add_argument('--allow-unc',action='store_true')
    args=parser.parse_args()
    try:
        SileroCPU(args.speech_model)
        YamnetCPU(args.reaction_model)
        if args.report.exists() or (args.analysis and args.analysis.exists()):
            raise SpeechError('OUTPUT_ALREADY_EXISTS')
        if args.analysis and args.analysis.resolve()==args.report.resolve():
            raise SpeechError('OUTPUT_PATHS_MUST_DIFFER')
        with args.mapping.open(encoding='utf-8-sig') as stream:
            mapping=loads(MappingManifest,stream.read(8*1024*1024+1))
        intake=inspect(args.project,mapping,args.ffprobe,mapping_base=args.mapping.parent,
            ffmpeg=args.ffmpeg if args.anchor else None,anchor_starts=args.anchor,allow_unc=args.allow_unc)
        paths={p.source_id:resolve_resource(p.resource,args.mapping.parent,allow_unc=args.allow_unc) for p in mapping.participants}
        speech=speech_analyze(intake,paths,args.speech_model,args.ffmpeg,args.cache/'speech',chunk_samples=args.chunk_samples)
        result=analyze(speech,paths,args.reaction_model,args.ffmpeg,args.cache/'reactions',chunk_samples=args.chunk_samples)
        if args.analysis:
            atomic_new(args.analysis,dumps(result.analysis))
        atomic_new(args.report,json.dumps(result.summary(),indent=2)+'\n')
    except (SpeechError,IntakeError) as exc:
        parser.exit(1,f'S05 analysis refused: {exc}\n')
    except KeyboardInterrupt:
        parser.exit(130,'S05 cancelled. Completed caches survive; sources unchanged.\n')
    except (OSError,ValueError,TypeError,KeyError,OverflowError):
        parser.exit(1,'S05 analysis failed; inspect local inputs/tools/cache privately. Sources unchanged.\n')
    print('Fused local event evidence written. Review required; no cuts or alignment certificate.')
    return 2


if __name__=='__main__':
    raise SystemExit(main())
