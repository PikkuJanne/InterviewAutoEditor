# Stable release and maintenance

The S15 build uses the accepted S14 application, launcher, runtime, wheels and
models unchanged. The builder accepts an explicit stable version to select
the archive identity and stable release notes. Its default remains the S14
candidate command. Historical evidence is preserved and scoped to its source.

From the clean integrated main commit, using the same pinned inputs as S14:

```powershell
python -B tools/s14_package.py --version 1.0.0 --runtime '<pinned install_only.tar.gz>' --wheels '<16 locked wheels>' --speech '<silero_vad.onnx>' --reaction '<yamnet.tflite>' --output '<new output directory>'
```

See [the offline build guide](S14_PACKAGING.md) for acquisition, exact locks,
licences and deterministic assembly. Build twice into distinct directories;
compare both ZIP hashes. The stable outputs are
`InterviewAutoEditor-1.0.0-windows-x64.zip`, matching `-source.zip` and
`SHA256SUMS.txt`. The source ZIP is the exact tracked release commit snapshot.
`PACKAGE.json` binds its commit, binary inputs and every unpacked file. A
separate public-safe `PROVENANCE.json` records the release commit, artifact
hashes, unchanged application/runtime comparison and applicable validation.

Integrate through the repository's current allowed workflow. Inspect branch
protection, rulesets, reviews, statuses, checks and Actions before merging.
Use normal merge/push, with expected head verification; never bypass rules,
force-push or replace a tag. After affected validation, tag the exact unused
`v1.0.0` main commit. Upload and verify all assets in a draft before publishing;
then independently download them and compare SHA256 and the remote peeled tag.
A draft is not publication. A later documentation checkpoint is recorded
separately from the immutable release commit/tag.

Native editor evidence can be retained only when application/launcher/binary
identities and output semantics remain unchanged. The S14 full clean Windows
and actual primary GUI results are separately identified, never relabelled as
a new S15 GUI run. S15 records final-asset checks and any newly executed tests
in its handover and evidence. Future exporter or media changes require affected
native and render validation. MLT/XML checks alone never certify editability.

Maintenance is on demand, after this step stops. Start from the live synchronized
main, read final state/handover, and scope one requested repair or compatibility
update. Follow [the exact compatibility procedure](S13_MAINTENANCE.md), preserve
unknown offsets, scoped source approvals and explicit plan migrations. New
versions receive new tags/assets; never replace `v1.0.0`. Keep real interviews,
transcripts, private paths and credentials out of public evidence. Report known
small-screen/DPI/accessibility limitations and unmeasured quality honestly.
Do not restart the retired owner study, invent S16 or schedule background work.
