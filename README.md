# InterviewAutoEditor

Create a new editable Kdenlive interview from one unedited Zoom MP4 and N
aligned, already cleaned participant PCM WAV files. The Windows AMD64 portable
**1.0.0** release bundles Python/Tk and both CPU models; processing stays local.

Download the full portable ZIP and verify its hash from the
[v1.0.0 release](https://github.com/PikkuJanne/InterviewAutoEditor/releases/tag/v1.0.0).
Extract everything, then double-click `InterviewAutoEditor.cmd`. Use
`InterviewAutoEditor-cli.cmd --self-check` to verify files and local CPU setup.
Kdenlive/FFmpeg and Microsoft's Visual C++ x64 v14 runtime are separate
prerequisites. The archive is unsigned; paid signing is not required.

Read the [quick start](docs/QUICKSTART.md), [release notes](docs/RELEASE_NOTES.md),
[exact compatibility matrix](docs/COMPATIBILITY.md) and
[offline rebuild/maintenance guide](docs/project/S15_RELEASE.md).

The output has one video track and N named audio tracks, useful aligned groups,
original media in the bin and reversible native effects. MP4 audio is excluded.
Keep the immutable generated run and edit a separate Kdenlive copy. Global
pause removal requires exact all-participant silence and every protection
check; uncertain audio and overlap remain. Full leading/trailing coverage and
recorded Zoom picture timing survive. Cleaned files are not processed again.

Tested editor: **Kdenlive 26.08.2 rev d4e87e4 / Windows 11 NT10.0.26300 /
AMD64**, rechecked against the latest stable release on 2026-10-31. Other
builds remain experimental until tested; arbitrary edited starters refuse.
Zero safe cuts is a valid conservative result. Lower optional Keep/Restore
controls can be clipped on small screens; CLI/native restoration is available.
Broader DPI/accessibility and numerical accuracy/effort are unmeasured. The
timed owner exercise/usefulness sign-off is retired, not passed.

Source development needs Python 3.12 and the explicit pinned local assets
described in the guides. Run `python -B -m unittest discover -s tools -p 'test_*.py' -v`;
model/decoder integration tests require the configured assets and never download
them. See [state](docs/project/STATE.json), [continuation](docs/NEXT_STEP.md) and
the latest handover before maintenance. Preserve the original [MIT licence](LICENSE)
and [third-party notices](THIRD_PARTY_NOTICES.md). Keep recordings, transcripts,
reports, private paths and credentials out of public Git and support uploads.

## Historical development notes

The following stage descriptions are retained as history. References to pending
S13/S14 work or experimental product releases describe those checkpoints;
the current release, compatibility scope and recovery instructions are above.

S14 adds an unsigned Windows x64 portable **1.0.0-rc.1** candidate with a bundled
Python/Tk runtime, pinned CPU dependencies and both models. See the
[portable quick start](docs/QUICKSTART.md), [candidate notes](docs/RELEASE_NOTES_RC1.md)
and [rebuild procedure](docs/project/S14_PACKAGING.md). Kdenlive/FFmpeg and the
Microsoft C++ x64 runtime are separate local prerequisites. Exact acceptance is recorded in the S14 handover;
stable integration/publication belongs to S15.

Create a conservative editable interview from an unedited starter in the prepared
local environment:

```powershell
.venv/Scripts/python.exe -B -m interview_auto_editor edit --project '<starter.kdenlive>' --output '<new private run folder>'
```

Success prints the project path. This ordinary path preserves original timing,
complete endings and uncertain audio, excludes the MP4 audio, and supports
repeatable source-local mutes. It needs no mapping/approval JSON or owner
benchmark exercise. See the [editor workflow](docs/project/S12_EDITOR_WORKFLOW.md)
for local setup, conservative automation limits and recovery. The legacy CLI
details and historical step descriptions below remain reference material.

InterviewAutoEditor is an experimental local Windows tool for turning a Zoom interview
starter project into a new, editable Kdenlive project. **S10 provides a recoverable
experimental CLI** for inspection, local CPU evidence, approved shared pause
plans, reversible cleanup and recorded-picture review. Run folders contain an
editable project, exact plans, private manifests and review reports. See the
[S10 quick start and recovery guide](docs/project/S10_CLI.md). S12 adds an explicit
original-timing policy that preserves unequal source endings and marks missing
picture; legacy schema-1 origin/exact-tail refusals remain. See the
[original-timing guide](docs/project/S12_ORIGINAL_TIMING.md) and
[current editor delivery audit](docs/fixtures/S12_EDITOR_DELIVERY.md) and
[retained production audit](docs/fixtures/S12_PRODUCTION_COVERAGE.md).

**S11 adds a minimal local desktop** over that same service: double-click
[`InterviewAutoEditor.pyw`](InterviewAutoEditor.pyw) in the prepared checkout.
Pick a starter and new output, choose Tight/Gentle, run/cancel and open the
editable project in Kdenlive. Mapping and source-time Keep/Restore remain
available for deliberate advanced choices.
See the [desktop guide](docs/project/S11_DESKTOP.md). This is a source/packaging
entry point; bundled-runtime and clean-install release checks remain later work.

The installed primary target is independently verified as **Kdenlive 26.08.2,
revision d4e87e4**. S13 tests this exact build on the observed Windows 11/AMD64
platform, which matches the latest stable checked on 2026-10-31. Use
`compatibility-probe --project '<starter>' --target-kdenlive '<kdenlive.exe>' --output '<new report.json>'`
to check structure and exact executable identity. A matching target allows
normal export; unverified targets remain experimental, and unsafe structures
stop export. See the [matrix](docs/COMPATIBILITY.md) and
[upgrade/migration guide](docs/project/S13_MAINTENANCE.md).
Its two-participant synthetic reference passed actual GUI
open/play/group-edit/undo/save/reopen/render checks. S12 adds actual native edit,
reopen and full-render checks on both complete real interviews. Product
release remains experimental; tested compatibility is scoped to that exact row.
S12 technical delivery is complete;
independent corpus accuracy and subjective utility remain unmeasured, and the
timed owner exercise is retired. S01 is complete: the
owner's example media is privately indexed, and a genuine four-participant starter was saved,
played and reopened in Kdenlive. Read-only validation retains unverified origins
and exact tail differences; the explicit S12 policy exports them without
certifying unknown offsets. See
[the compatibility record](docs/COMPATIBILITY.md),
[capture evidence](docs/fixtures/S01_CAPTURE.md) and
[private-input observations](docs/fixtures/S01_REAL_INPUTS.md). See the
[S02 export proof](docs/fixtures/S02_EXPORT_PROOF.md) for exact limits, usage,
native gain-edge measurements, GUI evidence and recovery instructions.

## Product workflow

- Read a simple, unedited project with one Zoom MP4 and a variable number of
  aligned, already-cleaned participant audio files.
- Shorten confident global pauses through one shared time map across all tracks,
  preserving speech, laughter, acknowledgements, overlap and uncertain events.
- Produce one video track and named participant audio tracks with useful aligned
  cuts and edit groups, excluding the MP4's embedded audio from audible output.
- Keep original media recoverable, preserve full leading and trailing sections,
  and retain the recorded timing of Zoom picture switches during speech.
- Isolate Kdenlive format details in replaceable adapters. Future versions require
  their own evidence and are never automatically claimed compatible.

These are the full product requirements. S06-S10 connect conservative approved
pause planning, grouped export, idle cleanup and picture review. Scoped actual
Kdenlive synthetic round trips pass; the desktop uses the same contracts and
recovery rules. S12 full-interview technical checks pass; broader compatibility
checks follow the exact S13 matrix; clean-install release checks remain S14 work.
Real source offsets, drift and subframe tails remain unverified. The observed
native one-frame sequence extent change is retained explicitly in the proof.

S03 adds a read-only intake core, full video timestamp/PCM sample probing,
explicit participant mapping, bounded offset diagnostics, rational timing and
strict versioned analysis/edit-plan records. It reports unresolved origins and
every source-tail difference; it never repairs alignment or drops tails. See
[S03 contracts and command usage](docs/project/S03_CONTRACTS.md). The existing
S02 exporter is unchanged.

S04 adds offline CPU speech evidence per participant and physical PCM channel,
with a pinned Silero ONNX model/runtime, bounded stateful processing, local
caches and conservative uncertainty protection. It preserves every intake
tail/origin review and creates no cuts, gain changes or editable project.
See [S04 setup, commands and limits](docs/project/S04_SPEECH.md) and
[model/runtime licences](THIRD_PARTY_NOTICES.md). Real interview content
acceptance and laughter protection are not established by VAD.

## Development and continuation

S05 adds local CPU YAMNet reaction evidence, empirical signal-floor review and
additive speech/uncertainty protection. S05's bounded labelled-development G04
passes under shared-removal and current no-attenuation rules. Full-interview,
held-out and gain-policy acceptance remain untested.
See [S05 setup, evidence and limits](docs/project/S05_REACTIONS.md).

S06 adds Tight/Gentle shared pause plans, exact source/output mapping and
source-time Keep overrides. Every deletion requires an explicit global
removable-gap label bound to the analysis; negative model results alone never
authorize a cut. Full exterior handles, protected content and uncertainty
survive. Legacy schema-1 requests still refuse unverified origins/unequal tails.
See [S06 contracts, usage and limits](docs/project/S06_PLANNER.md). S06 exports
plan data only; it does not yet create an automatically edited Kdenlive project.

S07 derives meaningful source-group turns and overlap boundaries, keeps minor
backchannels as guides, and exports N+1 synchronized clips per edit group using
the same approved shared map. Synthetic before/after projects, actual native
saves and the GUI render pass the scoped Kdenlive 26.08.2 rev. d4e87e4 gates.
Legacy source origin/tail refusals and EXPERIMENTAL compatibility remain. See
[S07 usage, recovery and limits](docs/project/S07_EXPORT.md).

S08 adds explicitly approved, reversible idle-microphone gain automation. It
retains protected content, shared microphones, full handles and source-time
overrides, audits conservative mix headroom, and exports editable native Volume
effects. Missing model activity or correlation never authorizes suppression.
See [S08 policy, evidence and restoration](docs/project/S08_CLEANUP.md) and the
current handover for its listening gate status. Legacy origin/tail refusals and
EXPERIMENTAL compatibility remain.

S09 observes probable recorded-picture boundaries near substantial source-group
handovers. Safe seams only narrow existing approved shared-silence deletions;
uncertain layouts restore time and retain review markers. Speech and original
picture/audio timing survive, including the 12.00/12.45 delay case. S08 cleanup
must be rebound to the refined map. See [S09 usage and limits](docs/project/S09_PICTURE.md).

Execute one named step per chat and stop after its verified Git checkpoint.
Start with [NEXT_STEP](docs/NEXT_STEP.md), [STATE](docs/project/STATE.json),
the latest linked handover and [AGENTS.md](AGENTS.md).
The [step index](docs/project/STEP_INDEX.md),
[product specification](docs/project/PRODUCT_SPEC.md),
[architecture](docs/project/ARCHITECTURE.md),
[execution protocol](docs/project/EXECUTION_PROTOCOL.md) and
[GitHub workflow](docs/project/GITHUB_WORKFLOW.md) define the work.

Use `codex/kdenlive26-overhaul` for development. The stable `main` branch is
reserved for the defined final integration step. Read
[the S00 inventory](docs/project/BOOTSTRAP_INVENTORY.md) for preservation,
provenance, environment and reuse decisions.

## Available checks

With Python 3.12 or later and Git on PATH (S03 uses Python 3.12.14):

```powershell
python -m unittest discover -s tools -p test_verify_checkpoint.py -v
python -B -m unittest discover -s tools -p 'test_*.py' -v
python tools/verify_checkpoint.py --repo .
```

Tests use disposable local Git repositories and public synthetic captures; they
need no private recordings or GitHub connection.
S03 real-tool tests additionally need FFmpeg/ffprobe on PATH or in
`IAE_FFMPEG`/`IAE_FFPROBE`; absent tools are reported as skipped tests.
S04 CPU integration tests also need the locked runtime, explicit local model
and generated development fixture; see the S04 guide. No tests download models.
The read-only verifier requires an already committed, pushed checkpoint and
network access. It checks the live branch SHA, upstream, worktree and basic state
references; it does not run CI, test Kdenlive or validate the full product.
Running it with uncommitted work correctly fails.

Keep real recordings, transcripts, credentials and private local paths outside
public Git. Ignored `.local/` notes retain machine-specific input locations;
public fixtures must be synthetic or explicitly shareable and reviewed.

The existing [MIT license](LICENSE) is preserved unchanged.
