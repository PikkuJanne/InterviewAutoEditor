## What I fixed

The picture ends first in both interviews. New projects keep the audio to its
real end and mark the empty picture. Earlier-ending microphones stop at their
own ends; remaining picture and other microphones continue. Original recordings
keep their timing and levels. Approved time removals still move all tracks
together.

The tested delivery copies are
`.local/S12/attempt-07/band_001-ready-native/project.kdenlive` and
`.local/S12/attempt-07/two_person_002-ready-native/project.kdenlive` in the existing
checkout. Immutable exports remain in the corresponding `*-ready/` folders.
Exact sources, hashes, commands and approvals
are recorded in private attempt-07 ledgers; old outputs and failures remain.

Implementation: `a817f93c051bf15041da4f25efcfbcc32fdb1ecd`. First production fix:
`9af678916f1dd42545330904229f7f8519826d71`. Original commit
`645f5c784b9ce9cb903590919873b7fe969f4b73`, held-out registration, unknown offsets
and earlier six review decisions remain recoverable. No held-out tuning occurred.

## What I tested

Both normal exports completed. Picture analysis now selects the actual picture
stream and observes the full recording; no recorded interval is unobserved.
The band retains 51,092 picture frames in a 51,093-frame project; the two-person
interview retains 47,004 in 47,005 frames, at the original 25 fps.

Both full renders after native save/reopen completed through installed Kdenlive
26.08.2 rev. d4e87e4, in 600.438 s (band) and 440.860 s (two-person).
Every original audio sample agrees at its original position within 0.5 PCM16
step. Peaks are -7.38 dBFS (band) and -2.15 dBFS (two-person), with no overloads.
All picture frames, including the last, agree in order in the small gray-frame
comparison. Each next frame is empty. These measurements do not replace human
judgments about the original sounds.
Every original/rendered picture timestamp and duration also matches the original
25 fps clock exactly, with no offset or rate change.

Both editable projects opened and played. Native synchronized moves, save, undo
and save passed for the band's five members and the two-person interview's three
members, with original source bounds retained. Both native saves closed and
reopened without repair or missing-media prompts. Their groups remained
selectable and editable, and every source/output bound matched after undo.
Failed automated drag/paste/spin attempts are retained and are not counted as
passes; literal digit-key entry and native keyboard controls resolved the edits
locally. An extra two-person automation quit stalled after successful reopen;
the saved project was unchanged, and only that owned process was stopped.

All **243 automated checks passed**, without skips, failures or errors, on the
implementation above. All eight source fingerprints and 243 earlier private
artifact/cache fingerprints still match. The [audit](../fixtures/S12_PRODUCTION_COVERAGE.md),
[measurements](../fixtures/S12_PRODUCTION_COVERAGE.json) and
[policy guide](../project/S12_ORIGINAL_TIMING.md) retain commands, failures,
recovery and distinctions between synthetic, file, editor and listening evidence.

## What I need from Janne

The two new sync replies are acceptable qualitative observations. Numerical
offsets and precision remain unset. Five earlier positives remain positive;
2B remains rejected and impossible to judge for timing.

The remaining listening questions use existing local sources, with no model
cuts/mutes shown. Exact files, original timecodes, participants, questions and
answer choices remain local in `.local/S12/attempt-07/HANDOVER_PRIVATE.md` and
`remaining-human-questions-private.json` beside it. They cover the source of
the two reported noises and missing sound/pause/idle observations in the two
already selected short sections. Only the corresponding correction or
acceptance decision waits. No approval has been transferred to another source.
Describing an idle microphone does not authorize muting it.

Reuse supplied observations; no new timing judgment or six-excerpt review is
requested. If timing is later questioned, accept **acceptable / unacceptable /
can't tell**, leaving numerical precision unset. Cut and mute approvals remain
separate. Raw replies and review details are excluded from this public report.

One short usefulness task is prepared in
`.local/S12/attempt-07/owner-usefulness/`, with `manual-baseline/project.kdenlive`
and `assisted/project.kdenlive`. In the privately specified source window, choose one pause
personally judged safe, shorten the same pause across picture and all four
microphones, and save a copy in each project. Record actual manual/assisted
seconds including listening/review, original pause timecodes and quality:
**useful / needs changes / not useful**. If no pause is safe, say so. This grants
no microphone mute. No valid earlier correction-time measurement was found.

Unprovided reply/laughter/overlap/unclear-sound/safe-pause/idle labels stay unknown.
Only their dependent edits and acceptance decisions are held. No new comparison
file or connection was created. Review material stays private.

## What happens next

Codex records Janne's replies privately, applies only a
correction whose source and approval agree, and reruns affected validation.
S12 remains incomplete. The 90%/70% targets are unmeasured and unclaimed.
S13-S15 remain pending.

Next prompt if needed: **Resume S12 only in the existing checkout. Read this
handover and current state/audit, verify the live checkpoint, complete only the
remaining recorded human gates and any resulting correction checks, preserve all sources, approvals and
failures, commit/push and stop at S12.**

Branch: `codex/kdenlive26-overhaul`. Resolve this handover's own checkpoint from
Git history. The full suite applies to the implementation above; later docs-only
changes need state/privacy/live synchronization checks. GitHub has no configured
workflows, which is not green CI. Paused with S12 blocked on the named human
decisions. The next thread must resume S12.

Commit/push status: verify live at checkpoint; final chat records the exact SHA.
