# S05 next — protect laughter overlap and uncertain sounds

S04 — Implement cached per-participant speech analysis — is **COMPLETE**.
Execute **S05 only** in the next chat after verifying this checkpoint.

- Branch: `codex/kdenlive26-overhaul`.
- S04 implementation: `aea03cf134ea6214c972900e117b03b389f262b9`.
- Latest handover: [S04.md](handovers/S04.md).
- Durable state: [STATE.json](project/STATE.json).
- Next brief: [S05.md](project/steps/S05.md).
- Existing contracts: [S03_CONTRACTS.md](project/S03_CONTRACTS.md).
- Speech setup/limits: [S04_SPEECH.md](project/S04_SPEECH.md).
- Measurements: [S04_SPEECH_EVIDENCE.json](fixtures/S04_SPEECH_EVIDENCE.json).

S04 produces local CPU speech and uncertainty events for every participant and
physical PCM channel. Silero VAD v5.1.2/model SHA, ONNX Runtime 1.20.1, NumPy
2.1.3, licences and transitive Windows/CPython 3.12 wheel hashes are pinned.
Continuous bounded decoding preserves resampler/model state across chunks.
Caches bind source content, inference/settings/runtime and decoder identity.
Model absence/corruption and corrupt cache structures fail visibly; analysis
does not download or substitute a detector. Runtime telemetry is disabled.

**90 tests passed, no skips**. All 16 annotated generated speech regions across
10 channel/case combinations are protected; chunked/single-buffer boundaries
match with zero-sample tolerance. Very soft speech needed uncertainty despite
negative VAD. This is synthetic development evidence, **not full G04**, laughter
protection or real-interview listening acceptance. S05 must evaluate reactions
and uncertainty with proper private labels and separate held-out acceptance.

The full private four-participant/eight-channel recordings were analyzed without
source changes; four caches reused identically. All 102 original preservation
checks passed. The existing S02 GUI render again passed all 11 measurements.
No new Kdenlive GUI editing/export occurred; compatibility is **EXPERIMENTAL**.

Preserve **all** timing findings: 51092 CFR video frames at 25/1, native sequence
extent deltas 0/1, stereo 192 kHz source counts and exact +/-4/375-second tails.
All four S03 origin diagnostics remain UNVERIFIED_INSUFFICIENT_ANCHORS; S01's
different historical correlation findings remain preserved and uncertified.
No alignment, zero offset or drift certificate follows from speech analysis.
V1 exact-coverage export still refuses unresolved tails/unverified origins.
No silent shift, stretch, truncation, padding, gain change or automatic cut.

At next-thread start resolve the checkpoint and verify live:

```powershell
git log -1 --format=%H -- docs/handovers/S04.md
python tools/verify_checkpoint.py --repo .
```

Recheck upstream, intended clean worktree and exact-SHA Actions runs/checks/
statuses. GitHub had no configured workflows at S04 start; absent CI is not a
green run. Resolve any failed synchronization on S04 before advancing. The final
chat records actual checkpoint SHA after normal push; this file cannot embed
its own containing SHA.

Ready-to-paste prompt:

> Execute S05 only in the existing InterviewAutoEditor checkout on
> codex/kdenlive26-overhaul. Read AGENTS.md, STATE.json, NEXT_STEP.md,
> docs/handovers/S04.md, execution/GitHub protocols, S03_CONTRACTS.md,
> S04_SPEECH.md and the S05 brief. S04 implementation is
> aea03cf134ea6214c972900e117b03b389f262b9. Resolve and verify the live S04
> checkpoint before editing. Benchmark and integrate reaction/event evidence
> with speech, per-track noise and uncertainty using local CPU models, pinned
> provenance/licences and labelled private development examples; keep held-out
> acceptance separate. Protect laughter/chuckles/yes/mm-hm and simultaneous talk,
> including events VAD misses. Preserve uncertainty; correlation/bleed is only
> supporting evidence and shared microphones remain inseparable. Preserve all
> sequence-extent/source-tail and uncertified origin/correlation findings. No
> source separation, transcript editorial deletion, silent media repair,
> automatic cuts or camera-recognition dependency. Keep real media, names, paths,
> hashes and transcripts private and compatibility EXPERIMENTAL. Complete S05
> gates, commit/push, verify synchronization and exact-SHA CI, provide a verbose
> handover and STOP.

Paused after S04. The next thread should execute S05 only.
