"""S12 offline measurements. Labels do not certify media or authorize edits.

Real inputs/labels/reports are private. This command never modifies a run, source,
approval, origin or tail. It never declares full-interview/utility acceptance.
"""
from dataclasses import dataclass
from fractions import Fraction as F
import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Literal

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from interview_auto_editor.cleanup import CleanupResult, validate_cleanup
from interview_auto_editor.contracts import dumps, fingerprint, loads, text
from interview_auto_editor.planner import PlanningResult, analysis_digest, plan_pauses
from interview_auto_editor.speech import atomic_new
from interview_auto_editor.timing import frame_time, rational


@dataclass(frozen=True)
class CorpusEntry:
    recording_id: str
    split: Literal['development', 'held_out']
    source_sha256: tuple[str, ...]

    def __post_init__(self):
        text(self.recording_id)
        if self.split not in ('development', 'held_out') or not self.source_sha256:
            raise ValueError('Explicit corpus partition and source identities required.')
        for value in self.source_sha256:
            fingerprint(value)


@dataclass(frozen=True)
class EvaluationCorpus:
    schema_version: Literal[1]
    frozen_configuration_sha256: str
    entries: tuple[CorpusEntry, ...]
    evidence: str

    def __post_init__(self):
        fingerprint(self.frozen_configuration_sha256)
        text(self.evidence)
        if len({e.recording_id for e in self.entries}) != len(self.entries):
            raise ValueError('One recording cannot belong to multiple partitions.')
        development = {s for e in self.entries if e.split == 'development' for s in e.source_sha256}
        held_out = {s for e in self.entries if e.split == 'held_out' for s in e.source_sha256}
        if not development or not held_out or development & held_out:
            raise ValueError('Distinct development and held-out recordings required.')


@dataclass(frozen=True)
class Label:
    label_id: str
    kind: Literal['word', 'acknowledgement', 'laughter', 'overlap', 'uncertainty',
                  'removable_gap', 'handover_gap', 'idle_noise']
    source_id: str
    start: F
    end: F
    basis: Literal['human_review', 'construction_label']
    evidence: str

    def __post_init__(self):
        text(self.label_id)
        text(self.source_id)
        text(self.evidence)
        if not F(0) <= rational(self.start) < rational(self.end):
            raise ValueError('Invalid independent label interval.')
        if self.kind in ('removable_gap', 'handover_gap') and self.source_id != 'all':
            raise ValueError('Removable time must be labelled across all tracks.')


@dataclass(frozen=True)
class EvaluationLabels:
    schema_version: Literal[1]
    recording_id: str
    split: Literal['development', 'held_out']
    analysis_sha256: str
    labels: tuple[Label, ...]
    evidence: str

    def __post_init__(self):
        text(self.recording_id)
        text(self.evidence)
        fingerprint(self.analysis_sha256)
        if len({v.label_id for v in self.labels}) != len(self.labels):
            raise ValueError('Duplicate independent label identity.')


