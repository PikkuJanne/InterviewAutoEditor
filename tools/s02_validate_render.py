#!/usr/bin/env python3
"""Measure the S02 synthetic GUI render; does not create GUI evidence."""
import argparse
from array import array
from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from s01_fixture_media import sha256
from s02_kdenlive_adapter import frames, props

FRAME_BYTES = 320 * 180 * 3


def semantic(project):
    """Compare timing, routing, clip gain, groups and guide; exclude UI/native IDs."""
    root = ET.parse(project).getroot()
    nodes = {n.get('id'): n for n in root if n.get('id')}
    seq = next(n for n in root.findall('tractor') if 'kdenlive:sequenceproperties.groups' in props(n))
    tracks = []
    for ref in seq.findall('track')[1:]:
        t = nodes[ref.get('producer')]
        entries = []
        for track_ref in t.findall('track'):
            position = 0
            for e in nodes[track_ref.get('producer')]:
                if e.tag == 'blank':
                    position += frames(e.get('length'), Fraction(25))
                elif e.tag == 'entry':
                    start, end = frames(e.get('in'), Fraction(25)), frames(e.get('out'), Fraction(25)) + 1
                    p = props(nodes[e.get('producer')])
                    gain = []
                    for f in e.findall('filter'):
                        fp = props(f)
                        keys = []
                        for item in fp['level'].split(';'):
                            time, db = item.split('=')
                            keys.append([frames(time, Fraction(25)), float(db)])
                        gain.append({'service': fp['mlt_service'], 'native_id': fp.get('kdenlive_id'), 'keys': keys})
                    entries.append({'position': position, 'source': [start, end], 'media': Path(p['resource']).name,
                                    'disable_audio': p.get('set.test_audio'), 'audio_index': p.get('audio_index'),
                                    'gain': gain})
                    position += end - start
        tracks.append({'name': props(t).get('kdenlive:track_name', ''), 'entries': sorted(entries, key=lambda e: e['position'])})
    sp = props(seq)
    groups = sorted(sorted(c['data'] for c in g['children']) for g in json.loads(sp['kdenlive:sequenceproperties.groups']))
    return {'profile': root.find('profile').attrib, 'tracks': tracks, 'groups': groups,
            'guides': json.loads(sp['kdenlive:sequenceproperties.guides']),
            'sequence_extent_frames': frames(seq.get('out'), Fraction(25)) + 1}


def decode(ffmpeg, path, audio=False):
    args = [str(ffmpeg), '-v', 'error', '-nostdin', '-i', str(path)]
    args += ['-vn', '-ac', '1', '-ar', '48000', '-t', '12.1', '-f', 'f32le', 'pipe:1'] if audio else ['-an', '-vf', 'scale=320:180', '-frames:v', '301', '-pix_fmt', 'rgb24', '-f', 'rawvideo', 'pipe:1']
    result = subprocess.run(args, capture_output=True, check=True, timeout=45).stdout
    return array('f', result) if audio else result


def amplitude(samples, hz, at, duration=.08):
    part = samples[round(at * 48000):round((at + duration) * 48000)]
    if len(part) != round(duration * 48000):
        raise ValueError('Missing audio probe samples.')
    angle = 2 * math.pi * hz / 48000
    return 2 * abs(sum(v * complex(math.cos(angle*i), math.sin(angle*i)) for i, v in enumerate(part))) / len(part)


def db_ratio(a, b):
    return 20 * math.log10(max(a, 1e-12) / max(b, 1e-12))


