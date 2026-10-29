#!/usr/bin/env python3
"""Measure a genuine S08 GUI render and native saves; no evidence generation."""
from fractions import Fraction as F
import argparse
import json
import math
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.cleanup import CleanupResult
from interview_auto_editor.contracts import loads
from s01_fixture_media import sha256
from s02_validate_render import FRAME_BYTES, amplitude, db_ratio, decode, semantic


def validate(bundle, native, moved, render, ffmpeg):
    bundle=Path(bundle)
    expected,actual=semantic(bundle/'cleaned.kdenlive'),semantic(native)
    movement=semantic(moved)
    cleanup=loads(CleanupResult,(bundle/'cleanup-result.json').read_text())
    audio=decode(ffmpeg,render,True)
    original=[decode(ffmpeg,bundle/f'media/participant-{i:02}.wav',True) for i in (1,2)]
    video=decode(ffmpeg,render)
    source_video=decode(ffmpeg,bundle/'media/zoom-source.mp4')
    pictures=[]
    for output in (0,49,50,74,75,104,105,106,132,133,157,158,232):
        src=output if output<105 else output+67
        frame=video[output*FRAME_BYTES:(output+1)*FRAME_BYTES]
        errors={lag:sum(abs(a-b) for a,b in zip(frame,source_video[(src+lag)*FRAME_BYTES:(src+lag+1)*FRAME_BYTES]))/FRAME_BYTES
                for lag in (-1,0,1) if 0<=src+lag<300}
        pictures.append({'output_frame':output,'source_frame':src,'best_offset':min(errors,key=errors.get),'rgb_mae':round(errors[0],6)})
    # Independently fixed probes from noise construction labels, not policy keys.
    noise=[]
    for i,hz,src in ((0,880,3.52),(0,880,9.6),(1,1100,1.3),(1,1100,7.4)):
        output=src if src<4.2 else src-2.68
        noise.append({'source_seconds':src,'output_seconds':output,'hz':hz,
                      'attenuation_db':round(db_ratio(amplitude(audio,hz,output,.12),amplitude(original[i],hz,src,.12)),3)})
    protected=[]
    # Fundamental amplitudes distinguish both protected sources in both overlaps.
    for i,hz,times in ((0,330,(1.9,2.3,7.9,8.3)),(1,440,(2.3,3.5,8.3,9.5))):
        for src in times:
            output=src if src<4.2 else src-2.68
            protected.append({'source':i,'source_seconds':src,'relative_db':round(db_ratio(
                amplitude(audio,hz,output,.12),amplitude(original[i],hz,src,.12)),3)})
    # These windows contain no gated source noise, so sample anchors compare
    # directly to the unchanged original sum, including two genuine overlaps.
    anchors=[]
    for src in (2.0,2.6,7.9,8.4,10.3):
        output=src if src<4.2 else src-2.68
        pos,at,width=round(output*48000),round(src*48000),4800
        errors={lag:sum((v-a-b)**2 for v,a,b in zip(audio[pos+lag:pos+lag+width],original[0][at:at+width],original[1][at:at+width]))/width
                for lag in range(-1920,1921,48)}
        anchors.append({'source_seconds':src,'best_lag_samples_grid48':min(errors,key=errors.get),'mse_at_zero':errors[0]})
    edges=[]
    for span in cleanup.spans:
        for frame in (span.start_frame,span.down_frame,span.up_frame,span.end_frame):
            output=frame if frame<105 else frame-67
            at=output*1920
            window=audio[max(0,at-480):at+480]
            edges.append({'source_frame':frame,'max_adjacent_delta':round(max(abs(a-b) for a,b in zip(window,window[1:])),7)})
    embedded=decode(ffmpeg,bundle/'media/zoom-source.mp4',True)
    marker=db_ratio(amplitude(audio,997,.2,.5),amplitude(embedded,997,.2,.5))
    checks={'native_timing_groups_guides_and_gain_equal':expected==actual,
            'four_noise_probes_at_least_30db_down':len(noise)==4 and all(n['attenuation_db'] < -30 for n in noise),
            'eight_protected_source_probes_within_half_db':len(protected)==8 and all(abs(p['relative_db'])<.5 for p in protected),
            'five_audio_anchors_within_one_frame':all(abs(a['best_lag_samples_grid48'])<=1920 and a['mse_at_zero']<.001 for a in anchors),
            'sixteen_native_gain_edges_without_large_discontinuity':len(edges)==16 and all(e['max_adjacent_delta']<.04 for e in edges),
            'decoded_mix_peak_below_safety_ceiling':max(map(abs,audio))<.95,
            'exact_233_video_frames':len(video)==233*FRAME_BYTES,
            'thirteen_picture_anchors_exact_source_map':all(p['best_offset']==0 and p['rgb_mae']<4 for p in pictures),
            'mp4_marker_at_least_50db_down':marker < -50,
            'encoded_padding_bounded_one_frame':233*1920<=len(audio)<=234*1920,
            'all_three_group_members_move_25_frames_source_bounds_and_gains_unchanged':all(
                len(t['entries'])==len(u['entries']) and all(dict(e,position=e['position']+(25 if j==5 else 0))==f
                for j,(e,f) in enumerate(zip(t['entries'],u['entries']))) for t,u in zip(expected['tracks'],movement['tracks']))}
    return {'schema_version':1,'passed':all(checks.values()),'checks':checks,
            'scope':'Generated tone/noise GUI render; measured boundaries, not subjective speech listening or held-out acceptance',
            'project_sha256':sha256(bundle/'cleaned.kdenlive'),'native_sha256':sha256(native),'moved_sha256':sha256(moved),
            'render_sha256':sha256(render),'video_frames':len(video)//FRAME_BYTES,'decoded_audio_samples':len(audio),
            'decoded_sample_peak':max(map(abs,audio)),'noise_probes':noise,'protected_probes':protected,
            'audio_anchors':anchors,'gain_edges':edges,'picture_anchors':pictures,
            'mp4_marker_db':round(marker,3),'native_extent_delta_frames':actual['sequence_extent_frames']-expected['sequence_extent_frames']}


