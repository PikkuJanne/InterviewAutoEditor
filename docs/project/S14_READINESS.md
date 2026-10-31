# S14 candidate acceptance and S15 readiness

The unsigned **1.0.0-rc.1 Windows AMD64** candidate from source
`94e2b290ca30e9e87ae815379d0e0738f8720d5c` passes the applicable S14 technical
acceptance. Exact measurements, archive hashes and qualifications are in
[S14_RC_VALIDATION.json](../fixtures/S14_RC_VALIDATION.json) and the
[verbose handover](../handovers/S14.md). Live Git synchronization remains a
separate checkpoint check. This does not publish a stable release.

| Requirement | Recorded result |
|---|---|
| Pinned portable runtime/dependencies/models | PASS: CPython 3.12.16, Tk 8.6.15, 16 locked wheels, unchanged Silero/YAMNet, complete per-file inventory and notices |
| Reproducible candidate assembly | PASS: two independent final builds have identical runnable/source ZIP hashes; upstream native binaries are pinned, not independently rebuilt |
| Clean Windows setup | PASS: fresh offline Windows Sandbox NT10.0.26100/AMD64, no system Python/pip; explicit external editor/tools and official C++ prerequisite |
| Normal CLI and recovery | PASS: starter-only CPU generation; missing-source refusal/restored retry; cancellation and exact-options resume; Unicode relocation; corruption refusal |
| Real desktop workflow | PASS: actual starter dialog, two neutral source mappings, new output, Start/ready status and Open copy in Kdenlive without repair; no supplied analysis/approval records or owner questionnaire |
| Primary native editor | PASS: observed 26.08.2 rev d4e87e4 / MLT 7.43.0 / Qt 6.11.1 on host NT10.0.26300; play, three-member group move, save, undo, quit, reopen and full GUI render |
| Native timing/content checks | PASS: 300 mapped pictures, RGB MAE 0, existing switch at frame 138, four zero-lag audio anchors, eight protected probes at the documented master gain, MP4 audio marker absent |
| Complete real interviews | PASS: both final-candidate regenerations complete with exact S12 native timeline/effect semantics; six null offsets, scoped mute and previous native/full-render evidence retained |
| Source and evidence preservation | PASS: 8 original files, 44 prior attempt-08 records and 243 earlier private artifacts retain their hashes; both native delivery projects unchanged |
| Final automated suite | PASS: 267 tests, zero skips/failures/errors, bundled Python on clean Sandbox; 736.036 seconds in unittest summary |
| Public-data review | PASS in reviewed scope: all 5,239 runnable ZIP entries and 334 source ZIP entries inspected; source ZIP equals the exact Git archive; private paths/names/credential patterns absent |
| Owner timing/usefulness sign-off | **Retired by owner, not passed**; unknown seconds, subjective quality/usefulness and 90%/70% targets remain null |
| Git/CI checkpoint | Verify live after the documentation commit/push; no Actions workflow is configured, and an empty check/status set is not green CI |
| Main integration, tag, stable assets/publication | NOT RUN: reserved for owner-commanded S15 |

The Microsoft C++ x64 v14 runtime is a separate official prerequisite. Its
tested installer is pinned and Microsoft-signed; it was installed only inside
Sandbox, with exit 0. The host's existing runtime was retained. The candidate
does not redistribute that installer, copied system DLLs, Kdenlive or FFmpeg.
The unchanged Python distribution includes its own upstream runtime files and
notices. No paid signing is required; the candidate archive itself is unsigned.

The measured package-clean environment does not create a new TESTED editor
registry row. The exact primary row remains NT10.0.26300/AMD64 and the observed
Kdenlive executable. Sandbox 26100 reports EXPERIMENTAL for that editor, as
expected. Other Windows versions, editor patches, broader DPI/accessibility,
download reputation/SmartScreen and arbitrary edited projects are not qualified.

In the small Sandbox viewport the primary desktop controls worked after
maximizing, while lower optional Keep/Restore controls were clipped. Use the
documented CLI/source-time restoration or native Kdenlive recovery where those
controls are inaccessible. Broader small-screen layouts remain unqualified.
This limitation does not change media preservation, editable output or the
tested CLI recovery. S15 must carry the limitation into release notes unless
it is repaired and validated.

No fresh full real-interview render was required by the cache-path repair.
S14's final regenerated timelines and every native effect match S12, whose
delivery projects and full-render hashes remain unchanged. Fresh native
open/edit/save/reopen/render evidence was obtained on the final candidate's
synthetic ordinary output. No new detector tuning, mute/cut authority,
subjective assessment or full transcript accuracy claim follows.

S15 must first verify this checkpoint live, inspect current review/protection
requirements, recheck the production/latest-stable editor scope and integrate
normally. If the release commit/tree differs, build final assets from that
actual commit and rerun affected checks. Verify the intended unused tag,
publish matching source/package/checksums/notices/provenance and verify remote
tag/assets. Do not replace tags, force-push, bypass required review or treat
this local candidate as an already published release.