def configuration_digest(result):
    """Freeze settings/models/preset and implementation; exclude corpus content."""
    header = result.plan.analysis.header
    files = sorted((ROOT / 'interview_auto_editor').rglob('*.py'))
    payload = {'preset': result.request.preset, 'tool_version': header.tool_version,
               'settings': header.settings, 'models': header.model_versions,
               'modules': [(p.relative_to(ROOT).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest())
                           for p in files]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def union(intervals):
    result = []
    for a, b in sorted(intervals):
        if result and a <= result[-1][1]:
            result[-1] = (result[-1][0], max(b, result[-1][1]))
        else:
            result.append((a, b))
    return result


def overlap(a, b, intervals):
    return sum((max(F(0), min(b, y) - max(a, x)) for x, y in intervals), F(0))


def ratio(numerator, denominator):
    return {'numerator': str(numerator), 'denominator': str(denominator),
            'fraction': str(F(numerator) / denominator) if denominator else None}


def evaluate(result, labels, corpus, cleanup=None):
    result = loads(PlanningResult, dumps(result))
    labels = loads(EvaluationLabels, dumps(labels))
    corpus = loads(EvaluationCorpus, dumps(corpus))
    if plan_pauses(result.plan.analysis, result.request) != result:
        raise ValueError('Planning result does not reproduce.')
    if labels.analysis_sha256 != analysis_digest(result.plan.analysis):
        raise ValueError('Independent labels belong to a different analysis.')
    if configuration_digest(result) != corpus.frozen_configuration_sha256:
        raise ValueError('Calibration changed after the corpus configuration was frozen.')
    entry = next((e for e in corpus.entries if e.recording_id == labels.recording_id), None)
    sources = {s.source_id: s for s in result.plan.analysis.sources}
    if entry is None or entry.split != labels.split or set(entry.source_sha256) != {s.sha256 for s in sources.values()}:
        raise ValueError('Corpus recording/split/source binding mismatch.')
    if labels.split == 'held_out' and any(v.basis != 'human_review' for v in labels.labels):
        raise ValueError('Held-out interview labels require independent human review.')
    if cleanup is not None:
        cleanup = validate_cleanup(result, cleanup)
    m = result.plan.time_map
    duration = frame_time(m.source_frames, m.fps)
    kept = [(frame_time(s.start, m.fps), frame_time(s.end, m.fps)) for s in m.retained]
    removed = [(a[1], b[0]) for a, b in zip(kept, kept[1:])]
    spans = cleanup.spans if cleanup is not None else ()
    content = {}
    idle_retained = idle_attenuated = F(0)
    for v in labels.labels:
        if v.end > duration:
            raise ValueError('Independent label exceeds source domain.')
        if v.kind not in ('removable_gap', 'handover_gap'):
            source = sources.get(v.source_id)
            if source is None or source.kind != 'participant_audio':
                raise ValueError('Independent audio label source does not resolve.')
        if v.kind == 'idle_noise':
            # Per-source union below avoids duplicate/overlapping idle labels.
            continue
        if v.kind in ('removable_gap', 'handover_gap'):
            continue
        item = content.setdefault(v.kind, {'labels': 0, 'fully_retained': 0, 'fully_audible': 0,
                                           'labelled_source_seconds': F(0), 'retained_source_seconds': F(0)})
        retained = overlap(v.start, v.end, kept)
        attenuated = any(s.source_id == v.source_id or v.kind == 'overlap' for s in spans
                         if frame_time(s.start_frame, m.fps) < v.end and frame_time(s.end_frame, m.fps) > v.start)
        item['labels'] += 1
        item['fully_retained'] += int(retained == v.end - v.start)
        item['fully_audible'] += int(retained == v.end - v.start and not attenuated)
        item['labelled_source_seconds'] += v.end - v.start
        item['retained_source_seconds'] += retained
    for identity in sources:
        idle = union((v.start, v.end) for v in labels.labels if v.kind == 'idle_noise' and v.source_id == identity)
        gain = union((frame_time(s.start_frame, m.fps), frame_time(s.end_frame, m.fps))
                     for s in spans if s.source_id == identity)
        for a, b in idle:
            for x, y in kept:
                lo, hi = max(a, x), min(b, y)
                if lo < hi:
                    idle_retained += hi - lo
                    idle_attenuated += overlap(lo, hi, gain)
    allowed = union((v.start, v.end) for v in labels.labels if v.kind in ('removable_gap', 'handover_gap'))
    removed_seconds = sum((b - a for a, b in removed), F(0))
    approved_seconds = sum((overlap(a, b, allowed) for a, b in removed), F(0))
    handovers = [v for v in labels.labels if v.kind == 'handover_gap']
    def record_digest(record):
        return hashlib.sha256(dumps(record).encode('utf-8')).hexdigest()
    return {'schema_version': 1, 'split': labels.split, 'acceptance': 'NOT_ESTABLISHED',
            'provenance': {'recording_id': labels.recording_id,
                           'configuration_sha256': corpus.frozen_configuration_sha256,
                           'analysis_sha256': labels.analysis_sha256,
                           'labels_sha256': record_digest(labels),
                           'corpus_sha256': record_digest(corpus),
                           'cleanup_sha256': record_digest(cleanup) if cleanup is not None else None,
                           'evaluator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
            'content': {k: {key: str(value) if isinstance(value, F) else value for key, value in values.items()}
                        for k, values in content.items()},
            'independently_approved_removal_seconds': ratio(approved_seconds, removed_seconds),
            'all_deletions_inside_independent_labels': approved_seconds == removed_seconds if removed else None,
            'excessive_handover_labels_shortened': ratio(sum(overlap(v.start, v.end, removed) > 0 for v in handovers), len(handovers)),
            'planned_idle_attenuation_source_seconds': ratio(idle_attenuated, idle_retained),
            'actual_noise_reduction_db': None, 'actual_render_sync': 'NOT_RUN',
            'actual_native_editability': 'NOT_RUN', 'manual_correction_seconds': None,
            'editing_effort_reduction': None, 'owner_listening': 'NOT_RUN'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result', required=True, type=Path)
    parser.add_argument('--labels', required=True, type=Path)
    parser.add_argument('--corpus', required=True, type=Path)
    parser.add_argument('--cleanup', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        def read(cls, path):
            with path.open('r', encoding='utf-8') as stream:
                return loads(cls, stream.read(8 * 1024 * 1024 + 1))
        report = evaluate(read(PlanningResult, args.result), read(EvaluationLabels, args.labels),
                          read(EvaluationCorpus, args.corpus),
                          read(CleanupResult, args.cleanup) if args.cleanup else None)
        atomic_new(args.output, json.dumps(report, indent=2) + '\n')
    except (OSError, ValueError):
        print('S12_EVALUATION_REFUSED: inspect private records; no input was modified.', file=sys.stderr)
        return 1
    print('S12 measurements written; full acceptance remains unestablished.')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
