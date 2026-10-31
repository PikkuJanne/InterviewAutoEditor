# Tested compatibility

## Current matrix — rechecked for S15 on 2026-10-31

The exact measured target is **26.08.2 rev d4e87e4 / Windows 11, NT
10.0.26300, AMD64**; MLT 7.43.0, Qt 6.11.1 and FFmpeg 8.1.1. Its executable
SHA-256 is `7a5bbf2e7764514a863fad756fe2195779475804706a8a74e73ab922def1d352`.
The official [download page](https://kdenlive.org/en/download/) and
[release index](https://kdenlive.org/categories/release/) list 26.08.2 as latest
stable at this check. Production and latest stable are the same row. No version
range is declared, so no additional oldest-supported build is implied.
The S15 check of the official release index still lists 26.08.2 as newest
stable. S14 additionally passed the final packaged ordinary output's actual
primary open/play/group move/save/undo/quit/reopen/GUI render. Clean Windows
Sandbox NT10.0.26100 passed setup, CPU generation and desktop operation, while
its editor registry remains EXPERIMENTAL. This does not extend the TESTED row.

| Build / structure / target | State and export behavior | Measured scope |
|---|---|---|
| Exact production/latest-stable build and platform above, document 1.1, simple starter, matching supplied executable | TESTED; normal export without experimental flag | Fresh S13 genuine open/play/three-member group move/save/undo/save/quit/reopen/GUI render; two-participant 25 FPS synthetic with shared cut, guides, native gain, relative media and embedded MP4 audio excluded. Prior S12 full two/four-participant native/render evidence retained. |
| Recognized document 1.1 simple starter, target omitted or executable/platform/writer outside measured row | EXPERIMENTAL; advanced export needs explicit opt-in to new copy | Structural checks only. Future 26 patches/27+ do not inherit tested status. Ordinary conservative edit remains available without a questionnaire. |
| Unknown document or unsafe topology, attributes, retiming, source processing or references | UNSUPPORTED; no project export, even with opt-in | Precise reason in probe; existing canonical analysis/planning and direct media analysis remain usable independently. Unsupported project timing is not inferred. |
| Official 26.11.70 development canary | NOT RUN; no tested claim | [Official testing notice](https://kdenlive.org/news/2026/october-testing/) describes upcoming relative-path changes. Optional canary was not installed; this does not block the stable row. |
| Other OS/build combinations, older pre-26 versions, unknown document families | No tested support | Probe decides experimental candidate vs unsupported from actual structure; there is no all-26.x or 26+ guarantee. |

Evidence: [S13 provenance](../tests/fixtures/s13-compatibility-26.08.2/PROVENANCE.json),
[render measurements](../tests/fixtures/s13-compatibility-26.08.2/render-validation.json),
[aggregate](fixtures/S13_COMPATIBILITY.json) and [S13 handover](handovers/S13.md).
Current implementation SHA is recorded in the handover. Earlier compatibility
labels below are historical checkpoint snapshots, superseded only within this
explicit tested scope. A tested format/build is not a stable product release,
word-accuracy score, performance promise or clean-install package certification.

The fresh GUI render contains 267 mapped frames with zero RGB MAE against this
synthetic source, four zero-lag measured audio anchors, retained overlap and gain
keys, and no audible MP4 marker. Native movement shifts all three final clips
25 frames without changing source bounds; undo restores full semantics.
The sanitized native copy also opens without repair or missing media.
Automated count/fractional-FPS coverage is separate from GUI coverage: 3/6/8-track
and fractional-FPS GUI operation, UNC and other machines remain untested.
The two complete private interview deliveries retain their S12 evidence; S13
does not claim a new full real-interview render or independent subjective score.

Use the [probe and maintenance guide](project/S13_MAINTENANCE.md). Supply
`--target-kdenlive` to bind the exact local binary. Without it the probe reports
EXPERIMENTAL even when the writer string says 26.08.2. It does not operate the
GUI. Canonical plans keep their existing exact schema/adapter identifier; no
silent migration, version downgrade or approval rebinding occurs. G02 and S13's
compatibility portion of G10 pass; completed clean-install evidence is in
[S14 acceptance](fixtures/S14_RC_VALIDATION.json). Stable release verification
is recorded separately by S15; earlier stage descriptions below are historical.

## Historical S01–S12 checkpoint records

Target family: Kdenlive 26.x. S01 independently confirmed the installed
**26.08.2 - rev. d4e87e4** build on Windows NT 10.0.26300.0 / AMD64.
MLT is 7.43.0; the Qt6Core DLL reports 6.11.1.0; bundled FFmpeg is 8.1.1.
The actual synthetic reference and S02 adapter-output round trips passed.
The minimal exporter is an experimental manual-cut proof. Real example media and
private excerpts are now located; initial intake and a native four-participant
starter open/save check are complete.

| Build and platform | Document capabilities | Status | Evidence commit/path |
|---|---|---|---|
| 26.08.2 rev. d4e87e4 / observed Windows build above | Saved document 1.1; MLT XML 7.43.0; integer-FPS simple starter; variable-count adapter; two-participant GUI export proof, shared manual cut/groups/guide, native entry Volume ramps, MP4-audio exclusion and relative references | EXPERIMENTAL product compatibility; bounded S02 G01/G02 PASS | [S02 proof](fixtures/S02_EXPORT_PROOF.md), [provenance](../tests/fixtures/kdenlive-26.08.2/s02-PROVENANCE.json), [render measurements](../tests/fixtures/kdenlive-26.08.2/s02-render-validation.json); implementation SHA in [S02 handover](handovers/S02.md) |

All three sanitized references opened in the actual application. The grouped
fixture passed play, group deletion/undo, save as a copy, close/reopen and GUI
render. A moved-folder open with spaces/Unicode passed. A private four-participant
starter created from the owner's media also passed play, save, close, reopen and
save-copy. Its track entries survived unchanged, but the sequence out point grew
by one frame on reopen/save; this is not full semantic equality. See
[the real-input record](fixtures/S01_REAL_INPUTS.md).

S02's new editable output passed open/play/group delete and move/undo/native
save/close/reopen/GUI render. Its 275-frame video follows the shared map; native
sequence extent grows by one frame while timeline semantics match. Native entry
Volume keyframes are editable and measured at approximately -60 dB plateau with
400 ms ramps. This does not establish subframe gain or subjective no-click quality.

Full interview timing/quality acceptance,
3/6/8-participant GUI fixtures, fractional-FPS GUI fixtures and UNC paths remain
untested. Public hand-authored count mutations are automated structural tests,
not GUI evidence. Future builds are untested; no all-26.x
or future-version compatibility guarantee is made. S01's capture/intake gate is
complete. S02's minimal exporter/native-gain proof is complete within its stated
scope. S03 now inventories exact source tails and diagnoses unverified offsets
without repairing them. Its strict plan contract refuses unresolved tails or
unverified origins. Integer/fractional timing and fractional starter parsing have
automated coverage; fractional-FPS GUI export remains untested. See
[S03 contracts](project/S03_CONTRACTS.md). The pending wider
regression matrix remains required before a broader tested compatibility claim.

S04 local speech analysis does not change the exporter or compatibility status.
Its new CPU/model, cache and sample-grid tests are analysis evidence, not new
Kdenlive GUI evidence. Source tails and origin/correlation reviews remain
unresolved; no real export is authorized. See [S04 limits](project/S04_SPEECH.md).

Do not replace this table with a blanket '26 and later' claim. Update only from actual evidence under docs/project/KDENLIVE_COMPATIBILITY.md.

S08's separate approved-idle policy adds native Volume curves on multiple clips,
including nonzero source in-points after a shared deletion. Actual 26.08.2 rev.
d4e87e4 open/save/render and synchronized group movement pass; native key curves
and source bounds survive. Four synthetic noise probes measure over 30 dB of
suppression, and protected source probes remain within 0.1 dB. Native restoration
and the listening gate are recorded separately in the
[S08 guide](project/S08_CLEANUP.md) and current handover. No broader build, track
count, intersample-peak or held-out quality claim is added.

S05 adds local CPU reaction/uncertainty fusion only. It preserves all S04 and
intake findings and does not change the exporter or the EXPERIMENTAL status.
S05's bounded labelled-development G04 passes with direct-human preview overlap
confirmation, whole-preview shared protection and protected-source attenuation
refusal. Per-microphone detection gaps and uncertain exact annotations remain;
this is not Kdenlive, alignment, full-interview or gain-policy acceptance. See
[S05 evidence and limits](project/S05_REACTIONS.md).

S06 shared pause planning adds no Kdenlive format mutation or adapter changes.
Its exact frame/sample tests and construction-labelled v1 JSON fixtures are
planner evidence, not application-generated projects. The existing S02 GUI
render was remeasured successfully with all eleven checks, preserving the
recorded native one-frame extent delta. No new GUI round trip or real export
was performed. Real source origins/tails remain unresolved and their v1
refusals remain in force. See [S06 evidence and limits](project/S06_PLANNER.md).

S07 adds a separate production adapter integration for approved plans, aligned
turn/overlap groups and cue guides. Its generated 25-FPS six-group fixture has
automated timing, routing, recovery and N-track coverage. **S07 scoped G02/G03/G07
PASS in actual 26.08.2 rev. d4e87e4.** Open/play/group ripple extraction and
move/undo/save/close/reopen/GUI render passed. Sanitized native evidence also
opened. Native timeline/groups/guides match with zero sequence extent change
for this capture; historical S01/S02's one-frame deltas remain recorded.
The GUI render has 233 frames, 13 exact picture anchors, seven zero-lag audio
anchors and both overlap sources. Initial startup trouble was resolved when
the user opened the application; inherited construction-source cache hashes
were removed after an initial reload warning. Neither failure is hidden.
Product compatibility remains EXPERIMENTAL. See [S07 details](project/S07_EXPORT.md),
[actual provenance](../tests/fixtures/s07-turns-26.08.2/PROVENANCE.json) and
[measurements](../tests/fixtures/s07-turns-26.08.2/render-validation.json).

S09's recorded-picture integration passes applicable synthetic G02/G03/G07/G08
in actual **26.08.2 rev. d4e87e4 / MLT 7.43.0 / Qt 6.11.1**. The 267-frame GUI
render matches every source picture under the shared map, with one existing
switch at output 105, zero measured audio-anchor lag and retained S08 gain.
Native group movement/undo/save/reopen preserve semantics with zero extent delta.
The exact 20-FPS 12.00/12.45 example is separate decoder/math evidence, not a GUI
compatibility claim. Layout confidence remains heuristic; unknown/gallery/pinned/
camera-off handover seams restore time. Real origin/tail refusals and
EXPERIMENTAL status remain. See [S09 rules](project/S09_PICTURE.md) and
[actual provenance](../tests/fixtures/s09-picture-26.08.2/PROVENANCE.json).

S10 connects the same exporter through a recoverable application service. Its
integrated output is byte-identical to direct S09 export at matching resource
depth. A new actual **26.08.2 rev. d4e87e4 / MLT 7.43.0 / Qt 6.11.1**
open/play/group move/undo/save/reopen/render regression and sanitized native open
pass. All twelve render measurements pass with 267 mapped pictures and no
measured anchor lag. See [S10 usage](project/S10_CLI.md) and
[new provenance](../tests/fixtures/s10-cli-26.08.2/PROVENANCE.json).
The structural compatibility-probe command does not verify an installed binary
or certify future versions. Compatibility remains EXPERIMENTAL; wider build,
track/FPS, full-interview and held-out acceptance claims are unchanged.

S11 adds a Tkinter desktop over the unchanged shared service/policies/exporter.
Its new synthetic workflow creates an immutable run and opens a sibling editable
copy in actual **26.08.2 rev. d4e87e4** without repair or missing media; visible
playback reaches the output end. No new full group-edit/save/reopen/render cycle
is claimed. The existing genuine S10 full regression and render remain separate
and are remeasured by the full suite. The installed executable SHA256 still
matches the recorded primary build. Desktop row scaling is not a wider native
Kdenlive track/build acceptance claim. See [desktop use](project/S11_DESKTOP.md)
and [focused workflow recording](fixtures/S11_WORKFLOW.md).
