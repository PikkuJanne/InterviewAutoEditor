#!/usr/bin/env python3
"""Measure the S01 25 FPS synthetic round trip; this does not perform GUI tests."""
import argparse
from array import array
from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

from s01_fixture_media import sha256
from s01_project_census import census

FRAME_BYTES = 320 * 180 * 3


def props(node):
    return {p.get('name'): p.text or '' for p in node.findall('property')}


def frame_number(timecode):
    hours, minutes, seconds = map(Fraction, timecode.split(':'))
    result = (hours * 3600 + minutes * 60 + seconds) * 25
    if result.denominator != 1:
        raise ValueError('Capture boundary is not representable at 25 FPS.')
    return int(result)


def semantic_capture(project):
    """Only the observed S01 fixture shape; deliberately not a general importer."""
    census(project)
    root = ET.parse(project).getroot()
    chains = {c.get('id'): props(c) for c in root.findall('chain')}
    playlists = {p.get('id'): p for p in root.findall('playlist')}
    tracks, groups, guides = [], None, None
    for tractor in root.findall('tractor'):
        properties = props(tractor)
        if 'kdenlive:sequenceproperties.groups' in properties:
            groups = json.loads(properties['kdenlive:sequenceproperties.groups'])
            guides = json.loads(properties.get('kdenlive:sequenceproperties.guides', '[]'))
        children = tractor.findall('track')
        if len(children) != 2 or any(t.get('producer') not in playlists for t in children):
            continue
        entries = []
        for child in children:
            playlist = playlists[child.get('producer')]
            position = 0
            for item in playlist:
                if item.tag == 'blank':
                    position += frame_number(item.get('length'))
                elif item.tag == 'entry':
                    start, end = frame_number(item.get('in')), frame_number(item.get('out')) + 1
                    chain = chains[item.get('producer')]
                    resource = chain['resource'].replace('\\', '/').rsplit('/', 1)[-1]
                    entries.append((position, start, end, resource, chain.get('set.test_audio'), chain.get('set.test_image')))
                    position += end - start
        gain = [props(f).get('level') for f in tractor.findall('filter')
                if props(f).get('mlt_service') == 'volume' and 'level' in props(f)]
        tracks.append({'name': properties.get('kdenlive:track_name', ''), 'entries': entries, 'gain': gain})
    profile = root.find('profile')
    return {'profile': {k: profile.get(k) for k in ('width', 'height', 'frame_rate_num', 'frame_rate_den',
                                                  'sample_aspect_num', 'sample_aspect_den', 'colorspace', 'progressive')},
            'tracks': tracks,
            'groups': sorted(sorted(c['data'] for c in group['children']) for group in groups),
            'guides': guides}


def tone_amplitude(samples, frequency, start_seconds, seconds=1, rate=48000):
    selected = samples[round(start_seconds * rate):round((start_seconds + seconds) * rate)]
    if len(selected) != round(seconds * rate):
        raise ValueError('Audio does not cover the required probe window.')
    angle = 2 * math.pi * frequency / rate
    real = sum(value * math.cos(angle * i) for i, value in enumerate(selected))
    imaginary = sum(value * math.sin(angle * i) for i, value in enumerate(selected))
    return 2 * math.hypot(real, imaginary) / len(selected)


def decode(ffmpeg, path, audio=False):
    arguments = ['-hide_banner', '-loglevel', 'error', '-nostdin', '-i', str(path)]
    if audio:
        arguments += ['-vn', '-t', '12.1', '-ac', '1', '-ar', '48000', '-f', 's16le', 'pipe:1']
    else:
        arguments += ['-an', '-vf', 'scale=320:180', '-frames:v', '301', '-pix_fmt', 'rgb24', '-f', 'rawvideo', 'pipe:1']
    result = subprocess.run([str(ffmpeg), *arguments], capture_output=True, check=True, timeout=45)
    if not audio:
        return result.stdout
    samples = array('h', result.stdout)
    if sys.byteorder != 'little':
        samples.byteswap()
    return samples


