"""Strict version-1 analysis/edit-plan wire contracts, independent of MLT.

    Fractions serialize as {numerator, denominator}; floats, unknown keys,
    implicit defaults and unknown schema versions fail closed. No migrations
    exist yet: future migrations must be explicit functions with fixture tests.
"""
from dataclasses import dataclass, fields, is_dataclass
from fractions import Fraction
import json
import re
from typing import Literal, get_args, get_origin, get_type_hints

from .timing import SharedTimeMap, ceil, frame_time, integer, rational


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('A nonempty string is required.')


def fingerprint(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('SHA256 fingerprint required.')


@dataclass(frozen=True)
class Header:
    schema_version: Literal[1]
    run_id: str
    project_sha256: str
    tool_version: str
    adapter_target: str
    settings: tuple[tuple[str, str], ...]
    model_versions: tuple[tuple[str, str], ...]

    def __post_init__(self):
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError('Unsupported schema version; explicit migration required.')
        for v in (self.run_id, self.tool_version, self.adapter_target):
            text(v)
        fingerprint(self.project_sha256)
        for pairs in (self.settings, self.model_versions):
            if len({k for k, _ in pairs}) != len(pairs):
                raise ValueError('Duplicate setting/model identifiers.')
            for k, v in pairs:
                text(k)
                text(v)


@dataclass(frozen=True)
class Source:
    source_id: str
    sha256: str
    kind: Literal['video', 'participant_audio']
    sample_rate: int  # zero for video
    sample_count: int
    duration: Fraction
    origin: Fraction
    verified_offset: Fraction | None
    origin_status: Literal['verified', 'unverified', 'offset_detected', 'inconsistent']
    channel_labels: tuple[str, ...]

    def __post_init__(self):
        text(self.source_id)
        fingerprint(self.sha256)
        rational(self.duration, positive=True)
        rational(self.origin)
        if self.origin_status == 'verified':
            rational(self.verified_offset)
        elif self.verified_offset is not None:
            raise ValueError('Unverified offsets must be null, never an asserted zero.')
        integer(self.sample_count)
        integer(self.sample_rate)
        if self.kind not in ('video', 'participant_audio') or self.origin_status not in ('verified', 'unverified', 'offset_detected', 'inconsistent'):
            raise ValueError('Unknown source kind/origin status.')
        if self.kind == 'participant_audio':
            integer(self.sample_rate, 1)
            integer(self.sample_count, 1)
            if self.duration != Fraction(self.sample_count, self.sample_rate) or not self.channel_labels:
                raise ValueError('Audio sample count/rate and channel labels are authoritative.')
        elif self.sample_rate != 0 or self.sample_count != 0:
            raise ValueError('Video uses frame timing, not invented audio samples.')
        for label in self.channel_labels:
            text(label)


@dataclass(frozen=True)
class Event:
    event_id: str
    source_id: str
    kind: Literal['speech', 'reaction', 'uncertainty', 'turn', 'overlap']
    start_sample: int
    end_sample: int
    protected_start: Fraction
    protected_end: Fraction
    confidence: Fraction
    evidence: str
    uncertainty_reason: str
    channel_labels: tuple[str, ...]

    def __post_init__(self):
        text(self.event_id)
        text(self.source_id)
        text(self.evidence)
        integer(self.start_sample)
        integer(self.end_sample, self.start_sample + 1)
        if self.kind not in ('speech', 'reaction', 'uncertainty', 'turn', 'overlap'):
            raise ValueError('Unknown event kind.')
        if not Fraction(0) <= rational(self.protected_start) < rational(self.protected_end):
            raise ValueError('Invalid protection.')
        if not Fraction(0) <= rational(self.confidence) <= 1:
            raise ValueError('Invalid confidence.')
        if self.kind == 'uncertainty':
            text(self.uncertainty_reason)


@dataclass(frozen=True)
class Review:
    source_id: str
    source_time: Fraction
    output_time: Fraction | None
    reason: str

    def __post_init__(self):
        text(self.source_id)
        text(self.reason)
        if rational(self.source_time) < 0 or (self.output_time is not None and rational(self.output_time) < 0):
            raise ValueError('Negative review time.')


@dataclass(frozen=True)
class ShotCandidate:
    source_id: str
    source_frame: int
    confidence: Fraction
    evidence: str
    review_reason: str

    def __post_init__(self):
        text(self.source_id)
        text(self.evidence)
        integer(self.source_frame)
        if not Fraction(0) <= rational(self.confidence) <= 1:
            raise ValueError('Invalid shot confidence.')


@dataclass(frozen=True)
class Analysis:
    header: Header
    fps: Fraction
    sources: tuple[Source, ...]
    events: tuple[Event, ...]
    shots: tuple[ShotCandidate, ...]
    reviews: tuple[Review, ...]

    def __post_init__(self):
        rational(self.fps, positive=True)
        sources = {s.source_id: s for s in self.sources}
        if len(sources) < 2 or len(sources) != len(self.sources) or sum(s.kind == 'video' for s in self.sources) != 1:
            raise ValueError('Distinct source identities, one video and participant audio are required.')
        if len({e.event_id for e in self.events}) != len(self.events):
            raise ValueError('Duplicate event identity.')
        for event in self.events:
            source = sources.get(event.source_id)
            if source is None or source.kind != 'participant_audio' or event.end_sample > source.sample_count:
                raise ValueError('Unresolved/out-of-range sample event.')
            if not event.protected_start <= Fraction(event.start_sample, source.sample_rate) < Fraction(event.end_sample, source.sample_rate) <= event.protected_end <= source.duration:
                raise ValueError('Protection must enclose the sample event within its source.')
            if not set(event.channel_labels) <= set(source.channel_labels):
                raise ValueError('Unresolved channel label.')
        for review in self.reviews:
            if review.source_id not in sources or review.source_time > sources[review.source_id].duration:
                raise ValueError('Unresolved/out-of-range review.')
        for shot in self.shots:
            source = sources.get(shot.source_id)
            if source is None or source.kind != 'video' or frame_time(shot.source_frame, self.fps) >= source.duration:
                raise ValueError('Unresolved/out-of-range picture candidate.')


@dataclass(frozen=True)
class GainPoint:
    source_id: str
    sample: int
    gain: Fraction  # linear amplitude, never a new normalization pass

    def __post_init__(self):
        text(self.source_id)
        integer(self.sample)
        if not Fraction(0) <= rational(self.gain) <= 1:
            raise ValueError('Gain outside reversible attenuation range.')


@dataclass(frozen=True)
class Override:
    source_id: str
    start: Fraction
    end: Fraction
    action: Literal['keep', 'audible']

    def __post_init__(self):
        text(self.source_id)
        if not Fraction(0) <= rational(self.start) < rational(self.end) or self.action not in ('keep', 'audible'):
            raise ValueError('Invalid source-time override.')


@dataclass(frozen=True)
class EditPlan:
    analysis: Analysis
    time_map: SharedTimeMap
    removed_reasons: tuple[str, ...]
    gains: tuple[GainPoint, ...]
    edit_units: tuple[int, ...]  # output frame boundaries, shared by all tracks
    overrides: tuple[Override, ...]
    reviews: tuple[Review, ...]
    tail_policy: Literal['exact_coverage', 'original_timing_with_gaps_v2']

    def __post_init__(self):
        m = self.time_map
        duration = frame_time(m.source_frames, m.fps)
        if self.analysis.fps != m.fps or self.tail_policy not in ('exact_coverage', 'original_timing_with_gaps_v2'):
            raise ValueError('Map rate/tail policy mismatch.')
        original = self.tail_policy == 'original_timing_with_gaps_v2'
        if original and m.source_frames != ceil(max(s.duration for s in self.analysis.sources) * m.fps):
            raise ValueError('Original timing requires the complete longest source extent.')
        for source in self.analysis.sources:
            # V2 preserves the starter clock, including unknown alignment. It
            # does not certify, replace or apply a diagnostic/verified offset.
            if source.origin != 0:
                raise ValueError('Nonzero source placement is unsupported.')
            if not original and (source.origin_status != 'verified' or source.verified_offset != 0):
                raise ValueError('Unverified/nonzero origin cannot authorize an export.')
            if not original and source.duration != duration:
                raise ValueError('Unresolved source tails; exact coverage required.')
        if len(self.removed_reasons) != len(m.retained) - 1:
            raise ValueError('Each removed interval requires a reason.')
        for reason in self.removed_reasons:
            text(reason)
        for event in self.analysis.events:
            if event.kind in ('speech', 'reaction', 'uncertainty', 'overlap') and not m.contains(event.protected_start, event.protected_end):
                raise ValueError('Removal intersects protected content.')
        sources = {s.source_id: s for s in self.analysis.sources}
        last = {}
        for point in self.gains:
            source = sources.get(point.source_id)
            if source is None or source.kind != 'participant_audio' or point.sample > source.sample_count or point.sample <= last.get(point.source_id, -1):
                raise ValueError('Unresolved/out-of-order gain point.')
            last[point.source_id] = point.sample
        # S08 may define safe envelope semantics. For now attenuation cannot
        # be authorized in a plan with protected audio on that source.
        for point in self.gains:
            if point.gain != 1 and any(e.source_id == point.source_id and e.kind in ('speech', 'reaction', 'uncertainty', 'overlap') for e in self.analysis.events):
                raise ValueError('Protected-source attenuation needs a later validated envelope policy.')
        if not self.edit_units or self.edit_units[0] != 0 or self.edit_units[-1] != m.output_frames or any(type(v) is not int for v in self.edit_units) or any(a >= b for a, b in zip(self.edit_units, self.edit_units[1:])):
            raise ValueError('Aligned edit units must partition the output.')
        for override in self.overrides:
            if override.source_id not in sources or override.end > sources[override.source_id].duration or not m.contains(override.start, override.end):
                raise ValueError('Override must resolve and remain retained.')
        for review in self.reviews:
            if review.source_id not in sources or review.source_time > sources[review.source_id].duration or review.output_time != m.map_time(review.source_time):
                raise ValueError('Review source/output locations disagree with the shared map.')


def to_data(value):
    if isinstance(value, Fraction):
        return {'numerator': value.numerator, 'denominator': value.denominator}
    if is_dataclass(value):
        return {f.name: to_data(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, tuple):
        return [to_data(v) for v in value]
    if value is None or type(value) in (str, int, bool):
        return value
    raise ValueError('Unsupported wire value; no floats or implicit encodings.')


def from_data(cls, value):
    origin, args = get_origin(cls), get_args(cls)
    if cls is Fraction:
        if not isinstance(value, dict) or set(value) != {'numerator', 'denominator'}:
            raise ValueError('Exact rational object required.')
        n, d = value['numerator'], value['denominator']
        integer(d, 1)
        if type(n) is not int:
            raise ValueError('Integer numerator required.')
        result = Fraction(n, d)
        if (n, d) != (result.numerator, result.denominator):
            raise ValueError('Canonical reduced rational required.')
        return result
    if origin is Literal:
        if not any(type(value) is type(v) and value == v for v in args):
            raise ValueError('Unknown literal/schema version.')
        return value
    if origin is tuple:
        if not isinstance(value, list):
            raise ValueError('Array required.')
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(from_data(args[0], v) for v in value)
        if len(value) != len(args):
            raise ValueError('Tuple arity mismatch.')
        return tuple(from_data(t, v) for t, v in zip(args, value))
    if type(None) in args:
        return None if value is None else from_data(next(t for t in args if t is not type(None)), value)
    if is_dataclass(cls):
        if not isinstance(value, dict) or set(value) != {f.name for f in fields(cls)}:
            raise ValueError('Missing/unknown contract fields.')
        hints = get_type_hints(cls)
        return cls(**{k: from_data(hints[k], v) for k, v in value.items()})
    if cls in (str, int, bool) and type(value) is cls:
        return value
    raise ValueError('Contract type mismatch.')


def loads(cls, raw):
    if len(raw) > 8 * 1024 * 1024:
        raise ValueError('Contract exceeds bounded size.')
    def unique(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ValueError('Duplicate JSON key.')
            result[k] = v
        return result
    try:
        return from_data(cls, json.loads(raw, object_pairs_hook=unique))
    except RecursionError as exc:
        raise ValueError('Contract nesting exceeds parser bounds.') from exc


def dumps(value):
    # Reparse: direct dataclass construction must satisfy the same strict types.
    data = to_data(value)
    from_data(type(value), data)
    return json.dumps(data, indent=2, ensure_ascii=False) + '\n'
