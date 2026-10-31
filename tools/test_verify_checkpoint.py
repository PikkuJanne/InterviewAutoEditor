"""Temporary local Git repos only: no network or real repository mutation."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from verify_checkpoint import verify, origin_matches


def run(*args, cwd=None):
    return subprocess.run(['git', *args], cwd=cwd, text=True,
                          capture_output=True, check=True).stdout.strip()


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='iae-checkpoint-test-')
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.remote = base / 'origin.git'
        self.repo = base / 'work'
        run('init', '--bare', str(self.remote))
        run('init', '-b', 'codex/test', str(self.repo))
        run('config', 'user.name', 'Fixture', cwd=self.repo)
        run('config', 'user.email', 'fixture@example.invalid', cwd=self.repo)
        run('remote', 'add', 'origin', str(self.remote), cwd=self.repo)
        (self.repo / 'docs/project/steps').mkdir(parents=True)
        (self.repo / 'docs/handovers').mkdir(parents=True)
        (self.repo / 'docs/project/STATE.json').write_text(json.dumps({
            'repository': 'PikkuJanne/InterviewAutoEditor',
            'latest_handover': 'docs/handovers/S00.md', 'next_step': 'S01'}))
        (self.repo / 'docs/project/steps/S01.md').write_text('Next step\n')
        (self.repo / 'docs/NEXT_STEP.md').write_text('S01\n')
        (self.repo / 'docs/handovers/S00.md').write_text('Fixture checkpoint\n')
        run('add', 'docs', cwd=self.repo)
        run('commit', '-m', 'Fixture baseline', cwd=self.repo)
        run('push', '-u', 'origin', 'HEAD', cwd=self.repo)

    def check(self):
        # A filesystem bare remote is deliberately substituted for GitHub in tests.
        return verify(self.repo, require_origin_identity=False)

    def commit_state_text(self, content):
        (self.repo / 'docs/project/STATE.json').write_text(content, encoding='utf-8')
        run('add', 'docs/project/STATE.json', cwd=self.repo)
        run('commit', '-m', 'Update fixture state', cwd=self.repo)
        run('push', cwd=self.repo)

    def fixture_state(self):
        return dict(repository='PikkuJanne/InterviewAutoEditor',
                    latest_handover='docs/handovers/S00.md',
                    next_step='S01')

    def assert_clean_synced_failure(self, issue):
        result = self.check()
        self.assertTrue(result['worktree_clean'], result)
        self.assertEqual(result['local_head'], result['live_remote_head'], result)
        self.assertFalse(result['passed'], result)
        self.assertIn(issue, result['issues'])

    def test_clean_live_sync_passes(self):
        result = self.check()
        self.assertTrue(result['passed'], result)
        self.assertEqual(result['local_head'], result['live_remote_head'])

    def test_dirty_tree_fails(self):
        (self.repo / 'untracked.txt').write_text('not committed')
        self.assertFalse(self.check()['passed'])

    def test_unpushed_commit_fails(self):
        (self.repo / 'docs/NEXT_STEP.md').write_text('changed\n')
        run('add', 'docs/NEXT_STEP.md', cwd=self.repo)
        run('commit', '-m', 'Unpushed', cwd=self.repo)
        result = self.check()
        self.assertFalse(result['passed'])
        self.assertNotEqual(result['local_head'], result['live_remote_head'])

    def test_live_remote_change_detected_without_fetch(self):
        other = Path(self.temp.name) / 'other'
        run('clone', '-b', 'codex/test', str(self.remote), str(other))
        run('config', 'user.name', 'Fixture', cwd=other)
        run('config', 'user.email', 'fixture@example.invalid', cwd=other)
        (other / 'docs/NEXT_STEP.md').write_text('remote changed\n')
        run('add', 'docs/NEXT_STEP.md', cwd=other)
        run('commit', '-m', 'Remote advanced', cwd=other)
        run('push', cwd=other)
        self.assertFalse(self.check()['passed'])

    def test_missing_upstream_fails(self):
        run('branch', '--unset-upstream', cwd=self.repo)
        self.assertFalse(self.check()['passed'])

    def test_unavailable_remote_fails(self):
        run('remote', 'set-url', 'origin', str(Path(self.temp.name) / 'absent.git'), cwd=self.repo)
        self.assertFalse(self.check()['passed'])

    def test_missing_handover_fails(self):
        (self.repo / 'docs/handovers/S00.md').unlink()
        run('add', '-u', 'docs/handovers/S00.md', cwd=self.repo)
        run('commit', '-m', 'Remove fixture handover', cwd=self.repo)
        run('push', cwd=self.repo)
        result = self.check()
        self.assertTrue(result['worktree_clean'])
        self.assertEqual(result['local_head'], result['live_remote_head'])
        self.assertFalse(result['passed'])
        self.assertIn('State handover path is missing or outside the repository.', result['issues'])

    def test_malformed_json_fails_clean_checkpoint(self):
        self.commit_state_text('{"repository":')
        self.assert_clean_synced_failure(
            'Checkpoint verification could not finish; inspect Git access and state locally.')

    def test_non_object_state_fails_clean_checkpoint(self):
        for state in ([], None, 42, 'state'):
            with self.subTest(state=state):
                self.commit_state_text(json.dumps(state))
                self.assert_clean_synced_failure('State must be a JSON object.')

    def test_invalid_handover_types_fail_clean_checkpoint(self):
        for handover in (42, [], {}, True):
            with self.subTest(handover=handover):
                state = self.fixture_state()
                state['latest_handover'] = handover
                self.commit_state_text(json.dumps(state))
                self.assert_clean_synced_failure(
                    'State does not reference a completed or blocked checkpoint handover.')

    def test_empty_handover_fails_clean_checkpoint(self):
        for handover in ('', '   '):
            with self.subTest(handover=handover):
                state = self.fixture_state()
                state['latest_handover'] = handover
                self.commit_state_text(json.dumps(state))
                self.assert_clean_synced_failure(
                    'State does not reference a completed or blocked checkpoint handover.')

    def test_outside_handover_fails_clean_checkpoint(self):
        outside = Path(self.temp.name) / 'outside.md'
        outside.write_text('Not a repository handover\n', encoding='utf-8')
        for handover in ('../outside.md', str(outside)):
            with self.subTest(handover=handover):
                state = self.fixture_state()
                state['latest_handover'] = handover
                self.commit_state_text(json.dumps(state))
                self.assert_clean_synced_failure(
                    'State handover path is missing or outside the repository.')

    def test_invalid_next_step_fails_clean_checkpoint(self):
        # Even an existing brief outside the named range must not authorize work.
        (self.repo / 'docs/project/steps/S16.md').write_text('Invalid step\n')
        run('add', 'docs/project/steps/S16.md', cwd=self.repo)
        run('commit', '-m', 'Add out-of-range fixture brief', cwd=self.repo)
        run('push', cwd=self.repo)
        for next_step in (42, True, [], {}, '', 'S1', 'S16',
                          '../../NEXT_STEP', str(self.repo / 'docs/NEXT_STEP')):
            with self.subTest(next_step=next_step):
                state = self.fixture_state()
                state['next_step'] = next_step
                self.commit_state_text(json.dumps(state))
                self.assert_clean_synced_failure(
                    'State next_step must be S00-S15, COMPLETE or null.')

    def test_completion_next_steps_pass(self):
        for next_step in (None, 'COMPLETE'):
            with self.subTest(next_step=next_step):
                state = self.fixture_state()
                state['next_step'] = next_step
                self.commit_state_text(json.dumps(state))
                self.assertTrue(self.check()['passed'])

    def test_missing_known_next_step_brief_fails(self):
        state = self.fixture_state()
        state['next_step'] = 'S15'
        self.commit_state_text(json.dumps(state))
        self.assert_clean_synced_failure('Next-step brief is missing.')

    def test_known_boundary_step_briefs_pass(self):
        for step in ('S00', 'S15'):
            (self.repo / 'docs/project/steps' / (step + '.md')).write_text('Named step\n')
        run('add', 'docs/project/steps/S00.md', 'docs/project/steps/S15.md', cwd=self.repo)
        run('commit', '-m', 'Add boundary fixture briefs', cwd=self.repo)
        run('push', cwd=self.repo)
        for next_step in ('S00', 'S15'):
            with self.subTest(next_step=next_step):
                state = self.fixture_state()
                state['next_step'] = next_step
                self.commit_state_text(json.dumps(state))
                self.assertTrue(self.check()['passed'])

    def test_origin_validation(self):
        self.assertTrue(origin_matches('git@github.com:PikkuJanne/InterviewAutoEditor.git'))
        self.assertTrue(origin_matches('https://github.com/PikkuJanne/InterviewAutoEditor.git'))
        self.assertTrue(origin_matches('ssh://git@github.com/PikkuJanne/InterviewAutoEditor.git'))
        self.assertFalse(origin_matches('https://example.com/PikkuJanne/InterviewAutoEditor.git'))
        self.assertFalse(origin_matches('https://github.com/other/InterviewAutoEditor.git'))


if __name__ == '__main__':
    unittest.main()
