"""S08 explicit idle approvals and reversible native-frame gain policy.

The v1 EditPlan gain refusal is intentionally unchanged. This separate policy
must reproduce before export; negative inference and correlation grant no rights.
"""
from dataclasses import dataclass
from fractions import Fraction as F
import hashlib
from typing import Literal

from .contracts import dumps, loads, fingerprint, text
from .timing import ceil, floor, integer, rational
from .turns import build_turns, pieces

ALGORITHM = 's08-approved-idle-1'
DB = -36
RAMP_SECONDS = F(1, 5)


def planning_digest(result):
    return hashlib.sha256(dumps(result).encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class IdleApproval:
    approval_id: str
    source_id: str
    start: F
    end: F
    basis: Literal['construction_label', 'human_review']
    evidence: str

    def __post_init__(self):
        for value in (self.approval_id, self.source_id, self.evidence):
            text(value)
        if not F(0) <= rational(self.start) < rational(self.end):
            raise ValueError('Invalid source-time idle approval.')
        if self.basis not in ('construction_label', 'human_review'):
            raise ValueError('Model absence or bleed cannot approve cleanup.')


@dataclass(frozen=True)
class CleanupRequest:
    schema_version: Literal[1]
    planning_sha256: str
    approvals: tuple[IdleApproval, ...]

    def __post_init__(self):
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError('Unsupported cleanup request version.')
        fingerprint(self.planning_sha256)
        if len({a.approval_id for a in self.approvals}) != len(self.approvals):
            raise ValueError('Duplicate idle approval identity.')
        previous = {}
        for a in self.approvals:
            if a.start <= previous.get(a.source_id, F(-1)):
                raise ValueError('Source approvals must be ordered and disjoint.')
            previous[a.source_id] = a.end


@dataclass(frozen=True)
class GainSpan:
    source_id: str
    approval_id: str
    start_frame: int  # unity here; native dB-linear ramp, then unity at end
    down_frame: int
    up_frame: int
    end_frame: int

    def __post_init__(self):
        text(self.source_id)
        text(self.approval_id)
        integer(self.start_frame)
        integer(self.down_frame, self.start_frame + 1)
        integer(self.up_frame, self.down_frame + 1)
        integer(self.end_frame, self.up_frame + 1)


@dataclass(frozen=True)
class CleanupResult:
    schema_version: Literal[1]
    algorithm: Literal['s08-approved-idle-1']
    request: CleanupRequest
    spans: tuple[GainSpan, ...]
    diagnoses: tuple[str, ...]

    def __post_init__(self):
        if type(self.schema_version) is not int or self.schema_version != 1 or self.algorithm != ALGORITHM:
            raise ValueError('Unsupported cleanup policy.')
        for reason in self.diagnoses:
            text(reason)


def subtract(intervals, barriers):
    for x, y in barriers:
        intervals = [(a, b) for c, d in intervals
                     for a, b in ((c, min(d, x)), (max(c, y), d)) if a < b]
    return intervals


def build_cleanup(result, request):
    """Independent authorization: approval AND protection AND shared-map bounds.

    Guards are at least S06's 120/200 ms. Explicit overlap protects ALL mics;
    shared mics always stay unity. Keep/audible intervals protect ALL tracks,
    including restoration on a microphone with incomplete event evidence.
    Full exterior handles, no-activity sources and each group edge stay unity.
    """
    layout = build_turns(result)  # strict S06 reproduction, origins and tails
    request = loads(CleanupRequest, dumps(request))
    if request.planning_sha256 != planning_digest(result):
        raise ValueError('Cleanup approval belongs to a different planning result.')
    plan, spans, diagnoses = layout.plan, [], []
    fps = plan.time_map.fps
    sources = {s.source_id: s for s in plan.analysis.sources}
    events = plan.analysis.events
    if events:
        first = min(e.protected_start for e in events)
        last = max(e.protected_end for e in events)
    else:
        first = last = F(0)
    for approval in request.approvals:
        s = sources.get(approval.source_id)
        if s is None or s.kind != 'participant_audio' or approval.end > s.duration:
            raise ValueError('Idle approval source/bounds do not resolve.')
        if len(s.channel_labels) != 1 or not events:
            diagnoses.append(approval.approval_id + ': shared microphone or no activity; unity retained')
            continue
        barriers = [(o.start, o.end) for o in plan.overrides]
        # Source-local protection plus all-track explicit overlap is mandatory.
        for e in events:
            if e.source_id == s.source_id or e.kind == 'overlap':
                es = sources[e.source_id]
                barriers.append((max(F(0), min(e.protected_start, F(e.start_sample, es.sample_rate)-F(3,25))),
                                 min(s.duration, max(e.protected_end, F(e.end_sample, es.sample_rate)+F(1,5)))))
        intervals = subtract([(max(first, approval.start), min(last, approval.end))], barriers)
        count = len(spans)
        for a, b in intervals:
            for begin, end, _ in pieces(plan):
                # One extra native frame on both sides covers frame evaluation
                # and sample interpolation. Never span a removed gap/group edge.
                lo = max(begin, ceil(a*fps)) + 1
                hi = min(end, floor(b*fps)) - 1
                ramp = max(2, ceil(RAMP_SECONDS*fps))
                if hi - lo >= 2*ramp + 1:
                    spans.append(GainSpan(s.source_id, approval.approval_id, lo, lo+ramp, hi-ramp, hi))
        if len(spans) == count:
            diagnoses.append(approval.approval_id + ': protected, exterior, removed or too short; unity retained')
    return CleanupResult(1, ALGORITHM, request, tuple(spans), tuple(diagnoses))


def validate_cleanup(result, cleanup):
    cleanup = loads(CleanupResult, dumps(cleanup))
    if build_cleanup(result, cleanup.request) != cleanup:
        raise ValueError('Cleanup does not reproduce its approved policy.')
    return cleanup


def db_at(spans, source_id, frame):
    """Exact dB interpolation on absolute source frames, unity outside spans."""
    for s in spans:
        if s.source_id != source_id or not s.start_frame <= frame <= s.end_frame:
            continue
        if frame < s.down_frame:
            return DB * F(frame-s.start_frame, s.down_frame-s.start_frame)
        if frame <= s.up_frame:
            return F(DB)
        return DB * F(s.end_frame-frame, s.end_frame-s.up_frame)
    return F(0)


def native_keys(cleanup, source_id, begin, end):
    """Absolute source keys for an entry effect; no resetting at output seams."""
    keys = {begin: F(0), end-1: F(0)}
    for s in cleanup.spans:
        if s.source_id == source_id and begin <= s.start_frame < s.end_frame < end:
            keys.update({s.start_frame: F(0), s.down_frame: F(DB), s.up_frame: F(DB), s.end_frame: F(0)})
    return tuple(sorted(keys.items())) if any(v for v in keys.values()) else ()
