# S09 synthetic picture/seam and cleanup fixture

This package contains generated tones/noise and grayscale video, with no recorded
people, voices or private interview material. The independent picture switch is
source frame 138 at 25 FPS; all participant tracks have construction-labelled
silence [4,7) s. S06 removes [105,172); S09 removes only [105,138), restoring
34 frames on every track. Output is 267 frames / 10.68 s, six three-clip groups,
four reversible native Volume spans and source/output review guides.

`before.kdenlive` is hand-relinked from the genuine S01 starter.
`picture-cleaned.kdenlive` is production adapter output. Neither is a new native
Kdenlive save. `construction.json` labels this distinction and hashes generated
inputs/results. Use `tools/s09_fixture.py` with a **new** directory to reproduce
construction. It never creates actual-application evidence.

`native-roundtrip.kdenlive`, `group-moved.kdenlive` and `native-undone.kdenlive`
are sanitized actual Kdenlive saves. The move changes the final group from
output 192 to 217 on all three tracks; Undo restores the original semantics.
`gui-render.mp4` is the actual full-project GUI render, not the primary editable
deliverable. The sanitized native and undo files happen to be byte-identical.
Resource relinking and removal of private metadata preserve timeline semantics.
See [PROVENANCE.json](PROVENANCE.json) and
[render-validation.json](render-validation.json) for exact evidence and hashes.

The actual capture is Kdenlive 26.08.2 rev. d4e87e4, MLT 7.43.0, Qt 6.11.1 on
Windows AMD64. Open/play/group move/undo/save/close-by-opening-another/reopen/render
passed without repair or missing media. All 267 rendered picture frames match
the shared source map, with exactly one switch at output 105. Protected tones,
audio anchors, idle attenuation and headroom survive. This is no human-speech,
real-layout, held-out, fractional-FPS GUI or wider-build acceptance claim.
Compatibility remains EXPERIMENTAL.

Private requests/results/projects may contain identities, notes, fingerprints
and timecodes. Do not publish real material using this synthetic package as an
assumed privacy scrubber. Full bin originals remain recoverable. Removing picture
observations recovers baseline S06 pacing; removing idle approvals recovers unity.
Source-time Keep restores intervals globally after replanning/rebinding.