def validate_restoration(bundle, ffmpeg):
    """Actual native bypass and actual second GUI render, not a PCM simulation."""
    import xml.etree.ElementTree as ET
    bundle=Path(bundle)
    project=bundle/'native-interval-restored.kdenlive'
    root=ET.parse(project).getroot()
    disabled=[f for f in root.iter('filter') if f.find("property[@name='kdenlive_id']") is not None
              and f.find("property[@name='disable']") is not None
              and f.find("property[@name='disable']").text=='1']
    y=decode(ffmpeg,bundle/'gui-restored.mp4',True)
    raw=decode(ffmpeg,bundle/'media/participant-01.wav',True)
    relative=db_ratio(amplitude(y,880,6.92,.12),amplitude(raw,880,9.6,.12))
    untouched=db_ratio(amplitude(y,880,3.52,.12),amplitude(raw,880,3.52,.12))
    checks={'exactly_one_native_clip_effect_bypassed':len(disabled)==1,
            'timing_groups_and_gain_keys_unchanged':semantic(project)==semantic(bundle/'cleaned.kdenlive'),
            'restored_plateau_within_half_db_of_original':abs(relative)<.5,
            'other_cleanup_interval_still_suppressed':untouched < -30,
            'restored_mix_peak_below_ceiling':max(map(abs,y))<.95}
    return {'schema_version':1,'passed':all(checks.values()),'checks':checks,
            'restored_source_seconds':9.6,'output_seconds':6.92,'restored_relative_db':round(relative,3),
            'other_interval_relative_db':round(untouched,3),'decoded_peak':max(map(abs,y)),
            'native_sha256':sha256(project),'render_sha256':sha256(bundle/'gui-restored.mp4')}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('bundle','native','moved','render','ffmpeg','report'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();report=validate(args.bundle,args.native,args.moved,args.render,args.ffmpeg)
    with args.report.open('x',encoding='utf-8') as out:out.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'checks':report['checks']},indent=2))
    raise SystemExit(0 if report['passed'] else 1)
