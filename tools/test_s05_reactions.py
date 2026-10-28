"""S05 safety regressions. Optional real tests use explicit LOCAL assets only."""
from dataclasses import replace
from fractions import Fraction
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from interview_auto_editor.contracts import Analysis, Event, dumps, loads
from interview_auto_editor.reactions import (Floor, Settings, YamnetCPU, analyze,
    identity, infer_channel, overlap_events, WINDOW)
from interview_auto_editor.speech import SpeechError, analyze as speech_analyze, decode_channel
from test_s04_speech import intake_for

try:
    import numpy as np
except ImportError:
    np=None

MODEL=os.environ.get('IAE_S05_MODEL')
SPEECH_MODEL=os.environ.get('IAE_S04_MODEL')
DEVELOPMENT=os.environ.get('IAE_S04_DEVELOPMENT')
FFMPEG=os.environ.get('IAE_FFMPEG')


def event(source,start,end,kind='speech',tag='a'):
    return Event(f'{source.source_id}:{tag}',source.source_id,kind,start,end,
        Fraction(start,source.sample_rate),Fraction(end,source.sample_rate),Fraction(1,2),
        'constructed-test-evidence','keep' if kind=='uncertainty' else '',source.channel_labels)


class SetupTests(unittest.TestCase):
    def test_benchmark_refuses_held_out_manifest(self):
        from s05_benchmark import Manifest
        with self.assertRaises(ValueError):
            loads(Manifest,'{"schema_version":1,"split":"held_out","provenance":"reserved","cases":[]}')

    def test_metrics_require_full_interval_not_any_hit(self):
        from s05_benchmark import protected_fraction
        self.assertEqual(protected_fraction([(Fraction(1),Fraction(2))],Fraction(0),Fraction(3)),Fraction(1,3))
        self.assertEqual(protected_fraction([(Fraction(0),Fraction(2)),(Fraction(1),Fraction(3))],Fraction(0),Fraction(3)),1)

    def test_missing_wrong_models_no_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'model'
            with self.assertRaisesRegex(SpeechError,'REACTION_MODEL_MISSING'):
                YamnetCPU(p)
            p.write_bytes(b'wrong')
            with self.assertRaisesRegex(SpeechError,'REACTION_MODEL_HASH_MISMATCH'):
                YamnetCPU(p)

    def test_missing_reaction_cli_is_private_safe(self):
        with tempfile.TemporaryDirectory() as d:
            args=[sys.executable,str(ROOT/'tools/s05_analyze.py')]
            for option in ('project','mapping','ffprobe','ffmpeg','speech-model','reaction-model','cache','report'):
                args+=['--'+option,str(Path(d)/'private-secret')]
            run=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(run.returncode,1)
            self.assertIn('MODEL_MISSING',run.stderr)
            self.assertNotIn(d,run.stderr)

    def test_strict_settings_and_floor(self):
        for kwargs in ({'reaction_threshold':0.1},{'onset':Fraction(-1)},
                       {'vocal_uncertainty':Fraction(2)},{'signal_minimum':Fraction(0)}):
            with self.assertRaises(SpeechError):
                Settings(**kwargs)
        with self.assertRaises(ValueError):
            loads(Settings,dumps(Settings()).replace('"numerator": 1','"numerator": true',1))
        with self.assertRaises(ValueError):
            Floor(0,-241,1)


