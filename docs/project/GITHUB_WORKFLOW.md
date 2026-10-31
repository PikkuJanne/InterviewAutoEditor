# Local and GitHub synchronization

Repository: PikkuJanne/InterviewAutoEditor. Expected SSH origin: git@github.com:PikkuJanne/InterviewAutoEditor.git. An authenticated HTTPS equivalent is acceptable. Never change a different origin without resolving the mismatch.

## Branch strategy
S00 creates or resumes `codex/kdenlive26-overhaul` from the verified intended base. Keep this branch through the development steps so a new thread has one obvious continuation point. If that name already contains unrelated work, preserve it and record a distinct branch. Push each checkpoint. main remains the stable integration branch until S15. A draft PR may be maintained when useful; do not merge unfinished work just to call it synchronized.

The historical inspected base was main at 0c445a400c96b1f85f17fcb0ee8916d283e22d6f, containing LICENSE only. Always fetch/inspect again. There may be local code absent from that old snapshot.

## Checkpoint sequence
1. Inspect `git status --short`, `git diff`, staged changes and remote state. Respect unrelated user changes; use a separate worktree if necessary. Never auto-stash or delete their files.
2. Run the step's applicable gates. Record exact commands, versions and outputs, including failures or NOT RUN.
3. Stage only reviewed intended paths. Check for credentials, private recordings, private filesystem paths and unintended generated files. Never rely solely on .gitignore, and do not use a blind `git add .`.
4. Commit implementation/test changes as a work commit if needed. Obtain its real full SHA. If no code changes were needed, identify the actual relevant existing commit rather than making an empty implementation commit.
5. Write/update the handover, STATE.json and NEXT_STEP.md with that implementation SHA, technical gate status, branch and next action. In the tracked record, synchronization is 'verify live at checkpoint'; do not invent an unperformed push result. The handover's final checkpoint SHA is resolved from Git history, not embedded into its own contents.
6. Commit the handover/state documents. Push the current branch normally, with upstream configured. Never force-push, rewrite published history, move a tag or bypass hooks/protection.
7. Query the live remote branch and compare its SHA to `git rev-parse HEAD`. Recheck clean working tree and matching upstream. `python tools/verify_checkpoint.py` provides a read-only check; it does not replace applicable tests or CI.
8. Check CI for this exact SHA when configured. If only docs changed after tested code, say so and run relevant documentation/state checks; do not falsely attribute tests to a different SHA. Finish with local and live remote SHA, CI URLs/status and the exact next prompt in the chat handover.

If push/auth/network/CI fails: diagnose and fix what is safe. Otherwise report SYNC BLOCKED or CI BLOCKED, show the actual local commit, preserve work and instruct the next thread to resume the same step. Never claim 'GitHub is in sync' on the basis of a local commit or a stale origin tracking ref.

## Divergence
Fetch and inspect the divergent commits. Integrate normal remote changes without overwriting them; meaningful conflicts require understanding both changes and rerunning affected gates. Do not use reset --hard, clean -fd, force push or an unreviewed conflict strategy. Preserve unrelated changes and explain any unavoidable blocker.

## Public repository hygiene
Use synthetic or explicitly shareable minimal fixtures. Keep interviews, transcripts, names, voices, raw screenshots, credentials and private local paths in ignored private locations. Committed reports use neutral fixture IDs. Sanitize Kdenlive XML resource URLs, bin labels, document notes and embedded properties before a fixture is published. CI must not need private recordings to pass public tests.

## Final integration
Starting S15 requests the defined final integration and release, after S14 passes. Respect required reviews/rules; if the environment needs approval, prepare the concrete result and report the exact blocker. Integrate normally to main, validate the resulting commit, push, tag v1.0.0 only if unused and appropriate, and publish matching assets. If version 1.0.0 already exists, stop to reconcile release intent rather than replace it. Follow RELEASE_CHECKLIST.md, including final continuation/maintenance state.
