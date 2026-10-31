# S05 attempt 04 — resumed development listening feedback

## Outcome and scope

**S05 remains BLOCKED at G04.** On 29 October 2026 the user returned to the
computer and supplied feedback on the three existing development clips.
Speech and external vocal-event envelopes are protected. The two-microphone
preview retains a complete combined timeline envelope, but exact source-bound
vocal spans and genuine simultaneous talk remain unconfirmed. No confirmed
vocal loss was found. S06 remains pending; compatibility stays EXPERIMENTAL.

This follow-up records labels and read-only measurements. Production analysis,
settings, models, media and projects are unchanged. No new audio is requested
or delivered. The previous one-file maximum and no-new-connection preference
remain. The earlier failed phone delivery is retained as a failure.

## Starting state

Repository `PikkuJanne/InterviewAutoEditor`, branch
`codex/kdenlive26-overhaul`, clean starting checkpoint
**f0ab0eb4b9d86508abfc39848289ca5060dd2815**. Normal fetch and the live checkpoint
helper verified local/remote equality, matching upstream and a clean worktree
before tracked edits. The S04 handover still resolves to
**1eeabd9af1b7a05405b222b1808d9295f48d79b2**, is an ancestor of HEAD, and its
speech/contracts/evidence paths are unchanged. Exact-SHA queries for both that
S04 checkpoint and the starting S05 checkpoint returned zero workflows, runs,
check-runs and statuses: **CI not configured**, not green.

Implementation remains **7cf553449a69d4e4518875f029e8933f1bee4656**. Read AGENTS,
STATE, NEXT_STEP, S04 and latest S05 handovers, execution/GitHub protocols,
S03/S04/S05 guides and brief, product/architecture/compatibility/contracts,
validation/release documents and the handover template. No subagents were
requested or spawned. No dependency or application upgrade was performed.
Existing target evidence remains Kdenlive **26.08.2 rev. d4e87e4**, MLT 7.43.0,
CPython 3.12.14 and FFmpeg 8.1.1.

## Changes and reasoning

- Keep direct-user comments and conservative evaluation envelopes in ignored
  local records. These supersede candidate descriptions; earlier corrections
  remain intact. Preserve approximate timing, unknown vocal onsets, unknown
  source attribution and uncertified original alignment. Do not manufacture
  exact sample labels from approximate human seconds.
- Compare four original private preview-channel mappings with their source PCM
  windows, rehash three involved original sources against canonical records,
  and compare the external file against its pinned development fingerprint.
  No preview resynthesis, source change or model fitting occurs.
- Measure private observations against existing full-source S04/S05 events,
  preserving inference context. Run the unchanged pinned CPU models on the
  already downloaded external development sample for its new coarse vocal
  envelopes. Preserve the canonical analysis byte-for-byte.
- Distinguish combined timeline preservation from each microphone's protection.
  An uncovered region in an intentionally broad envelope is not evidence of a
  lost word unless vocal content is independently labelled there.
- Ask one text-only clarification of whether the existing two-voice observation
  includes simultaneous talk. The answer is not inferred from distinct voices,
  activity intersections or correlation. No new listening file or connection
  is requested.
- Update STATE, NEXT_STEP, the S05 guide and aggregate evidence. Raw comments,
  mappings, fingerprints, source timecodes and media remain excluded from Git.

No model/runtime/licence choice changed. Google YAMNet TFLite v1 quantized Relu6,
Apache-2.0 provenance and ai-edge-litert 2.3.0 CPU runtime remain pinned. Silero
v5.1.2/ONNX Runtime 1.20.1/NumPy 2.1.3 are unchanged. The external cue remains
the previously downloaded ESC-50 development fold example, with dataset
CC BY-NC 3.0 terms and original CC0 attribution kept locally. It is neither a
private interview nor held-out acceptance example.

## Validation evidence

```powershell
.venv/Scripts/python.exe -B .local/S05/validate_human_review02.py
.venv/Scripts/python.exe -B .local/S01/validate_private_corpus.py
.venv/Scripts/python.exe -B .local/S05/check_public_attempt04.py --checkpoint
git diff --check
```

**PASS — partial coarse-envelope containment.** Six observation/channel
envelopes were checked; **five are fully protected**. These are channel/envelope
checks, not six independent human examples or sample-precise annotations.
The word-bearing full-clip envelope is fully protected on both PCM channels.
Both external vocal envelopes are fully protected, neither has a positive
speech-VAD hit, and the reaction model has positive hits. In the conservative
suffix containing the end vocal event, S04-only coverage is **59/75**, fused
coverage **1**. This establishes added envelope protection while leaving exact
event onset and classification confidence unresolved.

**INCOMPLETE — per-source two-voice evidence.** The combined two-source timeline
envelope is fully protected. One source has only partial coverage of the broad
observation envelope because its opening is uncovered; the user did not label
speech there. Do not call this an observed vocal loss or adjust its annotation
to the model's first detected sample. Source attribution/laughter onset and
genuine simultaneity remain unspecified. A text clarification is pending.
G04 is not waived by aggregate containment or generated acknowledgements.

