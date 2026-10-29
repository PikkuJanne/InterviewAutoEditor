# Next: S09 - account for recorded Zoom picture switches

**S08 is COMPLETE on applicable synthetic and retained bounded development fixtures, including the direct user listening pass. S09 remains pending and was not started.** Compatibility remains EXPERIMENTAL.

- Branch: `codex/kdenlive26-overhaul`.
- S08 implementation/evidence: `d95514fb6654171efea05980828dedd6b42d998a`.
- Prior blocked checkpoint: `86cfb215ed32333475d79c80e6916fd5e5bc1a10`; listening blocker now resolved.
- Handover: [S08.md](handovers/S08.md), including its dated completion follow-up.
- State: [STATE.json](project/STATE.json).
- Next brief: [S09.md](project/steps/S09.md).
- Cleanup guide: [S08_CLEANUP.md](project/S08_CLEANUP.md).
- Evidence: [S08_CLEANUP_EVIDENCE.json](fixtures/S08_CLEANUP_EVIDENCE.json).
- Actual provenance: [PROVENANCE.json](../tests/fixtures/s08-cleanup-26.08.2/PROVENANCE.json).

The user confirmed the existing 24.5-second synthetic TTS A/B: **"Pass: quieter noise, speech intact, no new clicks"**. This closes the required bounded S08 listening gate. The sample-evaluated speech comparison is separate from actual GUI tone/noise evidence and is not real-interview, alignment, held-out or full-interview acceptance. No further S08 user action or additional listening file is needed.

Existing validation remains unchanged: **159 broad tests, zero skips, 126.573 s**, then **20 final focused S08 tests, zero skips, 9.630 s**. The final focused run included one additional mixed-grid test and final restoration assertion. Actual **Kdenlive 26.08.2 rev. d4e87e4**, MLT 7.43.0, Qt 6.11.1 passed open/play/group movement/undo/save/close/reopen/render and native interval restoration. Eleven cleanup/five restoration measurements pass. Four noise probes are 31.7-43.8 dB down, eight protected probes within 0.1 dB, thirteen exact picture anchors and five zero-lag audio anchors. Output remains six groups/233 frames; peak 0.476731 and native extent delta zero. Earlier one-frame findings remain distinct.

S08 uses separate result-bound idle approvals with protected-event/overlap vetoes, shared-mic unity, all-track Keep/audible restoration, full exterior handles and group-edge unity margins. Canonical v1 protected-source gain refusal remains intact. Fixed -36 dB native ramps last at least 200 ms. Conservative PCM headroom checks give no phase-cancellation credit and never renormalize. One unchanged shared map governs all tracks; no new deletion authority.

For S09, inspect probable picture boundaries near handovers with conservative confidence/layout fallbacks. Refine seams only inside shared eligible silence. Preserve original picture/audio timing during speech and flag uncertain/unavoidable Zoom delays; the 12.00 speech/12.45 picture case must retain the full opening speech. No fake footage, freeze frames, independent video/audio shifts or facial identity requirement.

Keep all protected speech/reactions/uncertainty/overlap, shared microphones, overrides, global approvals, shared map/groups/handles/bin originals and S08 gain safeguards. Original real origins remain unverified/null, tails unequal and real planning/export refused. Keep private data local, held-out/full-interview acceptance separate and one-file/no-new-connection preferences. No source repair, normalization/denoising, per-track removal or camera retiming.

Before editing:

```powershell
git log -1 --format=%H -- docs/handovers/S08.md
python tools/verify_checkpoint.py --repo .
```

The completion chat records actual local/live/upstream equality and final exact-SHA CI. Reverify on the next thread. Initial checks again found zero workflows/runs/checks/statuses: **CI not configured**. Failed synchronization overrides continuation.

Ready-to-paste next-thread prompt:

> Execute S09 only in InterviewAutoEditor on codex/kdenlive26-overhaul. Read AGENTS.md, STATE.json, NEXT_STEP.md, docs/handovers/S08.md including the completion follow-up, execution/GitHub protocols, S03-S08 contracts/guides and the S09 brief. S08 implementation is d95514fb6654171efea05980828dedd6b42d998a; direct user listening feedback closed its bounded synthetic gate. Verify the containing completion checkpoint, live SHA equality, clean upstream/worktree and exact-SHA CI first. Implement picture-boundary analysis near handovers and safe shared-silence seam rules within S09. Preserve the full 12.00 speech/12.45 picture opening, original picture/audio timing during speech, all protection/overlap/shared mics/overrides/global approvals/shared map/groups/handles/bin originals, S08 gain/headroom safeguards and real-origin/tail refusals. Use conservative gallery/pinned/camera-off/uncertain fallbacks. No invented footage, freezes, independent retiming or facial identity requirement. Keep private data local, held-out acceptance separate and compatibility EXPERIMENTAL. Complete applicable G08 and actual Kdenlive regressions if export changes, update state/NEXT_STEP/S09 handover, commit/push/verify, provide a verbose handover and STOP. No S10.

Paused after S08. The next thread should execute S09 only.
