# Resume S12 — baseline review and production coverage integration

**S12 BLOCKED; no S13.** Both complete interviews are available. The owner has
answered the timing-provenance and marked-empty-ending questions. Preserve those
answers without treating them as alignment, gap or idle approvals.

Branch `codex/kdenlive26-overhaul`; implementation `645f5c784b9ce9cb903590919873b7fe969f4b73`.
Starting checkpoint `9dcc65ef5804dc05b67489c888844c930a62bdc1`.
Resolve this checkpoint from the handover's Git history and verify live equality.

- [State](project/STATE.json) and [complete handover](handovers/S12.md).
- [Current report](fixtures/S12_ATTEMPT_03.md) and [measurements](fixtures/S12_ATTEMPT_03.json).
- [Source coverage status](project/S12_SOURCE_COVERAGE_PROPOSAL.md), [procedure](project/S12_VALIDATION.md) and [brief](project/steps/S12.md).

Exact offline v2 coverage previews bind the unchanged real analyses and retain all
source sample counts/null offsets. Proposed common ends are 51093 and 47005 frames
at 25 FPS. These are coverage-only records; Application/desktop do not accept them.
Four Tight/Gentle real-input origin refusals remain. No real export was created.

Actual generated N2/192 kHz mono EOF experiment passes open/play/group-move/undo/
save/close/reopen/render in Kdenlive 26.08.2 rev. d4e87e4. All 300 picture anchors
retain their frame timing; frame 301 is black. PCM has 2311680 samples/channel and
matches a fixed mono-to-stereo reference within half an LSB, including the final
tail sample, then digital zero. Raw unity/pixel identity are false and reported.
Reopen adds one native extent frame; clip bounds remain unchanged. This is a
hand-constructed representation experiment, not real stereo/product acceptance.

Fresh full suite: **237 tests, zero skips, 254.017 s**. Six focused tests
pass. Core/adapter/desktop/model/settings/locks/licences/prior fixtures and frozen
held-out configuration are unchanged. Nine old manifests/four complete current
runs/one failed stress run and nine genuine-artifact hashes validate read-only.
Earlier complete-real-analysis, held-out exposure and actual low-resolution
two-hour stress evidence remain in [attempt 02](fixtures/S12_ATTEMPT_02.md).

Next: explicit reviewed source-clock baseline evidence, separately validated
production coverage integration and independent labels/approvals. The new 32.5 ms
reference-mix lag and insufficient-anchor result remain unresolved; band origins
remain unverified. Never relabel them zero or edit source durations. Preserve all
protected content/exterior handles, original picture timing/shared maps, refined
cleanup bindings, source-time Keep/audible, headroom and immutable jobs/caches.

Full edited-output/held-out/noise/sync/editability/manual correction-effort and
focused owner utility acceptance remain NOT RUN. No measured 90%/70% claim. At
most one local comparison audio file and no new connection. A concise optional
sync-review preference was asked; no answer or approval is inferred.

```powershell
git log -1 --format=%H -- docs/handovers/S12.md
python tools/verify_checkpoint.py --repo .
```

Final chat records actual pushed SHA/live/upstream equality and clean worktree.
Starting exact-SHA CI has zero workflows/runs/checks/statuses: not configured,
not green. Failed sync or configured failing CI requires resuming S12.

Ready-to-paste continuation prompt:

> Resume S12 only in InterviewAutoEditor on codex/kdenlive26-overhaul. Read AGENTS.md, docs/project/STATE.json, docs/NEXT_STEP.md, complete docs/handovers/S12.md including attempt 03, execution/GitHub protocols, S03-S12 guides and S12 brief. Implementation is 645f5c784b9ce9cb903590919873b7fe969f4b73; resolve the containing checkpoint and verify live/local/upstream equality, clean worktree and exact-SHA CI first. Both complete private inputs are available. Owner confirms new WAV leveling retained original timing and accepts preserving all audio with a marked empty ending; these answers do not approve alignment, gaps or idle gains. Read S12_ATTEMPT_03.md/JSON, source-coverage status and private source-bound owner reviews. The strict offline v2 CoveragePreview and synthetic native EOF experiment are not production export authority. Current v1 refusals remain. Resolve the 32.5 ms/insufficient-anchor and band baseline evidence explicitly, then implement/test a preserving production coverage contract without implicit migration, certification, source changes or approval rebinding. Keep frozen held-out configuration/exposure separate from tuning, all protected content/full handles/shared microphones/maps, original picture timing, exact refined cleanup bindings and recoverable Application/desktop jobs. Complete independent labels/approvals, valid full two-person/band editable outputs and actual retention/approval/noise/sync/editability/performance/correction-effort/owner acceptance; never claim unrun results. Preserve one-file/no-new-connection preferences. Run applicable gates, update state/NEXT_STEP/S12 handover, commit/push/verify, verbose handover and STOP. No S13.

Paused with S12 blocked. The next thread must resume S12.
