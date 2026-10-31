# S11 local desktop workflow

Current Create editable project uses the ordinary `edit` service. Existing local
assets are discovered automatically, original timing/unequal endings are retained,
and no benchmark, approval JSON or mandatory owner sign-off is needed. Optional
records retain their exact bindings. See [ordinary workflow](S12_EDITOR_WORKFLOW.md).
Legacy inspection/preview commands and the historical details below retain their
strict contracts. A saved old job remains readable; a changed implementation
requires regeneration in a new folder instead of rewriting a partial manifest.

The desktop calls the same [Application service](../../interview_auto_editor/application.py)
as the [CLI](S10_CLI.md). Compatibility remains **EXPERIMENTAL**, targeting
Kdenlive **26.08.2 rev. d4e87e4**. Kdenlive provides playback and timeline editing.
The UI adds no timing, inference, silence-certification or cleanup policy.

## Launch and local setup

With the existing Python 3.12 environment prepared, double-click
[`InterviewAutoEditor.pyw`](../../InterviewAutoEditor.pyw). The launcher prefers
the repository's existing `.venv/Scripts/pythonw.exe` over a different system
file association. It does not install or download anything. An existing Windows
shortcut can target that runtime with this `.pyw` file as its argument. The
module entry point is also available for development:

```powershell
.venv/Scripts/python.exe -B -m interview_auto_editor.desktop
```

This is a source-checkout/packaging entry point, **not** a bundled installer or
clean-install release. Runtime/model bundling, redistribution and acceptance
remain S14/S15. Tkinter 8.6 ships with the tested local Python 3.12.14 runtime;
there is no new dependency, model, lock or licence change.

Local setup selects existing ffprobe, ffmpeg, speech/reaction assets, a private
cache directory and the installed Kdenlive executable. These paths may also come
from `IAE_FFPROBE`, `IAE_FFMPEG`, `IAE_S04_MODEL`, `IAE_S05_MODEL`, `IAE_CACHE` and
`IAE_KDENLIVE`; tools can be discovered on PATH. No network setup runs in the UI.
Assets are frozen in each job snapshot. Ordinary fresh forms do not persist
setup globally; a saved job resumes its exact original setup.

## Process a project without a terminal

1. Choose the **unedited starter project**. Read-only structural validation
   resolves its media and proposes neutral participant rows. Suggestions do not
   identify people. Load an existing mapping or edit each source ID, track name
   and channel labels, then explicitly confirm the mapping. Multiple labels on
   one shared microphone remain inseparable. The core requires every participant
   file exactly once, and excludes the MP4's embedded audio.
2. Choose **Tight** or **Gentle**. Select Inspect inputs, Analyze audio, Preview
   edits or Create editable project. Choose a **new private run folder**.
   Create editable project selects the documented experimental original-timing
   path. Other legacy export modes retain their explicit opt-in requirements.
3. Where available, use **Reviewed records** to select the matching saved analysis,
   global gap approvals, picture observations or picture request, and optional
   idle cleanup approvals. All fields are optional. The ordinary mode can shorten
   measured all-channel digital silence within existing protection rules;
   uncertain gaps/noise remain intact. Fresh CPU analysis keeps unknown offsets
   unset and complete source endings through the original-timing policy.
4. Start. Fixed stage messages and an indeterminate bar report real service
   progress; there is no fabricated percentage/ETA. The form locks while the
   worker runs. Cancel remains available. Closing during work requests safe
   cancellation and leaves the window open until the worker finishes.
5. Review exact original-source/output seconds, retained gap decisions, origin
   diagnostics and recorded-picture markers. Removed locations have no output
   time. Double-click a review row to read its full reason. Full private records
   remain in the run folder. Editorial review is available without a mandatory
   questionnaire or sign-off gate.
6. **Open copy in Kdenlive** verifies the run's recorded artifacts, creates a new
   sibling `RUN-edit-<id>/project.kdenlive`, and launches the explicitly selected
   local executable using an argument array. Keeping the copy at the same folder
   depth preserves relative media references. Save manual edits in that copy;
   the validated run remains immutable. A successful launch is not a claim that
   an arbitrary installed build has passed compatibility tests.

