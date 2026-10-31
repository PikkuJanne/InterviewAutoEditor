# S05 attempt 02 — partial human listening review

## Outcome and scope

**S05 remains BLOCKED at its labelled-development G04 gate.** On 28 October
2026 the owner listened to the first phone review pack and corrected provisional
model descriptions. The observations are now recorded locally with approximate
timing and uncertain vocal origin retained. All reviewed coarse windows remain
fully protected. They do not establish complete positive coverage of speech,
laughter/chuckles, acknowledgements or genuine simultaneous talk.

A second **21-second** review pack is ready. No production code, thresholds,
models, runtime, adapter, original media or protection rule changed. S06 remains
pending; compatibility remains **EXPERIMENTAL**.

## Starting state

Branch `codex/kdenlive26-overhaul`, clean starting checkpoint
**272cdd7e5e139bfacae19285fe0ed2c09eb57edd**. Live remote/local equality,
matching upstream and clean worktree passed the read-only checkpoint helper;
normal fetch found no divergent work. Exact-SHA GitHub queries returned zero
workflows, runs, check-runs and statuses: CI not configured, not green.

Implementation remains **7cf553449a69d4e4518875f029e8933f1bee4656**.
The [original S05 handover](S05.md) retains complete implementation, provenance,
test, failure and timing evidence. AGENTS, current state/NEXT_STEP, execution/
GitHub protocols and the S05 brief were reread for this continuation. No
subagents were requested or spawned. Kdenlive remains 26.08.2 rev. d4e87e4;
Python 3.12.14, FFmpeg/ffprobe 8.1.1 and all pinned model/runtime versions are
unchanged.

## Changes and reasoning

- Direct user observations, their provenance, approximate seconds, phone MP3
  playback and unresolved sound identity are stored in ignored local review
  JSON/CSV. Predictions remain separate from the user's corrections.
- Two reviewed clips overlap the same original source material; they are not
  independent examples. The tentative laugh-like observation remains uncertainty,
  rather than being promoted to confirmed human laughter or a known word.
- Existing canonical protected intervals cover every reported coarse window on
  both physical channels. Reviewed non-human sounds are useful negative category
  evidence, not authorization to remove their surrounding audio or clear other
  uncertainty. No model threshold or protection event was changed.
- Additional candidate selection examined only development material, including
  strong speech windows. Generic event scores did not supply a confidently
  verified interview laugh. The second pack therefore labels its external
  laughter provenance explicitly instead of claiming it is an interview event.
- Review pack D is an eight-second exact private interview PCM excerpt selected
  from strong speech evidence. E is an eight-second preview of two original
  microphone channels, presented left/right with no gain or mixing. Each channel
  equals its original source samples; apparent simultaneity still needs human
  review and does not certify source alignment. F is a five-second example from
  the already downloaded ESC-50 development subset. Its source attribution and
  licence are retained locally. No held-out audio was opened.
- Private WAVs remain authoritative for engineering checks; the phone playback
  copies are compressed MP3s. The review instructions explicitly request sound
  type, complete audible timing and any omitted events. All new proposals remain
  unconfirmed until the user responds.
- Public updates contain aggregate review status only. Private labels, source
  identities, timecodes, paths, voices, source fingerprints and comments remain
  local. STATE, NEXT_STEP and this indexed continuation handover preserve the
  blocked gate and historical attempt rather than erasing it.

## Validation evidence

**PASS — local review persistence and protection check.** The local script reads
the saved direct observations and the original canonical fused analysis, converts
the reported coarse seconds to source time, and checks both physical channels.
All three reported windows have protected fraction 1. The uncertain vocal
candidate is retained through uncertainty; positive reaction classification is
not required. This is a coarse-window containment measurement, not exhaustive
event timing, human laughter acceptance or a new classifier-accuracy claim.

**PASS — next-pack sample preservation.** D retains original PCM frames; E's
left/right arrays equal the corresponding original source channel arrays.
Neither a gain adjustment nor original-file write occurs. F is copied from a
previously downloaded development file with its attribution; no reserved clip
is downloaded or evaluated. New previews/manifests are private and provisional.

