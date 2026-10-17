# Tested compatibility

Target family: Kdenlive 26.x. S01 independently confirmed the installed
**26.08.2 - rev. d4e87e4** build on Windows NT 10.0.26300.0 / AMD64.
MLT is 7.43.0; the Qt6Core DLL reports 6.11.1.0; bundled FFmpeg is 8.1.1.
The actual synthetic reference round trip passed. A product exporter has not
been implemented. Real example media and private excerpts are now located;
initial intake and a native four-participant starter open/save check are complete.

| Build and platform | Document capabilities | Status | Evidence commit/path |
|---|---|---|---|
| 26.08.2 rev. d4e87e4 / observed Windows build above | Saved document 1.1; MLT XML 7.43.0; linked input, video-only use, two participant tracks, groups/cuts, guide, track gain, relative references | EXPERIMENTAL product compatibility; synthetic reference checks PASS | [S01 capture record](fixtures/S01_CAPTURE.md), [provenance](../tests/fixtures/kdenlive-26.08.2/PROVENANCE.json), [render measurements](../tests/fixtures/kdenlive-26.08.2/render-validation.json); containing work commit resolved from Git history |

All three sanitized references opened in the actual application. The grouped
fixture passed play, group deletion/undo, save as a copy, close/reopen and GUI
render. A moved-folder open with spaces/Unicode passed. A private four-participant
starter created from the owner's media also passed play, save, close, reopen and
save-copy. Its track entries survived unchanged, but the sequence out point grew
by one frame on reopen/save; this is not full semantic equality. See
[the real-input record](fixtures/S01_REAL_INPUTS.md).

Full interview timing/quality acceptance,
3/6/8-participant GUI fixtures, fractional-FPS GUI fixtures, UNC paths and native
clip-gain edge behavior remain untested. Future builds are untested; no all-26.x
or future-version compatibility guarantee is made. S01's capture/intake gate is
complete. S02 must prove the eventual exporter and native gain edges separately;
S03 must validate offsets, drift and source-tail handling. The pending wider
regression matrix remains required before a broader tested compatibility claim.

Do not replace this table with a blanket '26 and later' claim. Update only from actual evidence under docs/project/KDENLIVE_COMPATIBILITY.md.