@unittest.skipUnless(np is not None,'Explicit pinned NumPy required')
class FusionTests(unittest.TestCase):
    class Model:
        def __init__(self,positive=True):
            self.np=np
            self.positive=positive
        def scores(self,x):
            scores=np.zeros(521,dtype='float32')
            if self.positive and np.max(np.abs(x))>0.01:
                scores[18]=0.9
            return scores

    def test_reaction_vad_miss_at_eof_chunk_equivalence(self):
        samples=np.zeros(WINDOW*2+73,dtype='<f4')
        samples[-71:]=0.02
        raw=samples.tobytes()
        reference=infer_channel([raw],self.Model())
        for size in (4,733*4,8192*4):
            self.assertEqual(reference,infer_channel((raw[i:i+size] for i in range(0,len(raw),size)),self.Model()))
        runs=reference[0]['reaction']
        self.assertEqual(runs[-1][1],len(samples))
        self.assertLessEqual(runs[-1][0],len(samples)-71)

    def test_uncertain_low_signal_survives_negative_models(self):
        samples=np.zeros(32000,dtype='<f4')
        samples[12000:13024]=0.00001  # Below S04 peak threshold, above floor
        regions,count,floor=infer_channel([samples.tobytes()],self.Model(False))
        self.assertFalse(regions['reaction'])
        self.assertTrue(any(a<=12000 and b>=13024 for a,b,_ in regions['uncertainty']))
        self.assertEqual(count,32000)
        self.assertEqual(floor[0],-240)

    def test_finite_overshoot_and_nonfinite_refusal(self):
        x=np.full(400,1.02,dtype='<f4')
        self.assertEqual(infer_channel([x.tobytes()],self.Model())[1],400)
        x[2]=float('nan')
        with self.assertRaisesRegex(SpeechError,'NONFINITE'):
            infer_channel([x.tobytes()],self.Model())

    def test_zero_audio_has_floor_without_silence_certificate(self):
        regions,count,floor=infer_channel([np.zeros(16001,dtype='<f4').tobytes()],self.Model(False))
        self.assertFalse(any(regions.values()))
        self.assertEqual(count,16001)
        self.assertEqual(floor[0],-240)

    def test_cancel_and_metadata_limit_fail_visibly(self):
        raw=np.ones(2000,dtype='<f4').tobytes()
        with self.assertRaisesRegex(SpeechError,'CANCELLED'):
            infer_channel([raw],self.Model(),cancel=lambda:True)
        with patch('interview_auto_editor.reactions.MAX_SIGNAL_RUNS',0):
            with self.assertRaisesRegex(SpeechError,'METADATA_LIMIT'):
                infer_channel([raw],self.Model())

    def test_noise_cannot_erase_existing_low_confidence_events(self):
        # Pairwise overlap includes quiet uncertainty even under a loud source.
        from interview_auto_editor.contracts import Header,Source
        s=Source('shared','1'*64,'participant_audio',1000,2000,Fraction(2),Fraction(0),None,'unverified',('person_a','person_b'))
        t=replace(s,source_id='quiet',channel_labels=('quiet',))
        v=Source('video','2'*64,'video',0,0,Fraction(2),Fraction(0),Fraction(0),'verified',())
        a=Analysis(Header(1,'test','3'*64,'test','experimental',(),()),Fraction(25),(v,s,t),
            (event(s,100,1000,tag='pcm0'),event(s,100,1000,tag='pcm1'),event(t,300,400,'uncertainty')),(),())
        overlaps=overlap_events(a)
        self.assertEqual(len(overlaps),2)  # Physical stereo is not two speakers.
        self.assertEqual({(e.start_sample,e.end_sample) for e in overlaps},{(300,400)})
        self.assertTrue(all(e.confidence==0 for e in overlaps))
        self.assertEqual(overlaps[0].channel_labels,('person_a','person_b'))
        self.assertEqual(overlap_events(replace(a,sources=(v,s),events=a.events[:2])),())

    def test_declared_nonzero_origin_is_not_repaired(self):
        from interview_auto_editor.contracts import Header,Source
        s=Source('a','1'*64,'participant_audio',100,200,Fraction(2),Fraction(1,2),None,'unverified',('a',))
        t=replace(s,source_id='b',origin=Fraction(0),channel_labels=('b',))
        v=Source('video','2'*64,'video',0,0,Fraction(3),Fraction(0),Fraction(0),'verified',())
        a=Analysis(Header(1,'test','3'*64,'test','experimental',(),()),Fraction(25),(v,s,t),
            (event(s,0,100),event(t,100,175)),(),())
        out=overlap_events(a)
        self.assertEqual([(e.start_sample,e.end_sample) for e in out],[(50,100),(100,150)])
        self.assertEqual(a.sources[1].origin,Fraction(1,2))


@unittest.skipUnless(np is not None and all((MODEL,SPEECH_MODEL,DEVELOPMENT,FFMPEG)),
                     'Explicit local S04/S05 models, generated speech and FFmpeg required')
