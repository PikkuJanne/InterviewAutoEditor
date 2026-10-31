"""Explicit file identity, timing inventory and shared-origin review gates."""
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Literal

from . import __version__
from .adapters.compatibility import PLAN_TARGET
from .adapters.kdenlive import IntakeError, read_starter, resolve_resource
from .contracts import Analysis, Header, Source, text, to_data
from .offsets import OriginDiagnostic, diagnostic_windows
from .probe import VideoProbe, fingerprint, probe_video, probe_wav, tool_version
from .timing import frame_time


@dataclass(frozen=True)
class FileMapping:
    resource: str
    source_id: str
    display_name: str
    channel_labels: tuple[str, ...]

    def __post_init__(self):
        for v in (self.resource, self.source_id, self.display_name, *self.channel_labels):
            text(v)
        if not self.channel_labels or self.source_id == 'video':
            raise IntakeError('INVALID_PARTICIPANT_MAPPING')


@dataclass(frozen=True)
class MappingManifest:
    schema_version: Literal[1]
    participants: tuple[FileMapping, ...]
    relocations: tuple[tuple[str, str], ...]

    def __post_init__(self):
        if type(self.schema_version) is not int or self.schema_version != 1 or not self.participants:
            raise IntakeError('UNSUPPORTED_OR_EMPTY_MAPPING')
        if len({p.source_id for p in self.participants}) != len(self.participants) or len({p.display_name.strip().casefold() for p in self.participants}) != len(self.participants):
            raise IntakeError('DUPLICATE_PARTICIPANT_ID_OR_NAME')
        if len({k for k, v in self.relocations}) != len(self.relocations):
            raise IntakeError('DUPLICATE_RELOCATION')
        for pair in self.relocations:
            for v in pair:
                text(v)


@dataclass(frozen=True)
class Diagnostic:
    severity: Literal['error', 'review', 'info']
    code: str
    source_id: str


@dataclass(frozen=True)
class IntakeResult:
    analysis: Analysis  # Local/private: contains source content fingerprints.
    clip_frames: int
    sequence_frames: int
    excluded_mp4_audio: int
    tails: tuple[tuple[str, Fraction], ...]
    diagnostics: tuple[Diagnostic, ...]
    origins: tuple[tuple[str, OriginDiagnostic], ...]
    ffprobe_version: str
    ffmpeg_version: str | None
    video_probe: VideoProbe

    @property
    def ready(self):
        return not any(d.severity in ('error', 'review') for d in self.diagnostics)

    def summary(self):
        """No paths, names, arbitrary project strings or source fingerprints.

        IDs are user-supplied and therefore also replaced in this console/report
        view. Full local contracts must never be staged with real inputs.
        """
        ids = {s.source_id: f'source_{i:02d}' for i, s in enumerate(self.analysis.sources)}
        return {
            'schema_version': 1, 'compatibility': 'EXPERIMENTAL', 'ready': self.ready,
            'ffprobe_version': self.ffprobe_version, 'fps': to_data(self.analysis.fps),
            'ffmpeg_diagnostic_version': self.ffmpeg_version,
            'video_timestamp_audit': to_data(self.video_probe),
            'clip_frames': self.clip_frames, 'sequence_frames': self.sequence_frames,
            'sequence_extent_delta_frames': self.sequence_frames - self.clip_frames,
            'mp4_audio_output_policy': 'EXCLUDED_BY_S02_EXPORT_ADAPTER',
            'excluded_linked_mp4_audio_tracks': self.excluded_mp4_audio,
            'sources': [{'id': ids[s.source_id], 'kind': s.kind, 'sample_rate': s.sample_rate,
                         'sample_count': s.sample_count, 'duration': to_data(s.duration),
                         'origin_status': s.origin_status} for s in self.analysis.sources],
            'source_end_minus_clip_end': [{'id': ids[k], 'seconds': to_data(v)} for k, v in self.tails],
            'diagnostics': [{'severity': d.severity, 'code': d.code,
                             'source': ids.get(d.source_id, 'project')} for d in self.diagnostics],
            'origin_diagnostics': [{'id': ids[k], **to_data(v)} for k, v in self.origins],
            'source_repair_performed': False, 'export_performed': False,
        }


