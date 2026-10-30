# S12 attempt 04 — one local sync review prepared

**S12 remains BLOCKED; no S13.** The owner requested “Prepare one short local
review.” This continuation prepares that one review, preserving the supplied
timing. It does not approve alignment, cuts, idle attenuation or utility.

The single private H.264/AAC MP4 is **62.12 seconds / 1553 frames**, with six
numbered A/B pairs. Each pair repeats the same four seconds of original picture:
**A** uses Zoom's original embedded reference sound; **B** uses one supplied
participant track at that same original clock position. Each participant has
early/middle/late coverage. The participant tracks are never summed together.
Original files are not shifted, trimmed, stretched, leveled, normalized or denoised.
Temporary review buffers resample 192 kHz to 48 kHz with 600 ms guards and no
dither, preserving both physical stereo channels. This comparison is not the
product export; original MP4 audio is deliberately confined to the labelled A
reference. Existing product exclusion/refusal rules remain unchanged.

The six windows are selected deterministically from existing model speech events
near fixed early/middle/late targets, with a 0.4 s preroll, within each recording
third. Selection is explicitly model-assisted, not independent human ground
truth. No new inference or model/policy calibration occurs. Existing held-out
registration/exposure is retained; preparing these excerpts does not establish
held-out content or utility acceptance. Media, exact source cues, fingerprints,
selection records and instructions remain ignored/private.

**PASS — actual review artifact QA:** all eleven checks pass. There are 36
sampled A/B picture anchors against original source positions, under the existing
<4 RGB MAE criterion, with zero offset best or within the declared 0.02-MAE tie
bound. All twelve audio encoding anchors have best added lag zero on the 48-sample
(1 ms) grid against the unshifted assembled review PCM. These test the presentation,
not the source's original alignment. Both streams start at zero; output has two
48 kHz audio channels. The decoder emits 2981888 samples/channel versus 2981760
intended samples, with 128 AAC suffix-padding samples. Peak is below full scale.
Intro/A/B decoded stills were visually inspected: readable labels in a separate
header, with original picture geometry retained.

All three source fingerprints, original analysis and every frozen core byte are
unchanged. Nine historical Application manifests validate read-only. Tight and
Gentle still refuse the two-person input for its original unverified origins.
No source has been certified or repaired, no independent cut/idle approval was
created, and no production project was exported. The earlier EOF preview/native
proof and complete-interview/long-stress measurements remain scoped evidence in
[attempt 03](S12_ATTEMPT_03.md) and [attempt 02](S12_ATTEMPT_02.md).

The private local review was linked and embedded in chat. The app-panel request
returned **queued**, not confirmed playback. Owner feedback is **PENDING**.
The focused response is SAME, CLEARLY OFF or UNSURE for pairs 1–6; an absent or
non-speaking face is unjudgeable. This asks for no broad replay or extra files.
The one-comparison-file/no-new-connection preference is preserved. Do not create
a second comparison or infer acceptance from this preparation request.

No tracked implementation/test/core/adapter/desktop/model/settings/lock/licence
or fixture changed. Implementation remains
`645f5c784b9ce9cb903590919873b7fe969f4b73`. Its **237 tests / zero skips / 254.017 s**
are retained attempt-03 evidence, not a fresh full-suite run. Applicable new
checks are actual media QA plus state/document/privacy consistency. Original
32.5 ms/insufficient-anchor diagnostics, null offsets, source ends, protected
events, shared maps, refined cleanup bindings and recoverable jobs remain intact.
All real edited-output, human-label, noise/sync/editability/correction-effort and
focused owner utility gates remain unrun. The 90%/70% targets remain unmeasured.

See [machine evidence](S12_SYNC_REVIEW.json), [handover](../handovers/S12.md),
[procedure](../project/S12_VALIDATION.md) and [NEXT_STEP](../NEXT_STEP.md).
Resume S12 only, recording actual source-bound feedback without upgrading a
bounded excerpt judgment to a full-recording certificate. No S13.
