#!/usr/bin/env python3
"""Build LOCAL synthetic speech cases from three explicitly generated TTS WAVs.

The cue labels come from construction, not VAD predictions. No real interview
audio or transcripts are read. TTS assets remain local; only evidence is public.
"""
import argparse
import json
from pathlib import Path
import wave


def build(folder):
    import numpy as np
    parts, labels = [], []
    cursor = 0
    rate = None
    for name, filename, gain in [('normal', 'synthetic-speech.wav', 1),
                                  ('soft', 'synthetic-speech.wav', 0.03),
                                  ('very_soft', 'synthetic-speech.wav', 0.003),
                                  ('short_yes', 'synthetic-yes.wav', 1),
                                  ('short_mm_hmm', 'synthetic-mm.wav', 1)]:
        with wave.open(str(folder / filename), 'rb') as wav:
            assert wav.getsampwidth() == 2 and wav.getnchannels() == 1
            sr = wav.getframerate()
            assert rate is None or rate == sr
            rate = sr
            audio = np.frombuffer(wav.readframes(wav.getnframes()), dtype='<i2').astype('float64') / 32768
        active = np.flatnonzero(audio != 0)
        audio = audio[active[0]:active[-1]+1] * gain
        # Deliberately non-window-aligned cue onsets and a short acknowledgement.
        gap = np.zeros(rate + 137)
        parts.append(gap)
        cursor += len(gap)
        if name == 'short_yes':
            assert len(audio) / rate < 0.6
        # Split construction labels at digital silence >100 ms, e.g. sentence
        # punctuation. A whole utterance span includes known non-speech gaps.
        sounding = np.flatnonzero(np.round(audio * 32767) != 0)
        breaks = np.flatnonzero(np.diff(sounding) > rate // 10)
        starts = [sounding[0], *(sounding[breaks+1])]
        ends = [*(sounding[breaks]+1), sounding[-1]+1]
        regions = [[int(cursor+a), int(cursor+b)] for a, b in zip(starts, ends)]
        labels.append({'id': name, 'start_sample': cursor, 'end_sample': cursor + len(audio),
                       'speech_regions': regions,
                       'gain': str(gain), 'provenance': 'known-generated-utterance-not-model-derived'})
        parts.append(audio)
        cursor += len(audio)
    parts.append(np.zeros(rate // 2 + 19))
    # Right channel is the polarity inverse: averaging would cancel all speech.
    mono = np.concatenate(parts)
    stereo = np.stack((mono, -mono), axis=1)
    output = folder / 'development-stereo.wav'
    with wave.open(str(output), 'wb') as wav:
        wav.setparams((2, 2, rate, len(mono), 'NONE', 'not compressed'))
        wav.writeframes(np.round(np.clip(stereo, -1, 1) * 32767).astype('<i2').tobytes())
    manifest = {'schema_version': 1, 'fixture': output.name, 'sample_rate': rate,
                'sample_count': len(mono), 'channels': 2,
                'provenance': 'Microsoft David Desktop local System.Speech synthetic development; not Kdenlive output; not human acceptance',
                'labels': labels}
    (folder / 'development-labels.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, required=True)
    args = parser.parse_args()
    manifest = build(args.folder)
    print(json.dumps({'synthetic_development_cases': len(manifest['labels']),
                      'sample_rate': manifest['sample_rate'], 'channels': manifest['channels']}))
