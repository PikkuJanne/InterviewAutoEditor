"""Desktop orchestration over Application. No timing, inference or export policy.

Jobs/mappings/requests/reports are private local data. Immutable job snapshots
live BESIDE a run, never inside its recoverable staging transaction.
"""
from dataclasses import dataclass, fields, replace
from fractions import Fraction
import json
import os
from pathlib import Path
from queue import Queue
import subprocess
from threading import Event, Thread
from typing import Literal
import uuid

from .adapters.kdenlive import read_starter, resolve_resource
from .application import Application, LIMIT, RunError, RunOptions, read_record
from .editing import Mute
from .contracts import Analysis, Override, dumps, loads, to_data
from .intake import FileMapping, MappingManifest
from .planner import PlannerRequest, analysis_digest
from .speech import atomic_new


STAGES = {'inspecting': 'Checking project and media', 'analyzing': 'Analyzing participant audio',
          'planning': 'Preparing shared edits', 'exporting': 'Creating editable project',
          'reporting': 'Writing private review', 'finalizing': 'Validating and finishing'}


@dataclass(frozen=True)
class DesktopJob:
    schema_version: Literal[1]
    options: tuple[tuple[str, str], ...]

    def __post_init__(self):
        names = [k for k, v in self.options]
        expected = {f.name for f in fields(RunOptions)}
        if (len(names) != len(set(names)) or not set(names) <= expected
                or not expected - {'mutes', 'target_kdenlive'} <= set(names)):
            raise RunError('INVALID_DESKTOP_JOB')
        values = dict(self.options)
        if (values['command'] not in ('inspect', 'analyze', 'plan', 'run', 'edit') or
                values['experimental'] not in ('true', 'false') or
                values['preset'] not in ('', 'tight', 'gentle') or
                any(not values[k] for k in ('project', 'mapping', 'ffprobe', 'output'))):
            raise RunError('INVALID_DESKTOP_JOB')

    @classmethod
    def from_options(cls, options):
        values = []
        for field in fields(RunOptions):
            value = getattr(options, field.name)
            values.append((field.name, json.dumps(to_data(value)) if field.name == 'mutes' else ('true' if value else 'false') if field.name == 'experimental'
                           else str(value) if value is not None else ''))
        return loads(cls, dumps(cls(1, tuple(values))))

    def run_options(self):
        values = dict(self.options)
        for key, value in values.items():
            if key == 'experimental':
                values[key] = value == 'true'
            elif key == 'mutes':
                values[key] = loads(tuple[Mute, ...], value)
            elif key not in ('command', 'preset'):
                path = Path(value) if value else None
                if path is not None and not path.is_absolute():
                    raise RunError('DESKTOP_JOB_REQUIRES_ABSOLUTE_PATHS')
                values[key] = path
        values['preset'] = values['preset'] or None
        return RunOptions(**values)


def discover_mapping(project):
    """Neutral suggestions only; a user must explicitly confirm every row."""
    starter = read_starter(project)
    return MappingManifest(1, tuple(FileMapping(str(track.resource), f'participant_{i:02}',
        f'Participant {i:02}', (f'participant_{i:02}',)) for i, track in
        enumerate((t for t in starter.tracks if t.audio), 1)), ())


def absolute_mapping(path):
    mapping = read_record(MappingManifest, path)
    if mapping.relocations:
        raise RunError('RELOCATION_EXPORT_UNSUPPORTED_USE_EXPLICIT_MAPPING')
    return replace(mapping, participants=tuple(replace(p,
        resource=str(resolve_resource(p.resource, Path(path).parent))) for p in mapping.participants))


def restored_request(analysis, request, source_id, start, end, action):
    """Parse exact source seconds; production contracts enforce all bounds."""
    if len(start) > 64 or len(end) > 64:
        raise RunError('INVALID_SOURCE_SECONDS')
    try:
        override = Override(source_id, Fraction(start), Fraction(end), action)
        updated = replace(request, overrides=request.overrides + (override,))
        # The shared service validates origins/tails, bounds and original binding.
        Application().plan(analysis, updated)
        return updated
    except (ValueError, ZeroDivisionError):
        raise RunError('INVALID_RESTORE_OR_UNSUPPORTED_ANALYSIS') from None


def prepare_job(options, mapping, request=None):
    """Exclusive private snapshots: no source overwrite, no approval rebinding."""
    output = options.output.absolute()
    if not output.name or output.name.startswith('.') or output.exists():
        raise RunError('RUN_ALREADY_EXISTS_USE_NEW_DESTINATION')
    if output.with_name('.' + output.name + '.incomplete').exists():
        raise RunError('EXPLICIT_RESUME_REQUIRED_OR_NO_PARTIAL_RUN')
    output.parent.mkdir(parents=True, exist_ok=True)
    prefix = output.parent / ('.' + output.name + '.desktop-')
    mapping_path = Path(str(prefix) + 'mapping.json')
    atomic_new(mapping_path, dumps(loads(MappingManifest, dumps(mapping))))
    options = replace(options, mapping=mapping_path)
    if request is not None:
        request_path = Path(str(prefix) + 'request.json')
        atomic_new(request_path, dumps(loads(PlannerRequest, dumps(request))))
        options = replace(options, request=request_path)
    # Freeze absolute paths; a reopened job is independent of process cwd.
    changes = {f.name: getattr(options, f.name).absolute() for f in fields(RunOptions)
               if isinstance(getattr(options, f.name), Path)}
    options = replace(options, **changes)
    job = DesktopJob.from_options(options)
    path = Path(str(prefix) + 'job.json')
    atomic_new(path, dumps(job))
    return path, job


