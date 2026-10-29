# Resume S08 — listening feedback pending

**S08 implementation and measured/actual-application checks are complete, but the required human listening comparison is pending. S08 remains BLOCKED; do not start S09.** Compatibility stays EXPERIMENTAL.

- Branch: `codex/kdenlive26-overhaul`.
- Implementation/evidence: `d95514fb6654171efea05980828dedd6b42d998a`.
- Initial work: `61085b5ab4b0532da4033a7d842e91a2112240ae`.
- Handover: [S08.md](handovers/S08.md).
- State: [STATE.json](project/STATE.json).
- Brief: [S08.md](project/steps/S08.md).
- Guide: [S08_CLEANUP.md](project/S08_CLEANUP.md).
- Evidence: [S08_CLEANUP_EVIDENCE.json](fixtures/S08_CLEANUP_EVIDENCE.json).
- Actual provenance: [PROVENANCE.json](../tests/fixtures/s08-cleanup-26.08.2/PROVENANCE.json).

Separate strict idle approvals leave canonical v1 gain refusals unchanged. Independent labels, protected content/overlap, all-track Keep/audible restoration, shared microphones, exterior handles and group seams constrain cleanup. Fixed -36 dB native ramps last at least 200 ms. One unchanged shared map governs all tracks; no new removal authority.

Broad suite: **159 tests, zero skips, 126.573 s**. Final focused S08 suite: **20 tests, zero skips, 9.630 s**, including one later mixed-grid test and final restoration assertion. All existing local CPU models/development assets enabled; no dependency/model/contract/inference changes.

Actual **Kdenlive 26.08.2 rev. d4e87e4**, MLT 7.43.0, Qt 6.11.1 passed open/play/native group movement/undo/save/close/reopen/render and native interval restoration. Eleven cleanup/five restoration measurements pass. Four noise probes are 31.7–43.8 dB down; eight protected probes within 0.1 dB. Thirteen picture anchors exact, five audio anchors zero measured lag, peak 0.476731. Six groups/233 frames, native extent delta zero; prior one-frame findings remain distinct. Native restore returns a suppressed interval to -0.087 dB relative to original without changing other cleanup.

One **24.5-second local synthetic TTS A/B** is presented: untreated **0–12 s**, cleaned **12.5–24.5 s**; noise **6.6–8.2 versus 19.1–20.7 s**. Three utterances/**187474 samples** stay exact under sample evaluation; noise plateau -36.013 dB, unchanged peak. This speech file is not a GUI render or real/held-out acceptance. Human confirmation of quieter noise, intact quiet responses and no new clicks/chopped syllables is still missing. No reply is not a pass. Reuse this one file; no new recording/connection.

Retained human overlap stays unity with no independently approved idle labels: 200/200 frames intact. Original corpus passes 102 assertions, five unchanged originals/twelve exact excerpts. Real origins remain unverified/null and tails unequal; planning/export refuse. No source repair, normalization/denoising, per-track removal or camera retiming. Private data local; held-out/full-interview acceptance separate.

Before resuming:

```powershell
git log -1 --format=%H -- docs/handovers/S08.md
python tools/verify_checkpoint.py --repo .
```

The closing chat records final actual local/live SHA and exact-SHA CI. Initial workflows/runs/checks/statuses absent: **CI not configured**. Verify again; failed sync is an additional blocker, never permission for S09.

Ready-to-paste prompt:

> Resume S08 only in InterviewAutoEditor on codex/kdenlive26-overhaul. Read AGENTS.md, STATE.json, NEXT_STEP.md, docs/handovers/S08.md, execution/GitHub protocols and S03–S08 guides. Implementation/evidence is d95514fb6654171efea05980828dedd6b42d998a. Verify containing checkpoint, live SHA equality, clean upstream/worktree and exact-SHA CI first. Only human feedback on the existing one-file 24.5-second local synthetic A/B remains: before 0–12 s, after 12.5–24.5 s; noise 6.6–8.2 versus 19.1–20.7 s. Reuse this file/measurements, no new connection/audio. Preserve protection/shared mics/overrides/global approvals/shared map/groups/handles and real origin/tail refusals. Record bounded feedback honestly, fix only if needed, update S08 state/evidence/handover, commit/push/verify and STOP. Do not start S09.

Paused with S08 blocked. The next thread must resume S08.
