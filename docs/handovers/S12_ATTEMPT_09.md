# S12 attempt 09 — ordinary generation, scoped full mute and native delivery

## Outcome and scope

**S12 COMPLETE technically**, subject to live checkpoint synchronization below.
Both real interviews have usable, editable Kdenlive deliveries. Ordinary CLI and
desktop Create accept a starter project without internal benchmark/review JSONs.
The two authorized noises are fully muted on their one participant track. Exact
source-clock checks retain all other audio, picture and complete endings. This
chat performs S12 only and stops before S13.

The supplied revision bundle was read as project material within the owner's
request to revise and continue the project. It was reconciled with the live
repository, not installed over it. The operating revision retires the timed
manual/assisted exercise, routine annotation/listening assignments and mandatory
subjective sign-off. **Retired by owner is not passed.** Unknown times, usefulness,
quality and unsupported 90%/70% targets remain null. No new editorial ambiguity
needed owner input. Technical setup/repairs/retries remained Codex's work.

## Starting state

Repository PikkuJanne/InterviewAutoEditor, existing development branch
`codex/kdenlive26-overhaul`, clean synchronized starting commit
`32a253c659aba9c4064d06c8096ff738fe050c6b`. Live HTTPS origin is the authenticated
equivalent of the expected SSH repository. Latest starting handover was attempt
08; S00–S11 completed, S12 blocked on the now-retired exercise, S13–S15 pending.
State, NEXT_STEP, handover, S12 brief and execution/GitHub protocols were checked.
The bundle's three text documents are retained only under ignored private
attempt-09 provenance. Existing instructions, licence, user work and all prior
attempts were preserved. No subagents were used.

Exact installed build: **Kdenlive 26.08.2 rev d4e87e4**, exe SHA-256
`7a5bbf2e7764514a863fad756fe2195779475804706a8a74e73ab922def1d352`, checked against
retained genuine version dialog/setup evidence. MLT 7.43.0, FFmpeg 8.1.1,
Qt 6.11.1, Windows AMD64; local Python 3.12. No editor/tool/model was installed or
updated. Original custom 1280x720/25fps native profile is preserved and hashed.

## Changed behavior and decisions

Initial implementation `3d6f1157665eb64f5b140956a2db8828785abb6c` introduced:

- `editing.py`: source mapping from native track order, discovery of already
  installed local tools/pinned CPU models, actual all-channel digital-silence
  measurement, and explicit repeatable source-time mute envelopes.
- `edit` CLI and desktop Create: normal starter-to-new-project flow, successful
  exit 0 and absolute ready-project path. Saved analyses can be reused without
  running models. Legacy commands and schema-1 strict timing remain available.
- Shared Application/export/job plumbing: private hashed mute options/reports,
  preserved originals, old saved jobs readable with an empty optional mute field,
  actionable local missing-source recovery, atomic new output and normal resume.
- Operating docs/AGENTS, S12 brief and workflow: owner exercise retired; plain
  delivery chat and verbose persisted engineering handover, with old evidence
  preserved and numerical claims explicitly unmeasured.

Final implementation **`0f30418fb789ec24b336355a78d97be2172de28c`** adds bounded optional native fragmentation and
explicit safeguard validation. Ordinary generated two-person XML with 516 short
groups repeatedly stalled startup/preview. The same unchanged media in a clearly
hand-authored one-group diagnostic opened/played promptly. The format adapter
now coalesces the smallest adjacent optional units toward 128 groups in the v2
original-timing path. All mandatory shared-removal seams survive even above the
soft target, and every exact speaker/overlap cue stays in the private report.
Current outputs retain 113/128 aligned groups and 4633/7561 semantic cues. Core
speech/reaction, turn thresholds, pacing and picture rules were not tuned.
128 is a tested representation choice for this build, not a universal editor
limit or future-version guarantee. Native loading/seeking still has observable
latency on large projects; a seamless performance promise is not made.

An explicit mute refuses if it crosses any track's source-time Keep/audible
interval. One narrow correction cannot bypass the separate existing safeguard.
This refusal has a focused regression and fixed actionable local diagnostic.
Approved mute keys use native Volume with -1000dB, which the actual integer PCM
renders verify as exact zero. Edge fades stay inside the specified envelope.
The measured native filter interpolates amplitude from the preceding frame's
evaluated dB gain; final fade starts were placed early enough to cover both
observed transient onsets. No participant/timecode/path is hard-coded in product
logic. Existing cleaned audio is never re-normalized/denoised. The native master
remains the reversible fixed 0.95/N rule, preserving relative source levels.

