# One step per thread

## Start each thread
1. Locate the existing checkout; read applicable AGENTS files. Inspect branch, origin, status, worktrees and uncommitted work. Do not reinstall this bundle over current state.
2. Read docs/project/STATE.json, docs/NEXT_STEP.md, the referenced latest handover and the selected step brief. Verify factual claims against the current repository.
3. Fetch origin safely if authorized/available; compare remote HEAD, local HEAD and the previous handover checkpoint. If another person changed the branch, reconcile normally. Do not force-push or erase their work.
4. Finish any prior failed sync before advancing. A completed implementation without a verified checkpoint is not permission to skip ahead.
5. State the one step being executed. Plan its internal tasks and proceed autonomously within scope.

## During the step
Implement through its exit gate. Resolve routine choices yourself and record material decisions. Do not pad work with unrelated refactors. Use relevant tests that address real failure modes. Work that requires the user's ear should be a small prepared comparison with clear timecodes, not an open-ended request to test everything.

If an essential file, actual Kdenlive build, credential or permission is unavailable, finish independently useful authorized work and stop at that gate. Mark BLOCKED, explain exactly what is missing, preserve the partial checkpoint and give a continuation prompt for the SAME step. Do not silently waive gates or label unrun work as complete.

## Close the step
Follow GITHUB_WORKFLOW.md. Update progress, decisions and evidence; write a detailed handover and NEXT_STEP. Commit and push. Verify live remote SHA == local HEAD and no owned uncommitted files remain. Resolve CI evidence for the exact commit when configured. State which checks apply to code and which to the final documentation checkpoint.

The persisted handover records the implementation commit, branch and its own path. It does not pretend to contain its own final commit hash. The final chat records the actual checkpoint SHA after commit/push. A new thread resolves that handover's containing commit from Git and verifies it against the branch. This avoids a self-referential endless documentation commit loop.

## Final response at every boundary
Use the HANDOVER_TEMPLATE.md structure. Be verbose and self-contained: identify the step/outcome, behavior changed, files, decisions, tests with commands/results, actual Kdenlive evidence, limitations, exact Git checkpoint/CI state, remaining work, user action if genuinely needed and the exact next-thread prompt. Do not say merely 'done, tests pass'.

End with: 'Paused after Sxx. The next thread should execute Syy only.' If blocked, say 'Paused with Sxx blocked. The next thread must resume Sxx.' Do not begin the next named step in the same response or through background work.

## State rules
STATE.json is the machine-readable progress record; NEXT_STEP.md is its human-readable entry point. Keep them consistent. Record technical gate status separately from synchronization, which must always be checked live. A blocked sync overrides a planned next step. State cannot override observed Git or a more recent user instruction.

All future steps start pending. Record actual validation only after execution. Each handover is a separate Sxx file; retries append clearly dated attempt sections or use an indexed attempt file and update the state link. Never delete failure evidence to make a gate appear clean.
