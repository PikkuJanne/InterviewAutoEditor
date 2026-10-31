# S12 attempt 07 — production coverage and real editor checks

Implementation: `a817f93c051bf15041da4f25efcfbcc32fdb1ecd`.
First production coverage commit: `9af678916f1dd42545330904229f7f8519826d71`.
Branch: `codex/kdenlive26-overhaul`. Date: 2026-10-31. **S12 only; acceptance
remains open.** This supersedes earlier claims that unequal-tail production
export and stream-1 picture analysis are unavailable. Earlier evidence is kept.

## Production behavior and exact input lineage

The normal Application/CLI export now accepts an explicit schema-2 request;
the original schema-1 refusals remain. See the
[policy and recovery guide](../project/S12_ORIGINAL_TIMING.md).
No source origin, duration, event, sample or frame timestamp was rewritten.
Unknown numerical offsets and listener precision remain null. Output placement
is the original zero; it is not a verified-zero source certificate.

Each new immutable run records its exact command, implementation SHA, project,
mapping, Analysis/request, models/tools, source hashes, profile hash, approvals
and reason privately. No historical job or failed run was resumed under changed
code. The initial held-out registration/configuration and all prior exposure
records remain unchanged. No settings were fitted to held-out content.

All eight original media fingerprints and 243 earlier private artifact/cache
fingerprints pass the retention check. Commit
`645f5c784b9ce9cb903590919873b7fe969f4b73` remains in ancestry.
Six original audio origin statuses/offsets are unchanged. The existing five
positive review decisions remain qualitative; rejected 2B remains unintelligible
and its timing unscorable. Previous conflicting correlation observations remain
diagnostics, not human measurements or applied offsets.

The existing pending audible safeguard was decoded strictly, checked against
its exact original Analysis/source/window binding and copied into the explicit
v2 request without broadening its scope. The original request bytes and earlier
unapplied jobs remain intact. This is preservation authority only: it creates
no global removal or idle-microphone permission.

## Complete production outputs

| Recording | Audio tracks | Recorded video frames | Shared output frames | Last real audio sample frame, zero based | Full picture observation |
|---|---:|---:|---:|---:|---|
| band_001 | 4 stereo / 192 kHz | 51,092 | 51,093 | 392,388,607 | 51,092 / 51,092 |
| two_person_002, held-out | 2 stereo / 192 kHz | 47,004 | 47,005 | 360,992,767 | 47,004 / 47,004 |

Both actual MP4s contain embedded audio at absolute stream 0 and picture at
absolute stream **1**. Picture analysis selects stream 1, covers the entire
recorded span, and reports **zero unobserved recorded frames**. Missing picture
coverage is separately [51092,51093) or [47004,47005) on the 25 fps project grid.
The longest audio continues 4/375 second beyond the actual picture end. Every
audio track stops at its own real sample end; the rest of the final project
frame is empty. Remaining picture is retained when a participant WAV ends first.

Latest normal-command runs at the implementation above completed atomically in
457.640 s (band) and 394.828 s (two-person), with exit 2: review required. They
reuse the exact complete picture observations from the earlier new-code run;
there is no new model inference or held-out calibration. They contain 113 and
516 native synchronized groups respectively. No time was removed and no
participant idle gain was applied because those permissions are missing.

The per-source media producers are shared across group boundaries. MP4 audio
is disabled. Native master mix gain is the fixed rule 0.95/N, retaining relative
participant levels. Original media remain byte-identical. The original custom
profile (1280x720, 25/1, progressive, SAR 1:1, DAR 16:9, colour space 601) is
preserved, verified against the inline profile and fingerprinted as an input.

## Automated and structural evidence

Final implementation suite: **243 tests, zero skips, zero failures/errors,
425.675 s**. Command: `python -B -m unittest discover -s tools -p 'test_*.py' -v`,
with explicit installed FFmpeg/ffprobe and the existing locked local models and
public development fixture. No new dependency/model/download was introduced.

Focused new checks cover equal endings, either source ending first, the last
sample/frame through the normal command, missing-coverage blanks, shared cuts
and restoration, stale bindings, full-stream picture observation and equivalence
of optimized picture measurements. Legacy export fixtures remain reproducible.
S10/S11 regression tests explicitly reobserve public synthetic picture inputs
after the implementation hash changed; all observation fields other than the
implementation fingerprint must match the historical record. Historical fixture
provenance is untouched. They do not silently rebind real approvals.

