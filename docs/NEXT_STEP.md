# Next: S11 - build the minimal desktop workflow

**S10 COMPLETE for applicable supported synthetic/recovery scope. S11 is pending
and was not implemented.** Execute one named step per chat. Compatibility remains
EXPERIMENTAL for Kdenlive 26.08.2 rev. d4e87e4.

- Branch: `codex/kdenlive26-overhaul`.
- S10 implementation: `00c16d9aa08ae7c7ea9114dd22d6db07d69fbd94`.
- Starting S09 completion checkpoint: `8431f9743fb4783505951b0e9bd66e9f80850273`.
- Handover: [S10.md](handovers/S10.md).
- State: [STATE.json](project/STATE.json).
- Next brief: [S11.md](project/steps/S11.md).
- CLI and recovery: [S10_CLI.md](project/S10_CLI.md).
- Evidence: [S10_CLI_EVIDENCE.json](fixtures/S10_CLI_EVIDENCE.json).
- Actual capture: [PROVENANCE.json](../tests/fixtures/s10-cli-26.08.2/PROVENANCE.json).

One shared Application service now connects inspect/analyze/plan/export/run/report
and structural compatibility probing. It publishes complete validated run bundles
atomically, preserves failed/cancelled staging and valid per-source caches, verifies
explicit resume and refuses existing completed destinations, changed inputs or
corrupt artifacts. Full manifests/reports/cache are PRIVATE for real material.
The structural probe does not certify an installed application or future builds.

All S03-S09 safeguards remain. Pictures only narrow existing approved shared
deletions, restoring time; original 12.00/12.45 speech/picture timing survives.
Cleanup must bind the refined result; stale requests refuse without silent
rebinding. Keep source-time overrides, protected content/uncertainty/laughter/
overlap/shared mics, full handles, groups/bin originals and conservative headroom.
Original real origins remain unverified/null, tails unequal and export refused.
No normalization/denoising, source repair, independent removal or camera retiming.

Final suite: **206 tests, zero skips, 182.595 s**, including 26 S10 tests. Seven
actual CLI modes returned review exit 2; repeat-run refusal 1/cancellation 130.
Actual **26.08.2 rev. d4e87e4 / MLT 7.43.0 / Qt 6.11.1** open/play/group move/
undo/save/reopen/render and sanitized native open pass. Twelve render checks pass:
267 mapped pictures, one switch at output 105, zero measured audio-anchor lags,
eight protected probes within 0.091 dB, idle-noise reduction and peak 0.476731.
Native extent delta is zero. Existing 20-FPS delay math is separate from GUI evidence.

Private preservation remains 102 assertions/five unchanged originals/twelve exact
excerpts; retained bounded overlap is 200/200 frames at unity with zero idle
approvals. No held-out/full interview acceptance, new listening or connection.
Preserve one-file/no-new-connection preferences and bounded S08 human acceptance.
Windows/NTFS finalization is tested; Linux/network filesystems, two-hour stress,
broader GUI/build matrices and packaging are NOT RUN. Atomic visibility does not
guarantee power-loss durability. Partial relocation/input/code changes require a
fresh run; corrupt derived data fails closed.

Before editing, resolve the containing checkpoint and verify live:

```powershell
git log -1 --format=%H -- docs/handovers/S10.md
python tools/verify_checkpoint.py --repo .
```

The final chat records actual local/live/upstream equality, clean worktree and
exact-SHA CI. Reverify at thread start. Initial queries found zero workflows/runs/
checks/statuses: **CI not configured**, not green CI. Failed synchronization or
configured failing CI requires resuming S10 before S11.

Ready-to-paste next-thread prompt:

> Execute S11 only in InterviewAutoEditor on codex/kdenlive26-overhaul. Read AGENTS.md, STATE.json, NEXT_STEP.md, docs/handovers/S10.md, execution/GitHub protocols, S03-S10 guides and the S11 brief. S10 implementation is 00c16d9aa08ae7c7ea9114dd22d6db07d69fbd94. Resolve the containing completion checkpoint; verify live/local/upstream SHA equality, a clean worktree and exact-SHA CI first. Build the minimal desktop workflow over the shared S10 Application service: project picker, explicit participant mapping, Tight/Gentle, progress/cancel, understandable errors, Open in Kdenlive and source-time Keep/Restore review. Preserve S03-S10 contracts, private-data boundaries, recoverable run transaction/cache rules, refined-result cleanup binding, original picture/audio timing and real-origin/exact-tail refusals. No timing/inference logic in the UI, account/cloud workflow or new listening requirement. Run applicable UI/core gates and actual Kdenlive regression if export changes; update state/NEXT_STEP and S11 handover, commit/push/verify, provide a verbose handover and STOP. No S12.

Paused after S10. The next thread should execute S11 only.
