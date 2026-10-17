# S04 next — cached per-participant speech analysis

S03 — Validate media timing and define exact data contracts — is **COMPLETE**.
Execute **S04 only** in the next chat after verifying this checkpoint.

- Branch: `codex/kdenlive26-overhaul`.
- S03 implementation: `8ee7fb69ecf11e840d1094c31183fc0ceefeb93f`.
- Latest handover: [docs/handovers/S03.md](handovers/S03.md).
- Durable state: [docs/project/STATE.json](project/STATE.json).
- Next brief: [docs/project/steps/S04.md](project/steps/S04.md).
- Interfaces and usage: [S03_CONTRACTS.md](project/S03_CONTRACTS.md).

The new read-only core probes full video timestamps and exact WAV sample counts,
requires explicit file/participant mapping and reports all tail/origin problems.
Strict typed v1 analysis/edit-plan contracts use rational time and one shared map.
75 tests passed with no skips, including integer/fractional FPS, mixed rates,
500 retained segments, VFR, truncated files and decoded shifted equal-duration
audio. S02's unchanged GUI render again passed all 11 measurements.

The actual private four-participant corpus remains unchanged and **uncertified
for alignment**. Full video audit: 51092 CFR frames at 25/1. Native sequence
extent deltas remain 0/1 before/after save, separate from clip coverage. The
stereo 192 kHz WAVs retain their exact source sample counts and ±4/375-second
tail differences. The new bounded diagnostic windows provide insufficient
reliable anchors; they do not replace S01's original varying correlation findings.
No sources were shifted/stretched or tails discarded. The v1 `exact_coverage`
plan policy refuses unresolved tails/unverified origins; non-destructive analysis
must propagate those flags. Compatibility remains **EXPERIMENTAL**.

S04 adds local CPU speech detection, pinned model/runtime provenance/licence,
bounded stateful decode/inference chunks, cached results and conservative
uncertainty records. Test soft speech/short acknowledgements, chunk equivalence
and missing-model errors. No automatic cuts, source repair or loudest-speaker
selection. Do not mistake speech detection alone for laughter protection.

At next-thread start resolve the checkpoint and verify live:

```powershell
git log -1 --format=%H -- docs/handovers/S03.md
python tools/verify_checkpoint.py --repo .
```

Recheck upstream, worktree and exact-SHA CI. Synchronization failure must be
resolved on S03 before advancing. Final chat records the actual pushed checkpoint
SHA; this file does not embed its own containing commit.

Ready-to-paste prompt:

> Execute S04 only in the existing InterviewAutoEditor checkout on
> codex/kdenlive26-overhaul. Read AGENTS.md, STATE.json, NEXT_STEP.md,
> docs/handovers/S03.md, the execution/GitHub protocols,
> docs/project/S03_CONTRACTS.md and the S04 brief. S03 implementation is
> 8ee7fb69ecf11e840d1094c31183fc0ceefeb93f. Resolve and verify the live checkpoint
> before editing. Implement local CPU per-participant speech analysis with pinned
> model/runtime provenance/licence, bounded chunks/model state, cache identity
> and conservative uncertainty events. Test soft speech, short acknowledgements,
> chunk equivalence and visible missing-model failure. Preserve the sequence
> extent, exact source tails and uncertified origin/correlation findings; no
> silent shifting/stretching/truncation or automatic cuts. Keep real media,
> names, paths and source hashes private and compatibility EXPERIMENTAL.
> Complete S04 gates, commit/push, verify synchronization and exact-SHA CI,
> provide a verbose handover and STOP.

Paused after S03. The next thread should execute S04 only.