Initial failed full-suite logs and failed native launches/renders are kept
privately. A prior assertion used the old version-2 rejection assumption; a
shared-producer assertion counted original starter chains; historical synthetic
picture evidence correctly rejected the changed implementation. These were fixed
and rerun, not deleted or relabelled as passes.

## Actual installed editor and render evidence

Build: **Kdenlive 26.08.2 rev. d4e87e4**, MLT 7.43.0, Qt 6.11.1. The live About
components dialog and executable hash agree with the retained build evidence.
Private action logs separate each actual action from project-file inspection.

Band working copy opened without repair/missing-media prompts and played with
changing recorded picture and active audio meters. A native one-frame group
move changed all five members equally without changing source in/out bounds.
Save, undo and save restored all 565 entries, 113 groups, the original extent
and master gain. Genuine moved/restored saves are preserved separately.
The latest implementation's five members moved from frame 51037 to 51038;
their distinct source ends remained unchanged. The restored project closed and
reopened without repair/missing-media prompts. Its five-member group could
again be selected and opened in the native duration editor, then cancelled.

The latest two-person production output also passed the native numeric group
move. All three members moved from output frame 46726 to 46727, retaining their
different source ends (47004 / 47005 / 47004). A genuine saved-file comparison
verified all 1,548 entries and 516 groups. Undo/save restored every original
source/output bound, the 47005-frame extent and the -6.466127808 dB master.
Earlier failed drag/paste/spin attempts are not passes: direct digit-key entry
and native keyboard checkbox navigation resolved that interaction locally.
The restored project closed and reopened without repair/missing-media prompts;
all three members were selected together. An additional automated quit stalled
after that successful reopen. The exact saved-file hash remained unchanged;
only that owned editor process was stopped. The failure evidence is retained.

The actual installed Kdenlive `--render` command rendered the genuine reopened
native saves to FFV1 / stereo PCM16 at 192 kHz. This is Kdenlive's own preset/render path,
not a separately hand-authored MLT/melt proof; a GUI Render-button click is not
claimed. Final post-reopen renders completed with exit 0 in **600.438 s** (band)
and **440.860 s** (two-person). Each invocation hashes its exact native project
and binds the original generation ledger. Earlier successful renders are also
retained: 825.594 s for the earlier band native save and 529.422 s for the raw
two-person ready output. They are separate runs, not relabelled final evidence.

| Actual render measurement | band_001 | two_person_002 |
|---|---:|---:|
| Rendered stereo sample frames | 392,394,240 | 360,998,400 |
| Original longest audio sample frames compared | 392,388,608 | 360,992,768 |
| Master linear gain | 0.2375 | 0.475 |
| Peak | -7.382716 dBFS | -2.150988 dBFS |
| Full-scale sample values | 0 | 0 |
| Worst original-clock participant-sum error | 0.5 PCM16 LSB | 0.5 PCM16 LSB |
| RMS error | 0.288478 PCM16 LSB | 0.267019 PCM16 LSB |
| Sample values differing by more than 2 LSB | 0 | 0 |
| Nonzero sample values after actual source audio EOF | 0 | 0 |

The exhaustive original-clock comparison includes every source sample and every
group boundary. It establishes sample placement, retained sounds, absence of
added MP4 audio and absence of added discontinuities beyond PCM rounding for
these renders. It does not turn model detections into independent content labels
or establish subjective noise acceptability. The untouched unity sums would
overload (band +5.104066 dBFS; two-person +4.315199 dBFS), which motivated the
generic reversible master setting rather than changing cleaned sources.

Band video decoded to exactly 51,093 rendered frames: 51,092 real picture frames
and one empty frame. Two-person video decoded to 47,005 frames: 47,004 real
picture frames and one empty frame. Every recorded frame in both renders matches
the same-index source frame exactly in the 64x36 gray comparison, including the
last real frame; each empty frame has maximum gray value 1. This is complete ordered frame/coverage evidence,
not a full-resolution RGB pixel-identity claim. Static neighbouring frames are
not promoted to independent numerical sync measurements.

