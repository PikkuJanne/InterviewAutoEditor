#!/usr/bin/env python3
"""Construct S08 labelled tone/noise export; never manufacture GUI evidence."""
from array import array
from dataclasses import replace
from fractions import Fraction as F
import argparse
import json
import math
from pathlib import Path
import sys
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.adapters.export import export_project
from interview_auto_editor.cleanup import CleanupRequest, IdleApproval, build_cleanup, planning_digest
from interview_auto_editor.contracts import dumps, loads
from interview_auto_editor.planner import PlanningResult, plan_pauses
from interview_auto_editor.probe import fingerprint
from s07_fixture import generate as generate_base


def generate(output, ffprobe):
    generate_base(output, ffprobe)
    folder = Path(output).resolve()
    # This file was just created by generate_base in an exclusive NEW folder.
    # Its media fingerprints predate the noise construction below; never ship it.
    (folder/'after.kdenlive').unlink()
    old = loads(PlanningResult, (folder/'planning-result.json').read_text())
    # Noise labels precede the policy and are independent of detector output.
    labels = {'p0': ((F(16,5), F(4)), (F(46,5), F(51,5))),
              'p1': ((F(22,25), F(47,25)), (F(7), F(197,25)))}
    for i, (identity, windows) in enumerate(labels.items()):
        path = folder/f'media/participant-{i+1:02}.wav'
        with wave.open(str(path), 'rb') as wav:
            data = array('h', wav.readframes(wav.getnframes()))
        for a, b in windows:
            lo, hi = int(a*48000), int(b*48000)
            for n in range(lo, hi):
                edge = min(1, (n-lo)/240, (hi-1-n)/240)
                data[n] += round(3000*edge*math.sin(2*math.pi*(880+i*220)*n/48000))
        with wave.open(str(path), 'wb') as wav:
            wav.setparams((1,2,48000,0,'NONE','not compressed'))
            wav.writeframes(data.tobytes())
    bindings = {'video': folder/'media/zoom-source.mp4', 'p0': folder/'media/participant-01.wav', 'p1': folder/'media/participant-02.wav'}
    a = replace(old.plan.analysis, sources=tuple(replace(s, sha256=fingerprint(bindings[s.source_id])) for s in old.plan.analysis.sources))
    from interview_auto_editor.planner import analysis_digest
    result = plan_pauses(a, replace(old.request, analysis_sha256=analysis_digest(a)))
    approvals = tuple(IdleApproval(f'{identity}-idle-{i}',identity,start,end,'construction_label',
                     'Independent generated noise-only interval; no vocal content')
                     for identity, intervals in labels.items() for i,(start,end) in enumerate(intervals))
    request = CleanupRequest(1, planning_digest(result), approvals)
    cleanup = build_cleanup(result, request)
    names = {'p0':'Participant 01','p1':'Participant 02'}
    reports = {}
    for name, policy in (('baseline',None),('cleaned',cleanup),('restored',build_cleanup(result,replace(request,approvals=())))):
        reports[name] = export_project(result,folder/'before.kdenlive',bindings,names,folder/(name+'.kdenlive'),ffprobe,experimental=True,cleanup=policy)
    for name,value in (('planning-result',result),('cleanup-request',request),('cleanup-result',cleanup)):
        (folder/(name+'.json')).write_text(dumps(value),encoding='utf-8',newline='\n')
    manifest = {'schema_version':1,'scope':'S08 generated tones/noise; construction labels, no recorded people',
        'project_origin':'Hand-relinked S01 native starter and production exports, not new Kdenlive saves',
        'gui_evidence':'NOT_RUN','source_frames':300,'output_frames':result.plan.time_map.output_frames,
        'noise_labels_seconds':{k:[[str(a),str(b)] for a,b in v] for k,v in labels.items()},
        'vocal_surrogate_labels_seconds':{'p0':[[1,3],[7,9]],'p1':[[2,4],[8,10]]},
        'independent_global_gap_seconds':[4,7],'exports':reports,
        'files':[{'path':p.relative_to(folder).as_posix(),'sha256':fingerprint(p)}
                 for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='construction.json']}
    (folder/'construction.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    return {'gain_spans':len(cleanup.spans),'export':reports['cleaned']}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--ffprobe',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(generate(args.output,args.ffprobe),indent=2))
