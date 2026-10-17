# S01 handover — attempt 02, capture and private intake complete

## Outcome and scope

**S01 COMPLETE** on 17 October 2026. The owner supplied the missing example media
folder after the [first blocked checkpoint](S01.md). It contains one MP4 and four
cleaned WAVs, with no existing Kdenlive project. The agent created a genuine
private starter in Kdenlive 26.08.2, checked its initial structure/media
assumptions, played/saved/reopened it, and indexed private samples for later work.
The earlier failures and blocked attempt remain preserved.

The production build and genuine synthetic reference evidence were already
complete. Together with the new initial real intake and corpus access, S01's exit
gate now passes. This does not accept real synchronization or interview quality,
and does not implement an importer/exporter. Product compatibility remains
EXPERIMENTAL. S02 is the next step and was not started in this chat.

## Starting state

Repository `PikkuJanne/InterviewAutoEditor`, branch `codex/kdenlive26-overhaul`,
resumed clean at `2ec1d2613853c52822125f55a6f21cdbfcecac75`. Safe fetch and the
live checkpoint verifier confirmed local/remote equality, correct upstream and
clean worktree. The current state, NEXT_STEP, S01 brief, prior handover and
execution/GitHub/product/compatibility instructions were inspected. The supplied
folder was the only newly searched personal location. No subagents were spawned.

The already verified production build remains **26.08.2 rev. d4e87e4**, MLT 7.43.0,
FFmpeg 8.1.1, Windows NT 10.0.26300.0 AMD64. The installed Qt6Core DLL reports
6.11.1.0. See [the original build/capture evidence](../fixtures/S01_CAPTURE.md)
for exact executable hash, provenance and startup failure history. The isolated
capture configuration opened successfully in this attempt. Existing owner
configuration was not reset. No dependency/model was installed.

## Changes and reasoning

- [S01_REAL_INPUTS.md](../fixtures/S01_REAL_INPUTS.md) records public-safe input
  observations, actual private starter provenance, exact limits and failed
  checks. It publishes no real names, paths, source hashes, media or screenshots.
- [S01_CAPTURE.md](../fixtures/S01_CAPTURE.md) records the second attempt while
  retaining the first checkpoint's blocked-input and failed-sanitization facts.
- README and [COMPATIBILITY.md](../COMPATIBILITY.md) distinguish completed S01
  intake from unimplemented product export and unverified real timing/quality.
- STATE and NEXT_STEP select S02 as the next authorized chat. This indexed
  handover supersedes the first attempt for current state without deleting it.

Ignored `.local/S01/private-corpus-index.json` now contains actual source/project
locations, explicit neutral-ID participant mapping, complete source hashes,
probe reports, signal windows and sample paths. Private native starter and
round-trip projects plus one-off inspection/validation scripts are under the
ignored corpus area. These are local evidence aids, not a public application API.
The source folder itself was not changed.

## Validation evidence

**Public automated suite PASS:**

```powershell
python -B -m unittest discover -s tools -p 'test_*.py' -v
```

42 tests passed in **45.408 seconds**: 25 capture/fixture tests plus 17 checkpoint
tests, running unchanged code from
`1d81a245a4a5986ecbfe4fff7d341b84d2ebcf78`. This retry changes public documentation
only. Documentation validation then passed **72 assertions across seven changed
public paths** using `python -B .local/S01/validate_attempt_02_docs.py`: state and
next-step consistency, local links, preserved first handover, private-name/path
and real-source-hash exclusions, unchanged public code/license, and ignored
corpus placement. The existing public review also passed for 19 capture/tool
paths, including fixture/render hashes. These gates are repeated after final
documentation edits. Live Git/CI results are recorded in the final chat.

**Private corpus check PASS:**

```powershell
python -B .local/S01/validate_private_corpus.py
```

102 assertions passed: five original media hashes unchanged; five uncut entries
at zero; named four-audio/one-video structure; no clip effects; original media
references; embedded MP4 audio excluded by chain and track routing; track
semantics survive reopen/save; twelve sample-exact excerpt WAV comparisons.
No source hash or real XML is published. The exact local runtime comes from
ignored `.local/S00-inputs.json`; the Windows Store `python` alias is not the
runtime used here.

**Actual GUI checks PASS:** new four-participant project created and saved in
Kdenlive; matching 1280x720/25 FPS profile; original MP4 inserted video-only;
four original WAVs placed at zero and tracks named. Playback showed changing
picture, timecode and meters between 00:01:00:10 and 00:01:10:10. Opening the
synthetic reference closed it; the real starter reopened without missing-media
or repair prompts and was saved as a new private copy. This is genuine native
GUI provenance. Group edits and renders of the real recording are **NOT RUN**;
the prior synthetic group-edit/undo/GUI-render PASS remains the evidence for
those reference capabilities.

**Failures retained and resolved or bounded:**

- Initial private comparison failed because it treated volatile native IDs as
  stable. Resolving source identity and track structure corrected that invalid
  comparison. A real one-frame sequence range change remains recorded, not
  ignored as equivalent.
- FFmpeg PCM stream-copy excerpts failed exact 30-second sample counts due to
  packet boundaries. They were retained privately. Separate replacement WAVs
  use exact original sample slicing; all twelve pass byte comparisons.
