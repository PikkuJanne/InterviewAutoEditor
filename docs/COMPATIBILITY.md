# Tested compatibility

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
