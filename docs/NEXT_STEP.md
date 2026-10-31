## What I fixed

Both interviews keep their original timing and complete endings. A new band
copy reduces only the two approved noises on the confirmed microphone; the
continuous answer remains intact. No pause was cut. Resume S12 only; no S13.

Read [state](project/STATE.json), [handover](handovers/S12_ATTEMPT_08.md),
[current audit](fixtures/S12_OWNER_CORRECTION.md),
[production policy](project/S12_ORIGINAL_TIMING.md) and the S12 brief/protocols.
Implementation remains `a817f93c051bf15041da4f25efcfbcc32fdb1ecd`.

## What I tested

The new band native copy passes actual Kdenlive 26.08.2 rev. d4e87e4 open/play,
synchronized move/save/undo/save/close/reopen and full-render checks. The
unchanged two-person project's earlier native/render proof is retained. Audio
scope, source timing/endings, picture packets, excluded MP4 audio and headroom
pass. All eight source hashes, six null audio offsets and 243 old artifact hashes
still match. The unchanged implementation's 243-test pass is reused.

Band delivery: `.local/S12/attempt-08/band_001-corrected-native/project.kdenlive`.
Two-person delivery: `.local/S12/attempt-07/two_person_002-ready-native/project.kdenlive`.

## What I need from Janne

Source identity and additional-event questions are answered. The old pause task
has no safe pause and is closed; do not repeat it or the six-excerpt review.
The remaining short task concerns the actual approved noise correction. Exact
files/timecodes/questions are in `.local/S12/attempt-08/HANDOVER_PRIVATE.md` and
`owner-usefulness/task-private.json`. Actual manual/assisted seconds and the
owner's quality judgment are still missing. Cut and mute approval stay separate.

## What happens next

Codex records replies privately and owns any scoped correction, editor retry,
rerender and evidence update. Keep old projects, jobs, failed runs, held-out
registration, approvals and unknowns recoverable. Do not tune on held-out media,
request existing files or create another comparison/connection. S12 stays open
and 90%/70% stay unclaimed until measured. Verify live Git equality and clean
status at the checkpoint and when resuming S12.

Commit/push status: verify live at checkpoint; final chat records the exact SHA.