**PASS — source preservation.** Four private preview-channel mappings are
sample-exact, three rehashed original sources match canonical records, the
external file matches its pinned development fingerprint, and the canonical
production analysis hash is unchanged. The corpus validator passes **102
assertions**, all **five** original media unchanged and **twelve** PCM excerpts
exact. Track semantics remain equal; whole-project semantics remain unequal
because the native sequence extent still differs by one frame.

**PASS — documentation/state/privacy/CLI consistency** is checked before commit.
The checkpoint validator scans public paths against actual private names, paths
and source hashes, checks local links, unchanged instructions/licence/S01–S04
contracts/fixtures and unchanged implementation, and confirms review exit 2
plus no-overwrite exit 1 on the public synthetic CLI. The final chat records
its actual result/count after execution.

**Inherited, not rerun:** 107 automated tests/zero skips, original full-source
reaction/cache integration and eleven S02 render measurements. No production
code changed; these are not newly attributed full-suite results.

**NOT RUN:** new Kdenlive GUI open/play/group-edit/save/reopen/render, product
export, precise/exhaustive content acceptance, held-out listening or two-hour
stress. Native editability evidence remains the actual S01/S02 synthetic record
on the exact build; XML/model checks do not substitute for GUI evidence.

An initial private validator used an incorrect fingerprint attribute and
stopped before producing a report. It was corrected to the existing `sha256`
field; the successful run generated the retained report. Production code,
sources, annotations and caches were not changed to obtain that result.
The first documentation diff check also rejected CRLF introduced by Windows
text writes. The three authored files were normalized back to LF before staging;
the corrected diff check passes. No failing diff was committed.

## Content and synchronization checks

All earlier S04/S05 speech, reaction, uncertainty and review records survive
unchanged. Shared microphones remain inseparable. Noise-floor estimates, class
scores, correlations and possible intersections remain supporting evidence.
No cuts, mute/gain changes, source separation, normalization, denoising, silent
media repair or camera dependency were introduced.

Preserve 51092 CFR video frames at 25/1, native sequence deltas 0/1, exact
192 kHz source counts and +/-4/375-second tails. S03 origins remain
UNVERIFIED_INSUFFICIENT_ANCHORS with null offsets, and S01 zero/+10ms/~−32.69ms
correlations remain uncertified. V1 unequal-tail/unverified-origin export
refusal remains. No held-out audio was opened, tuned on or repurposed.

## Git and CI

Implementation: **7cf553449a69d4e4518875f029e8933f1bee4656** (unchanged).
Branch: `codex/kdenlive26-overhaul`.
Handover: `docs/handovers/S05-attempt-04.md`.
Resolve its containing checkpoint from Git history. Final chat records actual
local/live SHA equality, clean worktree/upstream and exact-SHA CI after normal
push. No main integration, force push, tag, release or S06 work.

## Artifacts and recovery

Keep ignored original cues, phone previews, earlier corrections, upload receipts,
the unused single-file preview and new observation/containment records. No Page
or existing asset is deleted to hide failed delivery. No new upload, external
message, connection or public media publication occurred. Originals need no
restoration because they were not modified. The editable-project evidence
remains S02's native round-trip project; this follow-up creates no new interview.

## Remaining limitations and required next action

The new observations materially improve development evidence, including a
human-reviewed external reaction without a positive VAD hit. They do not supply
exact word/overlap bounds or identify the source of the private laughter. The
pending text clarification concerns whether the existing two voices overlap;
it requires no additional delivery. Record any answer and assess the remaining
source-bound label gap. Do not request a larger listening pack or silently
narrow labels to predicted activity. One audio file maximum and no new
connection remain the user's preferences. S05 stays blocked until its agreed
development gate is genuinely demonstrated; S06 is not authorized here.

## Next thread

> Continue S05 only in the existing InterviewAutoEditor checkout on
> codex/kdenlive26-overhaul. Read AGENTS.md, STATE.json, NEXT_STEP.md,
> docs/handovers/S05-attempt-04.md and prior S05 evidence, execution/GitHub
> protocols and S03/S04/S05 guides. Implementation remains
> 7cf553449a69d4e4518875f029e8933f1bee4656. Verify the containing checkpoint,
> live SHA equality, clean worktree/upstream and exact-SHA CI first. The user
> resumed by reviewing existing development clips. Keep coarse labels local
> and resolve direct-user clarification of simultaneity/source-bound content
> without fitting annotations to predictions. Do not request a new listening
> pack; honor the one-file maximum and no-new-connection preference. Preserve
> all uncertainty, shared groups, extent/tail/origin/correlation findings,
> original media and EXPERIMENTAL compatibility. Keep held-out acceptance
> separate. Do not waive G04 or begin S06. Complete authorized S05 work,
> commit/push/verify, provide a verbose handover and STOP.

## Pause

Paused with S05 blocked. The next thread must resume S05.