class RealCPU(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(DEVELOPMENT)/'development-stereo.wav'
        self.intake=intake_for(self.path,tail=Fraction(4,375))
        self.speech=speech_analyze(self.intake,{'participant':self.path},SPEECH_MODEL,FFMPEG,
                                  Path(self.temp.name)/'speech')

    def tearDown(self):
        self.temp.cleanup()

    def run_fusion(self,**kwargs):
        return analyze(self.speech,{'participant':self.path},MODEL,FFMPEG,Path(self.temp.name)/'reactions',**kwargs)

    def test_additive_full_extent_reviews_and_speech_labels(self):
        result=self.run_fusion(chunk_samples=733)
        self.assertEqual(result.analysis.events[:len(self.speech.analysis.events)],self.speech.analysis.events)
        self.assertEqual(result.analysis.sources,self.speech.analysis.sources)
        self.assertEqual(result.analysis.reviews[:len(self.speech.analysis.reviews)],self.speech.analysis.reviews)
        self.assertIs(result.speech.intake,self.intake)
        self.assertEqual(len(result.tracks[0].floors),2)
        self.assertEqual(result.summary()['sequence_extent_delta_frames'],1)
        self.assertFalse(result.summary()['ready'])
        self.assertFalse(result.summary()['reactions']['negative_model_certifies_silence'])
        labels=json.loads((Path(DEVELOPMENT)/'development-labels.json').read_text())
        for label in labels['labels']:
            for a,b in label['speech_regions']:
                endpoint=Fraction(a,self.intake.analysis.sources[1].sample_rate)
                for start,end in sorted((e.protected_start,e.protected_end) for e in result.analysis.events):
                    if start<=endpoint:
                        endpoint=max(endpoint,end)
                self.assertGreaterEqual(endpoint,Fraction(b,self.intake.analysis.sources[1].sample_rate))

    def test_real_model_chunk_equivalence_and_partial_eof(self):
        model=YamnetCPU(MODEL)
        source=self.intake.analysis.sources[1]
        expected=-(-source.sample_count*16000//source.sample_rate)
        def run(size):
            return infer_channel(decode_channel(self.path,0,FFMPEG,expected,chunk_samples=size),model)
        reference=run(65536)
        self.assertEqual(reference,run(733))
        self.assertEqual(reference,run(1))

    def test_mixed_sample_grids_and_reaction_source_tail(self):
        import wave
        from interview_auto_editor.probe import fingerprint
        for rate in (16000,44100,48000,96000,192000):
            count=rate//4+137
            x=(np.sin(np.arange(count)*2*np.pi*311/rate)*400).astype('<i2')
            p=Path(self.temp.name)/f'tail-{rate}.wav'
            with wave.open(str(p),'wb') as wav:
                wav.setparams((1,2,rate,count,'NONE','not compressed'))
                wav.writeframes(x.tobytes())
            before=fingerprint(p)
            intake=intake_for(p,tail=Fraction(4,375))
            speech=speech_analyze(intake,{'participant':p},SPEECH_MODEL,FFMPEG,Path(self.temp.name)/'mixed-speech')
            # Inject a positive event model, isolating source-grid/EOF behavior
            # from the semantic classification of this synthetic pure tone.
            with patch('interview_auto_editor.reactions.YamnetCPU',return_value=FusionTests.Model()):
                result=analyze(speech,{'participant':p},MODEL,FFMPEG,Path(self.temp.name)/'mixed-reactions')
            self.assertEqual(result.analysis.sources,intake.analysis.sources)
            reactions=[e for e in result.analysis.events if e.kind=='reaction']
            self.assertEqual(max(e.end_sample for e in reactions),count)
            self.assertEqual(max(e.protected_end for e in reactions),Fraction(count,rate))
            self.assertEqual(fingerprint(p),before)

    def test_cache_hit_invalidation_corruption_and_missing_model(self):
        first=self.run_fusion()
        with patch.object(YamnetCPU,'scores',side_effect=AssertionError('inference on hit')):
            hit=self.run_fusion(chunk_samples=17)
        self.assertEqual(hit.cache_hits,1)
        self.assertEqual(first.analysis,hit.analysis)
        source=self.intake.analysis.sources[1]
        decoder=('8.1.1','1'*64)
        self.assertNotEqual(identity(source,Settings(),decoder,2),identity(source,replace(Settings(),tail=Fraction(1)),decoder,2))
        self.assertNotEqual(identity(source,Settings(),decoder,2),identity(replace(source,sha256='4'*64),Settings(),decoder,2))
        self.assertNotEqual(identity(source,Settings(),decoder,2),identity(source,Settings(),('other','2'*64),2))
        base_key=identity(source,Settings(),decoder,2)
        with patch('interview_auto_editor.reactions.MODEL_SHA256','5'*64):
            self.assertNotEqual(identity(source,Settings(),decoder,2),base_key)
        p=Path(self.temp.name)/'reactions'/(first.tracks[0].key+'.json')
        p.write_text('{"schema_version":1,"unknown":true}')
        with self.assertRaisesRegex(SpeechError,'REACTION_CACHE_CORRUPT'):
            self.run_fusion()
        with self.assertRaisesRegex(SpeechError,'REACTION_MODEL_MISSING'):
            analyze(self.speech,{'participant':self.path},Path(self.temp.name)/'missing',FFMPEG,Path(self.temp.name)/'reactions')

    def test_cancellation_no_partial_cache_and_changed_source(self):
        with self.assertRaisesRegex(SpeechError,'CANCELLED'):
            self.run_fusion(cancel=lambda:True)
        self.assertFalse((Path(self.temp.name)/'reactions').exists())
        changed=replace(self.speech.analysis.sources[1],sha256='6'*64)
        bad=replace(self.speech,analysis=replace(self.speech.analysis,sources=(self.speech.analysis.sources[0],changed)))
        with self.assertRaisesRegex(SpeechError,'SOURCE_CHANGED'):
            analyze(bad,{'participant':self.path},MODEL,FFMPEG,Path(self.temp.name)/'reactions')


if __name__=='__main__':
    unittest.main()
