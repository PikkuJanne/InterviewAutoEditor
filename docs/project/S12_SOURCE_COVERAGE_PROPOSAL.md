# S12 source-clock and end-coverage proposal

**30 October continuation: empty-ending preference ACCEPTED; production export
integration and alignment review PENDING.** The owner confirms leveling alone
retained the new interview's original timing and accepts preserving all audio
with a marked empty ending. Neither answer accepts alignment, cuts or idle gains.
Current v1 origin and `exact_coverage` refusals remain unchanged. Neither interview
has an accepted edited output. Source media stays private and recoverable.

Attempt 03 adds a strict v2 **offline coverage preview**, plus a generated native
EOF experiment. See [current evidence](../fixtures/S12_ATTEMPT_03.md). The preview
keeps the complete original Analysis, null offsets and source counts; it records
coverage-only authority and cannot load as an EditPlan. Application and desktop
do not accept it. It is not a source-clock certificate or automatic migration.

The supplied real recordings expose a limitation of the current strict input
contract. Their small unequal ends do not, by themselves, establish damaged media
or justify asking the owner to trim the files. Supporting them safely needs an
explicit policy rather than invented equal durations or implicit certification.

## Measured input clocks

| Neutral corpus | Video frames / FPS | Exact video end | Audio end minus video end |
|---|---|---|---|
| Band development recording | 51092 / 25 | 2043.68 s | Three at -4/375 s; one at +4/375 s |
| Two-person held-out recording | 47004 / 25 | 1880.16 s | One at -4/375 s; one at +4/375 s |

All six participant WAVs have a measured sample rate of 192000 Hz. The differences
are approximately -10.667 or +10.667 ms. Native clip coverage, native sequence
extent and exact source ends remain distinct measurements. The additional native
sequence frame observed on save/reopen is not an extra captured picture.

For the new two-person input, unchanged S03 diagnostics at thirteen fixed source
positions find ten reliable anchors on one source at +65/2000 s and two reliable
anchors on the other at the same lag. Positive lag means the participant occurs
later than the embedded MP4 reference mix. The first source is diagnosed
`OFFSET_DETECTED`; the second has insufficient reliable anchors. These results
suggest a 32.5 ms baseline delay; they do not identify its cause, certify the
second source, establish lipsync or authorize shifting anything.

The existing band origin evidence remains unverified. The owner's confirmation
of production volume leveling supplies processing provenance, not an automatic
zero-offset certificate. The owner now confirms the new WAVs retained original
start/end timing through leveling only. This remains separate from alignment
acceptance and does not turn the measured 32.5 ms diagnostic into zero.

## Proposed source-clock treatment

Preserve every file at its original starter-clock position and record any
accepted baseline mismatch explicitly. Do not advance video, slide audio, change
speed or claim a measured nonzero lag is verified zero. Reviewer, actual source
fingerprints, project/analysis fingerprints, diagnostic limitations and the exact
accepted baseline would be mandatory in a new explicit review record.

Acceptance of an original baseline must be an actual reviewed decision. It
cannot be inferred from volume leveling, equal durations, negative VAD or this
proposal. Additional evidence is required for sources without sufficient anchors.
Original analysis statuses, null offsets, diagnostics and historical jobs remain
available; no existing record is rewritten as certified.

## Proposed treatment of unequal ends

To retain every original sample, end the shared timeline on the first project
frame boundary at or after **all** actual source ends. Record the uncovered
interval after each source EOF as explicit empty timeline coverage. This changes
neither original files nor their declared original clock positions.

| Corpus | Proposed shared end frame | Proposed shared end | Uncovered recorded picture |
|---|---|---|---|
| Band | 51093 | 2043.72 s | One final frame, [2043.68, 2043.72) |
| Two-person | 47005 | 1880.20 s | One final frame, [1880.16, 1880.20) |

The final empty picture interval must be visibly marked as missing recorded
coverage. It cannot freeze the previous picture, invent a camera view or move
later footage into earlier time. Each audio source contributes all its measured
samples, including the +10.667 ms tail. Beyond actual EOF, only explicitly
declared empty coverage is permitted; no replacement WAV or physical silence
padding is created. In these cases the resulting empty audio coverage would be
11/375 s for the longer sources and 19/375 s for the shorter sources.

This is a proposal for representing absence after EOF. It does not authorize
shortening a real pause, muting idle audio, removing a tail or trimming either
exterior handle. Global removals and source-local attenuation still need their
own independent approvals and protected-content checks. A single shared time
map must still govern every track and the declared empty coverage.

## Required implementation and evidence before use

No current Application/desktop option accepts this proposal. The new offline
coverage review/preview records are explicitly v2 and bind the exact unchanged
Analysis. A reviewed baseline contract and corresponding planner/export handling
are still required. Existing v1 files retain their meanings and refusals; there
is no silent migration or automatic approval rebinding.

Before enabling such a contract, prove exact source-sample retention through
partial final native audio frames, absence of EOF repeats/freezes, correct
picture gaps, shared duration, protected exterior content and recoverable bin
originals. Test both sources shorter/longer than video, mixed sample rates,
fractional FPS, changes to review bindings, cancellation/recovery and source-time
Keep/audible. Cleanup must bind the exact refined plan and retain unity on all
protected events, shared microphones and overlap.

Actual Kdenlive 26.08.2 open/play/group-move/undo/save/close/reopen/render now
passes for a separately constructed 12-second synthetic N2/192 kHz mono case.
All 300 recorded picture anchors retain their timing, frame 301 is black, and
the complete rendered PCM matches a fixed mono-to-stereo reference within one
LSB, including the final source sample. Raw mono-sum unity and pixel identity
are explicitly false: channel/image conversion remains visible in the report.
The native sequence adds one extent frame on reopen while clip bounds stay
unchanged; the actual GUI render still contains 301 frames. This is scoped
representation evidence, not a production adapter or real stereo acceptance.

Until the baseline decision, missing evidence and tested production integration exist,
real planning/export remain blocked. Preserve the complete read-only analyses,
source inventories, draft review records and recoverable jobs for resuming S12.
