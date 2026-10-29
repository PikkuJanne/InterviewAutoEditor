#!/usr/bin/env python3
"""Measure existing actual S09 native saves/render; never manufacture GUI proof."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.probe import fingerprint
from s02_validate_render import FRAME_BYTES, amplitude, db_ratio, decode, semantic


def validate(bundle,ffmpeg):
    bundle=Path(bundle)
    expected=semantic(bundle/'picture-cleaned.kdenlive')
    native=semantic(bundle/'native-roundtrip.kdenlive')
    moved=semantic(bundle/'group-moved.kdenlive')
    undone=semantic(bundle/'native-undone.kdenlive')
    render=bundle/'gui-render.mp4'
    audio=decode(ffmpeg,render,True)
    raw=[decode(ffmpeg,bundle/f'media/participant-{i:02}.wav',True) for i in (1,2)]
    video=decode(ffmpeg,render)
    source=decode(ffmpeg,bundle/'media/zoom-source.mp4')
    picture_errors=[]
    for out in range(len(video)//FRAME_BYTES):
        src=out if out<105 else out+33
        frame=video[out*FRAME_BYTES:(out+1)*FRAME_BYTES]
        ref=source[src*FRAME_BYTES:(src+1)*FRAME_BYTES]
        picture_errors.append(sum(abs(a-b) for a,b in zip(frame,ref))/FRAME_BYTES)
    # Independent luma threshold labels: source changes at 138, output at 105.
    means=[sum(video[i:i+FRAME_BYTES])/FRAME_BYTES for i in range(0,len(video),FRAME_BYTES)]
    transitions=[i for i in range(1,len(means)) if (means[i]>=128)!=(means[i-1]>=128)]
    protected=[]
    for i,hz,times in ((0,330,(1.9,2.3,7.9,8.3)),(1,440,(2.3,3.5,8.3,9.5))):
        for src in times:
            out=src if src<4.2 else src-1.32
            protected.append({'source':i,'source_seconds':src,'output_seconds':out,
                'relative_db':round(db_ratio(amplitude(audio,hz,out,.12),amplitude(raw[i],hz,src,.12)),3)})
    anchors=[]
    # Onset windows include ramps to avoid claiming sync from periodic plateaus.
    for src in (1.99,2.99,7.99,8.99):
        out=src if src<4.2 else src-1.32
        pos,at,width=round(out*48000),round(src*48000),4800
        errors={lag:sum((v-a-b)**2 for v,a,b in zip(audio[pos+lag:pos+lag+width],
            raw[0][at:at+width],raw[1][at:at+width]))/width for lag in range(-1920,1921,48)}
        anchors.append({'source_seconds':src,'output_seconds':out,'best_lag_samples_grid48':min(errors,key=errors.get),
                        'mse_at_zero':errors[0]})
    noise=[]
    for i,hz,src in ((0,880,3.52),(0,880,9.6),(1,1100,1.3),(1,1100,7.4)):
        out=src if src<4.2 else src-1.32
        noise.append(round(db_ratio(amplitude(audio,hz,out,.12),amplitude(raw[i],hz,src,.12)),3))
    embedded=decode(ffmpeg,bundle/'media/zoom-source.mp4',True)
    marker=db_ratio(amplitude(audio,997,.2,.5),amplitude(embedded,997,.2,.5))
    checks={
        'native_profile_timing_routing_groups_guides_gain_equal':expected==native,
        'undo_restores_native_semantics':expected==undone,
        'group_move_all_tracks_25_frames_source_and_gain_unchanged':all(len(t['entries'])==len(u['entries']) and
            all(dict(e,position=e['position']+(25 if j==5 else 0))==f for j,(e,f) in enumerate(zip(t['entries'],u['entries'])))
            for t,u in zip(expected['tracks'],moved['tracks'])),
        'exact_267_video_frames':len(video)==267*FRAME_BYTES,
        'every_rendered_picture_matches_shared_source_frame':len(picture_errors)==267 and max(picture_errors)<4,
        'one_existing_switch_at_output105_no_short_accidental_flash':transitions==[105],
        'eight_protected_source_probes_within_half_db':len(protected)==8 and all(abs(p['relative_db'])<.5 for p in protected),
        'four_audio_onset_anchors_within_one_frame':all(abs(a['best_lag_samples_grid48'])<=1920 and a['mse_at_zero']<.001 for a in anchors),
        'four_s08_noise_probes_more_than_30db_down':len(noise)==4 and all(d<-30 for d in noise),
        'mix_peak_below_safety_ceiling':max(map(abs,audio))<.95,
        'mp4_marker_at_least_50db_down':marker<-50,
        'encoded_padding_at_most_one_frame':267*1920<=len(audio)<=268*1920}
    return {'schema_version':1,'passed':all(checks.values()),'checks':checks,
        'scope':'Actual GUI synthetic tone/noise/luma output; no real/held-out or subjective word acceptance',
        'video_frames':len(video)//FRAME_BYTES,'picture_frames_measured':len(picture_errors),
        'maximum_picture_rgb_mae':max(picture_errors),'observed_output_switch_frames':transitions,
        'protected_probes':protected,'audio_anchors':anchors,'noise_relative_db':noise,
        'decoded_audio_samples_48000hz':len(audio),'decoded_peak':max(map(abs,audio)),
        'embedded_marker_db':round(marker,3),'native_sequence_extent_delta_frames':native['sequence_extent_frames']-expected['sequence_extent_frames'],
        'files':[{'path':name,'sha256':fingerprint(bundle/name)} for name in
                 ('picture-cleaned.kdenlive','native-roundtrip.kdenlive','group-moved.kdenlive','native-undone.kdenlive','gui-render.mp4')]}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('bundle','ffmpeg','report'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();r=validate(args.bundle,args.ffmpeg)
    with args.report.open('x',encoding='utf-8',newline='\n') as stream:stream.write(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'passed':r['passed'],'checks':r['checks']},indent=2))
    raise SystemExit(0 if r['passed'] else 1)
