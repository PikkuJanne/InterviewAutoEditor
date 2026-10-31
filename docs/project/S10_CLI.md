# S10 recoverable local CLI

For ordinary interviews use the current [editor workflow](S12_EDITOR_WORKFLOW.md):
`edit --project '<starter.kdenlive>' --output '<new private run folder>'`.
It selects the original-timing policy, discovers existing local assets, prints
the project path and exits 0. Internal mapping/approval and benchmark files are
optional. The legacy command defaults and exit codes below remain unchanged.

The shared [`Application`](../../interview_auto_editor/application.py) service
connects S03-S09 inspection, CPU analysis, pause planning, picture refinement,
cleanup and the unchanged grouped exporter. Run from the repository with Python
3.12 and the existing locked environment. Compatibility is **EXPERIMENTAL**,
targeting Kdenlive **26.08.2 rev. d4e87e4**. Commands perform no downloads, cloud
processing, new denoising/normalization or alignment repair.

## Supported synthetic example

These are generated tones/noise/pictures with explicit construction labels and
verified-zero synthetic origins, not a private interview or an automatic origin
certificate. Use a **new** output directory:

```powershell
.venv/Scripts/python.exe -B -m interview_auto_editor run --project tests/fixtures/s09-picture-26.08.2/before.kdenlive --mapping tests/fixtures/s09-picture-26.08.2/mapping.json --analysis tests/fixtures/s09-picture-26.08.2/analysis.json --request tests/fixtures/s10-cli-26.08.2/planner-request.json --picture tests/fixtures/s09-picture-26.08.2/picture-analysis.json --cleanup-request tests/fixtures/s09-picture-26.08.2/cleanup-request.json --ffprobe '<existing local ffprobe executable>' --output .local/example-run --experimental
.venv/Scripts/python.exe -B -m interview_auto_editor report --run .local/example-run
```

The primary deliverable is `project.kdenlive` inside the run folder: one video,
two named audio tracks, six groups, 267 shared output frames and four reversible
native gain spans. Full originals remain in the bin. Open/edit/save a **copy**;
modifying a generated artifact invalidates its run integrity check. The flattened
GUI render is validation evidence, not a substitute editable output.

## Commands and safeguards

All five pipeline commands use `--project`, `--mapping`, `--ffprobe` and `--output`
(a new directory). `inspect` writes inventory/review evidence. `analyze` writes
fused analysis and a neutral summary. `plan` requires `--analysis` and writes
plans without export. `export` requires `--analysis` and exports after fresh
inspection/replanning. `run` connects everything, using explicit saved analysis
or the existing pinned local CPU models.

```powershell
.venv/Scripts/python.exe -B -m interview_auto_editor inspect --project '<starter.kdenlive>' --mapping '<private mapping.json>' --ffprobe '<ffprobe>' --output '<new private inspection folder>'
.venv/Scripts/python.exe -B -m interview_auto_editor analyze --project '<starter.kdenlive>' --mapping '<private mapping.json>' --ffprobe '<ffprobe>' --ffmpeg '<ffmpeg>' --speech-model '<pinned silero.onnx>' --reaction-model '<pinned yamnet.tflite>' --cache '<private cache directory>' --output '<new private analysis folder>'
.venv/Scripts/python.exe -B -m interview_auto_editor plan --project '<starter.kdenlive>' --mapping '<private mapping.json>' --ffprobe '<ffprobe>' --analysis '<reviewed analysis.json>' --request '<planner-request.json>' --output '<new private plan folder>'
.venv/Scripts/python.exe -B -m interview_auto_editor export --project '<starter.kdenlive>' --mapping '<private mapping.json>' --ffprobe '<ffprobe>' --analysis '<reviewed analysis.json>' --request '<planner-request.json>' --output '<new private export folder>' --experimental
.venv/Scripts/python.exe -B -m interview_auto_editor compatibility-probe --project '<starter.kdenlive>' --output '<new probe report.json>'
```

The compatibility probe reads supported starter structure/resources and reports
EXPERIMENTAL or UNSUPPORTED. It explicitly does **not** verify the installed
binary or run a GUI test. Missing media/unknown structure stops export. UNC and
explicit relocation pairs remain unsupported in this integrated export path.

`--request` is a strict S06 **PlannerRequest**, not a PlanningResult wrapper.
Omission defaults to Tight, no deletion approvals and no overrides. `--preset
gentle` changes pacing while retaining the request's source-time approvals and
Keep/audible overrides. It never rebinds stale analysis approvals. Removing global
approvals restores identity time. A source-time Keep/audible interval on any
source preserves that interval on **all** tracks. See [S06](S06_PLANNER.md).

Saved `--analysis` is an explicit user-provided strict record. The service
rechecks project/FPS, source hashes/grids, labels/mapping and origins against fresh
inspection. It permits already recorded reviewed origins; it never upgrades
fresh inference or unverified real input to verified. Raw model analysis ordinarily
remains unverified and cannot complete planning/export. S10 adds no origin
acceptance UI or certification policy. Original real origin/exact-tail refusals
remain. No source shift, stretch, padding, truncation or inferred offset occurs.

