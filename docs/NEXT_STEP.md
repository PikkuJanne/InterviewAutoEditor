# Next: S10 - complete the recoverable CLI pipeline

**S09 is COMPLETE for applicable synthetic and retained bounded development
fixtures. S10 remains pending and was not implemented.** Compatibility remains
EXPERIMENTAL. Execute one named step per chat.

- Branch: `codex/kdenlive26-overhaul`.
- S09 implementation: `8e31359b0e20941d4fd81e35429d83776e4f47c5`.
- Starting S08 completion checkpoint: `ba9a638257a36534430db626b5d992afad3da327`.
- Handover: [S09.md](handovers/S09.md).
- State: [STATE.json](project/STATE.json).
- Next brief: [S10.md](project/steps/S10.md).
- Picture policy/commands: [S09_PICTURE.md](project/S09_PICTURE.md).
- Evidence: [S09_PICTURE_EVIDENCE.json](fixtures/S09_PICTURE_EVIDENCE.json).
- Actual provenance: [PROVENANCE.json](../tests/fixtures/s09-picture-26.08.2/PROVENANCE.json).

S09 keeps recorded-picture observations separate from speech protection and
silence approvals. A stable switch may narrow an existing approved shared
deletion, restoring time across every track. Unknown/gallery/pinned/camera-off,
ambiguous/brief transitions and insufficient seam coverage restore the affected
handover deletion. No picture identity is asserted. The 12.00 s speech / 12.45 s
picture example preserves all opening speech and the original .45 s lag.

S08 cleanup must bind the **refined** S06 result. Stale cleanup refuses. All
protected events/overlap/shared microphones/Keep/audible overrides, full exterior
handles, grouping, full bin originals, canonical v1 gain refusal and conservative
headroom survive. Real origins remain unverified/null, exact tails unequal and
planning/export refused. No source repair, normalization/denoising, fake footage,
freezes, per-track deletion or independent audio/video timing changes.

Final validation: **180 tests, zero skips, 145.749 s**; **20 focused S09 tests,
zero skips, 21.355 s**. Actual **26.08.2 rev. d4e87e4 / MLT 7.43.0 / Qt 6.11.1**
open/play/group move/undo/save/reopen/render and sanitized native open pass.
Twelve render checks pass: 267 mapped pictures, one switch at output 105, four
zero-lag audio anchors, eight protected probes within 0.1 dB, over 30 dB noise
reduction and peak 0.476731. Native extent delta is zero. The separate exact
20-FPS delayed-switch decode is automated evidence, not a GUI support claim.

Private originals and retained bounded overlap remain unchanged; held-out/full
interview acceptance and private picture/layout calibration are NOT RUN. Keep
private media/labels/names/fingerprints local. No new listening is required for
S09; preserve the one-file/no-new-connection preference and bounded S08 pass.
Current picture support has explicit frame/decoder/stream bounds; read the guide.

Before editing, resolve the containing checkpoint and verify live:

```powershell
git log -1 --format=%H -- docs/handovers/S09.md
python tools/verify_checkpoint.py --repo .
```

The closing chat records actual local/live/upstream equality and exact-SHA CI.
Reverify at the next thread start. Initial queries found zero workflows/runs/
checks/statuses: **CI not configured**, not green CI. Failed synchronization or
configured failing CI overrides continuation and requires resuming S09.

Ready-to-paste next-thread prompt:

> Execute S10 only in InterviewAutoEditor on codex/kdenlive26-overhaul. Read AGENTS.md, STATE.json, NEXT_STEP.md, docs/handovers/S09.md, execution/GitHub protocols, S03-S09 guides and the S10 brief. S09 implementation is 8e31359b0e20941d4fd81e35429d83776e4f47c5. Verify the containing checkpoint, live SHA equality, clean upstream/worktree and exact-SHA CI first. Connect inspect/analyze/plan/export/run/report and compatibility probing through one recoverable application service. Add manifests/reports, cancellation, atomic finalization, cache invalidation/reuse, missing-asset and repeat-run recovery, preserving source-time overrides and every S03-S09 safeguard. Picture observations cannot authorize new deletion or independent retiming; S08 cleanup binds the refined S06 result. Preserve full 12.00/12.45 opening speech, real origin/exact-tail refusals, all protected content/overlap/shared mics/overrides/handles/groups/bin originals and headroom. Keep private data local, held-out acceptance separate and compatibility EXPERIMENTAL. Run applicable G01/G03/G09 and actual Kdenlive regressions if export changes, update state/NEXT_STEP and S10 handover, commit/push/verify, provide a verbose handover and STOP. No S11.

Paused after S09. The next thread should execute S10 only.
