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

Do not replace this table with a blanket '26 and later' claim. Update only from actual evidence under docs/project/KDENLIVE_COMPATIBILITY.md.
