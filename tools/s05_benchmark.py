#!/usr/bin/env python3
"""Evaluate an explicit LOCAL development manifest. Never opens held-out data.

Clip-category labels measure clip detection only, never word/event retention.
No media, source paths, hashes or transcripts are included in the public summary.
"""
import argparse
from dataclasses import dataclass
from fractions import Fraction
import json
from pathlib import Path
import sys
import time
from typing import Literal

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.contracts import dumps, loads
from interview_auto_editor.probe import fingerprint, probe_wav
from interview_auto_editor.reactions import Settings as ReactionSettings, YamnetCPU, infer_channel
from interview_auto_editor.speech import Settings, SileroCPU, atomic_new, decode_channel, infer_regions


@dataclass(frozen=True)
class Label:
    kind: Literal['speech','acknowledgement','laughter','chuckle','simultaneous_talk','uncertainty','noise']
    start_sample: int
    end_sample: int


@dataclass(frozen=True)
class Case:
    fixture_id: str
    path: str  # Private manifest only, relative to that manifest when relative.
    pcm_channel: int
    annotation_method: Literal['construction_sample_bounds','human_sample_bounds','upstream_clip_category']
    labels: tuple[Label, ...]


@dataclass(frozen=True)
class Manifest:
    schema_version: Literal[1]
    split: Literal['development']
    provenance: str
    cases: tuple[Case, ...]


def protected_fraction(ranges,a,b):
    end=a
    covered=Fraction(0)
    for start,stop in sorted(ranges):
        lo,hi=max(start,a,end),min(stop,b)
        if lo<hi:
            covered+=hi-lo
            end=hi
    return covered/(b-a)


def evaluate(manifest,base,speech_model,reaction_model,ffmpeg):
    manifest=loads(Manifest,dumps(manifest))
    speech=SileroCPU(speech_model)
    reaction=YamnetCPU(reaction_model)
    results=[]
    total_seconds=0
    started=time.monotonic()
    for case in manifest.cases:
        path=Path(case.path)
        if not path.is_absolute():
            path=base/path
        ap=probe_wav(path)
        if not 0<=case.pcm_channel<ap.channels or not case.labels:
            raise ValueError('Invalid benchmark channel/labels')
        for label in case.labels:
            if not 0<=label.start_sample<label.end_sample<=ap.sample_count:
                raise ValueError('Out-of-range label')
        before=fingerprint(path)
        expected=-(-ap.sample_count*16000//ap.sample_rate)
        s,count=infer_regions(decode_channel(path,case.pcm_channel,ffmpeg,expected),speech)
        r,rcount,floor=infer_channel(decode_channel(path,case.pcm_channel,ffmpeg,expected),reaction)
        if count!=rcount or fingerprint(path)!=before:
            raise ValueError('Source/count changed')
        duration=ap.duration
        def bounds(runs,padding=True):
            onset,tail=(Settings().onset,Settings().tail) if padding else (0,0)
            return [(max(Fraction(0),Fraction(a,16000)-onset),min(duration,Fraction(b,16000)+tail)) for a,b,_ in runs]
        speech_raw=bounds(s['speech'],False)
        reaction_raw=bounds(r['reaction'],False)
        baseline=bounds(s['speech']+s['uncertainty'])
        fused=baseline+bounds(r['reaction']+r['uncertainty'])
        total_seconds+=float(duration)
        for label in case.labels:
            a,b=Fraction(label.start_sample,ap.sample_rate),Fraction(label.end_sample,ap.sample_rate)
            results.append({'id':case.fixture_id,'kind':label.kind,'annotation_method':case.annotation_method,
                'speech_model_hit':any(x<b and y>a for x,y in speech_raw),
                'reaction_model_hit':any(x<b and y>a for x,y in reaction_raw),
                's04_protected_fraction':str(protected_fraction(baseline,a,b)),
                'fused_protected_fraction':str(protected_fraction(fused,a,b)),
                'full_retention_assessable':case.annotation_method!='upstream_clip_category',
                'empirical_rms_floor_db_bin':floor[0]})
    elapsed=time.monotonic()-started
    groups=[]
    for kind in sorted({r['kind'] for r in results}):
        rows=[r for r in results if r['kind']==kind]
        groups.append({'kind':kind,'labels':len(rows),
            'speech_model_hits':sum(r['speech_model_hit'] for r in rows),
            'reaction_model_hits':sum(r['reaction_model_hit'] for r in rows),
            'reaction_hits_without_speech_model':sum(r['reaction_model_hit'] and not r['speech_model_hit'] for r in rows),
            'sample_bound_labels':sum(r['full_retention_assessable'] for r in rows),
            'fully_fused_protected_sample_bound_labels':sum(r['full_retention_assessable'] and r['fused_protected_fraction']=='1' for r in rows)})
    return {'schema_version':1,'step':'S05','split':'development','provenance':manifest.provenance,
        'compatibility':'EXPERIMENTAL','settings':{'speech':json.loads(dumps(Settings())),
            'reactions':json.loads(dumps(ReactionSettings()))},
        'seconds':round(elapsed,3),'source_channel_seconds':round(total_seconds,3),
        'real_time_factor_including_two_decodes':round(elapsed/total_seconds,6) if total_seconds else None,
        'groups':groups,'cases':results,'held_out_opened':False,
        'g04_private_interview_acceptance':'NOT_ESTABLISHED_BY_THIS_BENCHMARK',
        'warning':'Clip labels measure detection, not boundaries. Scores are uncalibrated. Noise hits are reported, never removed.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('manifest','speech-model','reaction-model','ffmpeg','report'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.report.exists():
        parser.exit(1,'Benchmark report already exists.\n')
    try:
        manifest=loads(Manifest,args.manifest.read_text(encoding='utf-8'))
        result=evaluate(manifest,args.manifest.parent,args.speech_model,args.reaction_model,args.ffmpeg)
        atomic_new(args.report,json.dumps(result,indent=2)+'\n')
    except (OSError,ValueError,TypeError,KeyError):
        parser.exit(1,'Benchmark refused; inspect private manifest, models and tools locally.\n')
    print('Development metrics written. Held-out data unopened; private G04 acceptance remains separate.')


if __name__=='__main__':
    main()
