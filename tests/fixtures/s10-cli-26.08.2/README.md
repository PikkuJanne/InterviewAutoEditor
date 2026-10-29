# S10 CLI application regression

Generated tone/noise/luma content copied byte-for-byte from the
[S09 construction](../s09-picture-26.08.2/README.md). No recorded people, private
interviews or held-out content. S10 ran the reviewed analysis, pause request,
picture observations and refined-bound cleanup through one recoverable CLI run.
See [commands and recovery](../../../docs/project/S10_CLI.md).

`planner-request.json` is the strict request extracted from S09's base result.
`picture-cleaned.kdenlive` is CLI adapter output with public relative media paths,
**not** Kdenlive-authored. Integrated output is normally `project.kdenlive` in a
private run folder. Full manifests contain local paths and stay ignored/local.

`native-roundtrip.kdenlive`, `group-moved.kdenlive` and `native-undone.kdenlive`
are sanitized actual **Kdenlive 26.08.2 rev. d4e87e4** saves. The native copy was
opened, played and saved. Its final three-member group moved 25 frames and was
undone/saved. Opening another project closed it, then it reopened without repair.
`gui-render.mp4` is the actual full-project MP4-H264/AAC GUI render, requested
00:00:10:17, UI completion 00:00:01. It is validation, not the primary output.
Resource/UI sanitization preserves timeline/effect semantics.

[PROVENANCE.json](PROVENANCE.json) binds raw/public artifact hashes.
[render-validation.json](render-validation.json) remeasures twelve S09 checks on
this new capture: 267 mapped pictures, one switch at output 105, protected probes,
original timing, idle noise, group movement/undo, headroom and MP4-audio exclusion.

```powershell
python -B tools/s09_validate_render.py --bundle tests/fixtures/s10-cli-26.08.2 --ffmpeg '<existing local ffmpeg>' --report '<new local report.json>'
```

Compatibility remains EXPERIMENTAL. This two-participant 25-FPS evidence adds no
private, held-out, human-word, future-build or wider GUI acceptance claim.
