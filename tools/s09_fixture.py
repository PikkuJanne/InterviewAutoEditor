#!/usr/bin/env python3
"""Construct a labelled S09 picture/noise fixture; never GUI evidence."""
from dataclasses import replace
from fractions import Fraction as F
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.adapters.export import export_project
from interview_auto_editor.cleanup import CleanupResult, build_cleanup, planning_digest
from interview_auto_editor.contracts import dumps, loads
from interview_auto_editor.picture import PictureRequest, analyze_picture, refine_picture_seams
from interview_auto_editor.planner import PlanningResult, analysis_digest, plan_pauses
from interview_auto_editor.probe import fingerprint, run_bounded
from s08_fixture import generate as generate_base


def generate(output,ffmpeg,ffprobe):
    generate_base(output,ffprobe)
    folder=Path(output).resolve()
    # Only replace our just-generated construction files in this exclusive new
    # directory. S08/real originals and all existing packages stay untouched.
    for name in ('baseline.kdenlive','cleaned.kdenlive','restored.kdenlive'):
        (folder/name).unlink()
    video=folder/'media/zoom-source.mp4'
    video.unlink()
    run_bounded([ffmpeg,'-v','error','-nostdin','-n','-f','lavfi','-i',
        "nullsrc=s=320x180:r=25:d=12,geq=lum='if(lt(N,138),40,190)+mod(N,5)':cb=128:cr=128",
        '-i',ROOT_MEDIA(),'-map','0:v:0','-map','1:a:0','-frames:v','300',
        '-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac',video])
    old=loads(PlanningResult,(folder/'planning-result.json').read_text())
    a=replace(old.plan.analysis,sources=tuple(replace(s,sha256=fingerprint(video)) if s.kind=='video' else s for s in old.plan.analysis.sources))
    base=plan_pauses(a,replace(old.request,analysis_sha256=analysis_digest(a)))
    req=PictureRequest(1,analysis_digest(a),'speaker_view','construction_label',
                       'Independent generated full-picture luma switch at frame 138 inside all-track silence [4,7)')
    picture=analyze_picture(a,req,video,ffmpeg,ffprobe)
    refinement=refine_picture_seams(base,picture)
    old_cleanup=loads(CleanupResult,(folder/'cleanup-result.json').read_text())
    base_cleanup=build_cleanup(base,replace(old_cleanup.request,planning_sha256=planning_digest(base)))
    cleanup=build_cleanup(refinement.result,replace(base_cleanup.request,planning_sha256=planning_digest(refinement.result)))
    bindings={'video':video,**{f'p{i}':folder/f'media/participant-{i+1:02}.wav' for i in range(2)}}
    report=export_project(base,folder/'before.kdenlive',bindings,{'p0':'Participant 01','p1':'Participant 02'},
                         folder/'picture-cleaned.kdenlive',ffprobe,experimental=True,picture=picture,cleanup=cleanup)
    for name,value in (('analysis',a),('planning-result',base),('picture-request',req),('picture-analysis',picture),
                       ('picture-refinement',refinement),('refined-planning-result',refinement.result),
                       ('base-cleanup',base_cleanup),('cleanup-request',cleanup.request),('cleanup-result',cleanup)):
        (folder/(name+'.json')).write_text(dumps(value),encoding='utf-8',newline='\n')
    manifest={'schema_version':1,'scope':'Synthetic tones/noise/luma pictures; no recorded people',
        'project_origin':'Hand-relinked S01 starter and production export, NOT newly Kdenlive-authored',
        'gui_evidence':'NOT_RUN_at_construction','independent_switch_source_frame':138,
        'independent_all_track_silence_seconds':[4,7],'source_frames':300,'baseline_removed_frames':[105,172],
        'refined_removed_frames':[105,138],'output_frames':267,'export':report,
        'files':[{'path':p.relative_to(folder).as_posix(),'sha256':fingerprint(p)} for p in sorted(folder.rglob('*'))
                 if p.is_file() and p.name!='construction.json']}
    (folder/'construction.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    return report


def ROOT_MEDIA():
    return Path(__file__).resolve().parents[1]/'tests/fixtures/kdenlive-26.08.2/media-2/zoom-source.mp4'


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('output','ffmpeg','ffprobe'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();print(json.dumps(generate(args.output,args.ffmpeg,args.ffprobe),indent=2))
