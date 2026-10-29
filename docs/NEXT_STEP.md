# Next: S06 — build the shared pause-removal planner

**S05 is complete for the agreed bounded development examples. S06 is pending
and was not started in the S05 thread.** A later thread must explicitly select
S06. Compatibility remains EXPERIMENTAL.

- Branch: `codex/kdenlive26-overhaul`.
- S05 implementation: `7cf553449a69d4e4518875f029e8933f1bee4656` (unchanged).
- Completion handover: [S05-attempt-05.md](handovers/S05-attempt-05.md).
- Earlier review diagnostics: [S05-attempt-04.md](handovers/S05-attempt-04.md).
- Delivery/pause history: [S05-attempt-03.md](handovers/S05-attempt-03.md).
- Full S05 implementation evidence: [S05.md](handovers/S05.md).
- State: [STATE.json](project/STATE.json).
- Next brief: [S06.md](project/steps/S06.md).
- S05 guide: [S05_REACTIONS.md](project/S05_REACTIONS.md).
- Evidence: [S05_EVENT_EVIDENCE.json](fixtures/S05_EVENT_EVIDENCE.json).

The user explicitly confirmed simultaneous talk in the existing two-source
preview. Its entire envelope is protected by the union of current events. One
shared time map retains that time on all sources; the current contract also
refuses attenuation on protected sources. A derived contract harness rejected
198/198 possible interior one-frame cuts and 4/4 mute/half-gain attempts, with
2/2 unity-gain controls accepted. Its synthetic origins are never real alignment
certificates. No actual plan, project or media was changed/exported.

This closes bounded S05 G04 preservation without inventing exact human timings:
six earlier uncertainty/noise channel observations, four new speech/external-
vocal channel envelopes, one full overlap group envelope and sixteen generated
construction-labelled speech/acknowledgement regions are protected. These are
different denominators; do not pool them into an accuracy score. External vocal
protection includes a human-reviewed reaction without a positive speech-VAD hit.

The individual-source full-preview protection fractions remain `1027/1600` and
`1`. The previous five-of-six broad channel-envelope diagnostic is retained.
Shared timeline protection plus current gain refusal proves preservation here;
it does not establish per-microphone detection completeness, safe gain policy,
useful pause removal, full-interview or held-out acceptance. Conservative noise
overprotection and unknown precise overlap/vocal boundaries remain explicit.

No more S05 listening is required. No new file was requested/delivered. Keep the
one-audio-file maximum and no-new-connection preference for any later explicitly
requested review. Phone delivery failures remain historical failures; returning
to the computer did not prove those routes worked. All private comments, source
mappings, fingerprints, timecodes, recordings, transcripts and labels stay local.
Held-out acceptance audio remains unopened and separate.

Preserve every S04/S05 speech/reaction/uncertainty/review event and shared
microphone group. Native sequence deltas stay 0/1, exact source tails survive,
and all S01/S03 origins/correlations remain uncertified with null offsets.
Real v1 export remains refused for unresolved origins/unequal tails. No silent
shifting, stretching, truncation, padding, gain changes or camera-dependent cuts.

Production code/settings/models/locks/events/exporter are unchanged. The earlier
107-test/zero-skip suite, full-source/cache integration, source preservation and
S02 render checks remain inherited evidence. No new GUI operation took place;
actual editability evidence remains S01/S02 on Kdenlive 26.08.2 rev. d4e87e4.

Verify the containing checkpoint before further edits:

```powershell
git log -1 --format=%H -- docs/handovers/S05-attempt-05.md
python tools/verify_checkpoint.py --repo .
```

The final chat records local/live equality, clean worktree/upstream and exact-SHA
CI. Absent workflows/checks mean **CI not configured**, never green CI.

Ready-to-paste next-thread prompt:

> Execute S06 only in the existing InterviewAutoEditor checkout on
> codex/kdenlive26-overhaul. Read AGENTS.md, STATE.json, NEXT_STEP.md,
> docs/handovers/S05-attempt-05.md, execution/GitHub protocols, S03/S04/S05
> guides/contracts and the S06 brief. S05 implementation remains
> 7cf553449a69d4e4518875f029e8933f1bee4656. Verify the containing checkpoint,
> live SHA equality, clean worktree/upstream and exact-SHA CI first. Build one
> shared pause-removal map from every protected event; preserve words,
> acknowledgements, reactions, uncertainty and simultaneous talk on all tracks.
> Keep full leading/trailing sections, shared groups, native extent, exact tails
> and uncertified origins/correlations. No silent media repair, per-source time
> removal, gain changes or camera-dependent deletion. Keep private data/labels
> local, held-out acceptance separate and compatibility EXPERIMENTAL. Preserve
> current real-export refusals. Complete S06 gates, commit/push/verify exact-SHA
> CI, provide a verbose handover and STOP.

Paused after S05. The next thread should execute S06 only.
