"""Conservative source-group turns; timeline structure never authorizes removal."""
from dataclasses import dataclass, replace
from fractions import Fraction as F

from .contracts import EditPlan, dumps, loads
from .planner import PlanningResult, plan_pauses
from .timing import ceil, floor

ALGORITHM = 's07-source-group-turns-1'
MIN_TURN = F(3, 5)
JOIN_GAP = F(3, 5)
MIN_UNIT = F(1, 2)


@dataclass(frozen=True)
class Cue:
    kind: str
    source_ids: tuple[str, ...]
    event_ids: tuple[str, ...]
    source_start: F
    source_end: F
    output_start: F
    output_end: F


@dataclass(frozen=True)
class TurnLayout:
    algorithm: str
    plan: EditPlan
    cues: tuple[Cue, ...]


def build_turns(result):
    """Reproduce S06 before deriving cuts. Brief/ambiguous activity gets cues.

    Source IDs describe recording groups, never inferred human voice identities.
    Cues are exact; frame cuts are structural only and do not remove samples.
    """
    result = loads(PlanningResult, dumps(result))
    if plan_pauses(result.plan.analysis, result.request) != result:
        raise ValueError('Planning result does not reproduce its approved request.')
    plan, cues = result.plan, []
    mapping, sources = plan.time_map, {s.source_id: s for s in plan.analysis.sources}
    spans, activity = [], []
    for source in plan.analysis.sources:
        speech = sorted((e for e in plan.analysis.events if e.source_id == source.source_id
                         and e.kind == 'speech' and e.confidence >= F(9, 10)
                         and len(source.channel_labels) == 1), key=lambda e: (e.start_sample, e.event_id))
        runs = []
        for event in speech:
            a, b = F(event.start_sample, source.sample_rate), F(event.end_sample, source.sample_rate)
            activity.append((a, b, source.source_id, event.event_id))
            if runs and a - runs[-1][1] <= JOIN_GAP:
                runs[-1] = (runs[-1][0], max(b, runs[-1][1]), runs[-1][2] + (event.event_id,))
            else:
                runs.append((a, b, (event.event_id,)))
        for a, b, ids in runs:
            kind = 'turn' if b - a >= MIN_TURN else 'backchannel'
            cues.append(Cue(kind, (source.source_id,), ids, a, b, mapping.map_time(a), mapping.map_time(b)))
            if kind == 'turn':
                spans.append((a, b, source.source_id, ids))
    represented = {i for c in cues for i in c.event_ids}
    for e in plan.analysis.events:
        if e.event_id not in represented:
            s = sources[e.source_id]
            a, b = F(e.start_sample, s.sample_rate), F(e.end_sample, s.sample_rate)
            cues.append(Cue('shared_activity' if len(s.channel_labels) > 1 else e.kind,
                            (s.source_id,), (e.event_id,), a, b, mapping.map_time(a), mapping.map_time(b)))
    candidates = set()
    spans.sort()
    for left, right in zip(spans, spans[1:]):
        if left[2] == right[2]:
            continue
        if right[0] >= left[1]:
            midpoint = (left[1] + right[0]) / 2
            output = mapping.map_time(midpoint)
            if output is not None:
                candidates.add(floor(output * mapping.fps + F(1, 2)))
    # Sweep raw confident speech to describe genuine multi-source activity.
    # Explicit overlap events below independently retain their own boundaries.
    starts, ends = {}, {}
    for a, b, identity, event_id in activity:
        starts.setdefault(a, []).append((event_id, identity))
        ends.setdefault(b, []).append(event_id)
    endpoints = sorted(set(starts) | set(ends))
    overlaps = []
    active = {}
    for a, b in zip(endpoints, endpoints[1:]):
        for event_id in ends.get(a, ()):
            active.pop(event_id)
        active.update(starts.get(a, ()))
        ids = tuple(sorted(set(active.values())))
        if len(ids) < 2:
            continue
        events = tuple(sorted(active))
        if overlaps and overlaps[-1][1] == a and overlaps[-1][2] == ids:
            overlaps[-1] = (overlaps[-1][0], b, ids, tuple(sorted(set(overlaps[-1][3] + events))))
        else:
            overlaps.append((a, b, ids, events))
    for a, b, ids, events in overlaps:
        cues.append(Cue('overlap', ids, events, a, b, mapping.map_time(a), mapping.map_time(b)))
    for cue in cues:
        if cue.kind == 'overlap' and cue.source_end - cue.source_start >= MIN_TURN:
            candidates.update((floor(cue.output_start * mapping.fps), ceil(cue.output_end * mapping.fps)))
    mandatory = {0, *(out.end for _, out in mapping.segments())}
    units = set(mandatory)
    minimum = ceil(MIN_UNIT * mapping.fps)
    # Never create a tiny unit beside another cut/seam. Cues remain available.
    for candidate in sorted(candidates):
        if all(abs(candidate - existing) >= minimum for existing in units):
            units.add(candidate)
    plan = replace(plan, edit_units=tuple(sorted(units)))
    return TurnLayout(ALGORITHM, plan, tuple(sorted(cues, key=lambda c: (c.source_start, c.source_end, c.kind, c.source_ids))))


def pieces(plan):
    """Aligned (source start, source end, output start) without crossing seams."""
    for source, output in plan.time_map.segments():
        bounds = [b for b in plan.edit_units if output.start <= b <= output.end]
        for a, b in zip(bounds, bounds[1:]):
            yield source.start + a - output.start, source.start + b - output.start, a
