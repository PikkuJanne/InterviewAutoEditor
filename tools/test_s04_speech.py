"""Focused S04 tests. Real CPU/model tests require explicit LOCAL assets."""
from dataclasses import replace
from fractions import Fraction
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import wave
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from interview_auto_editor.contracts import Analysis, Header, Source, dumps, loads
from interview_auto_editor.intake import Diagnostic
from interview_auto_editor.probe import fingerprint, probe_wav
from interview_auto_editor.speech import (MODEL_SHA256, Settings, SileroCPU, SpeechError,
    analyze, atomic_new, decode_channel, identity, infer_regions)

try:
    import numpy as np
except ImportError:
    np = None


def intake_for(path, *, tail=Fraction(0), sequence_delta=1):
    ap = probe_wav(path)
    duration = ap.duration
    source = Source('participant', fingerprint(path), 'participant_audio', ap.sample_rate,
                    ap.sample_count, duration, Fraction(0), None, 'unverified', ('shared_mic',))
    video = Source('video', '1'*64, 'video', 0, 0, duration-tail, Fraction(0), Fraction(0), 'verified', ())
    analysis = Analysis(Header(1, 'test', '2'*64, 'test', 'experimental', (), ()), Fraction(25), (video, source), (), (), ())
    # These unit tests construct an inventory directly, never a Kdenlive fixture.
    class FakeIntake:
        diagnostics = (Diagnostic('review', 'SHARED_ORIGIN_NOT_CERTIFIED', 'participant'),
                       Diagnostic('review', 'SOURCE_TAIL_RECONCILIATION_REQUIRED', 'participant'),
                       Diagnostic('info', 'OBSERVED_NATIVE_EXTRA_SEQUENCE_FRAME', 'video'))
        def summary(self):
            return {'compatibility': 'EXPERIMENTAL', 'ready': False,
                    'sequence_extent_delta_frames': sequence_delta,
                    'source_end_minus_clip_end': str(tail), 'origin_diagnostics': ['UNVERIFIED_INSUFFICIENT_ANCHORS']}
    result = FakeIntake()
    result.analysis = analysis
    return result


