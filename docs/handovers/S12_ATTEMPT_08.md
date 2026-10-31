## What I fixed

The two approved noises are reduced on the confirmed participant's microphone
in a new editable band copy. The speaker's answer, other microphones, picture
timing and full endings remain intact. No pause was cut. The original pause task
is closed because there is no safe pause in that answer.

New band project: `.local/S12/attempt-08/band_001-corrected-native/project.kdenlive`.
Two-person project: `.local/S12/attempt-07/two_person_002-ready-native/project.kdenlive`.
Earlier projects and approvals remain recoverable. This checkpoint changes
neither production code nor default settings. Production implementation is
`a817f93c051bf15041da4f25efcfbcc32fdb1ecd`; the first ending fix was
`9af678916f1dd42545330904229f7f8519826d71`.

## What I tested

The corrected band project opened and played in Kdenlive 26.08.2 rev. d4e87e4.
Its five-member group moved together, saved, undid and saved correctly. It closed
and reopened without repair or missing media; its volume controls remained
editable. The complete render passed the source-only noise, retained speech,
timing, full-ending, excluded MP4-audio and headroom checks. No time was removed.
The unchanged two-person project's earlier actual editor/render proof remains
valid. Both original deliveries and all eight media files still match their
recorded hashes; six unknown audio offsets and 243 old private artifacts remain.

The unchanged implementation's 243-test pass is reused. New measurements and
the limits of synthetic, file, editor and human evidence are in the
[current audit](../fixtures/S12_OWNER_CORRECTION.md) and
[numbers](../fixtures/S12_OWNER_CORRECTION.json). The prior audit and failed
attempts are preserved. No held-out tuning, new comparison media or connection.

## What I need from Janne

The source question and both short sections' additional-event questions are
answered; do not repeat them or the six old excerpt decisions. The answer has
no safe pause, so do not ask to shorten it. No general microphone mute follows.
Raw replies, exact original timecodes and the final prepared noise task remain
local in `.local/S12/attempt-08/HANDOVER_PRIVATE.md` and
`owner-usefulness/task-private.json` beside it.

The one remaining task uses matching manual and assisted copies to reduce the
same approved noises. Record actual manual/assisted seconds including listening,
review and saving, plus the owner's noise and usefulness judgment. No missing
measurement is zero; no valid earlier paired time measurement exists. Numerical
human sync offsets and precision remain unset. Five earlier positives and
rejected, timing-unscorable 2B remain unchanged.

## What happens next

Codex records the final answers privately, makes only scoped requested changes
in new copies and reruns affected checks. S12 remains open; 90% and 70% are
unmeasured and unclaimed. S13-S15 stay pending. Next prompt if needed: **Resume
S12 only, read this handover and state, verify the live checkpoint, finish the
recorded owner noise/usefulness gate and any resulting correction checks,
commit/push and stop at S12.**

Branch: `codex/kdenlive26-overhaul`. Resolve this handover's containing checkpoint
from Git. Later changes in this checkpoint are documentation only; actual
native-edit/render evidence is private and source-bound. GitHub has no configured
CI; zero checks is not green CI. Paused with S12 blocked on the named owner
decision. The next thread must resume S12.

Commit/push status: verify live at checkpoint; final chat records the exact SHA.
