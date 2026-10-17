# Canonical edit plan and invariants

The plan is versioned application data, not Kdenlive XML. Establish schema v1 in S03/S06 and validate every exported plan. Fields below are required concepts; choose an explicit machine schema and documented migrations during implementation.

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
