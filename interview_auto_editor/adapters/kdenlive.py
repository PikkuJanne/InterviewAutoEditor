"""Read-only, fail-closed intake of the observed simple document-1.1 family.

Fractional millisecond serialization is recovered only when uniquely within
half a millisecond of a project frame. This is parser coverage, not GUI proof.
"""
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .compatibility import ADAPTER_ID, select_adapter

MAX_XML = 8 * 1024 * 1024


class IntakeError(ValueError):
    """Stable diagnostic code; never includes project text or private paths."""


def props(node):
    return {p.get('name'): p.text or '' for p in node.findall('property')}


def xml_frames(value, fps):
    if isinstance(value, str) and re.fullmatch(r'\d+', value):
        return int(value)
    if not isinstance(value, str) or not re.fullmatch(r'\d+:[0-5]\d:[0-5]\d\.\d{3}', value):
        raise IntakeError('UNSUPPORTED_TIME_REPRESENTATION')
    h, m, s = map(Fraction, value.split(':'))
    seconds = h * 3600 + m * 60 + s
    position = seconds * fps
    candidate = (position + Fraction(1, 2)).numerator // (position + Fraction(1, 2)).denominator
    if abs(Fraction(candidate, 1) / fps - seconds) > Fraction(1, 2000) or fps >= 1000:
        raise IntakeError('AMBIGUOUS_FRAME_SERIALIZATION')
    return candidate


def resolve_resource(value, base, relocations=None, allow_unc=False):
    """Relinking is explicit, exact-reference based and read-only."""
    value = (relocations or {}).get(value, value)
    if not isinstance(value, str) or not value or '\x00' in value:
        raise IntakeError('INVALID_MEDIA_REFERENCE')
    if re.match(r'^[A-Za-z][\w+.-]*:', value) and not re.match(r'^[A-Za-z]:[/\\]', value):
        raise IntakeError('NONLOCAL_MEDIA_REFERENCE')
    if value.startswith(('\\\\', '//')) and not allow_unc:
        raise IntakeError('UNC_REQUIRES_EXPLICIT_OPT_IN_UNTESTED')
    path = Path(value)
    # Drive-relative Windows forms must never use the process's drive cwd.
    if re.match(r'^[A-Za-z]:[^/\\]', value):
        raise IntakeError('DRIVE_RELATIVE_MEDIA_REFERENCE')
    path = (path if path.is_absolute() else base / path).resolve()
    if str(path).startswith(('\\\\', '//')) and not allow_unc:
        raise IntakeError('UNC_REQUIRES_EXPLICIT_OPT_IN_UNTESTED')
    if not path.is_file():
        error = IntakeError('UNRESOLVED_MEDIA_REFERENCE')
        error.affected_input = path
        raise error
    return path


@dataclass(frozen=True)
class Track:
    resource: Path
    audio: bool
    end_frame: int
    stream_index: int


@dataclass(frozen=True)
class Starter:
    path: Path
    fps: Fraction
    clip_frames: int
    sequence_frames: int
    tracks: tuple[Track, ...]
    excluded_mp4_audio: int
    resources: tuple[Path, ...]
    compatibility: str = 'EXPERIMENTAL'
    profile_reference: str | None = None
    writer_version: str = '26.08.2'
    document_version: str = '1.1'
    adapter_id: str = ADAPTER_ID