def review_run(directory):
    """Verify journal hashes BEFORE reading private review/analysis records."""
    directory = Path(directory)
    manifest = Application.report(directory)
    names = {a.name for a in manifest.artifacts}
    report = {}
    if 'report.json' in names:
        with (directory / 'report.json').open(encoding='utf-8') as stream:
            raw = stream.read(LIMIT + 1)
        if len(raw) > LIMIT:
            raise RunError('RUN_ARTIFACT_NAME_OR_SIZE_LIMIT')
        report = json.loads(raw)
    analysis = read_record(Analysis, directory / 'analysis.json') if 'analysis.json' in names else None
    request = read_record(PlannerRequest, directory / 'planner-request.json') if 'planner-request.json' in names else None
    return manifest, report, analysis, request


def open_edit_copy(directory, executable):
    """Keep the run immutable and relative references at the same folder depth."""
    directory = Path(directory).absolute()
    manifest = Application.report(directory)
    if manifest.state != 'complete' or 'project.kdenlive' not in {a.name for a in manifest.artifacts}:
        raise RunError('NO_COMPLETED_EDITABLE_PROJECT')
    executable = Path(executable)
    if not executable.is_file() or (os.name == 'nt' and executable.suffix.lower() != '.exe'):
        raise RunError('SELECT_INSTALLED_KDENLIVE')
    folder = directory.with_name(directory.name + '-edit-' + uuid.uuid4().hex[:8])
    folder.mkdir()
    project = folder / 'project.kdenlive'
    with (directory / 'project.kdenlive').open(encoding='utf-8') as stream:
        content = stream.read(LIMIT + 1)
    if len(content) > LIMIT:
        raise RunError('RUN_ARTIFACT_NAME_OR_SIZE_LIMIT')
    atomic_new(project, content)
    subprocess.Popen([str(executable.resolve()), str(project)], shell=False)
    return project


def error_message(exc, stage=''):
    """Allowlisted actions, never interpolate exception text/private content."""
    code = str(exc)
    exact = {
        'RUN_ALREADY_EXISTS_USE_NEW_DESTINATION': 'That run already exists. Choose a new output folder.',
        'EXPLICIT_RESUME_REQUIRED_OR_NO_PARTIAL_RUN': 'An incomplete run needs Resume saved job with its original inputs. Otherwise choose a new folder.',
        'RESUME_INPUTS_CHANGED_USE_NEW_RUN': 'Inputs or settings changed. Preserve the incomplete run and start in a new folder.',
        'RUN_BUSY': 'Another process owns this run. Wait for it to finish before resuming.',
        'RUN_ARTIFACT_CHANGED_OR_MISSING': 'A saved run artifact changed or is missing. Preserve it for inspection; no automatic repair is performed.',
        'UNRESOLVED_MEDIA_REFERENCE': 'A referenced media file is missing. Restore it at its original location and reopen the starter.',
        'ANALYSIS_REQUIRES_LOCAL_MODELS_TOOLS_CACHE': 'Choose the installed local analysis assets in Local setup, or explicitly supply reviewed analysis.',
        'SAVED_ANALYSIS_SOURCE_MISMATCH': 'Reviewed analysis does not match this participant mapping or source media. Load the original mapping and matching records.',
        'SAVED_ANALYSIS_PROJECT_MISMATCH': 'Reviewed analysis belongs to a different starter. Choose matching records.',
        'Cleanup approval belongs to a different planning result.': 'Cleanup approvals belong to a different plan. Preview without cleanup, then explicitly load newly reviewed approvals, or leave cleanup off for unity gain.',
        'INVALID_RESTORE_OR_UNSUPPORTED_ANALYSIS': 'Use valid source seconds within verified exact coverage. Keep/Restore cannot certify alignment or repair tails.',
        'SELECT_INSTALLED_KDENLIVE': 'Select the installed Kdenlive executable in Local setup.',
    }
    if code in exact:
        return exact[code]
    if isinstance(exc, FileExistsError):
        return 'A destination or desktop snapshot already exists. Choose a new folder; existing files are preserved.'
    if isinstance(exc, FileNotFoundError):
        return 'A required file is missing. Check the selected local assets and restore missing files before retrying.'
    if stage == 'planning':
        return 'Planning refused. Check origin verification, exact source tails and matching reviewed approvals. No source repair is applied.'
    if stage == 'exporting':
        return 'Export refused. Check experimental opt-in, source integrity and the conservative headroom review. Originals are unchanged.'
    return 'Cannot complete this action. Check the supported unedited starter, participant mapping and selected local records/assets. Preserve any incomplete run for inspection.'


class Worker:
    """One cooperative worker; only the UI thread accesses widgets."""
    def __init__(self):
        self.events = Queue()
        self.cancel = Event()
        self.thread = None

    @property
    def busy(self):
        return self.thread is not None and self.thread.is_alive()

    def start(self, task):
        if self.busy:
            raise RunError('RUN_BUSY')
        self.cancel.clear()
        def work():
            stage = ''
            def progress(value):
                nonlocal stage
                stage = value
                self.events.put(('progress', STAGES[value]))
            try:
                result = task(Application(cancel=self.cancel.is_set, progress=progress))
                self.events.put(('done', result))
            except KeyboardInterrupt:
                self.events.put(('cancelled', 'Cancelled. Completed caches and incomplete run evidence remain local. Use Resume saved job with unchanged inputs.'))
            except Exception as exc:
                self.events.put(('error', error_message(exc, stage)))
        self.thread = Thread(target=work, daemon=False)
        self.thread.start()