## Validation commands and exact scope

Final implementation bytes passed:

```powershell
# Point these to the already-existing local assets; no private path is published.
$env:IAE_FFPROBE = '<installed-ffprobe.exe>'
$env:IAE_FFMPEG = '<installed-ffmpeg.exe>'
$env:IAE_S04_MODEL = '<pinned-silero.onnx>'
$env:IAE_S05_MODEL = '<pinned-yamnet.tflite>'
$env:IAE_S04_DEVELOPMENT = '<existing-S04-development-directory>'
.venv/Scripts/python.exe -B -m unittest discover -s tools -p 'test_*.py' -v
```

**250 tests, zero skipped/failed/errors, 432.853 seconds**. Log:
`.local/S12/attempt-09/full-tests-delivery-final.log`. Focused ordinary-workflow
suite: 7 tests in 18.798 seconds. Source bytes were frozen throughout the final
full suite and final real generations. The later checkpoint changes docs only.
Meaningful coverage includes normal starter-only CPU inference/generation,
sample grids/fractional timing, content/uncertainty protection, source-bound
mute clipping and restoration, any-track preservation conflicts, optional
coalescing without losing mandatory seams/cues, export and durable recovery.

Both complete real interviews use ordinary `edit` with retained exact mappings,
source-bound saved analyses and picture observations; the two-person run also
keeps its unchanged explicit pending-audibility request. Such JSON reuse is a
supported optimization, not an ordinary-user prerequisite. Current new accepted
runs have matching final implementation hashes and semantically match their
native-saved deliveries. Full actual commands and source paths remain in
ignored private command ledgers. No inference threshold or held-out setting
was changed. Neither real project has an approved removable shared interval;
zero frames were cut. A no-safe-pause result is not relabelled as useful removal.

## Actual native GUI checks — G02/G07

Computer-use skill controlled the already installed editor. Every action targeted
a returned Kdenlive window; no user desktop project was overwritten. Initial
owned diagnostic copies and failed probes remain retained. A pre-existing
unrelated editor process was left alone. Final deliveries each passed:

1. Open in actual 26.08.2 with the source picture/profile/media resolving.
2. Play with changing recorded picture, advancing monitor time and participant
   audio meters; seek to interior material. These are actual native observations,
   not inferred from XML or a backend render.
3. Select the final normal group and Edit Duration → increase position one
   project frame; save. Parsed genuine native output proves all 5/3 members
   advanced one frame with source bounds unchanged.
4. Undo and save; every original source/output row and timeline extent returns.
   Native effect/master timecode normalization is accounted for rather than
   falsely reported as a gain change.
5. Close the saved project and launch a fresh editor process to reopen it.
   No repair/missing-media dialog; groups, source rows, effect keys, master and
   ending bounds still match normal generated output. Exact reopened hashes bind
   the subsequent actual installed-editor renders.

Private receipts: `*_delivery` names are hyphenated in the actual paths:
`band_001-delivery-native-{moved,restored,reopened}.json` and the corresponding
`two_person_002-delivery-native-*` receipts under private attempt 09. Native
project folders have suffix `-delivery-native`. They contain genuine native
saved snapshots, not a hand-authored fixture claim. Earlier one-group coalesced
probe is diagnostic only and is not a delivered project.

| Fixture | Groups / entries | Members moved | Restored timeline frames | Native full render seconds |
|---|---:|---:|---:|---:|
| band_001 | 113 / 565 | 5 | 51093 | 676.953 |
| two_person_002 | 128 / 384 | 3 | 47005 | 554.250 |

## Full source/content/synchronization measurements — G01/G03–G08

After genuine GUI reopen, each **installed Kdenlive executable** ran its normal
`--render --render-preset 'IAE S12 EOF 192000 lossless experiment'` command on
the exact native delivery. Both exit 0. The retained preset is FFV1 plus stereo
PCM16/192000Hz so exhaustive source-sample checks are possible. This describes
the executable render route accurately; no GUI Render-button action is claimed.
Private invocation/completion/probe/measurement JSON and full media live under
each `*-delivery-render` folder. Renders are technical evidence; the primary
deliverables remain editable `.kdenlive` projects.

Every output audio sample (392394240 band,
360998400 two-person) matches the declared source-clock
participant-only reference to less than **0.501 PCM16 LSB**, including the native
mute interpolation. Full-scale values: zero. Nonzero values past the longest
actual participant EOF: zero. The master .2375/.475 is unchanged. No MP4 audio
route contributes; native video is audio-disabled and the entire mix agrees
with only the original cleaned participant sources. No relative shift, repeated
normalization, truncation, stretching or timeline removal occurred.

