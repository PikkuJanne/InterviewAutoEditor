"""Evidence registry for the observed document family, separate from plan data.

Only a matching local executable AND platform can select a tested target.
Project version strings alone never identify the application that will open it.
No project-provided program is executed by this probe.
"""
from dataclasses import dataclass
from pathlib import Path
import platform
import re

ADAPTER_ID = 'kdenlive-document-1.1-simple-v1'
PLAN_TARGET = 'kdenlive-26.08.2-experimental'  # Preserve existing strict wire data.


@dataclass(frozen=True)
class TestedBuild:
    version: str
    revision: str
    executable_sha256: str
    system: str
    release: str
    machine: str
    nt_version: str
    evidence: str


TESTED_BUILDS = (TestedBuild(
    '26.08.2', 'd4e87e4',
    '7a5bbf2e7764514a863fad756fe2195779475804706a8a74e73ab922def1d352',
    'Windows', '11', 'AMD64', '10.0.26300', 'docs/fixtures/S13_COMPATIBILITY.json'),)


def select_adapter(writer_version, document_version):
    """Candidate selection only; the complete structural reader still must pass."""
    if (document_version != '1.1' or not isinstance(writer_version, str)
            or not re.fullmatch(r'\d{2,3}\.\d{1,2}\.\d{1,3}', writer_version)
            or int(writer_version.split('.')[0]) < 26):
        return None
    return ADAPTER_ID


def assess(starter, target_kdenlive=None):
    from ..probe import fingerprint
    result = {'schema_version': 2, 'compatibility': 'EXPERIMENTAL',
        'reason': 'TARGET_BUILD_NOT_VERIFIED', 'adapter': starter.adapter_id,
        'writer_version': starter.writer_version, 'document_version': starter.document_version,
        'export_allowed': True, 'experimental_opt_in_required': True,
        'actual_application_test_performed': False, 'installed_build_verified': False,
        'capabilities': ['single_unedited_sequence', 'one_mp4_plus_n_wav',
            'shared_frame_grid', 'explicit_stream_selection', 'native_track_routing'],
        'participants': sum(t.audio for t in starter.tracks),
        'fps': {'numerator': starter.fps.numerator, 'denominator': starter.fps.denominator}}
    if target_kdenlive is None:
        return result
    try:
        digest = fingerprint(Path(target_kdenlive))
    except OSError:
        return {**result, 'compatibility': 'UNSUPPORTED', 'reason': 'TARGET_BUILD_UNREADABLE',
                'export_allowed': False}
    result['target_executable_sha256'] = digest
    for build in TESTED_BUILDS:
        if (digest == build.executable_sha256 and starter.writer_version == build.version
                and (platform.system(), platform.release(), platform.machine(), platform.version()) ==
                    (build.system, build.release, build.machine, build.nt_version)):
            return {**result, 'compatibility': 'TESTED', 'reason': 'EXACT_TARGET_AND_STRUCTURE_TESTED',
                'experimental_opt_in_required': False, 'installed_build_verified': True,
                'target_version': build.version, 'target_revision': build.revision,
                'evidence': build.evidence}
    return {**result, 'reason': 'TARGET_OR_WRITER_OUTSIDE_TESTED_MATRIX'}
