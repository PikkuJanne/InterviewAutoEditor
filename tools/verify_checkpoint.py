#!/usr/bin/env python3
"""Read-only checkpoint verification. Does not fetch, commit, push or check CI."""
import argparse
import json
from pathlib import Path
import subprocess
from urllib.parse import urlparse

EXPECTED_REPOSITORY = 'PikkuJanne/InterviewAutoEditor'
STEP_IDS = frozenset(f'S{number:02d}' for number in range(16))


def git(repo, *args):
    proc = subprocess.run(
        ['git', '-C', str(repo), *args], text=True, capture_output=True, timeout=30
    )
    if proc.returncode:
        # Remote errors can contain credential-bearing URLs; do not echo them.
        raise RuntimeError('Git operation failed: ' + args[0])
    return proc.stdout.strip()


def origin_matches(url):
    if url.startswith('git@github.com:'):
        path = url.split(':', 1)[1]
    else:
        parsed = urlparse(url)
        if parsed.scheme not in ('https', 'ssh') or parsed.hostname != 'github.com':
            return False
        path = parsed.path.lstrip('/')
    if path.endswith('.git'):
        path = path[:-4]
    return path.lower() == EXPECTED_REPOSITORY.lower()


def verify(repo, require_origin_identity=True):
    report = {'passed': False, 'branch': None, 'local_head': None,
              'live_remote_head': None, 'upstream': None,
              'worktree_clean': None, 'issues': [],
              'ci': 'Not checked by this helper; inspect exact-commit CI separately.'}
    issues = report['issues']
    try:
        branch = git(repo, 'symbolic-ref', '--quiet', '--short', 'HEAD')
        report['branch'] = branch
        report['local_head'] = git(repo, 'rev-parse', 'HEAD')
        origin = git(repo, 'remote', 'get-url', 'origin')
        if require_origin_identity and not origin_matches(origin):
            issues.append('Origin is not the expected GitHub repository; inspect privately.')
        status = git(repo, 'status', '--porcelain=v1', '--untracked-files=all')
        report['worktree_clean'] = not bool(status)
        if status:
            issues.append('Working tree has uncommitted or untracked non-ignored files.')
        try:
            report['upstream'] = git(repo, 'rev-parse', '--abbrev-ref', '@{upstream}')
            if report['upstream'] != 'origin/' + branch:
                issues.append('Upstream does not match origin/current-branch.')
        except RuntimeError:
            issues.append('No usable branch upstream is configured.')
        remote_ref = 'refs/heads/' + branch
        lines = git(repo, 'ls-remote', '--exit-code', 'origin', remote_ref).splitlines()
        entries = [line.split() for line in lines if line.strip()]
        exact = [entry[0] for entry in entries if len(entry) == 2 and entry[1] == remote_ref]
        if len(exact) != 1:
            issues.append('Live remote branch could not be resolved unambiguously.')
        else:
            report['live_remote_head'] = exact[0]
            if exact[0] != report['local_head']:
                issues.append('Local HEAD differs from the live remote branch.')
        root = Path(git(repo, 'rev-parse', '--show-toplevel'))
        state = json.loads((root / 'docs/project/STATE.json').read_text(encoding='utf-8'))
        if not isinstance(state, dict):
            issues.append('State must be a JSON object.')
            return report
        if state.get('repository') != EXPECTED_REPOSITORY:
            issues.append('State repository identity does not match the project.')
        if not (root / 'docs/NEXT_STEP.md').is_file():
            issues.append('docs/NEXT_STEP.md is missing.')
        handover = state.get('latest_handover')
        if not isinstance(handover, str) or not handover.strip():
            issues.append('State does not reference a completed or blocked checkpoint handover.')
        else:
            resolved = (root / handover).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
                issues.append('State handover path is missing or outside the repository.')
        next_step = state.get('next_step')
        if next_step not in (None, 'COMPLETE'):
            if not isinstance(next_step, str) or next_step not in STEP_IDS:
                issues.append('State next_step must be S00-S15, COMPLETE or null.')
            elif not (root / 'docs/project/steps' / (next_step + '.md')).is_file():
                issues.append('Next-step brief is missing.')
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired):
        issues.append('Checkpoint verification could not finish; inspect Git access and state locally.')
    report['passed'] = not issues
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = verify(args.repo)
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