def read_starter(project, relocations=None, allow_unc=False):
    path = Path(project).resolve()
    try:
        with path.open('rb') as stream:
            raw = stream.read(MAX_XML + 1)
        # Decode first; reject UTF-16/32 and declaration tricks that could bypass
        # byte searches. No DTD/entity processing or project-supplied execution.
        text = raw.decode('utf-8-sig')
        if len(raw) > MAX_XML or '\x00' in text or re.search(r'<!\s*(?:DOCTYPE|ENTITY)\b', text, re.I):
            raise IntakeError('UNSAFE_XML')
        root = ET.fromstring(text)
    except (UnicodeError, ET.ParseError, OSError) as exc:
        raise IntakeError('PROJECT_READ_FAILED') from exc
    if root.tag != 'mlt' or any(n.tag not in ('profile', 'producer', 'chain', 'playlist', 'tractor') for n in root):
        raise IntakeError('UNKNOWN_PROJECT_STRUCTURE')
    if len(list(root.iter())) > 100000:
        raise IntakeError('XML_NODE_LIMIT')
    def depth(node, level=0):
        if level > 32:
            raise IntakeError('XML_DEPTH_LIMIT')
        for child in node:
            depth(child, level + 1)
    depth(root)
    ids = [n.get('id') for n in root.iter() if n.get('id')]
    if len(ids) != len(set(ids)):
        raise IntakeError('DUPLICATE_XML_ID')
    allowed = {'mlt', 'profile', 'producer', 'chain', 'playlist', 'tractor', 'track', 'entry', 'property', 'filter', 'transition'}
    child_tags = {'mlt': {'profile', 'producer', 'chain', 'playlist', 'tractor'},
                  'profile': set(), 'producer': {'property'}, 'chain': {'property'},
                  'playlist': {'property', 'entry'}, 'entry': {'property'},
                  'property': set(), 'filter': {'property'}, 'transition': {'property'},
                  'tractor': {'property', 'track', 'filter', 'transition'}, 'track': set()}
    attributes = {'mlt': {'LC_NUMERIC', 'producer', 'version', 'root'},
        'profile': {'colorspace', 'description', 'display_aspect_den', 'display_aspect_num',
            'frame_rate_den', 'frame_rate_num', 'height', 'progressive',
            'sample_aspect_den', 'sample_aspect_num', 'width'},
        'producer': {'id', 'in', 'out'}, 'chain': {'id', 'in', 'out'},
        'playlist': {'id'}, 'entry': {'in', 'out', 'producer'},
        'tractor': {'id', 'in', 'out'}, 'track': {'hide', 'in', 'out', 'producer'},
        'filter': {'id', 'in', 'out'}, 'transition': {'id', 'in', 'out'}, 'property': {'name'}}
    for n in root.iter():
        names = [p.get('name') for p in n.findall('property')]
        if n.tag not in allowed or len(names) != len(set(names)):
            raise IntakeError('UNKNOWN_OR_DUPLICATE_XML_STRUCTURE')
        if any(child.tag not in child_tags[n.tag] for child in n):
            raise IntakeError('UNSUPPORTED_XML_NESTING_OR_PROCESSING')
        if any(k in n.attrib for k in ('speed', 'warp_speed')):
            raise IntakeError('SOURCE_RETIMING_UNSUPPORTED')
        if set(n.attrib) - attributes[n.tag]:
            raise IntakeError('UNKNOWN_XML_ATTRIBUTE')
    nodes = {n.get('id'): n for n in root if n.get('id')}
    for n in root.iter():
        if n.tag in ('track', 'entry') and n.get('producer') not in nodes:
            raise IntakeError('UNRESOLVED_PRODUCER')
    bins = [n for n in root.findall('playlist') if n.get('id') == 'main_bin']
    if len(bins) != 1:
        raise IntakeError('EXPECTED_MAIN_BIN')
    bp = props(bins[0])
    writer = bp.get('kdenlive:docproperties.kdenliveversion')
    document = bp.get('kdenlive:docproperties.version')
    if select_adapter(writer, document) is None:
        raise IntakeError('NO_RECOGNIZED_STRUCTURE_ADAPTER')
    if len(root.findall('profile')) != 1:
        raise IntakeError('EXPECTED_SINGLE_PROFILE')
    try:
        p = root.find('profile')
        num, den = int(p.get('frame_rate_num')), int(p.get('frame_rate_den'))
        if num <= 0 or den <= 0:
            raise ValueError()
        fps = Fraction(num, den)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise IntakeError('INVALID_FRAME_RATE') from exc
    base = Path(root.get('root', str(path.parent)))
    if not base.is_absolute():
        raise IntakeError('AMBIGUOUS_PROJECT_ROOT')
    resources = set()
    for chain in root.findall('chain'):
        cp = props(chain)
        if cp.get('mlt_service') not in ('avformat', 'avformat-novalidate') or chain.findall('filter') or any(k.startswith('warp_') for k in cp):
            raise IntakeError('SOURCE_PROCESSING_UNSUPPORTED')
        if cp.get('kdenlive:proxy', '-') not in ('', '-'):
            raise IntakeError('PROXY_SOURCE_UNSUPPORTED')
        if any(cp.get(key, '0') not in ('', '0', '0.0') for key in ('force_fps', 'video_delay', 'audio_delay')):
            raise IntakeError('SOURCE_TIMING_OVERRIDE_UNSUPPORTED')
        resources.add(resolve_resource(cp.get('resource'), base, relocations, allow_unc))
    seqs = [n for n in root.findall('tractor') if 'kdenlive:sequenceproperties.groups' in props(n)]
    if len(seqs) != 1:
        raise IntakeError('NESTED_OR_MULTIPLE_SEQUENCES')
    seq = seqs[0]
    refs = seq.findall('track')
    if not refs or props(nodes[refs[0].get('producer')]).get('resource') != 'black' or props(nodes[refs[0].get('producer')]).get('mlt_service') != 'color':
        raise IntakeError('EXPECTED_NATIVE_BACKGROUND')
    background = nodes[refs[0].get('producer')]
    if any(n is not background for n in root.findall('producer')) or background.findall('filter') or background.findall('link'):
        raise IntakeError('UNSUPPORTED_EXTRA_PRODUCER')
    for n in (seq, *(nodes[r.get('producer')] for r in refs[1:]), *root.findall('chain')):
        if n.get('in') is not None and xml_frames(n.get('in'), fps) != 0:
            raise IntakeError('NONZERO_CONTAINER_SOURCE_ORIGIN')
    for ref in refs:
        if ref.get('hide') not in (None, '') or (ref.get('in') is not None and xml_frames(ref.get('in'), fps) != 0):
            raise IntakeError('SEQUENCE_TRACK_ROUTING_OR_OFFSET')
    wrappers = [n for n in root.findall('tractor') if props(n).get('kdenlive:projectTractor') == '1']
    if len(wrappers) != 1 or len(wrappers[0].findall('track')) != 1 or wrappers[0].find('track').get('producer') != seq.get('id'):
        raise IntakeError('UNSUPPORTED_PROJECT_WRAPPER')
    known_tractors = {seq.get('id'), wrappers[0].get('id'), *(r.get('producer') for r in refs[1:])}
    if any(n.get('id') not in known_tractors for n in root.findall('tractor')):
        raise IntakeError('UNCONNECTED_OR_NESTED_TRACKS')
    for n in (wrappers[0], wrappers[0].find('track')):
        if n.get('in') is not None and xml_frames(n.get('in'), fps) != 0:
            raise IntakeError('NONZERO_PROJECT_WRAPPER_ORIGIN')
        if n.get('hide') not in (None, '') or n.findall('filter') or n.findall('transition'):
            raise IntakeError('PROJECT_WRAPPER_PROCESSING_UNSUPPORTED')
    for parent in (seq, *(nodes[r.get('producer')] for r in refs[1:])):
        if any(props(f).get('internal_added') != '237' or props(f).get('disable') != '1' for f in parent.findall('filter')):
            raise IntakeError('ACTIVE_EFFECTS_UNSUPPORTED')
    for transition in seq.findall('transition'):
        tp = props(transition)
        if tp.get('internal_added') != '237' or tp.get('mlt_service') not in ('mix', 'qtblend'):
            raise IntakeError('CUSTOM_TRANSITION_UNSUPPORTED')
    tracks, linked = [], []
    for ref in refs[1:]:
        node = nodes[ref.get('producer')]
        children = node.findall('track')
        audio = props(node).get('kdenlive:audio_track') == '1'
        if node.tag != 'tractor' or len(children) != 2 or any(nodes[c.get('producer')].tag != 'playlist' or c.get('hide') != ('video' if audio else 'audio') for c in children):
            raise IntakeError('UNSUPPORTED_TRACK_ROUTING')
        if any((c.get('in') is not None and xml_frames(c.get('in'), fps) != 0)
               or c.get('out') is not None for c in children):
            raise IntakeError('TRACK_PLAYLIST_OFFSET_OR_CROP_UNSUPPORTED')
        items = [e for c in children for e in nodes[c.get('producer')] if e.tag != 'property']
        if not items:
            continue
        if len(items) != 1 or items[0].tag != 'entry':
            raise IntakeError('EDITED_OR_SHIFTED_STARTER')
        e = items[0]
        if xml_frames(e.get('in'), fps) != 0 or list(e.findall('filter')) or list(e.findall('transition')):
            raise IntakeError('EDITED_OR_SHIFTED_STARTER')
        chain = nodes[e.get('producer')]
        cp = props(chain)
        if chain.tag != 'chain':
            raise IntakeError('NESTED_SOURCE_UNSUPPORTED')
        key = 'audio_index' if audio else 'video_index'
        try:
            index = int(cp.get(key, '-1'))
        except ValueError as exc:
            raise IntakeError('INVALID_STREAM_SELECTION') from exc
        if index < 0 or cp.get('set.test_audio' if audio else 'set.test_image') != '0':
            raise IntakeError('DISABLED_REQUIRED_STREAM')
        resource = resolve_resource(cp.get('resource'), base, relocations, allow_unc)
        end = xml_frames(e.get('out'), fps) + 1
        t = Track(resource, audio, end, index)
        if audio and resource.suffix.lower() == '.mp4':
            linked.append(t)
        else:
            if resource.suffix.lower() != ('.wav' if audio else '.mp4'):
                raise IntakeError('EXPECTED_MP4_AND_CLEANED_WAV')
            tracks.append(t)
    videos = [t for t in tracks if not t.audio]
    if len(videos) != 1 or not any(t.audio for t in tracks):
        raise IntakeError('EXPECTED_ONE_VIDEO_AND_PARTICIPANTS')
    if len({t.resource for t in tracks}) != len(tracks) or any(t.resource != videos[0].resource for t in linked):
        raise IntakeError('DUPLICATE_OR_UNEXPECTED_SOURCE')
    end = videos[0].end_frame
    if any(t.end_frame != end for t in tracks + linked):
        raise IntakeError('UNEQUAL_CLIP_GRID_COVERAGE')
    seq_end = xml_frames(seq.get('out'), fps) + 1
    if seq_end not in (end, end + 1):
        raise IntakeError('UNEXPLAINED_SEQUENCE_EXTENT')
    for node in (wrappers[0], wrappers[0].find('track'), *(nodes[r.get('producer')] for r in refs[1:])):
        if node.get('out') is not None and xml_frames(node.get('out'), fps) + 1 not in (end, end + 1):
            raise IntakeError('UNEXPLAINED_TRACK_OR_WRAPPER_EXTENT')
    if any(ref.get('out') is not None and xml_frames(ref.get('out'), fps) + 1 != end for ref in refs[1:]):
        raise IntakeError('SEQUENCE_TRACK_CROP_UNSUPPORTED')
    return Starter(path, fps, end, seq_end, tuple(tracks), len(linked), tuple(sorted(resources)),
                   profile_reference=bp.get('kdenlive:docproperties.profile') or None,
                   writer_version=writer, document_version=document)