Every encoded FFV1 picture packet and exact PTS/duration matches the retained
fully source-validated native render: 51092/47004 actual recorded frames in order
and one marked empty final picture frame. Prior source proof compares every
original frame at 64x36 gray and exact timestamps. Packet identity extends that
matching native render proof to these outputs; it is not a new claim of
full-resolution decoded source RGB equality. Missing camera footage is not
reconstructed. Audio after video EOF survives at its original time.

Four source-isolated installed-MLT diagnostic renders use the **actual native
saved filters** around the final two-event correction. Each target flat interior
has exactly zero sample values; adjacent target sound and all three other
microphones retain original-clock samples (maximum unedited normalized error
5.9604644830901776e-09).
The mixed-route full sample check is independent of these isolates. Exact local
source IDs, envelope/source/edited timecodes, native keys and source hashes stay
in `delivery-mute-ledger.json`, `delivery-isolated/result.json` and private owner
delivery notes. The change is two explicit events on one microphone only.

Every native unity boundary is checked with five explicit source/render samples,
including across one-second streaming blocks. Residual steps after the declared
source/gain reference are within the recorded tolerance; all complete-render
fade samples satisfy the same unfitted reference. These are mathematical checks,
not independent subjective click/noise acceptance. Broader idle-mic suppression,
numerical accuracy and word-by-word full-corpus human scores remain unmeasured.
No new protected content was automatically removed or muted. The original five
positive judgments retain their exact limited scope; the rejected timing-
unscorable excerpt and continuous no-safe-pause answer are not counted as passes.

## Controlled case and recovery — G04/G05/G09

The allowed small synthetic case uses one channel of existing synthetic TTS,
a short constructed reply/overlap, known exact shared silence and a target-mic
noise. The normal edit path removes **92/25 seconds (3.68s)** on one shared map,
keeps leading/trailing material and all constructed speech/reply/overlap, and
applies the explicit noise mute. Actual installed backend PCM agrees with the
declared time-map, native gain and standard mono-center-to-stereo matrix to
**3.901342376932959e-08 normalized**. Output is 308 frames. This is independent
synthetic construction, not real-detector labels or a native GUI-produced fixture.
Evidence: private `controlled-v2/audio-validation.json` and construction logs.

An actual old saved desktop job was copied, read/reviewed and replayed in new
private destinations. Equivalent picture observations were regenerated to bind
the current code, export was cancelled with no final output, and same-options
resume completed on attempt 2. Original job hash unchanged; no timing/usefulness
questionnaire is loaded. Existing public tests also exercise caches, missing
assets, relocation, changed-input refusal, exclusive destinations and recovery.
The final full band generation's first failed export is retained in its result
ledger; same-options resume and current native semantics are verified separately.

## Failed/limited observations retained

- Early optional-model skips and a mistaken development **file** environment
  value were harness setup, not passing real CPU evidence. Correct directory and
  all assets produced the final 250/zero-skip pass. An old desktop status-text
  expectation was updated to the new Ready project behavior and rerun.
- Initial grouping regression used wrong mixed sample grids/shared-mic labels;
  corrected independent construction now tests the intended many-turn case and
  more mandatory seams than the soft target. Earlier failed logs remain.
- Initial stereo TTS downmix cancelled opposite-polarity speech; rejected. The
  corrected single-channel construction has asserted nonzero speech and actual
  full sample validation. Initial mono/stereo reference omitted the declared
  center coefficient; corrected from the documented standard route, then checked
  against every sample rather than fitted to output.
- Early mute prototype used later onset fades; source-waveform/actual-native
  inspection showed the first transient onset was outside the flat. Final
  envelope starts were moved earlier, and all affected native/isolate/full-render
  checks were rerun. Prototype render/evidence remain clearly separate.
- An early streaming harness left a unity boundary observation null across its
  one-second block boundary. Explicit five-sample reads repair the measurement;
  the final full validator includes them. No audio was altered to satisfy it.
- Dense generated two-person startup/preview stalls, software-rendering/audio
  driver probes and the one-group diagnostic remain failures/diagnostics, not
  claimed current passes. Final 128-group actual native checks replace them.
- A late fresh band generation initially failed exporting under concurrent
  validation. Its generic first-failure log remains; same-options recovery is
  retained. Do not invent an exact first-failure cause that was not captured.

## Preservation and privacy

