#!/usr/bin/env python3
"""Measure the synthetic EOF GUI artifact; never manufacture native evidence."""
import argparse
import json
from pathlib import Path
import sys
import wave

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.probe import fingerprint, run_bounded
from s02_validate_render import semantic


def validate(folder, ffmpeg):
    folder = Path(folder)
    render = folder/'gui-render-192k.mkv'
    def decode(path, audio=False):
        args = [str(ffmpeg), '-v', 'error', '-nostdin', '-i', str(path)]
        args += ['-vn', '-f', 's16le', '-acodec', 'pcm_s16le', 'pipe:1'] if audio else ['-an', '-pix_fmt', 'rgb24', '-f', 'rawvideo', 'pipe:1']
        return run_bounded(args, timeout=45, limit=64*1024*1024)
    pcm = np.frombuffer(decode(render, True), dtype='<i2').reshape(-1,2).astype(np.int32)
    expected = np.zeros((2311680,), dtype=np.int32)  # 301 / 25 * 192000
    source_counts = []
    for i in (1,2):
        with wave.open(str(folder/f'media/participant-{i:02}.wav'), 'rb') as w:
            assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (192000,1,2)
            source = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.int32)
        source_counts.append(len(source))
        expected[:len(source)] += source
    size_ok = len(pcm) == len(expected)
    errors = pcm - expected[:,None] if size_ok else None
    # This fixture is mono on each source and Kdenlive renders stereo. Keep
    # raw-unity disagreement visible. Separately measure every sample against
    # a fixed sqrt(1/2) channel-conversion reference, never a fitted gain.
    mapped_errors = pcm - expected[:,None]*np.sqrt(0.5) if size_ok else None
    samples = {'source_counts': source_counts, 'rendered_samples_per_channel': len(pcm),
        'expected_samples_per_channel': len(expected),
        'whole_mix_max_error_lsb': int(np.abs(errors).max()) if errors is not None else None,
        'tail_max_error_lsb': int(np.abs(errors[2301952:2306048]).max()) if errors is not None else None,
        'after_last_source_eof_peak_lsb': int(np.abs(pcm[2306048:]).max()) if len(pcm) > 2306048 else None,
        'last_original_sample_expected': int(expected[2306047]),
        'last_original_sample_rendered': pcm[2306047].tolist() if len(pcm)>2306047 else [],
        'whole_mix_mismatched_samples_over_2_lsb': int(np.sum(np.abs(errors)>2)) if errors is not None else None,
        'fixed_channel_conversion_reference_gain': float(np.sqrt(0.5)),
        'measured_gain_diagnostic_only': float(np.dot(pcm[:,0].astype(np.float64), expected) / np.dot(expected.astype(np.float64), expected)) if size_ok else None,
        'fixed_channel_conversion_max_error_lsb': float(np.abs(mapped_errors).max()) if mapped_errors is not None else None,
        'fixed_channel_conversion_tail_max_error_lsb': float(np.abs(mapped_errors[2301952:2306048]).max()) if mapped_errors is not None else None,
        'fixed_channel_conversion_mismatches_over_1_lsb': int(np.sum(np.abs(mapped_errors)>1)) if mapped_errors is not None else None}
    frame_bytes = 320*180*3
    video = np.frombuffer(decode(render), dtype=np.uint8)
    original = np.frombuffer(decode(folder/'media/zoom-source.mp4'), dtype=np.uint8)
    pictures = {'rendered_frames': len(video)//frame_bytes,
        'recorded_frames': len(original)//frame_bytes,
        'recorded_picture_max_error': int(np.abs(video[:len(original)].astype(np.int16)-original.astype(np.int16)).max()) if len(video)>=len(original) else None,
        'final_empty_picture_peak_rgb': int(video[len(original):].max()) if len(video)>len(original) else None}
    anchors = []
    if len(video)==301*frame_bytes and len(original)==300*frame_bytes:
        v = video.reshape(-1, frame_bytes)
        s = original.reshape(-1, frame_bytes)
        for i in range(300):
            errors_by_offset = {j:float(np.abs(v[i].astype(np.int16)-s[i+j].astype(np.int16)).mean())
                                for j in (-1,0,1) if 0<=i+j<300}
            anchors.append({'frame': i, 'rgb_mae': errors_by_offset[0], 'best_offset': min(errors_by_offset, key=errors_by_offset.get)})
    pictures['frame_anchors'] = anchors
    base = semantic(folder/'constructed-coverage.kdenlive')
    native = semantic(folder/'native-restored.kdenlive')
    roundtrip = semantic(folder/'native-roundtrip.kdenlive')
    moved = semantic(folder/'native-moved.kdenlive')
    extent_delta = roundtrip['sequence_extent_frames']-native['sequence_extent_frames']
    move_ok = all(len(a['entries'])==len(b['entries'])==1 and
        a['entries'][0]['source']==b['entries'][0]['source'] and
        b['entries'][0]['position']-a['entries'][0]['position']==25 for a,b in zip(base['tracks'],moved['tracks']))
    construction = json.loads((folder/'construction.json').read_text(encoding='utf-8'))
    checks = {'originals_and_construction_unchanged': all(fingerprint(folder/p['path'])==p['sha256'] for p in construction['files']),
        'native_undo_semantics_equal': base==native,
        'native_reopen_timeline_semantics_equal': all(native[k]==roundtrip[k] for k in native if k!='sequence_extent_frames'),
        'native_extra_sequence_frame_reported_separately': extent_delta==1,
        'all_three_members_move_25_frames': move_ok and len(moved['tracks'])==3,
        'rendered_301_frames': pictures['rendered_frames']==301,
        # Same existing <4 RGB MAE / nearest-frame-zero criterion as S02/S07;
        # FFV1 is lossless after Kdenlive's image conversion, not before it.
        'all_300_recorded_picture_anchors_match': len(anchors)==300 and all(a['best_offset']==0 and a['rgb_mae']<4 for a in anchors),
        'one_empty_picture_no_freeze': pictures['final_empty_picture_peak_rgb']==0,
        'exact_rendered_pcm_duration': size_ok,
        'all_samples_match_fixed_channel_conversion_within_1_lsb': samples['fixed_channel_conversion_max_error_lsb'] is not None and samples['fixed_channel_conversion_max_error_lsb']<=1,
        'complete_partial_tail_including_last_sample': samples['fixed_channel_conversion_tail_max_error_lsb'] is not None and samples['fixed_channel_conversion_tail_max_error_lsb']<=1,
        'digital_zero_after_all_eofs': samples['after_last_source_eof_peak_lsb']==0}
    return {'schema_version': 1, 'passed': all(checks.values()), 'checks': checks,
        'pcm': samples, 'pictures': pictures, 'native_sequence_extent_delta_frames': extent_delta,
        'raw_unity_pcm_equality': samples['whole_mix_max_error_lsb']==0,
        'pixel_identical_to_direct_source_decode': pictures['recorded_picture_max_error']==0,
        'scope': 'Synthetic construction experiment and actual native GUI save/reopen/render only; not production interview export/approval or listening acceptance',
        'artifacts': {n:fingerprint(folder/n) for n in ['construction.json','native-moved.kdenlive','native-restored.kdenlive','native-roundtrip.kdenlive','gui-render-192k.mkv']}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, required=True)
    parser.add_argument('--ffmpeg', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.folder, args.ffmpeg)
    with args.report.open('x', encoding='utf-8', newline='\n') as out:
        out.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
