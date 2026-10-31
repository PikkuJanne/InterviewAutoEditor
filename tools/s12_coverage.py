"""Reviewed EOF coverage preview; deliberately NOT an EditPlan/export authority.

The separate v2 record preserves the complete v1 Analysis, including unresolved
origins. Neither this review nor its identity map authorizes cuts, gain changes
or source-clock acceptance. Existing Application/desktop v1 refusals still apply.
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

from interview_auto_editor.contracts import Analysis, dumps, fingerprint, loads, text
from interview_auto_editor.planner import analysis_digest
from interview_auto_editor.timing import FrameRange, SharedTimeMap, ceil, frame_time, integer, rational


@dataclass(frozen=True)
class CoverageReview:
    schema_version: Literal[2]
    analysis_sha256: str
    policy: Literal['preserve_samples_mark_empty_eof']
    reviewer: str
    evidence: str
    accepted: bool

    def __post_init__(self):
        if type(self.schema_version) is not int or self.schema_version != 2:
            raise ValueError('Explicit v2 coverage review required.')
        fingerprint(self.analysis_sha256)
        text(self.reviewer)
        text(self.evidence)
        if self.policy != 'preserve_samples_mark_empty_eof' or type(self.accepted) is not bool:
            raise ValueError('Unknown coverage policy/acceptance.')


@dataclass(frozen=True)
class SourceCoverage:
    source_id: str
    source_end: Fraction
    retained_samples: int  # zero for video, complete original count for audio
    clip_end_frame: int  # ceil of source EOF, never a fabricated source duration
    empty_until: Fraction

    def __post_init__(self):
        text(self.source_id)
        rational(self.source_end, positive=True)
        rational(self.empty_until, positive=True)
        integer(self.retained_samples)
        integer(self.clip_end_frame, 1)
        if self.source_end > self.empty_until:
            raise ValueError('Source EOF cannot be truncated.')


def _coverage(analysis):
    video = next(s for s in analysis.sources if s.kind == 'video')
    if video.duration * analysis.fps != int(video.duration * analysis.fps):
        raise ValueError('Recorded picture EOF must be a complete frame boundary.')
    # This bounded proposal covers only the observed less-than-one-frame tails.
    # Large gaps require another explicit policy, never implicit empty padding.
    if any(abs(s.duration - video.duration) >= 1 / analysis.fps for s in analysis.sources):
        raise ValueError('Coverage difference reaches one complete picture frame.')
    end = ceil(max(s.duration for s in analysis.sources) * analysis.fps)
    until = frame_time(end, analysis.fps)
    sources = tuple(SourceCoverage(s.source_id, s.duration, s.sample_count,
        ceil(s.duration * analysis.fps), until) for s in analysis.sources)
    return SharedTimeMap(analysis.fps, end, (FrameRange(0, end),)), sources


@dataclass(frozen=True)
class CoveragePreview:
    schema_version: Literal[2]
    analysis: Analysis
    review: CoverageReview
    time_map: SharedTimeMap
    sources: tuple[SourceCoverage, ...]
    authority: Literal['coverage_only_not_origin_or_edit_approval']

    def __post_init__(self):
        if type(self.schema_version) is not int or self.schema_version != 2:
            raise ValueError('Explicit v2 coverage preview required.')
        if self.authority != 'coverage_only_not_origin_or_edit_approval':
            raise ValueError('Coverage does not authorize origins or editing.')
        if not self.review.accepted or self.review.analysis_sha256 != analysis_digest(self.analysis):
            raise ValueError('Accepted review must bind the exact unchanged analysis.')
        expected_map, expected_sources = _coverage(self.analysis)
        if self.time_map != expected_map or self.sources != expected_sources:
            raise ValueError('Coverage must preserve every sample on one identity map.')
        if any(s.origin != 0 for s in self.analysis.sources):
            raise ValueError('This coverage preview cannot shift a source clock.')


def preview_coverage(analysis, review):
    """Read-only exact preview, even when alignment remains unresolved.

    Consumers must NOT substitute this for a v1 PlanningResult. No migration,
    source-status edit, approval rebinding, decoder or file write takes place.
    """
    analysis = loads(Analysis, dumps(analysis))
    review = loads(CoverageReview, dumps(review))
    time_map, sources = _coverage(analysis)
    result = CoveragePreview(2, analysis, review, time_map, sources,
        'coverage_only_not_origin_or_edit_approval')
    return loads(CoveragePreview, dumps(result))
