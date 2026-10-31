# Canonical edit plan and invariants

S12 adds the explicit `original_timing_with_gaps_v2` policy through schema-2
planner requests/results. It preserves unknown offsets and each source's full
end, with explicit empty coverage and one shared removal map. Schema-1 behavior
and refusals remain. See [the current policy](S12_ORIGINAL_TIMING.md) for exact
source/EOF/profile/headroom semantics; the v1 rules below remain historical and
executable, rather than being silently relaxed.

The plan is versioned application data, not Kdenlive XML. Establish schema v1 in S03/S06 and validate every exported plan. Fields below are required concepts; choose an explicit machine schema and documented migrations during implementation.

S03 establishes the executable typed v1 records and strict JSON codec in
[`contracts.py`](../../interview_auto_editor/contracts.py). See
[S03_CONTRACTS.md](S03_CONTRACTS.md) for fields, exact timing, migration rules,
origin review and the deliberately conservative `exact_coverage` tail policy.
S06 implements conservative pause planning against these unchanged v1 contracts.
Its separate v1 request/result records bind explicit removable-gap approvals to
the complete analysis and explain every shared deletion. See
[S06_PLANNER.md](S06_PLANNER.md) for fields, preset semantics, source-time
overrides, exact mapping and migration policy. This does not connect the S02
exporter to automatic plans yet. S07's separate integration now derives v1
`edit_units` from a reproducible approved S06 result and exports synchronized
groups. It preserves the analysis/request/map and adds no deletion authority.
The changed export passes its scoped synthetic actual-application gate; see
[S07 export](S07_EXPORT.md).

S08 preserves the canonical v1 gain-point refusal unchanged. Its separate strict
v1 CleanupRequest/CleanupResult authorizes only independently labelled idle
intervals, is bound to a reproducible complete S06 result, and is independently
validated before native export. It never changes the shared plan or weakens
event/override protection. See [S08 cleanup](S08_CLEANUP.md).

S09 keeps picture observations in separate strict v1 records bound to unchanged
audio analysis/video/implementation hashes. Its seam refinement can only narrow
existing approved S06 deletions, restoring time globally, then exactly reproduces
S06 and requires S08 cleanup rebinding. Source/output picture reviews remain
separate from speech protection and silence authority. See
[S09 picture rules](S09_PICTURE.md). No canonical schema migration is introduced.

## Required records
- Schema version, run ID, source project/media fingerprints, tool/model versions, settings and adapter target.
- Project frame rate as numerator/denominator, audio sample rates, source origins and explicitly verified offsets.
- Source intervals use half-open [start, end) semantics in an exact time representation. Keep integer samples per source and rational time/frame conversion; never independently accumulate rounded seconds.
- Per-track events: type, source bounds, evidence/confidence, protected bounds, shared-channel labels and uncertainty reason.
- Retained global intervals: exact source bounds, quantized project boundaries, output start/end and reason for each removed gap.
- Per-track gain envelopes, meaningful turns and overlap groups, aligned edit units, shot-change candidates and review flags.
- Overrides keyed to source identity/time, not just changing output timecodes. Review entries carry both source and output locations.

## Hard invariants
1. Source intervals remain ordered and non-overlapping; there is no reordering or invented source content.
2. One retained-interval map controls all tracks. A participant mute never removes time independently.
3. No deletion intersects protected speech, reaction or uncertainty. Outward protection rounding takes priority over a tighter gap target.
4. Output duration equals the sum of retained mapped durations, including untouched leading/trailing handles. All tracks share the same sequence end, with explicit silence where appropriate.
5. Frame conversion is performed consistently; absolute output positions are derived from the map, not incremental float addition. Convert half-open bounds to MLT inclusive ends only at the adapter boundary.
6. No negative/zero-length clip, invalid gain range, unresolved reference, accidental duplicate MP4 audio or cumulative A/V drift is exported.
7. A recorded picture switch cannot authorize cutting protected audio or independently sliding video.
8. Native/derived gating and restoring an interval are reproducible from source + plan + overrides. Originals remain untouched.

Examples/tests must include a fractional FPS, mixed sample rates, hundreds of cuts, an off-frame speech onset, a laugh inside apparent silence and overlap spanning an edit-unit boundary. Exact mathematical tests precede subjective quality calibration.
