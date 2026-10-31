#!/usr/bin/env python3
"""Measure the actual S07 synthetic GUI render, never manufacture GUI evidence."""
import argparse
import json
from pathlib import Path

from s01_fixture_media import sha256
from s02_validate_render import FRAME_BYTES, amplitude, db_ratio, decode, semantic


def validate(bundle, native, extracted, render, ffmpeg):
    bundle = Path(bundle)
    expected, actual = semantic(bundle/'after.kdenlive'), semantic(native)
    ripple = semantic(extracted)
    video = decode(ffmpeg, render)
    original = decode(ffmpeg, bundle/'media/zoom-source.mp4')
    pictures = []
    for out in (0,49,50,74,75,104,105,106,132,133,157,158,232):
        src = out if out < 105 else out + 67
        frame = video[out*FRAME_BYTES:(out+1)*FRAME_BYTES]
        errors = {lag: sum(abs(a-b) for a,b in zip(frame,original[(src+lag)*FRAME_BYTES:(src+lag+1)*FRAME_BYTES]))/FRAME_BYTES
                  for lag in (-1,0,1) if 0 <= src+lag < 300}
        pictures.append({'output_frame':out,'source_frame':src,'best_offset':min(errors,key=errors.get),'rgb_mae':round(errors[0],6)})
    audio = decode(ffmpeg, render, True)
    participants = [decode(ffmpeg,bundle/f'media/participant-{i:02}.wav',True) for i in (1,2)]
    anchors = []
    for at in (0.85,1.85,2.85,4.25,5.15,6.15,7.15):
        pos, width = round(at*48000), 19200
        src = pos if pos < 105*1920 else pos + 67*1920
        errors = {}
        for lag in range(-3840,3841,48):
            pairs=zip(audio[pos+lag:pos+lag+width],participants[0][src:src+width],participants[1][src:src+width])
            errors[lag]=sum((v-(a+b))**2 for v,a,b in pairs)/width
        anchors.append({'output_seconds':at,'source_seconds':src/48000,'best_lag_samples_grid_48':min(errors,key=errors.get),'mse_at_zero_lag':round(errors[0],9)})
    reference=decode(ffmpeg,bundle/'media/zoom-source.mp4',True)
    marker=db_ratio(amplitude(audio,997,0.2,0.5),amplitude(reference,997,0.2,0.5))
    overlap=[{'output_seconds':at,'p0_330hz':amplitude(audio,330,at,0.3),'p1_440hz':amplitude(audio,440,at,0.3)} for at in (2.2,5.52)]
    shifted=[dict(e,position=e['position']-(25 if i>1 else 0)) for i,e in enumerate(expected['tracks'][0]['entries']) if i!=1]
    # Names differ across tracks but source ranges/positions must be identical.
    shared_ripple=all([(e['position'],e['source']) for e in t['entries']]==[(e['position'],e['source']) for e in shifted] for t in ripple['tracks'])
    delta=actual['sequence_extent_frames']-expected['sequence_extent_frames']
    checks={'timeline_semantics_equal':all(expected[k]==actual[k] for k in expected if k!='sequence_extent_frames'),
        'native_extent_delta_reported':delta in (0,1),
        'ripple_extracted_25_frames_from_every_track':shared_ripple,
        'ripple_retains_five_groups':len(ripple['groups'])==5,
        'exact_233_video_frames':len(video)==233*FRAME_BYTES,
        'picture_anchors_exact_shared_map':all(p['best_offset']==0 and p['rgb_mae']<4 for p in pictures),
        'audio_anchors_within_one_frame':all(abs(a['best_lag_samples_grid_48'])<=1920 and a['mse_at_zero_lag']<0.001 for a in anchors),
        'both_sources_present_in_both_overlaps':all(min(o['p0_330hz'],o['p1_440hz'])>0.05 for o in overlap),
        'embedded_997hz_at_least_50db_down':marker < -50,
        'audio_padding_at_most_one_frame':233*1920<=len(audio)<=234*1920}
    return {'schema_version':1,'passed':all(checks.values()),'checks':checks,
        'project_sha256':sha256(bundle/'after.kdenlive'),'native_sha256':sha256(native),
        'extracted_sha256':sha256(extracted),'gui_render_sha256':sha256(render),
        'video_frames':len(video)//FRAME_BYTES,'audio_samples_48000hz':len(audio),
        'whole_project_semantic_equal':expected==actual,'native_sequence_extent_delta_frames':delta,
        'picture_anchors':pictures,'audio_anchors':anchors,'overlap_amplitudes':overlap,
        'embedded_997hz_attenuation_db':round(marker,3),
        'scope':'Synthetic S07 actual GUI render and native saves; not private alignment, human accuracy or held-out acceptance'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('bundle','native','extracted','render','ffmpeg','report'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    result=validate(args.bundle,args.native,args.extracted,args.render,args.ffmpeg)
    with args.report.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'checks':result['checks'],'frames':result['video_frames'],'marker_db':result['embedded_997hz_attenuation_db']},indent=2))
    raise SystemExit(0 if result['passed'] else 1)