def validate(project, roundtrip, render, media, ffmpeg):
    expected, actual = semantic(project), semantic(roundtrip)
    sem_equal = expected == actual
    extent_delta = actual['sequence_extent_frames'] - expected['sequence_extent_frames']
    timeline_equal = all(expected[k] == actual[k] for k in expected if k != 'sequence_extent_frames')
    video, source = decode(ffmpeg, render), decode(ffmpeg, Path(media) / 'zoom-source.mp4')
    anchors = []
    if len(video) == 275 * FRAME_BYTES and len(source) == 300 * FRAME_BYTES:
        for output in (0, 34, 99, 100, 101, 149, 249, 274):
            src = output if output < 100 else output + 25
            frame = video[output * FRAME_BYTES:(output+1) * FRAME_BYTES]
            errors = {offset: sum(abs(a-b) for a,b in zip(frame, source[(src+offset)*FRAME_BYTES:(src+offset+1)*FRAME_BYTES]))/FRAME_BYTES
                      for offset in (-1, 0, 1) if 0 <= src+offset < 300}
            anchors.append({'output_frame': output, 'source_frame': src, 'rgb_mae': round(errors[0], 6), 'best_offset': min(errors, key=errors.get)})
    audio = decode(ffmpeg, render, True)
    original_mix = decode(ffmpeg, Path(media) / 'zoom-source.mp4', True)
    contamination = db_ratio(amplitude(audio, 997, 3.2, .5), amplitude(original_mix, 997, 3.2, .5))
    # Use the same tone's active pre-gate/post-gate samples; P02 starts later.
    levels = {str(at): amplitude(audio, 330, at) for at in (1.34, 1.5, 1.7, 1.9, 2.1, 2.3, 2.5, 2.68)}
    baseline = levels['2.68']
    gains = {at: round(db_ratio(v, baseline), 3) for at, v in levels.items()}
    # Audio anchors after the removed second must move by the same 48000 samples.
    after_p01 = amplitude(audio, 330, 6.5, .2)
    after_p02 = amplitude(audio, 440, 7.9, .2)
    participants = [decode(ffmpeg, Path(media) / f'participant-{i:02d}.wav', True) for i in (1, 2)]
    audio_anchors = []
    # Include synthetic onsets, not only periodic tone plateaus, to disambiguate lag.
    for output_start in (2.6, 6.2, 7.55, 9.05):
        at, width = round(output_start * 48000), 19200
        source_at = at if at < 192000 else at + 48000
        errors = {}
        for lag in range(-3840, 3841, 48):
            pairs = zip(audio[at+lag:at+lag+width], participants[0][source_at:source_at+width], participants[1][source_at:source_at+width])
            errors[lag] = sum((a - (b+c)) ** 2 for a,b,c in pairs) / width
        best = min(errors, key=errors.get)
        audio_anchors.append({'output_start_seconds': output_start, 'source_start_seconds': source_at/48000,
                              'best_lag_samples_grid_48': best, 'same_position_mse': round(errors[0], 8)})
    # Check sample discontinuities specifically around all native gain boundaries.
    edges = []
    for f in (35, 45, 55, 65):
        at = f * 1920
        window = audio[at-480:at+480]
        edges.append({'frame': f, 'max_adjacent_sample_delta': round(max(abs(a-b) for a,b in zip(window, window[1:])), 7)})
    checks = {'timeline_semantics_equal': timeline_equal,
              'native_sequence_extent_change_is_recorded_one_frame': extent_delta == 1,
              'exact_275_video_frames': len(video) == 275 * FRAME_BYTES,
              'picture_anchors_exact_mapping': len(anchors) == 8 and all(a['best_offset'] == 0 and a['rgb_mae'] < 4 for a in anchors),
              'mp4_marker_at_least_50db_down': contamination < -50,
              'native_gain_plateau_at_least_45db_down': max(gains['1.9'], gains['2.1']) < -45,
              'native_gain_ramps_measured': gains['1.5'] > gains['1.7'] > gains['1.9'] and gains['2.1'] < gains['2.3'] < gains['2.5'] < gains['2.68'],
              'no_large_gain_edge_discontinuity': all(e['max_adjacent_sample_delta'] < .04 for e in edges),
              'both_audio_anchors_after_cut_present': min(after_p01, after_p02) > .05,
              'audio_anchors_within_one_frame': all(abs(a['best_lag_samples_grid_48']) <= 1920 and a['same_position_mse'] < .001 for a in audio_anchors),
              'audio_padding_at_most_one_frame': 528000 <= len(audio) <= 529920}
    return {'schema_version': 1, 'passed': all(checks.values()), 'checks': checks,
            'project_sha256': sha256(project), 'native_roundtrip_sha256': sha256(roundtrip), 'gui_render_sha256': sha256(render),
            'video_frames': len(video)//FRAME_BYTES, 'decoded_audio_samples_48000hz': len(audio),
            'whole_project_semantic_equal': sem_equal, 'native_sequence_extent_delta_frames': extent_delta,
            'picture_anchors': anchors, 'embedded_997hz_attenuation_db': round(contamination,3),
            'audio_anchors': audio_anchors,
            'native_gain_relative_db': gains, 'gain_edges': edges,
            'after_cut_amplitudes': {'p01_330hz': after_p01, 'p02_440hz': after_p02},
            'scope': 'Synthetic S02 entry-gain and manual shared cut only; no subjective listening, real alignment or subframe gain claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('project', 'roundtrip', 'render', 'media', 'ffmpeg', 'report'):
        parser.add_argument('--' + arg, type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.project, args.roundtrip, args.render, args.media, args.ffmpeg)
    with args.report.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
