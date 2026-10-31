"""S10 application service. Private recoverable runs; unchanged S03-S09 policy.

Only a complete, validated staging directory is renamed to the requested new
destination. Failed/cancelled attempts and completed caches remain local.
"""
from contextlib import contextmanager
from dataclasses import dataclass, replace
import hashlib
import json
import os
from pathlib import Path
import platform
from typing import Literal
import uuid

from . import __version__
from .adapters.export import export_project
from .adapters.kdenlive import read_starter, resolve_resource
from .cancellation import Cancelled, checkpoint, scope
from .cleanup import CleanupRequest, build_cleanup
from .contracts import Analysis, dumps, loads, to_data
from .intake import MappingManifest, inspect
from .picture import PictureAnalysis, PictureRequest, analyze_picture, refine_picture_seams, validate_picture, coverage_report
from .planner import PlannerRequest, analysis_digest, explain, plan_pauses
from .probe import fingerprint, tool_version
from .reactions import YamnetCPU, analyze as reaction_analyze
from .speech import SileroCPU, SpeechError, atomic_new, analyze as speech_analyze
from .turns import build_turns


SERVICE = 's10-recoverable-cli-1'
LIMIT = 8 * 1024 * 1024
ARTIFACTS = frozenset(('inputs.json', 'intake.json', 'analysis.json',
    'analysis-report.json', 'planner-request.json', 'planning-result.json',
    'picture-analysis.json', 'picture-refinement.json', 'refined-planning-result.json',
    'cleanup-result.json', 'edit-plan.json', 'project.kdenlive', 'report.json'))


class RunError(ValueError):
    """Fixed public-safe diagnostic, never raw paths, content or source hashes."""


@dataclass(frozen=True)
class Artifact:
    name: str
    sha256: str

    def __post_init__(self):
        if self.name not in ARTIFACTS or len(self.sha256) != 64 or any(c not in '0123456789abcdef' for c in self.sha256):
            raise RunError('INVALID_RUN_ARTIFACT')


@dataclass(frozen=True)
class RunManifest:
    schema_version: Literal[1]
    service: Literal['s10-recoverable-cli-1']
    identity_sha256: str
    command: Literal['inspect', 'analyze', 'plan', 'export', 'run']
    state: Literal['building', 'failed', 'cancelled', 'complete']
    attempt: int
    stage: str
    artifacts: tuple[Artifact, ...]
    failure_code: Literal['NONE', 'FAILED', 'CANCELLED']

    def __post_init__(self):
        if self.attempt < 1 or self.stage not in ('starting', 'inspecting', 'analyzing',
                'planning', 'exporting', 'reporting', 'finalizing'):
            raise RunError('INVALID_RUN_STATE')
        if len({a.name for a in self.artifacts}) != len(self.artifacts):
            raise RunError('DUPLICATE_RUN_ARTIFACT')
        Artifact('inputs.json', self.identity_sha256)


@dataclass(frozen=True)
class RunOptions:
    command: str
    project: Path
    mapping: Path
    ffprobe: Path
    output: Path
    analysis: Path | None = None
    request: Path | None = None
    picture: Path | None = None
    picture_request: Path | None = None
    cleanup_request: Path | None = None
    preset: str | None = None
    ffmpeg: Path | None = None
    speech_model: Path | None = None
    reaction_model: Path | None = None
    cache: Path | None = None
    experimental: bool = False


def read_record(cls, path):
    with Path(path).open(encoding='utf-8-sig') as stream:
        return loads(cls, stream.read(LIMIT + 1))


def json_text(value):
    return json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n'


