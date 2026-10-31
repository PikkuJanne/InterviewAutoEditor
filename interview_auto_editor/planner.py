"""S06 conservative shared pause planner. No decoding, gain or media writes.

Absence of model events is not approval to delete. Removable-gap approvals are
explicit source-time evidence bound to the entire immutable analysis digest.
The v1 EditPlan and its origin/tail refusals remain the export authority.
"""
from dataclasses import dataclass
from fractions import Fraction as F
import hashlib
from typing import Literal

from .contracts import (Analysis, EditPlan, Override, Review, dumps, fingerprint,
                        loads, text)
from .timing import FrameRange, SharedTimeMap, ceil, frame_time, rational, removable_frames


ALGORITHM = 's06-shared-pauses-1'


@dataclass(frozen=True)
class Preset:
    different_threshold: F
    different_residual: F
    same_threshold: F
    same_residual: F
    onset: F
    tail: F
    confidence: F


PRESETS = {
    'tight': Preset(F(4, 5), F(1, 4), F(3, 2), F(1, 2), F(3, 25), F(1, 5), F(9, 10)),
    'gentle': Preset(F(6, 5), F(1, 2), F(5, 2), F(9, 10), F(3, 25), F(1, 5), F(9, 10)),
}


def analysis_digest(analysis):
    return hashlib.sha256(dumps(analysis).encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class GapApproval:
    approval_id: str
    start: F
    end: F
    basis: Literal['construction_label', 'human_review']
    evidence: str

    def __post_init__(self):
        text(self.approval_id)
        text(self.evidence)
        if not F(0) <= rational(self.start) < rational(self.end):
            raise ValueError('Invalid approved global source-time interval.')
        if self.basis not in ('construction_label', 'human_review'):
            raise ValueError('A model-negative result cannot approve silence.')


@dataclass(frozen=True)
class PlannerRequest:
    schema_version: Literal[1, 2]
    analysis_sha256: str
    preset: Literal['tight', 'gentle']
    approvals: tuple[GapApproval, ...]
    overrides: tuple[Override, ...]

    def __post_init__(self):
        if type(self.schema_version) is not int or self.schema_version not in (1, 2):
            raise ValueError('Unsupported planner request version.')
        fingerprint(self.analysis_sha256)
        if self.preset not in PRESETS:
            raise ValueError('Unknown pause preset.')
        if len({a.approval_id for a in self.approvals}) != len(self.approvals):
            raise ValueError('Duplicate gap approval identity.')
        # Coalesced/disjoint approvals keep one unambiguous provenance per cut.
        if any(a.end >= b.start for a, b in zip(self.approvals, self.approvals[1:])):
            raise ValueError('Gap approvals must be ordered, disjoint and coalesced.')


@dataclass(frozen=True)
class GapDecision:
    source_start: F
    source_end: F
    rule: Literal['same', 'different', 'uncertain']
    outcome: Literal['removed', 'kept']
    reason: str
    residual_target: F
    removed: tuple[FrameRange, ...]
    approval_ids: tuple[str, ...]


@dataclass(frozen=True)
class PlanningResult:
    schema_version: Literal[1, 2]
    algorithm: Literal['s06-shared-pauses-1']
    request: PlannerRequest
    plan: EditPlan
    decisions: tuple[GapDecision, ...]

    def __post_init__(self):
        if self.schema_version not in (1, 2) or self.algorithm != ALGORITHM:
            raise ValueError('Unsupported planning result.')
        expected_policy = 'exact_coverage' if self.schema_version == 1 else 'original_timing_with_gaps_v2'
        if self.request.schema_version != self.schema_version or self.plan.tail_policy != expected_policy:
            raise ValueError('Planning result/request timing policy mismatch.')
        if analysis_digest(self.plan.analysis) != self.request.analysis_sha256:
            raise ValueError('Planner request belongs to a different analysis.')
        if self.request.overrides != self.plan.overrides or self.plan.gains:
            raise ValueError('Planner must retain overrides and cannot change gain.')
        removed = tuple(r for d in self.decisions for r in d.removed)
        actual = tuple(FrameRange(a.end, b.start) for a, b in
                       zip(self.plan.time_map.retained, self.plan.time_map.retained[1:]))
        if removed != actual:
            raise ValueError('Decisions must explain every shared removal.')
        approvals = {a.approval_id: a for a in self.request.approvals}
        for d in self.decisions:
            if not F(0) <= d.source_start < d.source_end or d.residual_target < 0:
                raise ValueError('Invalid gap decision.')
            text(d.reason)
            if bool(d.removed) != (d.outcome == 'removed') or len(d.removed) != len(d.approval_ids):
                raise ValueError('Invalid removal decision provenance.')
            for r, identity in zip(d.removed, d.approval_ids):
                a = approvals.get(identity)
                start, end = frame_time(r.start, self.plan.time_map.fps), frame_time(r.end, self.plan.time_map.fps)
                if a is None or not a.start <= start < end <= a.end or not d.source_start <= start < end <= d.source_end:
                    raise ValueError('Removal outside approved source time.')


@dataclass
class _Island:
    start: F
    end: F
    events: list


def _islands(analysis, preset):
    sources = {s.source_id: s for s in analysis.sources}
    intervals = []
    # Turns also remain conservative barriers, but never create extra splits.
    for event in analysis.events:
        source = sources[event.source_id]
        raw_start, raw_end = F(event.start_sample, source.sample_rate), F(event.end_sample, source.sample_rate)
        start = min(event.protected_start, max(F(0), raw_start - preset.onset))
        end = max(event.protected_end, min(source.duration, raw_end + preset.tail))
        intervals.append((start, end, event))
    islands = []
    for start, end, event in sorted(intervals, key=lambda row: (row[0], row[1], row[2].event_id)):
        if islands and start <= islands[-1].end:
            islands[-1].end = max(end, islands[-1].end)
            islands[-1].events.append(event)
        else:
            islands.append(_Island(start, end, [event]))
    return islands


def _boundary(island, sources, left):
    def time(e):
        return F(e.end_sample if left else e.start_sample, sources[e.source_id].sample_rate)
    bound = (max if left else min)(time(e) for e in island.events)
    return bound, [e for e in island.events if time(e) == bound]


def _rule(left, right, sources, confidence):
    # Activity at the exact boundary must be confident single-group speech.
    # Shared microphones and simultaneous boundary speakers are ambiguous.
    def speaker(events):
        if any(e.kind != 'speech' or e.confidence < confidence or
               len(sources[e.source_id].channel_labels) != 1 for e in events):
            return None
        identities = {e.source_id for e in events}
        return next(iter(identities)) if len(identities) == 1 else None
    a, b = speaker(left), speaker(right)
    return 'uncertain' if a is None or b is None else 'same' if a == b else 'different'


def _subtract(start, end, overrides):
    pieces = [(start, end)]
    for override in overrides:
        next_pieces = []
        for a, b in pieces:
            if override.end <= a or override.start >= b:
                next_pieces.append((a, b))
            else:
                if a < override.start:
                    next_pieces.append((a, override.start))
                if override.end < b:
                    next_pieces.append((override.end, b))
        pieces = next_pieces
    return pieces


def plan_pauses(analysis, request):
    """Deterministic, inference-free planning on validated v1 source coordinates.

    Approvals cover *every* track, never a per-microphone silence decision.
    No approvals, no activity or uncertain anchors preserve the full recording.
    V1 retains its origin/tail refusals. Explicit V2 requests preserve original
    placement without alignment certification and represent absence after EOF.
    """
    analysis = loads(Analysis, dumps(analysis))
    request = loads(PlannerRequest, dumps(request))
    if analysis_digest(analysis) != request.analysis_sha256:
        raise ValueError('Planner request belongs to a different analysis.')
    sources = {s.source_id: s for s in analysis.sources}
    video = next(s for s in analysis.sources if s.kind == 'video')
    frames = video.duration * analysis.fps
    if frames.denominator != 1:
        raise ValueError('Video extent must be exact whole project frames.')
    if request.schema_version == 2:
        frames = ceil(max(s.duration for s in analysis.sources) * analysis.fps)
    policy = 'exact_coverage' if request.schema_version == 1 else 'original_timing_with_gaps_v2'
    whole = SharedTimeMap(analysis.fps, int(frames), (FrameRange(0, int(frames)),))
    reviews = tuple(Review(r.source_id, r.source_time, whole.map_time(r.source_time), r.reason)
                    for r in analysis.reviews)
    # Reuse strict origin/tail/override/gain invariants BEFORE decisions.
    EditPlan(analysis, whole, (), (), (0, whole.output_frames), request.overrides, reviews, policy)
    if any(a.end > frame_time(whole.source_frames, analysis.fps) for a in request.approvals):
        raise ValueError('Gap approval exceeds recording extent.')
    preset = PRESETS[request.preset]
    islands = _islands(analysis, preset)
    decisions, cuts, reasons = [], [], []
    for left, right in zip(islands, islands[1:]):
        raw_end, left_events = _boundary(left, sources, True)
        raw_start, right_events = _boundary(right, sources, False)
        rule = _rule(left_events, right_events, sources, preset.confidence)
        residual = F(0)
        selected, approval_ids = [], []
        reason = 'uncertain_boundary_preserved'
        if rule != 'uncertain':
            threshold = preset.same_threshold if rule == 'same' else preset.different_threshold
            nominal = preset.same_residual if rule == 'same' else preset.different_residual
            protection = (left.end - raw_end) + (raw_start - right.start)
            residual = max(nominal, protection)
            reason = 'below_gap_threshold'
            if raw_start - raw_end > threshold:
                # Existing model protection can exceed preset guards. Only add
                # residual slack; never shrink any existing protection.
                extra = max(F(0), nominal - protection) / 2
                a, b = left.end + extra, right.start - extra
                reason = 'no_approved_safe_frame'
                for approval in request.approvals:
                    start, end = max(a, approval.start), min(b, approval.end)
                    if start >= end:
                        continue
                    for x, y in _subtract(start, end, request.overrides):
                        first, last = removable_frames(x, y, analysis.fps)
                        if first < last:
                            selected.append(FrameRange(first, last))
                            approval_ids.append(approval.approval_id)
                if selected:
                    reason = f'{request.preset}_{rule}_approved_pause'
        decisions.append(GapDecision(raw_end, raw_start, rule, 'removed' if selected else 'kept',
                                      reason, residual, tuple(selected), tuple(approval_ids)))
        cuts.extend(selected)
        reasons.extend(f'{reason};approval={identity}' for identity in approval_ids)
    retained, cursor = [], 0
    for cut in cuts:
        retained.append(FrameRange(cursor, cut.start))
        cursor = cut.end
    retained.append(FrameRange(cursor, whole.source_frames))
    mapping = SharedTimeMap(analysis.fps, whole.source_frames, tuple(retained))
    reviews = tuple(Review(r.source_id, r.source_time, mapping.map_time(r.source_time), r.reason)
                    for r in analysis.reviews)
    # Shared seam boundaries only. Meaningful turn/group construction is S07.
    units = (0, *(output.end for _, output in mapping.segments()))
    plan = EditPlan(analysis, mapping, tuple(reasons), (), units, request.overrides, reviews, policy)
    result = PlanningResult(request.schema_version, ALGORITHM, request, plan, tuple(decisions))
    return loads(PlanningResult, dumps(result))


def explain(result):
    """Exact source/output mapping with null output locations inside removals.

    This report contains source identities/timecodes: keep real reports private.
    Rational seconds are paired with frame indices; no misleading float clocks.
    """
    result = loads(PlanningResult, dumps(result))
    mapping = result.plan.time_map
    return {
        'schema_version': 1, 'algorithm': result.algorithm, 'preset': result.request.preset,
        'source_frames': mapping.source_frames, 'output_frames': mapping.output_frames,
        'removed_frames': mapping.source_frames - mapping.output_frames,
        'timing_policy': result.plan.tail_policy,
        'alignment_certified_by_this_plan': False,
        'source_coverage': [{'source_id': s.source_id, 'real_end_seconds': str(s.duration),
                             'clip_end_frame': ceil(s.duration * mapping.fps),
                             'empty_source_seconds': [str(s.duration), str(frame_time(mapping.source_frames, mapping.fps))],
                             'mapped_real_end_seconds': str(mapping.map_time(s.duration)),
                             'original_origin_status': s.origin_status,
                             'verified_offset': None if s.verified_offset is None else str(s.verified_offset)}
                            for s in result.plan.analysis.sources],
        'source_duration': str(frame_time(mapping.source_frames, mapping.fps)),
        'output_duration': str(frame_time(mapping.output_frames, mapping.fps)),
        'segments': [{'source_frames': [s.start, s.end], 'output_frames': [o.start, o.end],
                      'source_seconds': [str(frame_time(s.start, mapping.fps)), str(frame_time(s.end, mapping.fps))],
                      'output_seconds': [str(frame_time(o.start, mapping.fps)), str(frame_time(o.end, mapping.fps))]}
                     for s, o in mapping.segments()],
        'gaps': [{'source_seconds': [str(d.source_start), str(d.source_end)],
                  'rule': d.rule, 'reason': d.reason, 'residual_target': str(d.residual_target),
                  'removed': [{'source_frames': [r.start, r.end],
                               'output_seam': str(mapping.map_time(frame_time(r.end, mapping.fps))),
                               'approval_id': identity} for r, identity in zip(d.removed, d.approval_ids)]}
                 for d in result.decisions],
        'reviews': [{'source_id': r.source_id, 'source_seconds': str(r.source_time),
                     'output_seconds': None if r.output_time is None else str(r.output_time),
                     'reason': r.reason} for r in result.plan.reviews],
    }