Read-only hash verification: **8 original
inputs, 44 attempt-08
records/projects and 243 older private
artifacts unchanged**. Both original complete analyses/events match exactly;
six measured offsets stay null rather than becoming zero. Old studies/task,
`645f5c` registration, historical implementation and rejected judgments remain
recoverable. The separate pending audible request's bytes and conditions remain
unchanged and are applied only within their original scope. No held-out tuning,
new external connection, upload or owner comparison deliverable was created.
Native media, names, screenshots, transcripts, private paths and credentials
remain excluded from public Git. Current public metrics use neutral fixture IDs.

## Git and CI

Implementation: `0f30418fb789ec24b336355a78d97be2172de28c` (plus initial `3d6f1157665eb64f5b140956a2db8828785abb6c`).
Branch: `codex/kdenlive26-overhaul`. Handover:
`docs/handovers/S12_ATTEMPT_09.md`. Its containing final checkpoint SHA is resolved
from Git history and given in final chat after push, not embedded recursively.

Source/tests/workflow were committed after the 250-test pass; final checkpoint
edits only this audit, state, NEXT_STEP and handover/references. Relevant final
checks: JSON parse, state/step/handover consistency, public-path/privacy review,
`git diff --check`, ordinary normal-run/native integrity and read-only
`python tools/verify_checkpoint.py --repo .`. No unrelated work was reset,
discarded or force-pushed. Live branch SHA must equal local HEAD and upstream
after normal push; final chat records the observed result. If synchronization
fails, S12 remains the continuation despite the technical gates passing.

No repository Actions workflow is configured. Exact final-SHA status/run queries
are performed after push; do not call an empty check set green CI. Private corpus
tests were local and are not attributed to a CI run. S13 compatibility and S14
packaging/clean-install checks have not run, and no PR was merged, release/tag
created or stable compatibility claim made.

## Artifacts and ordinary use

Primary deliveries are native saved/reopened editable projects under ignored
private attempt-09 `band_001-delivery-native` and `two_person_002-delivery-native`.
Absolute local paths and the correction's edited timeline timecodes are supplied
privately in chat and `HANDOVER_PRIVATE.md`; originals and all intermediate
copies are preserved. The full MKVs and source isolates are verification outputs,
not substitutes for the editable projects. Disable the target Volume effect on
an editable copy or regenerate without its `--mute` flags to restore that source.
Remove approved global intervals to restore shared time; original bin media
remains available. Reopen native copies as editable working projects; immutable
normal generation manifests should remain untouched.

From repository PowerShell, this is the next-interview command (new output):

```powershell
.\.venv\Scripts\python.exe -B -m interview_auto_editor edit --project (Read-Host "Starter project path") --output ("outputs\Interview-" + (Get-Date -Format yyyyMMdd-HHmmss))
```

Installed pinned local assets are discovered; the command has no annotation,
mapping or questionnaire prerequisite. Advanced reuse/mute options are documented
in [ordinary workflow](../project/S12_EDITOR_WORKFLOW.md). Full leading/trailing
and uncertain content survive, and digital-silence conservatism may leave useful
nonzero-room-tone pauses for editing. The original source alignment is preserved;
this does not certify unknown measured offsets as zero.

## Remaining limits and next thread

No S12 owner action is required. The exercise is retired, not a missing sign-off.
Unmeasured independent/subjective metrics and digital-silence conservatism limit
claims, not the declared practical technical delivery. Current exact build remains
experimental. No arbitrary-recording word-loss guarantee, effort-reduction score,
future-version guarantee or full real-pipeline memory measurement is asserted.

Next owner/action: the owner starts a new chat and commands **S13 only**. First
verify this checkpoint live. S13 checks exact supported/stable 26 builds,
capability states and future adapter migration guidance under its brief. This
handover is not permission to execute it automatically. S14/S15 stay pending.

Ready-to-paste prompt:

> In InterviewAutoEditor on codex/kdenlive26-overhaul, inspect Git and read AGENTS.md,
> docs/project/STATE.json, docs/NEXT_STEP.md, docs/handovers/S12_ATTEMPT_09.md,
> docs/project/steps/S13.md and execution/GitHub protocols. Verify the synchronized
> S12 checkpoint; implementation is 0f30418fb789ec24b336355a78d97be2172de28c. Execute S13 only. Preserve the retired
> owner exercise, all private evidence and separate scoped safeguard conditions.
> Complete exact compatibility/capability/migration gates, commit and push,
> verify live remote SHA equals local HEAD and tracked work is clean, write a
> verbose handover, then STOP before S14. Do not recreate owner QA assignments.

## Pause

Paused after S12. The next thread should execute S13 only. No S13/background
next-step work is running.