def _validate_reused_summary(path, current):
    """Only cache-hit counters may differ after a crash or a resumed attempt."""
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise RunError('RUN_SUMMARY_DUPLICATE_FIELD')
            result[key] = value
        return result
    with path.open(encoding='utf-8') as stream:
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise RunError('RUN_ARTIFACT_NAME_OR_SIZE_LIMIT')
    saved = json.loads(raw, object_pairs_hook=unique)
    expected = json.loads(json_text(current))
    if not isinstance(saved, dict):
        raise RunError('RUN_SUMMARY_CONFLICT')
    for layer in ('speech', 'reactions'):
        if layer in expected:
            for summary in (saved, expected):
                item = summary.get(layer)
                if not isinstance(item, dict):
                    raise RunError('RUN_SUMMARY_CONFLICT')
                hits = item.pop('cache_hits', None)
                if type(hits) is not int or not 0 <= hits <= len(expected[layer]['tracks']):
                    raise RunError('RUN_SUMMARY_CONFLICT')
    if json.dumps(saved, sort_keys=True, allow_nan=False) != json.dumps(expected, sort_keys=True, allow_nan=False):
        raise RunError('RUN_SUMMARY_CONFLICT')


def _replace_manifest(path, manifest):
    """Only this service's owned journal is replaceable; all artifacts exclusive."""
    # Scratch is outside the staged bundle: abrupt process death cannot leave
    # an untracked temporary file inside the eventually published directory.
    temporary = path.parent.parent / ('.iae-journal-' + uuid.uuid4().hex)
    try:
        atomic_new(temporary, dumps(manifest))
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _rename_new(source, destination):
    """Atomic directory publication with no replacement, including empty dirs."""
    if os.name == 'nt':
        os.rename(source, destination)  # Windows refuses any existing target.
    elif platform.system() == 'Linux':
        import ctypes
        libc = ctypes.CDLL(None, use_errno=True)
        rename = getattr(libc, 'renameat2', None)
        if rename is None:
            raise RunError('ATOMIC_DIRECTORY_PUBLICATION_UNAVAILABLE')
        if rename(-100, os.fsencode(source), -100, os.fsencode(destination), 1):
            error = ctypes.get_errno()
            raise OSError(error, 'Atomic new-directory publication failed.')
    else:
        raise RunError('ATOMIC_DIRECTORY_PUBLICATION_UNAVAILABLE')


@contextmanager
def _run_lock(path):
    """OS advisory lock releases even on process death; marker is never unlinked.

    Keeping the inode avoids the unlink/recreate race between waiting processes.
    A stale marker is harmless. No PID guessing or forced lock removal is needed.
    """
    if path.is_symlink():
        raise RunError('RUN_LOCK_CONFLICT')
    try:
        atomic_new(path, 'IAE-S10-LOCK\n')
    except FileExistsError:
        pass
    with path.open('r+b') as stream:
        if stream.read(32) != b'IAE-S10-LOCK\n':
            raise RunError('RUN_LOCK_CONFLICT')
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise RunError('RUN_BUSY') from None
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


