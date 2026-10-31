"""Independent S12 scoring regressions; these are not interview acceptance."""
from dataclasses import replace
from fractions import Fraction as F
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from interview_auto_editor.cleanup import CleanupRequest, IdleApproval, build_cleanup, planning_digest
from interview_auto_editor.contracts import dumps, loads, to_data
from interview_auto_editor.planner import analysis_digest, plan_pauses
from test_s06_planner import request, two_events
from s12_evaluate import (CorpusEntry, EvaluationCorpus, EvaluationLabels, Label,
                          configuration_digest, evaluate)
from s12_timing import fixture


class QualityTests(unittest.TestCase):
    def setUp(self):
        self.analysis = two_events()
        self.result = plan_pauses(self.analysis, request(self.analysis))
        self.corpus = EvaluationCorpus(1, configuration_digest(self.result), (
            CorpusEntry('development', 'development', tuple(s.sha256 for s in self.analysis.sources)),
            CorpusEntry('unopened-distinct', 'held_out', ('9' * 64,))), 'Independent source registration.')

    def labels(self, *labels):
        return EvaluationLabels(1, 'development', 'development', analysis_digest(self.analysis),
                                labels, 'Independent construction labels, not model predictions.')

    def label(self, kind, source, start, end, identity=None):
        return Label(identity or kind, kind, source, F(start), F(end), 'construction_label',
                     'Generated independent source-time interval.')

    def test_labelled_loss_partial_loss_and_unity_have_actual_denominators(self):
        labels = self.labels(self.label('word', 'p0', 2, 3),
            self.label('acknowledgement', 'p1', 4, F(17, 4)),
            self.label('laughter', 'p0', F(31, 10), F(33, 10)),
            self.label('handover_gap', 'all', F(16, 5), F(147, 25)))
        report = evaluate(self.result, labels, self.corpus)
        self.assertEqual(report['content']['word']['fully_audible'], 1)
        self.assertEqual(report['content']['acknowledgement']['fully_retained'], 0)
        self.assertEqual(report['content']['laughter']['retained_source_seconds'], '1/10')
        self.assertEqual(report['excessive_handover_labels_shortened']['fraction'], '1')
        self.assertEqual(report['acceptance'], 'NOT_ESTABLISHED')
        self.assertIsNone(report['actual_noise_reduction_db'])
        self.assertEqual(report['provenance']['configuration_sha256'], self.corpus.frozen_configuration_sha256)
        self.assertEqual(report['provenance']['analysis_sha256'], analysis_digest(self.analysis))
        self.assertIsNone(report['provenance']['cleanup_sha256'])

    def test_removal_outside_independent_labels_is_detected(self):
        labels = self.labels(self.label('removable_gap', 'all', 4, 5))
        report = evaluate(self.result, labels, self.corpus)
        self.assertFalse(report['all_deletions_inside_independent_labels'])
        self.assertEqual(report['independently_approved_removal_seconds']['numerator'], '1')
        self.assertEqual(report['independently_approved_removal_seconds']['denominator'], '67/25')
        self.assertIsNone(report['excessive_handover_labels_shortened']['fraction'])

    def test_empty_metrics_remain_unknown_and_never_claim_utility(self):
        identity = plan_pauses(self.analysis, request(self.analysis, approvals=()))
        report = evaluate(identity, self.labels(), self.corpus)
        self.assertEqual(report['content'], {})
        self.assertIsNone(report['all_deletions_inside_independent_labels'])
        self.assertIsNone(report['independently_approved_removal_seconds']['fraction'])
        self.assertIsNone(report['planned_idle_attenuation_source_seconds']['fraction'])
        self.assertIsNone(report['editing_effort_reduction'])
        self.assertEqual(report['owner_listening'], 'NOT_RUN')

    def test_duplicate_idle_labels_do_not_inflate_source_seconds_and_content_gain_is_detected(self):
        cleanup = build_cleanup(self.result, CleanupRequest(1, planning_digest(self.result), (
            IdleApproval('idle', 'p0', F(6), F(7), 'construction_label', 'Generated idle interval.'),)))
        self.assertTrue(cleanup.spans)
        labels = self.labels(self.label('idle_noise', 'p0', 6, 7, 'idle1'),
            self.label('idle_noise', 'p0', F(25, 4), F(27, 4), 'idle2'),
            self.label('word', 'p0', F(32, 5), F(33, 5)))
        report = evaluate(self.result, labels, self.corpus, cleanup)
        self.assertEqual(report['planned_idle_attenuation_source_seconds']['denominator'], '1')
        self.assertEqual(report['content']['word']['fully_retained'], 1)
        self.assertEqual(report['content']['word']['fully_audible'], 0)
        with self.assertRaises(ValueError):
            evaluate(self.result, labels, self.corpus, replace(cleanup, spans=()))

    def test_split_source_configuration_and_stale_label_bindings_fail_closed(self):
        with self.assertRaises(ValueError):
            EvaluationCorpus(1, self.corpus.frozen_configuration_sha256, (
                self.corpus.entries[0], CorpusEntry('other', 'held_out', ('2' * 64,))), 'Bad split.')
        with self.assertRaises(ValueError):
            replace(self.corpus, entries=(self.corpus.entries[0], replace(self.corpus.entries[1], recording_id='development')))
        for labels, corpus in ((replace(self.labels(), analysis_sha256='0' * 64), self.corpus),
                               (replace(self.labels(), split='held_out'), self.corpus),
                               (self.labels(), replace(self.corpus, frozen_configuration_sha256='0' * 64))):
            with self.assertRaises(ValueError):
                evaluate(self.result, labels, corpus)
        with self.assertRaises(ValueError):
            evaluate(self.result, self.labels(self.label('word', 'missing', 1, 2)), self.corpus)
        held = replace(self.corpus, entries=(CorpusEntry('development', 'held_out',
            self.corpus.entries[0].source_sha256), CorpusEntry('distinct', 'development', ('9' * 64,))))
        with self.assertRaisesRegex(ValueError, 'human review'):
            evaluate(self.result, replace(self.labels(self.label('word', 'p0', 2, 3)), split='held_out'), held)

    def test_strict_codec_and_cli_exclusive_private_safe_refusal(self):
        for changes in ({'schema_version': 2}, {'extra': True}):
            data = to_data(self.labels()); data.update(changes)
            with self.assertRaises(ValueError):
                loads(EvaluationLabels, json.dumps(data))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, record in (('result', self.result), ('labels', self.labels()), ('corpus', self.corpus)):
                (root / f'{name}.json').write_text(dumps(record), encoding='utf-8')
            output = root / 'report.json'
            args = [sys.executable, '-B', str(Path(__file__).with_name('s12_evaluate.py')),
                    '--result', str(root/'result.json'), '--labels', str(root/'labels.json'),
                    '--corpus', str(root/'corpus.json'), '--output', str(output)]
            run = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(run.returncode, 2, run.stderr)
            before = output.read_bytes()
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 1)
            self.assertEqual(before, output.read_bytes())
            (root/'labels.json').write_text('{"private-source-name": "bad"}', encoding='utf-8')
            run = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertNotIn(folder, run.stderr)
            self.assertNotIn('private-source-name', run.stderr)

    def test_two_hour_fixture_uses_exact_real_domains_without_media_or_origin_repair(self):
        for fps, expected in ((F(25), F(7200)), (F(30000, 1001), F(36036, 5))):
            a, req = fixture(fps)
            self.assertEqual(a.sources[0].duration, expected)
            self.assertEqual(len(a.sources), 9)
            self.assertEqual(len(a.events), 600)
            self.assertEqual(len(req.approvals), 599)
            self.assertTrue(all(s.duration == expected for s in a.sources))
            self.assertTrue(all(s.verified_offset == 0 for s in a.sources))


if __name__ == '__main__':
    unittest.main()