class MissingModelTests(unittest.TestCase):
    def test_missing_model_and_cli_are_visible_without_media_access(self):
        with tempfile.TemporaryDirectory() as d:
            model = Path(d) / 'absent.onnx'
            with self.assertRaisesRegex(SpeechError, 'MODEL_MISSING'):
                SileroCPU(model)
            args = [sys.executable, str(ROOT/'tools/s04_analyze.py')]
            for option in ('project', 'mapping', 'ffprobe', 'ffmpeg', 'model', 'cache', 'report'):
                args += ['--'+option, str(model)]
            run = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertIn('MODEL_MISSING', run.stderr)
            self.assertNotIn(str(model), run.stderr)
            self.assertFalse(model.exists())

    def test_wrong_model_hash_refused_before_import(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'wrong.onnx'
            p.write_bytes(b'not a model')
            with self.assertRaisesRegex(SpeechError, 'MODEL_HASH_MISMATCH'):
                SileroCPU(p)

    def test_atomic_exclusive_publication(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'new.json'
            atomic_new(p, 'complete\n')
            with self.assertRaises(FileExistsError):
                atomic_new(p, 'changed')
            self.assertEqual(p.read_text(), 'complete\n')
            self.assertEqual(list(Path(d).iterdir()), [p])

    def test_settings_strict_codec(self):
        self.assertEqual(loads(Settings, dumps(Settings())), Settings())
        with self.assertRaises(ValueError):
            dumps(replace(Settings(), signal_peak=0.1))
        with self.assertRaises(ValueError):
            replace(Settings(), merge_samples=True)


@unittest.skipUnless(np is not None, 'NumPy optional; install locked S04 runtime')
class StreamingTests(unittest.TestCase):
    def fake(self):
        class Stateful:
            np = globals()['np']
            def reset(self): self.seen = 0
            def probability(self, samples):
                self.seen += 1
                return 0.75 if self.seen in (2, 3, 6) else 0.05
        return Stateful()

    def test_state_crosses_arbitrary_io_chunks_exactly(self):
        audio = np.zeros(512*7+31, dtype='<f4').tobytes()
        expected = infer_regions([audio], self.fake())
        for size in (4, 508, 2048, 7004, 65536):
            actual = infer_regions((audio[i:i+size] for i in range(0, len(audio), size)), self.fake())
            self.assertEqual(actual, expected)
        self.assertEqual(expected[1], len(audio)//4)
        self.assertEqual(len(expected[0]['speech']), 1)  # coalesced; short burst kept

    def test_uncertainty_keeps_non_speech_signal_without_claiming_speech(self):
        audio = np.full(512, 0.001, dtype='<f4').tobytes()
        regions, _ = infer_regions([audio], self.fake())
        self.assertEqual(regions['speech'], [])
        self.assertEqual(regions['uncertainty'][0][:2], (0, 512))

    def test_invalid_pcm_and_cancellation(self):
        for value in (float('nan'), float('inf')):
            with self.assertRaisesRegex(SpeechError, 'DECODED_AUDIO'):
                infer_regions([np.full(512, value, dtype='<f4').tobytes()], self.fake())
        with self.assertRaisesRegex(SpeechError, 'CANCELLED'):
            infer_regions([np.zeros(512, dtype='<f4').tobytes()], self.fake(), cancel=lambda: True)

    def test_finite_resampler_overshoot_is_not_clipped_or_normalized(self):
        model = self.fake()
        seen = []
        def probability(samples):
            seen.extend(samples.tolist())
            return 0.01
        model.probability = probability
        samples = np.full(512, 1.1, dtype='<f4')
        regions, _ = infer_regions([samples.tobytes()], model)
        self.assertEqual(seen, samples.tolist())
        self.assertEqual(regions['uncertainty'][0][:2], (0,512))

    def test_stalled_decoder_is_killed_and_reaped(self):
        stopped = threading.Event()
        class Pipe:
            def read(self, n):
                stopped.wait(2)
                return b''
            def close(self): pass
        class Process:
            stdout = Pipe()
            returncode = None
            def poll(self): return self.returncode
            def kill(self):
                self.returncode = -1
                stopped.set()
            def wait(self, timeout=None): return self.returncode
        process = Process()
        with patch('interview_auto_editor.speech.subprocess.Popen', return_value=process):
            with self.assertRaisesRegex(SpeechError, 'DECODER_TIME_OR_ERROR_LIMIT'):
                list(decode_channel('unused', 0, 'unused', 100, idle_timeout=0.05))
        self.assertTrue(stopped.is_set())
        self.assertEqual(process.returncode, -1)


MODEL = os.environ.get('IAE_S04_MODEL')
FIXTURE = os.environ.get('IAE_S04_DEVELOPMENT')
FFMPEG = os.environ.get('IAE_FFMPEG')


@unittest.skipUnless(MODEL and FIXTURE and FFMPEG and np is not None,
                     'Explicit local model/development fixture/FFmpeg needed; no implicit downloads')
class RealCPUTests(unittest.TestCase):
    def setUp(self):
        self.path = Path(FIXTURE)/'development-stereo.wav'
        self.labels = json.loads((Path(FIXTURE)/'development-labels.json').read_text())
        self.intake = intake_for(self.path, tail=Fraction(4,375))
        self.source = self.intake.analysis.sources[1]
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def run_analysis(self, **kwargs):
        return analyze(self.intake, {'participant': self.path}, MODEL, FFMPEG,
                       Path(self.temp.name)/'cache', **kwargs)

    def test_known_speech_and_short_acknowledgements_protected(self):
        result = self.run_analysis(chunk_samples=733)
        for label in self.labels['labels']:
            for channel in (0, 1):
                events = [e for e in result.analysis.events if f'pcm_channel={channel};' in e.evidence]
                protected = sorted((e.protected_start, e.protected_end) for e in events)
                for a_sample, b_sample in label['speech_regions']:
                    a = Fraction(a_sample, self.source.sample_rate)
                    b = Fraction(b_sample, self.source.sample_rate)
                    endpoint = a
                    for start, end in protected:
                        if start <= endpoint:
                            endpoint = max(endpoint, end)
                    self.assertGreaterEqual(endpoint, b, label['id'])
        self.assertTrue(any(e.kind == 'speech' for e in result.analysis.events))
        self.assertTrue(any(e.kind == 'uncertainty' for e in result.analysis.events))
        # Keep all original extent, origin, tail and correlation findings.
        self.assertEqual(result.analysis.sources, self.intake.analysis.sources)
        self.assertEqual(result.summary()['origin_diagnostics'], ['UNVERIFIED_INSUFFICIENT_ANCHORS'])
        self.assertEqual(result.summary()['sequence_extent_delta_frames'], 1)
        self.assertEqual(result.summary()['source_end_minus_clip_end'], '4/375')
        self.assertFalse(result.summary()['ready'])
        reasons = {r.reason for r in result.analysis.reviews}
        self.assertTrue({d.code for d in self.intake.diagnostics} <= reasons)

    def test_real_decode_and_model_chunk_equivalence_zero_tolerance(self):
        model = SileroCPU(MODEL)
        expected_count = -(-self.source.sample_count * 16000 // self.source.sample_rate)
        raw = b''.join(decode_channel(self.path, 0, FFMPEG, expected_count, chunk_samples=65536))
        reference = infer_regions([raw], model)
        for chunk in (1, 733, 8192):
            blocks = decode_channel(self.path, 0, FFMPEG, expected_count, chunk_samples=chunk)
            self.assertEqual(infer_regions(blocks, model), reference)
        self.assertLessEqual(abs(reference[1]-expected_count), 1)

    def test_cache_hits_and_invalidations_and_corruption(self):
        first = self.run_analysis()
        with patch.object(SileroCPU, 'probability', side_effect=AssertionError('inference on hit')):
            hit = self.run_analysis(chunk_samples=17)
        self.assertEqual(hit.cache_hits, 1)
        self.assertEqual(hit.analysis, first.analysis)
        changed = self.run_analysis(settings=replace(Settings(), onset=Fraction(1,4)))
        self.assertEqual(changed.cache_hits, 0)
        decoder = ('8.1.1', '3'*64)
        key = identity(self.source, Settings(), decoder, 2)
        self.assertNotEqual(key, identity(replace(self.source, sha256='4'*64), Settings(), decoder, 2))
        self.assertNotEqual(key, identity(self.source, Settings(), ('changed', '5'*64), 2))
        with patch('interview_auto_editor.speech.MODEL_SHA256', '6'*64):
            self.assertNotEqual(key, identity(self.source, Settings(), decoder, 2))
        p = Path(self.temp.name)/'cache'/(first.tracks[0].key+'.json')
        p.write_text('{"bad":true}')
        with self.assertRaisesRegex(SpeechError, 'CACHE_CORRUPT'):
            self.run_analysis()

    def test_cancel_leaves_no_partial_cache_and_source_change_refused(self):
        with self.assertRaisesRegex(SpeechError, 'CANCELLED'):
            self.run_analysis(cancel=lambda: True)
        self.assertFalse((Path(self.temp.name)/'cache').exists())
        self.intake.analysis = replace(self.intake.analysis,
            sources=(self.intake.analysis.sources[0], replace(self.source, sha256='7'*64)))
        with self.assertRaisesRegex(SpeechError, 'SOURCE_CHANGED'):
            self.run_analysis()

    def test_decoder_failure_count_limits_and_stalled_cancellation(self):
        with self.assertRaises(SpeechError):
            list(decode_channel(self.path, 0, FFMPEG, 1))
        with self.assertRaisesRegex(SpeechError, 'CHUNK_BOUNDS'):
            list(decode_channel(self.path, 0, FFMPEG, 100, chunk_samples=0))
        with self.assertRaisesRegex(SpeechError, 'CANCELLED'):
            list(decode_channel(self.path, 0, FFMPEG, 100, cancel=lambda: True))

    def test_mixed_sample_grids_and_active_source_tail_are_preserved(self):
        for rate in (16000,44100,48000,96000,192000):
            count = rate//3 + 137
            samples = (np.sin(np.arange(count) * 2*np.pi*311/rate) * 2000).astype('<i2')
            p = Path(self.temp.name)/f'{rate}.wav'
            with wave.open(str(p), 'wb') as wav:
                wav.setparams((1,2,rate,count,'NONE','not compressed'))
                wav.writeframes(samples.tobytes())
            before = fingerprint(p)
            intake = intake_for(p, tail=Fraction(4,375))
            result = analyze(intake, {'participant':p}, MODEL, FFMPEG, Path(self.temp.name)/'mixed-cache', chunk_samples=733)
            self.assertEqual(result.analysis.sources, intake.analysis.sources)
            self.assertEqual(max(e.end_sample for e in result.analysis.events), count)
            self.assertEqual(max(e.protected_end for e in result.analysis.events), Fraction(count,rate))
            self.assertEqual(before,fingerprint(p))


if __name__ == '__main__':
    unittest.main()