class Journal:
    def __init__(self, directory, command, identity, resume):
        self.directory = directory
        self.path = directory / 'manifest.json'
        if resume:
            self.manifest = read_record(RunManifest, self.path)
            if self.manifest.identity_sha256 != identity or self.manifest.command != command:
                raise RunError('RESUME_INPUTS_CHANGED_USE_NEW_RUN')
            self.verify()
            self.manifest = replace(self.manifest, state='building', failure_code='NONE',
                                    attempt=self.manifest.attempt + 1)
        else:
            directory.mkdir()  # exclusive, no adoption of an unrelated directory
            self.manifest = RunManifest(1, SERVICE, identity, command, 'building', 1,
                                        'starting', (), 'NONE')
        self.save()

    def verify(self):
        if self.directory.is_symlink():
            raise RunError('RUN_SYMLINK_REFUSED')
        if any(p.name not in ARTIFACTS | {'manifest.json'} for p in self.directory.iterdir()):
            raise RunError('UNRECOGNIZED_STAGING_FILE_INSPECT_PRIVATELY')
        for artifact in self.manifest.artifacts:
            p = self.directory / artifact.name
            if p.is_symlink() or not p.is_file() or fingerprint(p) != artifact.sha256:
                raise RunError('RUN_ARTIFACT_CHANGED_OR_MISSING')

    def save(self, **changes):
        self.manifest = replace(self.manifest, **changes)
        _replace_manifest(self.path, self.manifest)

    def record(self, name):
        artifact = Artifact(name, fingerprint(self.directory / name))
        previous = next((a for a in self.manifest.artifacts if a.name == name), None)
        if previous is not None and previous != artifact:
            raise RunError('RUN_ARTIFACT_CHANGED')
        if previous is None:
            self.save(artifacts=self.manifest.artifacts + (artifact,))

    def write(self, name, content):
        # A crash between publication and journal update leaves an orphan. Only
        # exact deterministic reproduction may adopt it; never overwrite it.
        path = self.directory / name
        encoded = content.encode('utf-8')
        if name not in ARTIFACTS or len(encoded) > LIMIT:
            raise RunError('RUN_ARTIFACT_NAME_OR_SIZE_LIMIT')
        if path.exists():
            if path.is_symlink() or path.stat().st_size != len(encoded) or path.read_bytes() != encoded:
                raise RunError('RUN_ARTIFACT_CONFLICT')
        else:
            temporary = self.directory.parent / ('.iae-artifact-' + uuid.uuid4().hex)
            try:
                atomic_new(temporary, content)
                os.link(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)
        self.record(name)