Every original and rendered picture packet also passes the exact presentation
timestamp/duration check: source starts at 0, every picture is spaced by 1/25 s,
and every duration is 1/25 s. Both recordings and both post-reopen renders have
zero timestamp/duration mismatches. The extra output packet is the marked empty
ending. This verifies original picture timing separately from image similarity;
it is not a human numerical audio-sync judgment.

Earlier stripped-profile headless render attempts looped on an empty profile
and were terminated; their logs remain. The production profile fix followed the
actual failure. Kdenlive's versioned
[render entry point](https://raw.githubusercontent.com/KDE/kdenlive/v26.08.2/src/main.cpp)
and [profile repository](https://raw.githubusercontent.com/KDE/kdenlive/v26.08.2/src/profiles/profilerepository.cpp)
were consulted for that diagnosis.

The delivery copies are `.local/S12/attempt-07/band_001-ready-native/project.kdenlive`
and `.local/S12/attempt-07/two_person_002-ready-native/project.kdenlive`.
Immutable normal-command outputs remain in the corresponding `*-ready/` folders;
genuine moved/restored saves and post-reopen renders are separate artifacts.
All source/output bounds in both delivery copies match the original generated
projects after the temporary edit was undone. No owner usefulness-task file was
changed by editor verification.

Normal-command and render wall times above are actual measurements. Earlier
parent-process memory measurements remain in the historical audit; they exclude
decoder children. Full current-pipeline peak memory was not measured, and is
not inferred from those older measurements or synthetic stress results.

## Current G01–G09 scope

| Gate | Evidence now executed | Remaining acceptance limit |
|---|---|---|
| G01 | Eight original media hashes unchanged; both native projects resolve; exhaustive participant-only rendered audio matches | None for these unchanged source outputs |
| G02 | Both exact-build projects open/play/group-move/save/undo/save/close/reopen/render without repair or missing media | Resolved for these two outputs; later corrections need affected checks again |
| G03 | Shared-map/cut/restore tests; every actual audio sample and recorded frame retains its original position | Human judgments are qualitative and section-specific; original offsets remain unknown, with no whole-recording numerical certificate |
| G04 | Every source sample retained in both actual renders; synthetic protected-content tests pass | Independent complete content/held-out labels and their denominators remain incomplete |
| G05 | No time removed; no gap approval invented; stale approvals refuse | Removable/handover labels and separately scoped cut approvals are missing; zero edits is not a 90% result |
| G06 | Actual peaks, no full-scale samples, no added signal/discontinuity beyond PCM rounding | Subjective noise quality and exact source-matched two-noise correction remain pending; no idle suppression result is claimed |
| G07 | Both native groups move all members equally, preserve source bounds and remain editable after reopen; shared-removal/restoration tests pass | Owner's representative correction/quality task remains unanswered |
| G08 | Actual stream 1 fully observed; all recorded frames in order; no introduced flashes in the gray comparison; no picture retiming | Independent selected-section content/picture acceptance remains bounded by supplied human observations |
| G09 | Two new atomic production runs; separate native copies/renders; legacy jobs/failures/caches retained; cancellation/resume/missing-asset tests pass | Future approved changes require new destinations and their own matching evidence |

These rows distinguish executed mechanical checks from unfinished human
acceptance. They do not declare all S12 gates passed.

## Human evidence and remaining acceptance

Two newly requested source sections received positive qualitative sync replies
and a named active speaker. No numerical offset/precision, complete sound labels,
safe pauses or idle microphone labels can be inferred from these replies. Exact
raw observations/source bindings are private; no new comparison file or service
connection was created.

A narrow two-noise reduction received separate approval, but the named WAV is
exact digital zero throughout the reviewed 20 seconds. Another participant WAV
has a burst in the reported second. The approval has **not** been transferred
to that microphone or applied to silence. Only that correction awaits the
source-identity clarification. Both original and later approvals remain private.

Independent content/removable-pause/idle labels, scoped noise acceptance and
actual owner correction-time/quality measurements remain incomplete. Missing
answers hold only the dependent edit/acceptance decision. No missing answer
prevents the program fixes or other project preparation. The **90%** and **70%**
targets remain **unmeasured and unclaimed**. S13-S15 remain pending.
