# S12 attempt 08 — approved correction and remaining owner usefulness review

Production code remains `a817f93c051bf15041da4f25efcfbcc32fdb1ecd`. The operator
edit began at checkpoint `1ddf529509a6cbf02ee1824789f1118fe9d96f17` on
`codex/kdenlive26-overhaul`. **S12 remains incomplete; no S13.** Previous
[production evidence](S12_PRODUCTION_COVERAGE.md) and all failed attempts remain.

## Scope and review handling

The owner resolved the two-noise source question. The narrow prior approval now
matches the actual participant source. A new native working copy contains one
editable Volume effect with two -24 dB dips and short fades. This is an explicit
owner-approved manual correction after the normal production export, not an
automatic idle-microphone decision or a relaxed protection rule. Production
code, models, presets, inference and held-out settings are unchanged.

Raw replies, exact source hashes, operator script hash, original timecodes,
waveform bounds and actual editor actions remain in private attempt-08 ledgers.
The human times were approximate; numerical listener precision is unset. The
operator placed fades around the two confirmed bursts, including an onset just
before the listener's rounded second. Waveform support is not independent
listening evidence. No other participant effect or shared time removal was added.

The requested additional-event questions are answered for both selected source
sections. Their existing main-speech and positive qualitative sync observations
remain. No additional short replies, laughter, overlap, unclear sounds, safe
pauses or idle intervals were reported; this does not create mute authority or
a word-by-word annotation denominator. Five older positives and rejected,
timing-unscorable 2B remain unchanged. The previous pause usefulness task is
closed as ineligible: the answer is continuous and no safe pause was identified.
It contributes no correction-time or pause-automation measurement.

All eight media hashes, six original null audio offsets, original analyses,
both immutable normal runs, both earlier native/render inputs and 243 earlier
private artifact hashes pass retention checks. Initial held-out registration,
old jobs, failures and past approvals remain recoverable.

## Actual native project and render

New delivery: `.local/S12/attempt-08/band_001-corrected-native/project.kdenlive`.
The unchanged two-person delivery remains
`.local/S12/attempt-07/two_person_002-ready-native/project.kdenlive`; its previous
exact-build open/play/group-edit/save/reopen/full-render proof is reused.

In actual **Kdenlive 26.08.2 rev. d4e87e4**, the new band copy opened without
repair or missing-media prompts and played the corrected passage with changing
picture and active meters. A native one-frame move changed all five members of
the final group together. Save, undo and save restored every source/output bound.
The genuine save closed and reopened; the corrected participant's native Volume
keyframe curve and editable gain controls were visible. All 565 entries, 113
groups and exact approved gain keys survived. One stale non-target screenshot
was discarded; activating the selected editor and recapturing resolved it before
any input. Existing user editor instances were not altered.

The installed Kdenlive `--render` path rendered that exact reopened native save
to FFV1 / stereo PCM16 at 192 kHz, exit **0**, **588.500 s**.
This is an actual installed-editor render, distinct from XML checks and
synthetic evidence; no GUI Render-button action is claimed.

| Measured result | Value |
|---|---:|
| Output stereo sample frames | 392,394,240 |
| Original longest audio sample frames retained | 392,388,608 |
| Mix peak | -7.382716 dBFS |
| Full-scale values / nonzero values after real source EOF | 0 / 0 |
| Outside approved fades: worst change from previous actual render | 0 PCM16 LSB |
| Outside fades: worst original-clock participant-sum error | 0.500000 PCM16 LSB |
| Approved flat gain: worst original-clock mix error | 0.500368 PCM16 LSB |
| Every sample including fades: worst unfitted native-gain reference error | 0.500368 PCM16 LSB |
| Measured corrected-source reductions, two plateaus | -23.999803 / -23.999284 dB |
| Recorded / rendered picture frames | 51,092 / 51,093 |
| Different encoded picture packets versus prior fully checked render | 0 |
| Picture timestamp/duration mismatches | 0 |

The audio comparison examines every sample outside the two short fade envelopes
and tests the intended source-only reduction against the other unchanged
participant samples inside both flat plateaus. The native unity-key boundary
checks quantify extra sample steps. Native frame interpolation is reported
explicitly, not treated as a source-clock shift or guessed human timing.
These are engineering checks, not subjective noise/click acceptance.

An explicit gain reference also tests every sample inside the fades. It evaluates
the approved dB keys and interpolates amplitude from the previous native frame's
gain to the current one, following the
[MLT volume implementation](https://github.com/mltframework/mlt/blob/master/src/modules/normalize/filter_volume.c).
The reference is tested against the installed build's actual output; that
upstream source is not claimed to identify the exact compiled binary. No lag,
gain or offset is fitted to the render. The initial raw-step assertion failed
on steps of 8 and 9 PCM16 LSB: it incorrectly treated the source transient as a
gain discontinuity. Its result and failure remain retained. The corrected
check accounts for the declared source gain and native fade, with maximum
whole-render residual 0.500368 PCM16 LSB and boundary residual steps below 1 LSB.
The media and correction were not changed or rerendered to pass that check.

Task-copy preparation also initially compared native group JSON ordering.
Kdenlive had reordered its serialization; an independent canonical comparison
confirmed identical group membership, source/output bounds and master level.
Preparation then passed without changing either project.

All 51,093 current FFV1 picture packets and presentation timestamps match the
prior actual render, including the last real and marked empty frame. Its earlier
full source-frame comparison was at 64x36 gray; no new full-resolution source-RGB
identity claim is made. The original MP4 audio is absent from the measured
participant-only mix. Leading/trailing content, the continuous answer and
original picture timing are retained.

The unchanged implementation's **243 tests / zero skips/failures/errors /
425.675 s** remain applicable; no unnecessary full-suite rerun is claimed for
this private native edit and documentation checkpoint. New actual editor,
render, source-retention and documentation checks are separate evidence.

## Remaining acceptance and usefulness

Only the final owner judgment about this correction and the actual comparable
manual/assisted correction-time and quality measurements remain requested.
Exact local files, original timecodes and one representative task are in the
private handover and `owner-usefulness/task-private.json`. It uses the approved
noise correction rather than asking for a pause inside speech. Both task copies
have identical source timing, groups and master level; only the prepared noise
effect differs, so level differences cannot bias the task.

No automatic pause or general idle-microphone edit is inferred. Unknown word
counts, human numerical offsets, precision and correction times stay unset.
Neither the **90%** pause target nor **70%** effort target is claimed. Native
noise reduction is measured on this scoped operator correction, not advertised
as automatic noise-detection accuracy. S12 cannot be marked complete while its
required owner utility/quality result is missing; S13-S15 remain pending.