def inspect(project, mapping, ffprobe, *, mapping_base=None, ffmpeg=None, anchor_starts=(), allow_unc=False):
    anchor_starts = tuple(anchor_starts)
    if bool(ffmpeg) != bool(anchor_starts) or len(anchor_starts) > 32:
        raise IntakeError('DIAGNOSTIC_REQUIRES_FFMPEG_AND_ONE_TO_32_ANCHORS')
    relocations = dict(mapping.relocations)
    starter = read_starter(project, relocations, allow_unc)
    base = Path(mapping_base).resolve() if mapping_base else starter.path.parent
    records = {}
    for p in mapping.participants:
        path = resolve_resource(p.resource, base, allow_unc=allow_unc)
        if any(path.samefile(existing) for existing in records):
            raise IntakeError('DUPLICATE_PHYSICAL_PARTICIPANT_FILE')
        records[path] = p
    audios = [t for t in starter.tracks if t.audio]
    video = next(t for t in starter.tracks if not t.audio)
    if set(records) != {t.resource for t in audios}:
        raise IntakeError('MAPPING_MUST_MATCH_ALL_AND_ONLY_PARTICIPANT_FILES')
    if any(video.resource.samefile(p) for p in records):
        raise IntakeError('DUPLICATE_PHYSICAL_SOURCE')
    before = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in (*starter.resources, starter.path)}
    vp = probe_video(video.resource, ffprobe, video.stream_index)
    diagnostics = []
    if vp.cadence != 'CFR_AUDITED':
        diagnostics.append(Diagnostic('error', vp.cadence, 'video'))
    if vp.fps != starter.fps:
        diagnostics.append(Diagnostic('error', 'SOURCE_PROJECT_FRAME_RATE_MISMATCH', 'video'))
    if vp.start != 0:
        diagnostics.append(Diagnostic('error', 'NONZERO_VIDEO_TIMESTAMP_ORIGIN', 'video'))
    duration = frame_time(starter.clip_frames, starter.fps)
    sources = [Source('video', fingerprint(video.resource), 'video', 0, 0, vp.duration,
                      vp.start, Fraction(0) if vp.start == 0 and vp.cadence == 'CFR_AUDITED' else None,
                      'verified' if vp.start == 0 and vp.cadence == 'CFR_AUDITED' else 'unverified', ())]
    tails = [('video', vp.duration - duration)]
    origins = []
    for track in audios:
        record = records[track.resource]
        if track.stream_index != 0:
            raise IntakeError('PCM_WAV_REQUIRES_STREAM_ZERO')
        ap = probe_wav(track.resource)
        status = 'unverified'
        if ffmpeg and anchor_starts:
            # The selected diagnostic reference is the first embedded audio
            # stream; probe its actual index rather than presume index 1.
            from .probe import run_bounded
            import json
            md = json.loads(run_bounded([ffprobe, '-v', 'error', '-protocol_whitelist', 'file,pipe', '-i', video.resource,
                                        '-show_entries', 'stream=index,codec_type', '-of', 'json']))
            reference_audio = [s['index'] for s in md['streams'] if s['codec_type'] == 'audio']
            if len(reference_audio) != 1:
                raise IntakeError('AMBIGUOUS_OR_MISSING_REFERENCE_MIX')
            origin = diagnostic_windows(video.resource, track.resource, ffmpeg, anchor_starts,
                                        min(vp.duration, ap.duration), reference_audio[0], track.stream_index)
            origins.append((record.source_id, origin))
            if origin.status == 'OFFSET_DETECTED':
                status = 'offset_detected'
            elif origin.status == 'INCONSISTENT_LAGS_REVIEW_OFFSET_OR_DRIFT':
                status = 'inconsistent'
            # Correlation to a cleaned/mixed recording is diagnostic evidence,
            # not a full alignment certificate even when all peaks are zero.
            diagnostics.append(Diagnostic('review', origin.status, record.source_id))
        diagnostics.append(Diagnostic('review', 'SHARED_ORIGIN_NOT_CERTIFIED', record.source_id))
        sources.append(Source(record.source_id, fingerprint(track.resource), 'participant_audio',
                              ap.sample_rate, ap.sample_count, ap.duration, Fraction(0), None,
                              status, record.channel_labels))
        tails.append((record.source_id, ap.duration - duration))
    for source_id, delta in tails:
        if delta <= -1 / starter.fps:
            diagnostics.append(Diagnostic('error', 'SOURCE_TRUNCATED_BEFORE_CLIP_END', source_id))
        elif delta != 0:
            diagnostics.append(Diagnostic('review', 'SOURCE_TAIL_RECONCILIATION_REQUIRED', source_id))
    if starter.sequence_frames != starter.clip_frames:
        diagnostics.append(Diagnostic('info', 'OBSERVED_NATIVE_EXTRA_SEQUENCE_FRAME', 'video'))
    for p, signature in before.items():
        if (p.stat().st_size, p.stat().st_mtime_ns) != signature:
            raise IntakeError('SOURCE_CHANGED_DURING_INSPECTION')
    header = Header(1, 'intake', fingerprint(starter.path), __version__, PLAN_TARGET, (), ())
    analysis = Analysis(header, starter.fps, tuple(sources), (), (), ())
    return IntakeResult(analysis, starter.clip_frames, starter.sequence_frames, starter.excluded_mp4_audio,
                        tuple(tails), tuple(diagnostics), tuple(origins), tool_version(ffprobe),
                        tool_version(ffmpeg) if ffmpeg else None, vp)
