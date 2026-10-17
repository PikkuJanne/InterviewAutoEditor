# InterviewAutoEditor

InterviewAutoEditor is a planned local Windows tool for turning a Zoom interview
starter project into a new, editable Kdenlive project. **There is no working editor
yet.** The repository contains the planning bootstrap, Git checkpoint tooling
and S01's genuine synthetic Kdenlive reference captures and capture tools.

The installed primary target is independently verified as **Kdenlive 26.08.2,
revision d4e87e4**. Its two-participant synthetic reference passed actual GUI
open/play/group-edit/undo/save/reopen/render checks. Product compatibility remains
experimental: there is no exporter yet. S01 is complete: the owner's example
media is privately indexed, and a genuine four-participant starter was saved,
played and reopened in Kdenlive. Initial intake exposed timing differences that
still require S03 validation. See [the compatibility record](docs/COMPATIBILITY.md),
[capture evidence](docs/fixtures/S01_CAPTURE.md) and
[private-input observations](docs/fixtures/S01_REAL_INPUTS.md).

## Planned workflow

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

These are requirements, not implemented capabilities. Audio processing, model
installation, export and desktop UI development have not started.

## Development and continuation

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

With Python 3.9 or later and Git on PATH (S00 uses Python 3.12.14):

```powershell
python -m unittest discover -s tools -p test_verify_checkpoint.py -v
python -B -m unittest discover -s tools -p 'test_*.py' -v
python tools/verify_checkpoint.py --repo .
```

Tests use disposable local Git repositories and public synthetic captures; they
need no private recordings or GitHub connection.
The read-only verifier requires an already committed, pushed checkpoint and
network access. It checks the live branch SHA, upstream, worktree and basic state
references; it does not run CI, test Kdenlive or validate the full product.
Running it with uncommitted work correctly fails.

Keep real recordings, transcripts, credentials and private local paths outside
public Git. Ignored `.local/` notes retain machine-specific input locations;
public fixtures must be synthetic or explicitly shareable and reviewed.

The existing [MIT license](LICENSE) is preserved unchanged.
