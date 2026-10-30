# S12 attempt 05 — rejected review pair and fidelity investigation

**S12 remains BLOCKED; no S13.** The owner reports that pairs **1, 3, 4, 5 and
6 work**, while **pair 2B is unintelligible**. Both the initial severe “off” report
and the clarification are retained against the exact private artifact/source/
project/analysis/window identities. This confirms owner-reported playback, not
the app panel's route. Five positive qualitative excerpts are not a full-recording
certificate. Pair 2 remains rejected and **unscorable for sync**; no human timing
magnitude, word/reaction boundaries, gap or idle approvals were supplied.

## Actual investigation

Read-only checks trace the existing B2 passage back to the original WAV:

- Independent native-rate container decoding equals Python's original PCM bytes.
- Independent resampling continuously from the actual file origin equals the
  previous guarded 48 kHz review buffer **exactly: zero differing sample values**.
- All **192000 stereo sample frames / 384000 values** of encoded B2 are compared
  with its unshifted expected buffer. Encoder-reproduction SNR is
  **44.602707 dB**, channel correlations exceed **0.99998**,
  and decoded peak **0.843595386** is below full scale. Both input
  channels are identical in this window. The other eleven A/B segments were also
  measured. These are encoding-fidelity metrics, not idle-noise suppression.

No gross extraction/resampling/stored-AAC corruption is detected. This points to
the selected source passage rather than an added conversion error, but the exact
cause of what the owner heard remains unestablished. Numerical reproduction does
not prove intelligible source speech or a particular player's playback behavior.
The earlier construction-QA pass therefore remains scoped; it cannot overrule
this failed human review. The model-selected passage was unsuitable for sync
judgment. No model threshold is fitted to this held-out case, no replacement is
silently selected, and the failed case is not removed from evidence.

## Additional original-clock diagnostics

The unchanged S03 2 kHz / four-second / +/-100 ms method was applied to **all six
pre-existing review windows**, including rejected pair 2. Positions were fixed
before owner feedback. These are additional event-assisted diagnostics, not a
replacement for the earlier thirteen regularly spaced anchors.

| Source | Existing review pairs | Estimated lags | Diagnostic outcome |
|---|---|---|---|
| participant_01 | 1, 4, 5 | -10 / +32.5 / +32.5 ms | INCONSISTENT_LAGS_REVIEW_OFFSET_OR_DRIFT |
| participant_02 | 2, 3, 6 | +32.5 / +32.5 / +32.5 ms | OFFSET_DETECTED |

Every added anchor passes the unchanged local reliability rules, including B2's
0.761423 correlation score despite its human-reported unintelligibility. This
demonstrates why correlation is not intelligibility or origin certification.
The early disagreement is retained; it is not discarded or explained as proven
drift. The prior ten +32.5 ms anchors and prior insufficient-anchor result remain
historical evidence. No offset is applied, no source becomes verified zero, and
all original source statuses/null offsets/analysis records remain unchanged.

## Preservation and checkpoint boundary

A private **pending source-time audible request** binds the exact unchanged
analysis and covers the rejected four-second source window. Under the existing
policies it retains time on all tracks and restores unity on all microphones.
It contains **zero gap/idle approvals**, changes no job, and grants no export
authority. Tight/Gentle still refuse current origins with it. Different analysis
or refined cleanup plans require explicit matching reviewed bindings. This keeps
uncertain possible content available; no trimming, muting, denoising, replacement,
normalization, repair or picture/audio shift is authorized.

The original review and all source hashes remain unchanged. Exactly **one** S12
comparison remains; **no new media or connection** was created. Core, adapter,
desktop, models/settings/locks/licences, prior fixtures, caches and recoverable
Application jobs remain intact. No new Kdenlive operation or inference/tuning.
Implementation remains `645f5c784b9ce9cb903590919873b7fe969f4b73`. Its **237 tests / zero skips / 254.017 s** are
retained attempt-03 evidence; the full suite was not repeated for metadata-only
work. Actual new checks are native/resampling/AAC fidelity, diagnostics, strict
pending-request/refusals, provenance and documentation/privacy consistency.

Remaining: reviewed baseline evidence consistent with all observations, explicit
production EOF integration, independent content/removable-gap/idle labels and
approvals, accepted real editable outputs and actual full/held-out retention,
noise/sync/editability/correction-effort/owner utility metrics. The 90%/70%
targets remain unmeasured. Preserve the one-file/no-new-connection preference;
the owner need not repeat the full review merely to restate this rejection.

See [evidence](S12_SYNC_FEEDBACK.json), [prior review construction](S12_SYNC_REVIEW.md),
[handover](../handovers/S12.md) and [NEXT_STEP](../NEXT_STEP.md). Resume S12 only.
