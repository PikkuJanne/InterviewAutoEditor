"""Exact half-open source time; rounding only at named grid boundaries."""
from dataclasses import dataclass
from fractions import Fraction


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError('Expected an integer in range.')
    return value


def rational(value, positive=False):
    if not isinstance(value, Fraction) or (positive and value <= 0):
        raise ValueError('Expected exact rational time/rate.')
    return value


def floor(value):
    rational(value)
    return value.numerator // value.denominator


def ceil(value):
    return -floor(-value)


def frame_time(frame, fps):
    return Fraction(integer(frame), 1) / rational(fps, positive=True)


def sample_time(sample, rate):
    return Fraction(integer(sample), integer(rate, 1))


def sample_bounds(start, end, rate):
    """Outward protection rounding, independently from absolute bounds."""
    integer(rate, 1)
    if not Fraction(0) <= rational(start) < rational(end):
        raise ValueError('Invalid half-open time interval.')
    return floor(start * rate), ceil(end * rate)


def protected_frames(start, end, fps):
    rational(fps, positive=True)
    if not Fraction(0) <= rational(start) < rational(end):
        raise ValueError('Invalid protection interval.')
    return floor(start * fps), ceil(end * fps)


def removable_frames(start, end, fps):
    """Inward rounding cannot expand a removable gap into protected time."""
    protected_frames(start, end, fps)
    return ceil(start * fps), floor(end * fps)


@dataclass(frozen=True)
class FrameRange:
    start: int
    end: int

    def __post_init__(self):
        integer(self.start)
        integer(self.end, self.start + 1)

    @property
    def length(self):
        return self.end - self.start


@dataclass(frozen=True)
class SharedTimeMap:
    """One map for every track; full first/last handles are mandatory.

    Domain is the explicitly reconciled source frame extent, not a native
    sequence's potentially extra out frame. Source sample tails must be resolved
    by intake/plan validation before this map may authorize an export.
    """
    fps: Fraction
    source_frames: int
    retained: tuple[FrameRange, ...]

    def __post_init__(self):
        rational(self.fps, positive=True)
        integer(self.source_frames, 1)
        if not self.retained or self.retained[0].start != 0 or self.retained[-1].end != self.source_frames:
            raise ValueError('Full leading and trailing handles are required.')
        previous = -1
        for interval in self.retained:
            if interval.start <= previous or interval.end > self.source_frames:
                raise ValueError('Retained ranges must be ordered, disjoint and coalesced.')
            previous = interval.end

    @property
    def output_frames(self):
        return sum(r.length for r in self.retained)

    def segments(self):
        offset = 0
        for source in self.retained:
            yield source, FrameRange(offset, offset + source.length)
            offset += source.length

    def map_time(self, source_time):
        """Removed locations return None; the final endpoint maps exactly."""
        rational(source_time)
        if source_time == frame_time(self.source_frames, self.fps):
            return frame_time(self.output_frames, self.fps)
        for source, output in self.segments():
            a, b = frame_time(source.start, self.fps), frame_time(source.end, self.fps)
            if a <= source_time < b:
                return frame_time(output.start, self.fps) + source_time - a
        return None

    def contains(self, start, end):
        return any(frame_time(r.start, self.fps) <= start < end <= frame_time(r.end, self.fps)
                   for r in self.retained)