**Inherited, not rerun:** the unchanged implementation's 107-test/zero-skip suite,
16 generated protected regions, four full-source/eight-channel integration,
four identical cache hits, 102 original corpus checks and 11 S02-render checks
remain the evidence recorded in the original S05 handover. This continuation
changes documentation/state only; repeating model inference or GUI tests would
not validate the new human observations. Applicable JSON, link, privacy and
state-consistency checks run before the documentation checkpoint.

**NOT RUN:** complete positive private-category acceptance, full held-out
listening, new Kdenlive open/play/group-edit/save/reopen/render. No exporter or
editable project changed; existing S01/S02 actual GUI evidence remains in force.

## Content and synchronization checks

All S04/S05 speech/reaction/uncertainty records remain intact. No automatic cuts,
gain changes, denoising, normalization, source separation or camera dependency
were introduced. Shared microphones remain one group. Native sequence deltas
0/1, 51092 CFR video frames at 25/1, full stereo 192 kHz source counts, exact
+/-4/375-second tails and every uncertified S01/S03 origin/correlation finding
remain unchanged. Null offsets remain null; real export stays refused by the
existing origin/tail constraints. Human phone observations do not certify sync.

## Git and CI

Implementation: **7cf553449a69d4e4518875f029e8933f1bee4656** (unchanged).
Branch: `codex/kdenlive26-overhaul`.
Handover: `docs/handovers/S05-attempt-02.md`.
The containing checkpoint SHA is resolved from this file's Git history; the
closing chat records actual local/live equality, clean worktree/upstream and
exact-SHA CI after normal push. Persisted synchronization remains verify-live.
No main merge, force push, tag, release or next-step work is performed.

## Artifacts and usage

Ignored local first-round review records include human observations and their
coarse-window protection check. The second review folder contains D/E/F WAVs,
phone MP3s, provenance/attribution, unconfirmed proposals and a README. Exact
private locations are provided only in chat/local references. Public aggregate
status is in [S05_EVENT_EVIDENCE.json](../fixtures/S05_EVENT_EVIDENCE.json);
[S05_REACTIONS.md](../project/S05_REACTIONS.md) describes unchanged setup/behavior.

The user can answer in chat with sound type, approximate onset/end and omissions.
Conservative seconds can be rounded outward onto exact source samples; retain
their human annotation precision rather than pretending sample-accurate hearing.
The next pack's descriptions remain model-assisted hypotheses. No user CSV
editing or media upload is required. No restoration is needed: originals and
production analysis are unchanged.

## Remaining limitations and blockers

Positive, representative human-confirmed development categories remain incomplete.
The first feedback adds negative/uncertain observations and does not establish
all words, laughter/chuckles, yes/mm-hm or simultaneous talk. The external
laughter example provides declared supplementary provenance, not a claim of
cleaned-Zoom laughter retention or held-out performance. Missing categories may
require another targeted development excerpt. Keep later acceptance independent
of selection/tuning and retain source timing/identity uncertainty.

## Next thread

> Resume S05 only on codex/kdenlive26-overhaul. Read AGENTS.md, STATE.json,
> NEXT_STEP.md, docs/handovers/S05-attempt-02.md and the original S05 handover,
> S03/S04/S05 guides and execution/GitHub protocols. Implementation remains
> 7cf553449a69d4e4518875f029e8933f1bee4656. Resolve and verify the containing
> checkpoint, live SHA equality, clean worktree/upstream and exact-SHA CI first.
> Incorporate direct phone-review corrections from the local records without
> promoting uncertain sound identity or approximate boundaries to stronger truth.
> Obtain the missing confirmed positive development categories using the prepared
> D/E/F pack and additional focused examples if required. Keep external sample
> provenance and held-out acceptance separate. Preserve all protection, grouping,
> native extent/tails and uncertified origin/correlation findings; no silent
> repair, source separation, gain changes, automatic cuts or camera dependency.
> Keep private data local and compatibility EXPERIMENTAL. Complete S05's real
> development gate, commit/push/verify/handover and STOP. Do not execute S06.

## Pause

Paused with S05 blocked. The next thread must resume S05.
