"""Ordinary editor choices, kept separate from detector/benchmark evidence."""
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
import os
import shutil
import wave

from .cancellation import checkpoint
from .contracts import text
from .intake import FileMapping, MappingManifest
from .planner import GapApproval, PlannerRequest, analysis_digest
from .timing import ceil, floor


@dataclass(frozen=True)
class Mute:
    source_id: str
    start: F
    end: F

    def __post_init__(self):
        text(self.source_id)
        if not isinstance(self.start, F) or not isinstance(self.end, F) or not 0 <= self.start < self.end:
            raise ValueError('Mute requires ordered original-source seconds.')


def local_asset(name):
    """Existing local assets only. Never download a model or guess a source."""
    root = Path(__file__).resolve().parents[1]
    defaults = {
        'ffprobe': ('IAE_FFPROBE', Path(os.environ.get('ProgramFiles', 'C:/Program Files'))/'Kdenlive/bin/ffprobe.exe'),
        'ffmpeg': ('IAE_FFMPEG', Path(os.environ.get('ProgramFiles', 'C:/Program Files'))/'Kdenlive/bin/ffmpeg.exe'),
        'speech_model': ('IAE_S04_MODEL', root/'.local/S04/silero_vad.onnx'),
        'reaction_model': ('IAE_S05_MODEL', root/'.local/S05/yamnet.tflite'),
        'cache': ('IAE_CACHE', root/'.local/editor-cache'),
    }
    env, default = defaults[name]
    return Path(os.environ.get(env) or (shutil.which(name) if name in ('ffprobe', 'ffmpeg') else '') or default).absolute()


def starter_mapping(starter):
    # File names identify tracks without inferring a person's identity.
    return MappingManifest(1, tuple(FileMapping(str(t.resource), f'participant_{i:02}',
        f'{i:02} {t.resource.stem}', (f'participant_{i:02}',))
        for i, t in enumerate(reversed([t for t in starter.tracks if t.audio]), 1)), ())


def ordinary_request(analysis, bindings, preset='tight'):
    """Only measured all-channel digital silence can authorize an automatic cut.

    Exact zero PCM is deliberately narrower than negative speech/reaction
    inference. These are program decisions, never independent quality labels.
    Existing protected events, handles and shared-map rules still constrain cuts.
    """
    quiet = None
    for source in analysis.sources:
        if source.kind != 'participant_audio':
            continue
        intervals, begin = [], None
        with wave.open(str(bindings[source.source_id]), 'rb') as pcm:
            if pcm.getsampwidth() == 1:  # unsigned PCM needs a different zero
                return PlannerRequest(2, analysis_digest(analysis), preset, (), ())
            count, rate = pcm.getnframes(), pcm.getframerate()
            for tick in range(ceil(F(count * 10, rate))):
                checkpoint()
                pos = tick * rate // 10
                stop = min(count, (tick + 1) * rate // 10)
                data = pcm.readframes(stop - pos)
                silent = bool(data) and not data.strip(b'\0')
                if silent and begin is None:
                    begin = F(pos, rate)
                if not silent and begin is not None:
                    intervals.append((begin, F(pos, rate)))
                    begin = None
            if begin is not None:
                intervals.append((begin, source.duration))
        if quiet is None:
            quiet = intervals
        else:
            # Linear intersection of ordered, disjoint original-clock spans.
            common, i, j = [], 0, 0
            while i < len(quiet) and j < len(intervals):
                a, b = max(quiet[i][0], intervals[j][0]), min(quiet[i][1], intervals[j][1])
                if a < b:
                    common.append((a, b))
                if quiet[i][1] < intervals[j][1]:
                    i += 1
                else:
                    j += 1
            quiet = common
    approvals = tuple(GapApproval(f'pcm-zero-{i}', a, b, 'digital_silence',
        'All original participant PCM channels are exactly zero; not an independent annotation.')
        for i, (a, b) in enumerate(quiet or ()) if b - a > F(3, 2))
    return PlannerRequest(2, analysis_digest(analysis), preset, approvals, ())


def validate_mutes(analysis, mutes):
    sources = {s.source_id: s for s in analysis.sources if s.kind == 'participant_audio'}
    previous = {}
    for mute in sorted(mutes, key=lambda m: (m.source_id, m.start)):
        source = sources.get(mute.source_id)
        if source is None or mute.end > source.duration:
            raise ValueError('Mute participant or original-source bounds do not resolve.')
        if ceil(mute.start * analysis.fps) + 4 > floor(mute.end * analysis.fps):
            raise ValueError('Mute needs at least four project frames for silent interior and edge fades.')
        if mute.start <= previous.get(mute.source_id, F(-1)):
            raise ValueError('Mute ranges must be disjoint with a gap between them.')
        previous[mute.source_id] = mute.end


def mute_keys(mutes, identity, begin, end, fps):
    # MLT dB keyframes plus its sample interpolation: -1000 dB rounds to exact
    # zero at supported PCM depths. One-frame edge fades are inside the bounds.
    spans = [(ceil(m.start*fps), floor(m.end*fps)) for m in mutes if m.source_id == identity]
    if not any(a < end and b > begin for a, b in spans):
        return ()
    def level(frame):
        return -1000 if any(a < frame < b-1 for a, b in spans) else 0
    keys = {begin: level(begin), end-1: level(end-1)}
    for a, b in spans:
        # The native filter interpolates from the previous frame's gain. Unity
        # at b-1 therefore finishes the audible fade at b, inside the request.
        for frame, db in ((a, 0), (a+1, -1000), (b-2, -1000), (b-1, 0)):
            if begin <= frame < end:
                keys[frame] = db
    return tuple(sorted(keys.items()))
