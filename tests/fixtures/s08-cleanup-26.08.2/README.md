# S08 synthetic cleanup evidence

Generated mono PCM tones/noise and a generated test-picture MP4; no recorded
people. The starter is a hand-relinked S01 native reference. Exports are from
production code and are **not** Kdenlive-authored. See `construction.json` for
independent labels, original file hashes, shared removal and peak-bound report.

`baseline.kdenlive` and `restored.kdenlive` are byte-identical exports with no
gain. `cleaned.kdenlive` adds four native Volume envelopes. All three retain six
synchronized video-plus-two-audio groups, full source references and 233 frames.
Only the globally approved `[105,172)` source-frame interval is removed.

`native-roundtrip.kdenlive`, `group-moved.kdenlive` and
`native-interval-restored.kdenlive` are sanitized **actual Kdenlive 26.08.2 rev.
d4e87e4 saves**. `gui-render.mp4` and `gui-restored.mp4` are actual GUI renders.
Sanitization removes local root/profile/browser/render paths and changes only
resource locations to verified byte-identical generated media. Raw captures
stay local. `PROVENANCE.json` separates observed GUI actions from construction.

`render-validation.json` measures eleven checks, including four noise plateaus,
eight protected-source probes, sixteen gain edges, thirteen picture anchors,
five audio anchors, mixed peak, source routing and synchronized group movement.
`restoration-validation.json` measures native effect bypass and the second GUI
render. These measurements do not certify real human speech quality or held-out
acceptance. The separate synthetic speech listening status is in the S08 handover.

Reproduce construction into a new directory:

```powershell
python tools/s08_fixture.py --output '<new folder>' --ffprobe '<local ffprobe>'
```

Remeasure existing actual application artifacts:

```powershell
python tools/s08_validate_render.py --bundle tests/fixtures/s08-cleanup-26.08.2 --native tests/fixtures/s08-cleanup-26.08.2/native-roundtrip.kdenlive --moved tests/fixtures/s08-cleanup-26.08.2/group-moved.kdenlive --render tests/fixtures/s08-cleanup-26.08.2/gui-render.mp4 --ffmpeg '<local ffmpeg>' --report '<new report.json>'
```

Re-running construction never manufactures native application or listening
evidence. The moved-folder regression verifies byte-exact re-export with relative
references and no inference. Product compatibility remains EXPERIMENTAL.
