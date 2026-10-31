## What I fixed

Both interviews now generate new editable projects with their original timing
and full endings. Audio continues after the picture ends, and the empty picture
is marked. Original recordings, old runs and review decisions remain recoverable.
S12 is still open; do not start S13.

Read [state](project/STATE.json), [current handover](handovers/S12_ATTEMPT_07.md),
[production audit](fixtures/S12_PRODUCTION_COVERAGE.md),
[policy](project/S12_ORIGINAL_TIMING.md), the S12 brief and both execution/GitHub
protocols. Earlier audits remain historical evidence. Implementation:
`a817f93c051bf15041da4f25efcfbcc32fdb1ecd`.

## What I tested

Both normal exports and full renders from Kdenlive 26.08.2 rev. d4e87e4 completed.
They retain every participant sample within normal PCM rounding, every recorded
picture frame in order and marked empty endings, with no mix overload. All 243
automated checks passed without skips.

Both real projects opened and played. Band five-clip and two-person three-clip
group move/save/undo/save checks passed. Both saved projects closed and reopened
intact, remained editable, and passed full renders after reopening. Delivery
copies are in `.local/S12/attempt-07/band_001-ready-native/` and
`.local/S12/attempt-07/two_person_002-ready-native/`, each `project.kdenlive`.

## What I need from Janne

The narrow noise approval is retained, but the named source is silent at that
second. The pending source-identity question affects only that correction.
Positive timing judgments grant no pause cuts or microphone mutes.

The local band usefulness task uses the privately recorded short source window
and separate manual/assisted copies. Exact files, timecodes and questions are in
`.local/S12/attempt-07/HANDOVER_PRIVATE.md`. Record actual correction seconds including review, a
personally safe pause's original timecode and Janne's quality judgment. Missing
sound/pause/idle labels stay unknown; do not use model detections as listening
evidence or repeat the old six-pair review.

## What happens next

Codex records human replies privately, applies only a
source-matched approved correction and reruns affected checks. S12 and the
90%/70% targets stay unclaimed until measured. Do not ask for the existing files,
tune the held-out recording, create another comparison/connection or start S13.
Resolve the handover's containing checkpoint with Git and verify live branch
equality and clean status before resuming.

Commit/push status: verify live at checkpoint; final chat records the exact SHA.