Optional `--picture` supplies reusable S09 observations; alternatively
`--picture-request` plus `--ffmpeg` performs bounded observation. Pictures only
narrow approved deletions, restoring shared time. All opening speech and original
12.00/12.45 timing survive. On resume, observations are reused after request,
analysis, implementation and decoder validation. See [S09](S09_PICTURE.md) for
frame budgets/layout fallbacks.

Optional `--cleanup-request` must bind the **refined** S06 result, including its
overrides. A base-bound request refuses; the service never silently rebinds it.
`plan` can first write the refined result for explicit review/rebinding before a
new export run. Source-time restoration requires corresponding cleanup bindings.
All protected events, overlap, shared microphones, exterior handles, native unity
margins and conservative headroom checks remain in [S08](S08_CLEANUP.md).

## Transaction and recovery

The final directory must not exist or have a hidden name. Its sibling
`.NAME.incomplete` is created exclusively. Strict v1 `manifest.json` records
command, service/input identity, attempt, stage, state and artifact hashes.
`inputs.json` records project/source/request/mapping/model/tool hashes and local
paths, implementation module hashes, runtime/platform and settings. This is
reproducibility evidence, not a signed approval certificate.

Completed artifacts are published exclusively. A crash between writing and
journaling can adopt only byte-identical deterministic reproduction. Resume
rehashes inputs/tools/sources, reproduces plans/refinement/cleanup/export and
checks journaled artifacts. It never overwrites inconsistent files. Every
JSON/project artifact has an 8 MiB bound; oversize data fails visibly. The private
report retains intake diagnostics, exact source/output/null review locations,
removal reasons, picture markers, cleanup and restoration instructions.

After validation the service fsyncs files/journal and atomically renames the
directory with **no replacement**, including an existing empty target. This is
verified on Windows/NTFS. Linux has a fail-closed renameat2 path; other platforms
refuse finalization. Linux/network filesystems were NOT RUN. Atomic visibility is
not a power-loss durability guarantee. Cancellation after commit belongs to a
subsequent operation.

Use Ctrl-C or `--cancel-file '<local flag path>'` (presence requests cancellation).
The service never creates/removes the flag. Bounded probes, hash loops, CPU
decoding/inference and peak frames cooperate; pure planning checks at stage
boundaries. Decoder children are killed/reaped. Failed/cancelled attempts leave
no partial final folder; completed caches and `.NAME.incomplete` survive.
The first completed analysis summary is retained on resume; its contents are
revalidated, allowing only valid cache-hit counters to differ on the new attempt.
New runs record their own cache-hit counts.

After removing your cancel flag, rerun the **same command and input/settings**
with `--resume`. A finalization crash with a complete staged journal still
reports incomplete until rename succeeds. `.NAME.lock` uses an OS advisory lock
released by process death; its harmless marker remains. Unrecognized existing
lock files are never modified. Abrupt death can leave private `.iae-*` scratch
beside the run; these are never bundled or considered success. Inspect/remove
only diagnosed derived scratch locally.

Missing files/models/tools can fail before journaling. Restore the asset and
rerun without `--resume` if no incomplete folder exists; otherwise resume
explicitly. Changed input bytes, settings, code or paths refuse partial resume:
start a new folder and reuse valid per-source caches. Never edit journal hashes
to bypass refusal. Corrupt cache/artifact data fails visibly; inspect the affected
derived entry privately, preserving originals and failure evidence. A completed
run is immutable: repeat invocation, including `--resume`, refuses. Regenerate
into a new directory.

Speech/reaction caches retain S04/S05 identities: content/grid/labels,
settings/protection, implementation, models/runtime and decoder. Both models and
runtime remain mandatory on hits. Changing pacing does not rerun inference.
Changed sources/models/decoders/settings invalidate affected entries or fail
validation. Explicit saved-analysis planning needs no model. Move source/output
packages together to retain relative resources; moving output alone does not
carry media. Regenerate using current mappings. Partial-run relocation refuses
because reproducibility identity includes paths.

`report --run` verifies historical artifacts and prints fixed stages/states/counts;
it does not revalidate current source media. Exit **2** means complete with review
required (also structural compatibility probes), **1** failure/refusal/incomplete
report, **130** cancellation. Exit 2 is never an alignment certificate.

## Privacy and evidence

**Keep whole runs, caches, mappings, requests, reports and plans private for real
material.** They can contain names, fingerprints, paths and timecodes. Console
errors omit input content/paths/hashes. Native projects/guides remain private;
even neutral summaries need publication review. No held-out material, additional
listening file or connection is required.

The [synthetic regression](../../tests/fixtures/s10-cli-26.08.2/README.md)
separates CLI construction from actual native saves/render. See
[S10 evidence](../fixtures/S10_CLI_EVIDENCE.json) and the
[handover](../handovers/S10.md). Full/held-out interviews, wider GUI track/FPS/build
matrices, two-hour stress and packaging remain later gates.
