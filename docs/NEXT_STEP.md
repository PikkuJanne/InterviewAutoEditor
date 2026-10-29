# Next: S12 - validate full interviews and calibrate quality

**S11 COMPLETE for supported synthetic desktop/recovery scope. S12 is pending
and has not started.** Execute one named step per thread. Compatibility remains
EXPERIMENTAL for Kdenlive 26.08.2 rev. d4e87e4.

- Branch: `codex/kdenlive26-overhaul`.
- S11 implementation: `7d8d06dd4142f12e6da436a206964a894905d0bb`.
- Starting S10 checkpoint: `e88e138a891078c3a04e9fb8f9117273dd0651d3`.
- Handover: [S11.md](handovers/S11.md).
- State: [STATE.json](project/STATE.json).
- Next brief: [S12.md](project/steps/S12.md).
- Desktop: [S11_DESKTOP.md](project/S11_DESKTOP.md).
- Evidence: [S11_DESKTOP_EVIDENCE.json](fixtures/S11_DESKTOP_EVIDENCE.json).
- Visible workflow: [S11_WORKFLOW.md](fixtures/S11_WORKFLOW.md).

The minimal desktop now handles starter selection, explicit participant mapping,
Tight/Gentle, service modes, progress/cancel, private review, source-time
Keep/Restore and opening a separate editable copy in Kdenlive. Double-click
`InterviewAutoEditor.pyw` in the prepared checkout; no installation/download occurs.
Bundled runtime/clean-install/release work remains S14/S15.

Application, CLI, policies, contracts, adapters, assets/locks/licences and prior
fixtures are unchanged. Desktop jobs/mappings/requests are exclusive private
snapshots beside the run. Resume explicitly picks the original job and applies
its original options; form edits are excluded. The service still verifies full
inputs/code/artifacts/cache and atomically publishes a NEW validated folder.
Corruption refuses; no deletion/repair or implicit approval rebinding occurs.

Keep/audible restores original source time on ALL tracks for a NEW run. Picture
observations only narrow approved deletions. Cleanup must bind the refined result;
changed pacing/overrides can require explicitly reviewed rebinding or unity gain.
Keep protected content/uncertainty/laughter/overlap/shared mics, full exterior
handles, groups/bin originals, canonical gain refusal, conservative headroom and
the original 12.00/12.45 speech/picture lag. Original real origins remain
unverified/null, exact tails unequal and planning/export refused. No source repair,
retiming, normalization/denoising or invented footage is authorized.

Final full suite: **224 tests, zero skips, 200.744 s**, including 18 S11 tests.
Focused suite: **18 tests, zero skips, 22.426 s**, no ignored Tcl cleanup errors.
New actual visible desktop synthetic run/open-copy/Keep plus Kdenlive open/play
pass. Synthetic output remains 267 frames/six groups/four gains; explicit
restoration without cleanup yields 300 frames/unity. The exporter did not change:
no new full group-edit/save/reopen/render was run. Genuine S10 full native/render
evidence remains separate and is remeasured by the full suite.

Private preservation passes 102 assertions/five unchanged originals/twelve exact
excerpts. The bounded overlap stays 200/200 frames at unity. No new listening,
connection, private full export, tuning or held-out access. Preserve one-file and
no-new-connection preferences and bounded S08 human acceptance.

8/64-row Tk tests are presentation scaling; core media export tests cover
1/2/3/6/8 audio tracks. Full/held-out interview acceptance, long stress, wider
native track/FPS/build/screen-reader coverage and clean-install packaging remain
unaccepted. Linux/network publication remains untested; atomic visibility is not
a power-loss durability promise. Partial input/code/path changes require a new run.

Before editing, resolve this handover's containing checkpoint and verify live:

```powershell
git log -1 --format=%H -- docs/handovers/S11.md
python tools/verify_checkpoint.py --repo .
```

Final chat records actual local/live/upstream equality, clean worktree and exact
CI state. Reverify at thread start. Starting exact-SHA queries found zero
workflows/runs/checks/statuses: **CI not configured**, not green CI. Failed sync
or configured failing CI requires resuming S11 before S12.

Ready-to-paste next-thread prompt:

> Execute S12 only in InterviewAutoEditor on codex/kdenlive26-overhaul. Read AGENTS.md, STATE.json, NEXT_STEP.md, docs/handovers/S11.md, execution/GitHub protocols, S03-S11 guides and the S12 brief. S11 implementation is 7d8d06dd4142f12e6da436a206964a894905d0bb. Resolve the containing completion checkpoint and verify live/local/upstream equality, clean worktree and exact-SHA CI first. Validate full interviews and calibrate quality within S12: scenario matrix, complete two-person and band interviews, distinct held-out excerpts and long timing fixture, actual retention/approval/noise/sync/editability/performance/correction-effort metrics and focused owner acceptance. Preserve all origin/exact-tail refusals, explicit independent approvals, protected content, original picture timing, shared maps, refined cleanup bindings, private data and recoverable Application/desktop jobs. Resolve missing origin/tail evidence through explicit reviewed contracts; never repair or certify it implicitly. Keep held-out acceptance separate from tuning and preserve one-audio-file/no-new-connection preferences. Do not claim unrun full-interview/held-out or utility acceptance. Run applicable gates, update state/NEXT_STEP/S12 handover, commit/push/verify, give a verbose handover and STOP. No S13.

Paused after S11. The next thread should execute S12 only.