The checkout's **Load synthetic example** button explicitly selects the existing
S09 starter/mapping/analysis/pictures/cleanup and S10 gap request. These contain
generated tones/noise/pictures and construction labels, with no recorded people.
It still requires mapping confirmation, a new destination and experimental
opt-in. This is a reproducible demonstration, not an origin certificate for real
interviews. It produces 267 shared frames, six groups and four native gain spans.

## Keep and Restore

Review a completed plan/export, then choose **Keep / Restore source interval**.
Select a source identity and enter original source seconds as exact fractions or
decimal text, with inclusive start and exclusive end. Both actions retain that
time on **every** track. Restore audible also restores unity through the existing
S08 override rule. Production contracts validate the interval and binding.

Apply creates a pending request for the **next new run**. It neither changes the
completed run nor creates a silence approval. Choose the original matching
starter/mapping, leave the matching picture observations selected, and select a
new output folder. Pending restoration can be discarded. Starting another
project/example or reviewing another run clears pending restoration.

Pacing/override changes can invalidate cleanup's complete refined-plan binding.
The desktop preserves that refusal: it never silently rebinds old approvals.
Preview without cleanup, then explicitly load independently reviewed/rebound
cleanup approvals, or clear cleanup for unity gain. Changing analysis similarly
requires genuinely matching approvals/observations. Original unverified origins,
null offsets and unequal exact tails still refuse even identity export.

## Recovery and privacy

Beside `RUN`, the desktop writes exclusive `.RUN.desktop-mapping.json`, optional
`.RUN.desktop-request.json` and `.RUN.desktop-job.json`. The strict versioned job
freezes all service options as absolute paths. It is configuration, not a signed
approval or replacement for the service manifest. All these files are **PRIVATE**
for real material. Partial snapshot failure may leave completed configuration
files; choose a new destination and preserve those for local inspection.

The unchanged service owns `.RUN.incomplete`, advisory locks, source/tool/code
identities, artifact hashes, cache validation, no-overwrite and atomic final
publication. The desktop never inserts its files into that staging directory.
Cancel/failure retains staged evidence and completed caches; no partial final
folder is shown as success. Probe/hash/decode/peak cancellation is cooperative;
pure planning still checks at stage boundaries.

**Resume saved job** explicitly picks the original `.RUN.desktop-job.json` and
resumes its original options; current form edits are not applied. Changed
inputs/settings/code/paths refuse. Existing completed destinations refuse. If
an asset failed before staging existed, restore it and use a new run destination.
Corruption fails closed; nothing is automatically deleted or repaired. **Review
saved run** verifies historical artifact hashes; it does not revalidate current
source media. See [S10 recovery](S10_CLI.md) for journal/lock/platform details.

UI errors use fixed, actionable text and never interpolate raw exception paths,
names, hashes or content. The local form/review deliberately displays the user's
chosen paths and review data. Keep screenshots, whole runs, mappings, requests,
reports and caches out of public Git/CI. The desktop has no account/cloud flow.
No new listening or connection is required.

## Evidence and limits

See [workflow recording](../fixtures/S11_WORKFLOW.md),
[aggregate evidence](../fixtures/S11_DESKTOP_EVIDENCE.json),
[focused checks](../../tools/test_s11_desktop.py) and
[handover](../handovers/S11.md). The full suite retains all S03-S10 safeguards,
including the original 12.00/12.45 picture lag, source-time restoration,
protected events/full handles, grouping/bin originals and conservative headroom.
There are no changes to the Application service, policies or export adapter.

Tk row scaling at 8 and 64 participants is a presentation smoke check; it is not
a 64-track media/export or native Kdenlive acceptance claim. Existing core
synthetic exports cover 1/2/3/6/8 audio tracks. Wider GUI track/FPS/build matrices,
screen readers, small-screen layouts, Linux/network filesystem publication,
two-hour stress, full/held-out interviews and clean-install packaging remain
unaccepted. Prior actual Kdenlive full edit/save/reopen/render evidence is
retained separately; S11's new visible application check is open/play only.
