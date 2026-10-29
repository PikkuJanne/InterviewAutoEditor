# Next: S07 — export clear speaker turns and grouped edits

**S06 is complete on applicable exact/synthetic and retained bounded development
fixtures. S07 remains pending and was not started.** Compatibility is EXPERIMENTAL.

- Branch: `codex/kdenlive26-overhaul`.
- S06 implementation: `9a9299d88c132d1d4e5fdfbd6d97f9d4fff9e9bd`.
- Handover: [S06.md](handovers/S06.md).
- State: [STATE.json](project/STATE.json).
- Next brief: [S07.md](project/steps/S07.md).
- Planner/schema/usage: [S06_PLANNER.md](project/S06_PLANNER.md).
- Measurements: [S06_PLANNER_EVIDENCE.json](fixtures/S06_PLANNER_EVIDENCE.json).
- Prior human-development gate: [S05-attempt-05.md](handovers/S05-attempt-05.md).

S06 produces one shared frame-quantized map from all protected events. It adds
Tight/Gentle pacing, confident different/same source-group rules, protection-aware
residuals, source-time Keep overrides and exact source/output explanations.
Canonical Analysis/EditPlan remain v1; separate strict v1 request/result records
retain approval and decision provenance. Every deletion requires an explicit
all-track removable-gap approval bound to the complete analysis. Negative
VAD/reaction/noise-floor/correlation results never certify removable silence.
Unknown, shared-microphone or reaction boundaries preserve gaps. No activity or
no approvals preserves the recording, including complete exterior sections.

Final full suite: **124 tests, zero skips, 92.131 seconds**, with local CPU
models/FFmpeg. After LF-only wire-fixture cleanup the final S06 suite passed
**17 tests, zero skips, 8.891 seconds**. Tests cover 500 planned cuts each at
25 and 30000/1001 FPS, five sample grids and exact duration conservation.
Public synthetic 30-second fixtures retain 7/7 protected events and place 2/2
deletions inside independent construction labels in each preset: Tight 591
frames, Gentle 603. These are mathematical fixtures, not human accuracy or
Kdenlive-authored project evidence.

The production planner preserves the entire eight-second human-confirmed overlap
preview in a separate derived-coordinate harness. Synthetic harness origins
never certify originals. Actual real analysis still refuses planning/export for
unverified origins; null offsets, unequal exact tails and native sequence deltas
remain untouched. Source checks pass 102 assertions: five unchanged originals
and twelve sample-exact excerpts. All eleven existing S02 GUI-render measurements
pass. No new GUI operation or automatic editable-project export occurred.

Retain all S04/S05 events/reviews, shared microphone groups, full handles, native
extent and exact tails. No silent shifting, stretching, padding, truncation,
gain change, per-track removal or camera retiming. S07 must obtain actual
Kdenlive **26.08.2 rev. d4e87e4** evidence for changed export; XML/MLT-only tests
cannot replace open/play/group-edit/save/reopen/render evidence.

Real useful-removal rate, natural pace, full-interview/held-out acceptance and
gain policy remain unaccepted. Held-out audio stays separate and unopened.
No new listening is needed for S06. Preserve the user's one-audio-file maximum
and no-new-connection preference for later explicitly requested review.
Private media, labels, source fingerprints and paths stay local.

Verify the containing checkpoint before editing:

```powershell
git log -1 --format=%H -- docs/handovers/S06.md
python tools/verify_checkpoint.py --repo .
```

The closing chat records actual local/live equality, clean upstream/worktree and
exact-SHA CI after normal push. Absent workflows/checks mean **CI not configured**,
never green CI. Failed synchronization requires resuming S06 before advancing.

Ready-to-paste next-thread prompt:

> Execute S07 only in the existing InterviewAutoEditor checkout on
> codex/kdenlive26-overhaul. Read AGENTS.md, STATE.json, NEXT_STEP.md,
> docs/handovers/S06.md, execution/GitHub protocols, S03/S04/S05/S06
> contracts/guides and the S07 brief. S06 implementation is
> 9a9299d88c132d1d4e5fdfbd6d97f9d4fff9e9bd. Verify the containing checkpoint,
> live local/remote SHA equality, clean upstream/worktree and exact-SHA CI first.
> Export meaningful speaker turns and synchronized grouped edits using the one
> shared map. Preserve protected content, overlap, shared microphones, source-time
> overrides, explicit all-track gap approvals and complete exterior handles.
> Keep original unverified/null origins, native extent deltas and unequal exact
> tails; preserve current real-planning/export refusals. No silent media repair,
> per-track removal, gain changes or camera retiming. Keep private data local,
> held-out acceptance separate and compatibility EXPERIMENTAL. Obtain actual
> Kdenlive 26.08.2 rev. d4e87e4 evidence for changed export; do not substitute
> XML/MLT tests. Complete S07 gates, commit/push/verify exact-SHA CI, provide a
> verbose handover and STOP.

Paused after S06. The next thread should execute S07 only.