class Application:
    """Shared callable API for the CLI and a future thin UI. No UI policy."""

    def __init__(self, cancel=lambda: False, progress=lambda stage: None):
        self.cancel = cancel
        self.progress = progress

    def inspect(self, options, mapping):
        return inspect(options.project, mapping, options.ffprobe, mapping_base=options.mapping.parent)

    def analyze(self, options, intake, paths):
        if not all((options.speech_model, options.reaction_model, options.ffmpeg, options.cache)):
            raise RunError('ANALYSIS_REQUIRES_LOCAL_MODELS_TOOLS_CACHE')
        # Both mandatory before media inference, on hits and resumed runs too.
        SileroCPU(options.speech_model)
        YamnetCPU(options.reaction_model)
        speech = speech_analyze(intake, paths, options.speech_model, options.ffmpeg,
                                options.cache / 'speech', cancel=self.cancel)
        fused = reaction_analyze(speech, paths, options.reaction_model, options.ffmpeg,
                                options.cache / 'reactions', cancel=self.cancel)
        return fused.analysis, fused.summary()

    def plan(self, analysis, request, picture=None, cleanup_request=None):
        base = plan_pauses(analysis, request)
        refinement = refine_picture_seams(base, picture) if picture else None
        result = refinement.result if refinement else base
        # Never rebind a stale approval silently. Caller supplies a request bound
        # to this exact refined result, as S08/S09 require.
        cleanup = build_cleanup(result, cleanup_request) if cleanup_request else None
        layout = build_turns(result)
        return base, result, refinement, cleanup, layout

    def export(self, options, base, bindings, names, output, picture=None, cleanup=None):
        return export_project(base, options.project, bindings, names, output,
                              options.ffprobe, experimental=options.experimental,
                              picture=picture, cleanup=cleanup)

    def compatibility_probe(self, project):
        # This is structural probing, not a claim about the installed binary.
        try:
            starter = read_starter(project)
        except (OSError, ValueError, TypeError, KeyError, StopIteration):
            return {'schema_version': 1, 'compatibility': 'UNSUPPORTED',
                    'reason': 'STARTER_OR_MEDIA_NOT_SUPPORTED', 'export_allowed': False,
                    'actual_application_test_performed': False}
        return {'schema_version': 1, 'compatibility': starter.compatibility,
                'adapter': '26.08.2', 'experimental_opt_in_required': True,
                'actual_application_test_performed': False,
                'installed_build_verified': False, 'fps': to_data(starter.fps)}

    @staticmethod
    def report(directory):
        directory = Path(directory).absolute()
        if directory.is_symlink():
            raise RunError('RUN_SYMLINK_REFUSED')
        manifest = read_record(RunManifest, directory / 'manifest.json')
        names = {a.name for a in manifest.artifacts}
        if manifest.state == 'complete':
            required = {'inputs.json', 'intake.json', 'report.json'}
            if manifest.command != 'inspect':
                required |= {'analysis.json', 'analysis-report.json'}
            if manifest.command in ('plan', 'export', 'run'):
                required |= {'planner-request.json', 'planning-result.json', 'edit-plan.json'}
            if manifest.command in ('export', 'run'):
                required.add('project.kdenlive')
            if not required <= names:
                raise RunError('INCOMPLETE_RUN_MANIFEST')
        if any(a.name == 'inputs.json' and a.sha256 != manifest.identity_sha256 for a in manifest.artifacts):
            raise RunError('RUN_IDENTITY_MISMATCH')
        for artifact in manifest.artifacts:
            p = directory / artifact.name
            if p.is_symlink() or fingerprint(p) != artifact.sha256:
                raise RunError('RUN_ARTIFACT_CHANGED_OR_MISSING')
        # A crash after journal commit but before rename is still incomplete.
        if directory.name.endswith('.incomplete') and manifest.state == 'complete':
            manifest = replace(manifest, state='building', stage='finalizing')
        return manifest

    def _inputs(self, options):
        names = ('project', 'mapping', 'analysis', 'request', 'picture', 'picture_request',
                 'cleanup_request', 'ffprobe', 'ffmpeg', 'speech_model', 'reaction_model')
        files = {name: {'path': str(Path(value).resolve()), 'sha256': fingerprint(value)}
                 for name in names if (value := getattr(options, name)) is not None}
        root = Path(__file__).parent
        implementation = {p.relative_to(root).as_posix(): fingerprint(p)
                          for p in sorted(root.rglob('*.py'))}
        return {'schema_version': 1, 'service': SERVICE, 'tool_version': __version__,
                'python': platform.python_version(), 'platform': platform.platform(),
                'command': options.command, 'preset': options.preset,
                'experimental': options.experimental, 'files': files,
                'cache': str(options.cache.resolve()) if options.cache else None,
                'implementation': implementation, 'privacy': 'PRIVATE_LOCAL_ONLY'}

    @staticmethod
    def _validate_analysis(analysis, intake):
        if (analysis.header.project_sha256 != intake.analysis.header.project_sha256 or
                analysis.header.adapter_target != intake.analysis.header.adapter_target or
                analysis.fps != intake.analysis.fps or len(analysis.sources) != len(intake.analysis.sources)):
            raise RunError('SAVED_ANALYSIS_PROJECT_MISMATCH')
        for saved, current in zip(analysis.sources, intake.analysis.sources):
            # A supplied reviewed record may already carry explicit verified-zero
            # origins. The service never upgrades origins in freshly analyzed data.
            if replace(saved, origin_status=current.origin_status,
                       verified_offset=current.verified_offset) != current:
                raise RunError('SAVED_ANALYSIS_SOURCE_MISMATCH')

    def run(self, options, *, resume=False):
        if options.command not in ('inspect', 'analyze', 'plan', 'export', 'run'):
            raise RunError('UNKNOWN_COMMAND')
        if options.picture and options.picture_request:
            raise RunError('CHOOSE_SAVED_PICTURE_OR_REQUEST')
        if options.preset not in (None, 'tight', 'gentle'):
            raise RunError('UNKNOWN_PRESET')
        if options.command in ('plan', 'export') and not options.analysis:
            raise RunError('SAVED_ANALYSIS_REQUIRED')
        final = Path(options.output).absolute()
        if final.name.startswith('.'):
            raise RunError('FINAL_RUN_NAME_MUST_NOT_BE_HIDDEN')
        partial = final.with_name('.' + final.name + '.incomplete')
        if final.is_symlink() or partial.is_symlink():
            raise RunError('RUN_SYMLINK_REFUSED')
        final.parent.mkdir(parents=True, exist_ok=True)
        with _run_lock(final.with_name('.' + final.name + '.lock')):
            if final.exists():
                raise RunError('RUN_ALREADY_EXISTS_USE_NEW_DESTINATION')
            if partial.exists() != resume:
                raise RunError('EXPLICIT_RESUME_REQUIRED_OR_NO_PARTIAL_RUN')
            journal = None
            try:
                # No cancelling during the very short journal/failure bookkeeping.
                with scope(self.cancel):
                    inputs = self._inputs(options)
                    mapping = read_record(MappingManifest, options.mapping)
                    if mapping.relocations:
                        raise RunError('RELOCATION_EXPORT_UNSUPPORTED_USE_EXPLICIT_MAPPING')
                    starter = read_starter(options.project)
                    bindings = {p.source_id: resolve_resource(p.resource, options.mapping.parent)
                                for p in mapping.participants}
                    bindings['video'] = next(t.resource for t in starter.tracks if not t.audio)
                    inputs['sources'] = {k: {'path': str(p), 'sha256': fingerprint(p)}
                                         for k, p in bindings.items()}
                    inputs['ffprobe_version'] = tool_version(options.ffprobe)
                    if options.ffmpeg:
                        inputs['ffmpeg_version'] = tool_version(options.ffmpeg)
                identity = hashlib.sha256(json_text(inputs).encode('utf-8')).hexdigest()
                journal = Journal(partial, options.command, identity, resume)
                journal.write('inputs.json', json_text(inputs))

                def stage(name):
                    checkpoint()
                    journal.save(stage=name)
                    self.progress(name)  # fixed stage strings only
                    checkpoint()

                with scope(self.cancel):
                    stage('inspecting')
                    intake = self.inspect(options, mapping)
                    journal.write('intake.json', json_text(intake.summary()))
                    report = {'schema_version': 1, 'privacy': 'PRIVATE_LOCAL_ONLY',
                              'compatibility': 'EXPERIMENTAL', 'intake': intake.summary(),
                              'restore': 'Replan with source-time keep/audible; remove global approvals for identity time; remove idle approvals for unity. Export to a NEW run. Bin originals remain recoverable.'}
                    if options.command != 'inspect':
                        stage('analyzing')
                        if options.analysis:
                            analysis = read_record(Analysis, options.analysis)
                            self._validate_analysis(analysis, intake)
                            analysis_report = {'mode': 'EXPLICIT_SAVED_ANALYSIS',
                                               'inference_performed': False}
                        else:
                            analysis, analysis_report = self.analyze(options, intake,
                                {k: v for k, v in bindings.items() if k != 'video'})
                        journal.write('analysis.json', dumps(analysis))
                        # Cache-hit counts legitimately differ on resume; persist
                        # first-attempt evidence and return current counts separately.
                        if not (partial / 'analysis-report.json').exists():
                            journal.write('analysis-report.json', json_text(analysis_report))
                        else:
                            _validate_reused_summary(partial / 'analysis-report.json', analysis_report)
                            journal.record('analysis-report.json')
                        if options.command != 'analyze':
                            stage('planning')
                            request = read_record(PlannerRequest, options.request) if options.request else PlannerRequest(1, analysis_digest(analysis), 'tight', (), ())
                            if options.preset:
                                request = replace(request, preset=options.preset)
                            journal.write('planner-request.json', dumps(request))
                            picture = read_record(PictureAnalysis, options.picture) if options.picture else None
                            if options.picture_request:
                                if not options.ffmpeg:
                                    raise RunError('PICTURE_REQUIRES_LOCAL_DECODER')
                                picture_request = read_record(PictureRequest, options.picture_request)
                                saved_picture = partial / 'picture-analysis.json'
                                if saved_picture.exists():
                                    picture = read_record(PictureAnalysis, saved_picture)
                                    validate_picture(analysis, picture)
                                    if (picture.request != picture_request or
                                            picture.decoder_sha256 != fingerprint(options.ffmpeg) or
                                            picture.decoder_version != tool_version(options.ffmpeg)):
                                        raise RunError('SAVED_PICTURE_BINDING_MISMATCH')
                                else:
                                    picture = analyze_picture(analysis, picture_request,
                                        bindings['video'], options.ffmpeg, options.ffprobe,
                                        stream_index=next(t.stream_index for t in starter.tracks if not t.audio))
                            if picture:
                                journal.write('picture-analysis.json', dumps(picture))
                                report['picture_coverage'] = coverage_report(analysis, picture)
                                report['picture_stream_index'] = next(t.stream_index for t in starter.tracks if not t.audio)
                            cleanup_request = read_record(CleanupRequest, options.cleanup_request) if options.cleanup_request else None
                            base, result, refinement, cleanup, layout = self.plan(analysis, request, picture, cleanup_request)
                            journal.write('planning-result.json', dumps(base))
                            if refinement:
                                journal.write('picture-refinement.json', dumps(refinement))
                                journal.write('refined-planning-result.json', dumps(result))
                            if cleanup:
                                journal.write('cleanup-result.json', dumps(cleanup))
                            journal.write('edit-plan.json', dumps(layout.plan))
                            report['planning'] = explain(result)
                            if request.schema_version == 2:
                                report['turn_cues'] = to_data(layout.cues)
                            report['picture_markers'] = to_data(refinement.markers) if refinement else []
                            report['cleanup'] = to_data(cleanup) if cleanup else None
                            if options.command in ('export', 'run'):
                                stage('exporting')
                                # Always revalidate/reproduce export on resume. Use
                                # a private owned candidate at the same depth so
                                # final relative media paths remain byte-identical.
                                scratch = final.parent / ('.iae-export-' + uuid.uuid4().hex)
                                scratch.mkdir()
                                candidate = scratch / 'project.kdenlive'
                                try:
                                    report['export'] = self.export(options, base, bindings,
                                        {p.source_id: p.display_name for p in mapping.participants},
                                        candidate, picture, cleanup)
                                    checkpoint()
                                    journal.write('project.kdenlive', candidate.read_text(encoding='utf-8'))
                                finally:
                                    candidate.unlink(missing_ok=True)
                                    scratch.rmdir()
                    stage('reporting')
                    journal.write('report.json', json_text(report))
                    stage('finalizing')
                    # Current paths, tools, review inputs, code and source bytes
                    # must still match, even after a long inference/audit.
                    if self._inputs(options) != {k: v for k, v in inputs.items() if k not in ('sources', 'ffprobe_version', 'ffmpeg_version')}:
                        raise RunError('INPUT_CHANGED_DURING_RUN')
                    if any(fingerprint(p) != inputs['sources'][k]['sha256'] for k, p in bindings.items()):
                        raise RunError('SOURCE_CHANGED_DURING_RUN')
                    journal.verify()
                    checkpoint()
                journal.save(state='complete', failure_code='NONE')
                # Critical section: cancellation after commit belongs to the next
                # operation. There is no incomplete final directory to clean up.
                _rename_new(partial, final)
                return journal.manifest
            except BaseException as exc:
                if journal is not None:
                    try:
                        journal.save(state='cancelled' if isinstance(exc, KeyboardInterrupt) or
                                     (isinstance(exc, SpeechError) and str(exc) == 'ANALYSIS_CANCELLED') else 'failed',
                                     failure_code='CANCELLED' if isinstance(exc, KeyboardInterrupt) or
                                     (isinstance(exc, SpeechError) and str(exc) == 'ANALYSIS_CANCELLED') else 'FAILED')
                    except OSError:
                        pass  # disk/power failure: original journal/artifacts remain
                if isinstance(exc, SpeechError) and str(exc) == 'ANALYSIS_CANCELLED':
                    raise Cancelled() from None
                raise
