"""S09 recorded-picture observations and conservative shared-silence seams.

No face identity, audio inference or independent picture clock. Observations do
not change the canonical Analysis or certify silence. Refinement can only RESTORE
frames deleted by a reproducible, explicitly approved S06 plan.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
import hashlib
from pathlib import Path
from typing import Literal

from .contracts import Analysis, dumps, fingerprint as check_hash, loads, text
from .planner import (GapApproval, PlanningResult, analysis_digest, plan_pauses)
from .probe import fingerprint, probe_video, run_bounded, tool_version
from .timing import FrameRange, ceil, floor, frame_time
from .turns import JOIN_GAP, MIN_TURN

ALGORITHM = 's09-recorded-picture-1'
SEAM_ALGORITHM = 's09-restore-only-seams-1'
WIDTH, HEIGHT = 96, 54
PIXELS = WIDTH * HEIGHT
MAX_FRAMES = 8192
MIN_SHOT = F(1, 2)
RADIUS = F(3, 2)


@dataclass(frozen=True)
class PictureRequest:
    schema_version: Literal[1]
    analysis_sha256: str
    layout: Literal['speaker_view', 'gallery', 'pinned', 'camera_off', 'uncertain']
    basis: Literal['construction_label', 'human_review']
    evidence: str

    def __post_init__(self):
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError('Unsupported picture request.')
        check_hash(self.analysis_sha256)
        if self.layout not in ('speaker_view', 'gallery', 'pinned', 'camera_off', 'uncertain') or self.basis not in ('construction_label', 'human_review'):
            raise ValueError('Explicit reviewed layout required; no inferred identity.')
        text(self.evidence)


@dataclass(frozen=True)
class Boundary:
    source_frame: int
    mean_difference: F
    changed_fraction: F
    stable_before: int
    stable_after: int

    def __post_init__(self):
        from .timing import integer, rational
        integer(self.source_frame, 1)
        integer(self.stable_before)
        integer(self.stable_after)
        for value in (self.mean_difference, self.changed_fraction):
            if not F(0) <= rational(value) <= 1:
                raise ValueError('Invalid picture measurement.')


@dataclass(frozen=True)
class PictureWindow:
    handover: F
    frames: FrameRange
    boundaries: tuple[Boundary, ...]


@dataclass(frozen=True)
class PictureAnalysis:
    schema_version: Literal[1]
    algorithm: Literal['s09-recorded-picture-1']
    request: PictureRequest
    video_sha256: str
    implementation_sha256: str
    decoder_sha256: str
    decoder_version: str
    windows: tuple[PictureWindow, ...]

    def __post_init__(self):
        if self.schema_version != 1 or self.algorithm != ALGORITHM:
            raise ValueError('Unsupported picture analysis.')
        for value in (self.video_sha256, self.implementation_sha256, self.decoder_sha256):
            check_hash(value)
        text(self.decoder_version)


@dataclass(frozen=True)
class PictureMarker:
    kind: str
    source_time: F
    output_time: F | None
    confidence: F
    reason: str


@dataclass(frozen=True)
class PictureRefinement:
    schema_version: Literal[1]
    algorithm: Literal['s09-restore-only-seams-1']
    input_planning_sha256: str
    picture_sha256: str
    result: PlanningResult
    markers: tuple[PictureMarker, ...]


def digest(value):
    return hashlib.sha256(dumps(value).encode('utf-8')).hexdigest()


def _handover_pairs(analysis):
    """Substantial S07 recording-group runs, never a facial/speaker identity."""
    runs = []
    for source in analysis.sources:
        if source.kind != 'participant_audio' or len(source.channel_labels) != 1:
            continue
        joined = []
        for e in sorted((e for e in analysis.events if e.source_id == source.source_id
                         and e.kind == 'speech' and e.confidence >= F(9, 10)),
                        key=lambda e: (e.start_sample, e.end_sample)):
            a, b = F(e.start_sample, source.sample_rate), F(e.end_sample, source.sample_rate)
            if joined and a - joined[-1][1] <= JOIN_GAP:
                joined[-1] = (joined[-1][0], max(b, joined[-1][1]))
            else:
                joined.append((a, b))
        runs.extend((a, b, source.source_id) for a, b in joined if b-a >= MIN_TURN)
    runs.sort()
    return tuple(sorted({(left[1], right[0]) for left, right in zip(runs, runs[1:]) if left[2] != right[2]}))


def handovers(analysis):
    return tuple(sorted({right for _, right in _handover_pairs(analysis)}))


def window_ranges(analysis):
    video = next(s for s in analysis.sources if s.kind == 'video')
    total = video.duration * analysis.fps
    if total.denominator != 1:
        raise ValueError('Picture observations require exact source video frames.')
    if not F(1) <= analysis.fps <= 120:
        raise ValueError('Picture analysis supports audited rates from 1 to 120 FPS.')
    # Include the preceding gap and a half-second left picture handle. Long
    # gaps count against the explicit budget; no partial coverage is implied.
    lefts = {t: min(left for left, right in _handover_pairs(analysis) if right == t) for t in handovers(analysis)}
    return tuple((t, FrameRange(max(0, floor(min(t-RADIUS, lefts[t]-MIN_SHOT)*analysis.fps)),
                               min(int(total), ceil((t+RADIUS)*analysis.fps))))
                 for t in handovers(analysis))


def confidence(boundary, fps, layout):
    minimum = ceil(MIN_SHOT * fps)
    return F(9, 10) if (layout == 'speaker_view' and
        boundary.mean_difference >= F(24, 255) and boundary.changed_fraction >= F(11, 20)
        and min(boundary.stable_before, boundary.stable_after) >= minimum) else F(1, 2)


def inspect_frames(frames, start):
    """Low-resolution luma cuts with measured persistent pictures either side.

    Scores are engineering thresholds, not calibrated semantic confidence.
    Motion, flashes, fades and brief reactions remain review observations.
    """
    if not frames or any(type(f) is not bytes or len(f) != PIXELS for f in frames):
        raise ValueError('Complete fixed-size picture frames required.')
    found = []
    def difference(a, b):
        return sum(abs(x-y) for x, y in zip(a, b))
    for i in range(1, len(frames)):
        delta = [abs(x-y) for x, y in zip(frames[i-1], frames[i])]
        mean, broad = F(sum(delta), PIXELS*255), F(sum(d >= 24 for d in delta), PIXELS)
        # Lower candidate threshold deliberately retains uncertain transitions.
        if mean < F(10, 255) or broad < F(1, 4):
            continue
        before = after = 0
        for j in range(i-1, -1, -1):
            if difference(frames[j], frames[i-1]) > 12*PIXELS:
                break
            before += 1
        for j in range(i, len(frames)):
            if difference(frames[j], frames[i]) > 12*PIXELS:
                break
            after += 1
        found.append(Boundary(start+i, mean, broad, before, after))
    return tuple(found)


def validate_picture(analysis, picture):
    analysis = loads(Analysis, dumps(analysis))
    picture = loads(PictureAnalysis, dumps(picture))
    video = next(s for s in analysis.sources if s.kind == 'video')
    if (picture.request.analysis_sha256 != analysis_digest(analysis) or
            picture.video_sha256 != video.sha256 or
            picture.implementation_sha256 != fingerprint(Path(__file__))):
        raise ValueError('Picture observations belong to different inputs or implementation.')
    expected = window_ranges(analysis)
    if tuple((w.handover, w.frames) for w in picture.windows) != expected:
        raise ValueError('Incomplete or stale handover picture coverage.')
    if sum(w.frames.length for w in picture.windows) > MAX_FRAMES:
        raise ValueError('Picture analysis exceeds bounded frame budget.')
    for w in picture.windows:
        previous = w.frames.start
        for b in w.boundaries:
            if not previous < b.source_frame < w.frames.end:
                raise ValueError('Unordered/out-of-window picture boundary.')
            if b.stable_before > b.source_frame-w.frames.start or b.stable_after > w.frames.end-b.source_frame:
                raise ValueError('Picture stability exceeds observed coverage.')
            previous = b.source_frame
    return picture


def analyze_picture(analysis, request, video_path, ffmpeg, ffprobe):
    """Read local audited video in one decode pass; no model or network operation.

    Select absolute decoder frame numbers BEFORE scaling; no approximate seeking,
    FPS filter, frame interpolation or inference from filename/face identity.
    Oversized runs fail, never publish partial observations. Ctrl-C reaps FFmpeg.
    """
    analysis = loads(Analysis, dumps(analysis))
    request = loads(PictureRequest, dumps(request))
    video = next(s for s in analysis.sources if s.kind == 'video')
    if request.analysis_sha256 != analysis_digest(analysis) or fingerprint(video_path) != video.sha256:
        raise ValueError('Picture input binding mismatch.')
    windows = window_ranges(analysis)
    if sum(r.length for _, r in windows) > MAX_FRAMES:
        raise ValueError('Picture analysis exceeds bounded frame budget.')
    probe = probe_video(video_path, ffprobe)
    if (probe.fps, probe.duration, probe.start, probe.cadence) != (analysis.fps, video.duration, F(0), 'CFR_AUDITED'):
        raise ValueError('Picture source timing not audited CFR.')
    # Merge ranges for a single bounded decode, including overlapping handovers.
    merged = []
    for _, r in windows:
        if merged and r.start <= merged[-1].end:
            merged[-1] = FrameRange(merged[-1].start, max(r.end, merged[-1].end))
        else:
            merged.append(r)
    images = {}
    decoder_hash = fingerprint(ffmpeg)
    version = tool_version(ffmpeg)
    if merged:
        select = '+'.join(f'between(n,{r.start},{r.end-1})' for r in merged)
        count = sum(r.length for r in merged)
        raw = run_bounded([ffmpeg, '-v', 'error', '-nostdin', '-protocol_whitelist', 'file,pipe',
            '-i', Path(video_path).resolve(), '-map', '0:0', '-an', '-sn', '-dn',
            '-vf', f"select='{select}',scale={WIDTH}:{HEIGHT}:flags=area,format=gray",
            '-frames:v', count, '-fps_mode', 'passthrough', '-f', 'rawvideo', 'pipe:1'],
            limit=count*PIXELS, timeout=120)
        if len(raw) != count*PIXELS:
            raise ValueError('Incomplete picture decode; no partial observations.')
        cursor = 0
        for r in merged:
            for frame in range(r.start, r.end):
                images[frame] = raw[cursor:cursor+PIXELS]
                cursor += PIXELS
    if fingerprint(video_path) != video.sha256 or fingerprint(ffmpeg) != decoder_hash:
        raise ValueError('Picture source or decoder changed during analysis.')
    observed = tuple(PictureWindow(t, r, inspect_frames([images[f] for f in range(r.start, r.end)], r.start))
                     for t, r in windows)
    result = PictureAnalysis(1, ALGORITHM, request, video.sha256, fingerprint(Path(__file__)),
                             decoder_hash, version, observed)
    return validate_picture(analysis, result)


def refine_picture_seams(base, picture):
    """Reduce S06 deletions only. Replan/revalidate S06, then rebind S08 cleanup.

    Unknown layout, ambiguous changes or insufficient edge coverage restore the
    affected handover deletion. A stable cut inside approved silence can become
    the new right edge; the retained new picture starts at that existing frame.
    """
    base = loads(PlanningResult, dumps(base))
    if plan_pauses(base.plan.analysis, base.request) != base:
        raise ValueError('Planning result does not reproduce its approved request.')
    picture = validate_picture(base.plan.analysis, picture)
    fps = base.plan.analysis.fps
    minimum = ceil(MIN_SHOT*fps)
    allowed, actions = [], []
    changed = False
    for decision in base.decisions:
        relevant = [w for w in picture.windows if w.handover == decision.source_end and decision.rule == 'different']
        for cut in decision.removed:
            chosen = cut
            reason = 'original_approved_seam'
            if relevant:
                w = relevant[0]
                near = [b for b in w.boundaries if cut.start-minimum < b.source_frame < cut.end+minimum]
                covered = w.frames.start <= cut.start-minimum and w.frames.end >= cut.end+minimum
                inside = [b for b in near if cut.start < b.source_frame < cut.end]
                safe = (covered and picture.request.layout == 'speaker_view' and len(near) == 1
                        and len(inside) == 1 and confidence(inside[0], fps, picture.request.layout) >= F(9, 10))
                if safe:
                    chosen = FrameRange(cut.start, inside[0].source_frame)
                    reason = 'seam_at_existing_stable_picture_restored_shared_silence'
                elif (covered and picture.request.layout == 'speaker_view' and len(near) == 1
                      and near[0].source_frame == cut.end and confidence(near[0], fps, picture.request.layout) >= F(9, 10)):
                    pass  # An already aligned seam needs no new timing decision.
                elif not covered or picture.request.layout != 'speaker_view' or near:
                    chosen = None
                    reason = 'handover_deletion_restored_uncertain_layout_coverage_or_flash'
            if chosen != cut:
                changed = True
                actions.append((frame_time(cut.end if chosen is None else chosen.end, fps), reason))
            if chosen is not None:
                allowed.append(chosen)
    result = base
    if changed:
        approvals = []
        for original in base.request.approvals:
            parts = [(max(original.start, frame_time(r.start, fps)), min(original.end, frame_time(r.end, fps))) for r in allowed]
            parts = [(a, b) for a, b in parts if a < b]
            approvals.extend(GapApproval(f'{original.approval_id}:s09:{i}', a, b, original.basis,
                                        original.evidence) for i, (a, b) in enumerate(parts))
        result = plan_pauses(base.plan.analysis, replace(base.request, approvals=tuple(approvals)))
        # Independent monotonicity check: every previously retained interval is
        # still retained. No new deletion, override/gain or analysis authority.
        if any(not result.plan.time_map.contains(frame_time(r.start, fps), frame_time(r.end, fps))
               for r in base.plan.time_map.retained):
            raise ValueError('Picture refinement attempted to enlarge a deletion.')
    mapping = result.plan.time_map
    markers = []
    def marker(kind, t, conf, reason):
        markers.append(PictureMarker(kind, t, mapping.map_time(t), conf, reason))
    for w in picture.windows:
        marker('picture_handover_review', w.handover, F(0),
               f'{picture.request.layout}; recorded picture identity unverified; original speech timing retained')
        for b in w.boundaries:
            t = frame_time(b.source_frame, fps)
            marker('probable_picture_boundary', t, confidence(b, fps, picture.request.layout),
                   'Recorded transition; speech-relative delay is uncertain/unavoidable, never independently retimed')
    for t, reason in actions:
        marker('picture_seam_review', t, F(0), reason)
    # Retain short/ambiguous activity as review metadata without picture splits.
    sources = {s.source_id: s for s in base.plan.analysis.sources}
    for e in base.plan.analysis.events:
        s = sources[e.source_id]
        if e.kind != 'speech' or F(e.end_sample-e.start_sample, s.sample_rate) < MIN_TURN or len(s.channel_labels) > 1:
            marker('picture_activity_kept', F(e.start_sample, s.sample_rate), F(0),
                   'Short/reaction/overlap/uncertain/shared-mic activity retained; no picture-follow rule')
    return loads(PictureRefinement, dumps(PictureRefinement(1, SEAM_ALGORITHM, digest(base), digest(picture),
                                  result, tuple(sorted(set(markers), key=lambda m: (m.source_time, m.kind, m.reason))))))
