# S03 next — validate timing and exact contracts

S02 — Prove editable Kdenlive 26 export — is **COMPLETE**. Execute **S03 only**
in the next chat after verifying this checkpoint.

- Branch: `codex/kdenlive26-overhaul`.
- S02 implementation: `9ba13e40551652a267f4fba4a2f9cfde2061984b`.
- Latest handover: [docs/handovers/S02.md](handovers/S02.md).
- Durable state: [docs/project/STATE.json](project/STATE.json).
- Next brief: [docs/project/steps/S03.md](project/steps/S03.md).
- Evidence: [S02 exporter proof](fixtures/S02_EXPORT_PROOF.md),
  [provenance](../tests/fixtures/kdenlive-26.08.2/s02-PROVENANCE.json),
  [render measurements](../tests/fixtures/kdenlive-26.08.2/s02-render-validation.json),
  [S01 real timing observations](fixtures/S01_REAL_INPUTS.md).

The proof build remains Kdenlive 26.08.2 rev. d4e87e4. S02's minimal adapter
exports a new manual shared-cut project with variable named audio tracks,
groups, a guide and MP4 audio disabled. Actual two-participant open/play/group
delete and move/undo/save/close/reopen/GUI render passed. Native entry Volume
keyframes are editable; 400 ms ramps and a −60 dB plateau were measured. Derived
PCM was not needed for this proof. No automatic speech/pause decisions.

All compared timeline semantics match, but whole-project equality is **false**:
native sequence extent grows 275→276 frames while clip coverage and GUI video
render stay 275. Preserve this finding. The real four-track starter reads with
51092 clip frames and initial/saved extent deltas 0/1; it was not exported or cut.
Stereo 192 kHz WAV tail differences and varying subframe correlation findings
remain unchanged. Real alignment is uncertified; do not slide/stretch audio,
retime video or discard source tails silently.

53 public tests passed. The GUI render passed 11 checks: eight mapped picture
anchors, four zero-lag audio windows, MP4 marker 63.085 dB down, measured native
gain and exact 275 video frames. Private corpus recheck passed 102 assertions,
five original hashes and twelve exact PCM excerpts. Compatibility remains
**EXPERIMENTAL**. Subjective listening, real export/quality, subframe native gain,
broader GUI count/fractional/UNC matrix and future builds are still unproved.

S03 implements intake/probing/file mapping, rational frame/sample timing,
shared-origin validation, explicit offset diagnostics and typed versioned
contracts. Detect VFR, truncation, shifted equal-duration audio, unsupported
edited inputs and unresolvable paths; test integer/fractional FPS and mixed
sample rates. Do not implement speculative universal sync or unrequested repair.

At the next thread start resolve the checkpoint and verify live:

```powershell
git log -1 --format=%H -- docs/handovers/S02.md
python tools/verify_checkpoint.py --repo .
```

Inspect newer work, matching upstream and clean intended worktree; compare local
HEAD to live origin. A failed synchronization must finish on S02 first. Final
chat records the pushed SHA; this file does not embed its own containing commit.

Ready-to-paste prompt:

> Execute S03 only in the existing InterviewAutoEditor checkout on
> codex/kdenlive26-overhaul. Read AGENTS.md, docs/project/STATE.json,
> docs/NEXT_STEP.md, docs/handovers/S02.md, execution/GitHub protocols and
> docs/project/steps/S03.md. S02 implementation is
> 9ba13e40551652a267f4fba4a2f9cfde2061984b; resolve the handover checkpoint from
> Git history and verify live local/remote equality and clean intended worktree.
> Implement probing/file mapping, rational frame/sample timing, shared-origin
> validation, explicit offset diagnostics and typed versioned contracts. Detect
> VFR, shifted equal-duration audio, truncation and unsafe edited structures;
> test integer/fractional FPS and mixed sample rates. Preserve S01/S02 sequence
> extent, source-tail and correlation findings, shared-map/MP4-audio rules and all
> originals. Do not silently retime or discard tails. Use the ignored private
> corpus index without publishing its data. Keep compatibility EXPERIMENTAL
> until its required matrix passes. Complete S03 gates, commit, push, verify live
> SHA equality/clean status and exact-SHA CI, provide a verbose handover and STOP.
