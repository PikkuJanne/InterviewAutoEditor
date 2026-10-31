# Exact-build compatibility and on-demand maintenance

S13 separates project structure, the project writer's version and the locally
selected editor binary. The registry is in
[`adapters/compatibility.py`](../../interview_auto_editor/adapters/compatibility.py).
The [current matrix](../COMPATIBILITY.md) is deliberately an exact build/platform
claim. A plausible XML file or a successful MLT render cannot promote a build.

## Probe and export

From the prepared checkout, create a NEW report:

```powershell
.venv/Scripts/python.exe -B -m interview_auto_editor compatibility-probe --project '<simple starter.kdenlive>' --target-kdenlive '<installed kdenlive.exe>' --output '<new private report.json>'
```

The probe reads UTF-8 XML and local media references, validates the complete
simple-starter topology and hashes the supplied executable. It never executes a
project-supplied program, starts the editor, downloads media or writes a project.
Omit `--target-kdenlive` for structure-only probing. Schema-2 report exit codes:
0 TESTED; 2 EXPERIMENTAL; 1 UNSUPPORTED or failed report publication. Reports
never overwrite an existing destination. Diagnostics use fixed codes.

TESTED requires the exact registered executable SHA-256, writer patch and
observed platform tuple. The application/document/MLT versions are distinct.
The executable hash identifies the measured installation; it is not a signature,
whole-installation integrity attestation or a claim for other library bundles.
The probe cites retained genuine evidence and explicitly says that it did not
operate the editor during probing.

`edit`, `run` and `export` accept the same optional `--target-kdenlive` flag.
A matching target permits normal export without `--experimental`. An unregistered
binary, another platform, an absent target or a different writer patch remains
EXPERIMENTAL and needs explicit opt-in for advanced commands. Ordinary `edit`
already chooses the documented conservative experimental path, so this adds no
setup/review prerequisite to ordinary generation. A supplied unreadable target
refuses export. Target hashes are bound into recoverable runs and rechecked before
publication; changed binaries cannot silently resume or retain tested status.

A future well-formed writer version with document 1.1 can select the observed
simple-starter adapter as a candidate. It must pass every structure, timing,
stream, media and routing check before experimental export is possible. Unknown
attributes, unknown document versions, nested/edited timelines, retiming, active
processing and unsafe references stop export even with opt-in. The original
writer/document versions are preserved; no silent downgrade occurs.

Unsupported **project timing is not imported for analysis**. Existing independent
canonical Analysis records, local source-media inference and planning remain
usable through the analysis modules/tools; a capability refusal neither deletes
them nor changes detector/planner contracts. It is not safe to infer an arbitrary
unknown timeline's timing from its media. Restore a simple starter in a tested
editor before running the complete project pipeline.

## New stable build procedure

1. Check official downloads/releases on demand; record date, exact patch,
   revision, platform and source URLs. Keep production installed. Use a separate
   portable/test installation and synthetic media for candidate builds. No
   recurring automation or automatic update is created.
2. Capture a genuine starter in that build and retain the raw hash privately.
   Record application, document, MLT, Qt and FFmpeg independently. Sanitize a copy;
   state which metadata/paths changed. Generated or hand-mutated XML is labelled
   as such, never native evidence. Open the sanitized copy as a separate check.
3. Run the probe on the genuine starter. Compare sequence/bin references, track
   routing, groups, guide serialization, native gain keys, EOF, streams, custom
   profiles and path resolution. Relative-root semantics deserve particular
   attention: the announced 26.12 development changes include relative paths.
4. If semantics differ, add a versioned adapter/capability implementation at the
   adapter boundary, with precise refusal codes and independent regression
   cases. Do not broaden allowlists solely to make one document parse. Keep
   analysis, pause removal, audibility, turns and picture rules separate.
5. Exercise open/play, group move or ripple edit/undo, save a NEW copy, close,
   reopen and render in the actual candidate. Compare semantic timing, names,
   groups, effects, source/output bounds and audio/picture anchors. Cover the
   production patch again if exporter behavior changes. Test the oldest build
   before declaring any range; otherwise publish only individual measured rows.
6. Run the public suite with existing pinned local CPU assets. Check full private
   interviews when affected; preserve unknown offsets, complete ends, scoped
   mutes, original media and retired owner-study records. Do not ask the owner
   to repeat routine QA. Numerical accuracy claims still need independent labels.
7. Only after required native checks pass, add the exact build identity/evidence
   to `TESTED_BUILDS` and the matrix. Record implementation commit separately
   from the documentation checkpoint. Commit, push, verify live SHA and clean
   worktree. Unknown future versions never inherit tested status.

Prereleases are optional canaries, never release prerequisites. On 2026-10-31
official 26.11.70 development testing was available. It was not installed/run:
S13 establishes the production/latest-stable row; relative-path behavior remains
unverified on that development build. Its absence from the tested matrix is
non-blocking and is not a missing production test.

## Plan/cache migrations

No canonical wire-schema migration is needed in S13. Strict Analysis/EditPlan
schema 1, PlannerRequest/PlanningResult schema 1/2 and both tail policies retain
their codecs and invariants. The historical `kdenlive-26.08.2-experimental`
`adapter_target` string remains an exact wire identifier, now centralized as
`PLAN_TARGET`; its spelling is not a runtime compatibility decision. Do not
replace it in old JSON just because a build gains tested status.

If a future schema changes, implement a named old-version-to-new-version codec.
Read and validate the old record, write a NEW record, retain original bytes/hash,
record both versions and migration implementation, and validate exact rational
intervals, protected events, one shared time map, EOF, source hashes, overrides
and scoped approval bindings. Unknown schema versions fail closed. Do not
certify null offsets, widen mute authority, rebind stale approvals or synthesize
human judgments during migration. Inference caches remain source/model/decoder
bound; adapter changes alone need no new inference when those identities agree.

Old desktop schema-1 jobs lacking optional `mutes` and/or `target_kdenlive` load
with their original empty/default meanings. Run manifests include implementation
hashes; an old incomplete transaction cannot resume after changed code/settings.
Read/verify its retained artifacts, create a NEW destination, explicitly reuse
valid source-bound analysis and regenerate dependent picture records if their
implementation binding changed. Keep the old job and failed staging evidence.
Never edit an old manifest to defeat recovery's identity check.