- Optional SciPy signal inspection did not start because SciPy is absent. No
  package was installed. Existing NumPy 2.3.5 provided the bounded local check.
- The first attempt's startup, offset-placement, root-resolution and newline
  failures remain in its original handover/capture record.

## Content and synchronization checks

The sources total about 34 minutes. Video metadata is 1280x720, 25/1 nominal and
average FPS, 51092 frames and 2043.68 seconds. Cleaned audio is stereo **192 kHz,
16-bit PCM**. One WAV has 392388608 sample frames; three have 392384512, a
4096-sample / 21.333333333 ms difference. The embedded mix is stereo 48 kHz AAC.
The profile's colorspace 601 matches the reported matrix family; no wider color
or format support follows from this one example.

Every native clip entry covers 51092 project frames. Its 2043.68-second coverage
is 10.666666667 ms shorter than the longest WAV and that much longer than the
others. On reopen/save the sequence's inclusive `out` grows from 00:34:03.640 to
00:34:03.680, while all clip entries remain unchanged. Ordered track semantics
match; **whole-project semantics are not equal**. S02/S03 must account for this
native sequence extent and source-tail behavior before claiming exact export.

Three limited 20-second correlation windows against the embedded mix show
different subframe peaks (0, +10 ms and approximately -32.69 ms for stronger
comparisons). Inactive channels provide no anchor. This is not per-participant
offset/drift certification or a retiming instruction. No audio/picture was
shifted, no source was normalized or denoised, and no original was overwritten.
Speech/laughter/overlap retention, noise cleanup, pause quality and subjective
lip-sync/listening acceptance are **NOT RUN**; those require later pipeline work.

Three private 30-second excerpt sets cover [0,30), [1000,1030) and [2013,2043).
Their twelve WAVs each have exactly 5760000 original sample frames and byte-match
source ranges. Video previews were re-encoded privately without embedded audio.
Content-specific labels are pending; the full original corpus remains located
for later selection. No claim is made that these windows contain every event
needed for quality acceptance.

## Git and CI

Relevant implementation commit: **1d81a245a4a5986ecbfe4fff7d341b84d2ebcf78**.
No implementation change or empty work commit was needed for this retry.
Branch: `codex/kdenlive26-overhaul`. Handover:
`docs/handovers/S01-attempt-02.md`. Resolve its documentation checkpoint SHA from
Git history; the final chat gives the actual pushed SHA and CI state.

Synchronization must be verified live at this checkpoint. Do not infer it from
the previous clean result or a tracking ref. Stage only reviewed public docs;
keep the corpus, raw XML, screenshots and local scripts ignored. Preserve the
existing license and origin. No reset, stash, force-push, PR, tag, release or main
integration is requested. At the preceding checkpoint GitHub exposed zero
workflows/runs/checks/statuses; inspect this exact new SHA before finishing and
do not describe absent CI as green.

## Artifacts and usage

Public evidence and the three synthetic `.kdenlive` projects remain under
`tests/fixtures/kdenlive-26.08.2/`; public tests require no private media. For the
real interview, consult the ignored corpus index and open its original native
starter path in Kdenlive. Use new copies for later exporter experiments. Keep
the five authoritative original source hashes as the recovery baseline. Never
pass the real project through the synthetic-only sanitizer.

## Remaining limitations and blockers

No essential S01 access blocker remains. No user action is required to start the
next step. S01 completion is bounded to the selected brief's capture/intake gate;
it does not waive remaining regression work. Product export, native clip gain
edges and G01/G02 proof are S02. Exact source offset/drift/tail contracts are
S03. GUI 3/6/8-participant, fractional-rate and supported UNC coverage remain
NOT RUN and required before broader tested compatibility. The earlier N=3/6/8
media-generation smoke is not GUI evidence. No future-version guarantee exists.

## Next thread

Execute **S02 — Prove editable Kdenlive 26 export** only. Read state and this
handover, resolve/verify the live checkpoint, then follow the S02 brief.

> Execute S02 only in the existing InterviewAutoEditor checkout on
> codex/kdenlive26-overhaul. Read AGENTS.md, docs/project/STATE.json,
> docs/NEXT_STEP.md, docs/handovers/S01-attempt-02.md, the execution/GitHub protocols
> and docs/project/steps/S02.md. Verify live local/remote SHA equality and clean
> state before editing. S01 implementation is
> 1d81a245a4a5986ecbfe4fff7d341b84d2ebcf78; resolve the latest documentation
> checkpoint from Git. Use genuine public references and the ignored private
> corpus index. Build the minimal adapter and one manually specified shared
> interior cut, writing a new editable project with N named audio tracks,
> embedded MP4 audio excluded, a group and guide. Prove G01/G02 through actual
> open/play/group-edit/undo/save/reopen/GUI-render, and test native gain edges.
> Retain the recorded native sequence/tail findings; do not implement automatic
> speech/pause decisions or start S03. Commit, push, verify live SHA equality and
> clean status, inspect exact-SHA CI, provide a verbose handover and STOP.

## Pause

Paused after S01. The next thread should execute S02 only.