def validate(package, roundtrip, render, ffmpeg, ffprobe):
    package = Path(package)
    if not Path(render).is_file():
        raise ValueError('Render must be an existing local file.')
    reference = package / 'grouped-gain.kdenlive'
    original = package / 'media-2/zoom-source.mp4'
    manifest = json.loads((package / 'media-2/synthetic-media.json').read_text(encoding='utf-8'))
    if (manifest['video_frames'], manifest['fps'], manifest['participants']) != (300, [25, 1], 2):
        raise ValueError('This measurement is limited to the S01 300-frame capture.')
    for item in manifest['files']:
        if Path(item['path']).name != item['path'] or sha256(package / 'media-2' / item['path']) != item['sha256']:
            raise ValueError('Synthetic source package changed.')
    probe = subprocess.run([str(ffprobe), '-v', 'error', '-show_entries',
                            'stream=codec_name,codec_type,width,height,r_frame_rate,sample_rate,channels,nb_frames,duration',
                            '-show_entries', 'format=duration', '-of', 'json', str(render)],
                           capture_output=True, text=True, check=True, timeout=20)
    metadata = json.loads(probe.stdout)
    video = decode(ffmpeg, render)
    source = decode(ffmpeg, original)
    exact_frames = len(video) == len(source) == 300 * FRAME_BYTES
    anchors = []
    if exact_frames:
        for index in (0, 99, 100, 199, 200, 299):
            actual = video[index * FRAME_BYTES:(index + 1) * FRAME_BYTES]
            errors = {}
            for candidate in range(max(0, index - 1), min(300, index + 2)):
                expected = source[candidate * FRAME_BYTES:(candidate + 1) * FRAME_BYTES]
                errors[candidate - index] = sum(abs(a - b) for a, b in zip(actual, expected)) / FRAME_BYTES
            anchors.append({'frame': index, 'same_frame_rgb_mae': round(errors[0], 6),
                            'best_offset_frames': min(errors, key=errors.get)})
    audio = decode(ffmpeg, render, audio=True)
    embedded = decode(ffmpeg, original, audio=True)
    marker_source = tone_amplitude(embedded, 997, 1.5)
    marker_render = tone_amplitude(audio, 997, 1.5)
    attenuation = 20 * math.log10(max(marker_render, 1e-12) / max(marker_source, 1e-12))
    participant_01 = tone_amplitude(audio, 330, 1.5)
    participant_02 = tone_amplitude(audio, 440, 3)
    semantics_equal = semantic_capture(reference) == semantic_capture(roundtrip)
    checks = {'semantic_round_trip_equal': semantics_equal, 'exact_300_video_frames': exact_frames,
              'picture_anchor_mae_below_4': bool(anchors) and all(a['same_frame_rgb_mae'] < 4 for a in anchors),
              'picture_anchor_best_matches_same_frame': bool(anchors) and all(a['best_offset_frames'] == 0 for a in anchors),
              'embedded_marker_at_least_50db_lower': attenuation < -50,
              'both_participant_tones_present': min(participant_01, participant_02) > 100,
              'decoded_audio_padding_within_one_frame': 576000 <= len(audio) <= 577920}
    return {'schema_version': 1, 'passed': all(checks.values()), 'checks': checks,
            'fixture': 'grouped-gain.kdenlive', 'reference_sha256': sha256(reference),
            'roundtrip_sha256': sha256(roundtrip), 'gui_render_sha256': sha256(render),
            'render_bytes': Path(render).stat().st_size, 'probe': metadata,
            'picture_anchors': anchors, 'decoded_audio_samples_48000hz': len(audio),
            'marker_997hz_attenuation_db': round(attenuation, 3),
            'render_tone_amplitudes_s16': {'participant_01_330hz': round(participant_01, 3),
                                          'participant_02_440hz': round(participant_02, 3),
                                          'embedded_997hz': round(marker_render, 6)},
            'scope': 'Synthetic reference only; GUI provenance recorded separately. No interview quality or native gain-edge claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, type=Path)
    parser.add_argument('--roundtrip', required=True, type=Path)
    parser.add_argument('--render', required=True, type=Path)
    parser.add_argument('--ffmpeg', required=True, type=Path)
    parser.add_argument('--ffprobe', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.package, args.roundtrip, args.render, args.ffmpeg, args.ffprobe)
        with args.report.open('x', encoding='utf-8', newline='\n') as output:
            output.write(json.dumps(result, indent=2) + '\n')
    except (OSError, ValueError, KeyError, TypeError, StopIteration, ET.ParseError, subprocess.SubprocessError):
        parser.exit(1, 'Capture validation failed to finish. Inspect inputs/output privately.\n')
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
