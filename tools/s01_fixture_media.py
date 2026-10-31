#!/usr/bin/env python3
"""Generate synthetic capture media, never a .kdenlive project or GUI evidence."""
import argparse
from array import array
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import wave

SAMPLE_RATE = 48000


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def media_settings(participants, frames, fps):
    rate = Fraction(fps)
    if not 1 <= participants <= 32:
        raise ValueError('Participant count must be between 1 and 32.')
    if rate not in (Fraction(25), Fraction(30000, 1001)):
        raise ValueError('Capture media supports 25/1 or 30000/1001 FPS.')
    duration = Fraction(frames, 1) / rate
    samples = duration * SAMPLE_RATE
    if frames < 1 or duration > 120 or samples.denominator != 1:
        raise ValueError('Use positive frames, <=120 seconds and whole audio samples.')
    return rate, duration, int(samples)


def write_tone(path, samples, frequency, windows):
    """Mono PCM with silent handles and short ramps; no recorded voices."""
    data = array('h', [0]) * samples
    ramp = SAMPLE_RATE // 200
    for start, end in windows:
        for sample in range(start, end):
            envelope = min(1, (sample - start) / ramp, (end - 1 - sample) / ramp)
            data[sample] = round(8000 * envelope * math.sin(2 * math.pi * frequency * sample / SAMPLE_RATE))
    if sys.byteorder != 'little':
        data.byteswap()
    with wave.open(str(path), 'wb') as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(data.tobytes())


def generate(output, ffmpeg, participants=2, frames=300, fps='25/1'):
    rate, duration, samples = media_settings(participants, frames, fps)
    version = subprocess.run([str(ffmpeg), '-version'], capture_output=True, text=True, check=True, timeout=15)
    version_line = version.stdout.splitlines()[0]
    if not version_line.startswith('ffmpeg version '):
        raise ValueError('Executable did not identify itself as FFmpeg.')
    output = Path(output)
    # Refuse even an empty existing directory: a failed attempt remains inspectable.
    output.mkdir(parents=True, exist_ok=False)
    records = []
    reference = output / 'embedded-reference.wav'
    write_tone(reference, samples, 997, [(0, samples)])
    records.append({'path': reference.name, 'role': 'embedded_audio_reference', 'tone_hz': 997})
    for index in range(participants):
        path = output / f'participant-{index + 1:02d}.wav'
        start = samples * (index + 1) // (3 * (participants + 1))
        width = samples // 8
        windows = [(start, start + width), (start + samples // 2, start + samples // 2 + width)]
        frequency = 330 + index * 110
        write_tone(path, samples, frequency, windows)
        records.append({'path': path.name, 'role': 'synthetic_participant', 'tone_hz': frequency,
                        'active_sample_intervals': windows})
    video = output / 'zoom-source.mp4'
    arguments = ['-hide_banner', '-loglevel', 'error', '-nostdin', '-n', '-f', 'lavfi', '-i',
                 f'testsrc2=size=320x180:rate={rate.numerator}/{rate.denominator}',
                 '-i', reference.name, '-map', '0:v:0', '-map', '1:a:0',
                 '-frames:v', str(frames), '-c:v', 'libx264', '-preset', 'veryfast',
                 '-crf', '28', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k',
                 '-movflags', '+faststart', video.name]
    try:
        subprocess.run([str(Path(ffmpeg).resolve()), *arguments], cwd=output,
                       capture_output=True, check=True, timeout=180)
    except (subprocess.SubprocessError, OSError) as exc:
        # Decoder diagnostics may contain local paths; keep failures local.
        (output / 'generation-failed.txt').write_bytes(
            b'FFmpeg generation failed; partial files are retained. No complete manifest exists.\n')
        raise RuntimeError('FFmpeg generation failed; inspect the local output directory.') from exc
    records.append({'path': video.name, 'role': 'zoom_like_video_with_contamination_tone'})
    for record in records:
        record['sha256'] = sha256(output / record['path'])
        record['bytes'] = (output / record['path']).stat().st_size
    manifest = {'schema_version': 1, 'provenance': 'generated_synthetic_media_no_recorded_people',
                'kdenlive_project_created': False, 'kdenlive_gui_evidence': 'NOT RUN',
                'participants': participants, 'fps': [rate.numerator, rate.denominator],
                'video_frames': frames, 'duration_seconds': [duration.numerator, duration.denominator],
                'audio_sample_rate': SAMPLE_RATE, 'audio_samples': samples,
                'audio_channels': 1, 'audio_sample_width_bytes': 2,
                'ffmpeg_version': version_line, 'ffmpeg_arguments': arguments, 'files': records}
    (output / 'synthetic-media.json').write_bytes((json.dumps(manifest, indent=2) + '\n').encode('utf-8'))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path, help='New local directory (must not exist).')
    parser.add_argument('--ffmpeg', required=True, type=Path, help='Existing local ffmpeg executable.')
    parser.add_argument('--participants', type=int, default=2)
    parser.add_argument('--frames', type=int, default=300)
    parser.add_argument('--fps', default='25/1', choices=['25/1', '30000/1001'])
    args = parser.parse_args()
    try:
        result = generate(args.output, args.ffmpeg, args.participants, args.frames, args.fps)
    except (ValueError, OSError, subprocess.SubprocessError, RuntimeError):
        parser.exit(1, 'Generation failed; inputs were not overwritten. Inspect local inputs/output.\n')
    print(json.dumps({'generated': True, 'participants': result['participants'],
                      'video_frames': result['video_frames'], 'kdenlive_gui_evidence': 'NOT RUN'}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
