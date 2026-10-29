# S06 shared pause planning

S06 implements deterministic local pause planning in
[`planner.py`](../../interview_auto_editor/planner.py). It reads a strict v1
`Analysis`, creates one v1 `EditPlan`, and wraps that plan with reproducibility
and decision records. It performs no inference, media writes, gain changes or
Kdenlive export. Product compatibility remains **EXPERIMENTAL**, with actual
application evidence limited to the S01/S02 Kdenlive **26.08.2 rev. d4e87e4**
round trips. S07 will connect useful speaker turns/groups to export.

## Authorization to shorten a gap

Every protected event on every participant source contributes to the global
union: speech, reactions, uncertainty, overlap and conservatively also turn
records. Protection is expanded to at least 120 ms before raw activity and
200 ms after it, clipped only to that source's actual extent. Longer existing
protection survives. Shared microphones remain one inseparable source group.

S04/S05 explicitly do **not** certify silence from absent events, low scores,
noise floor or correlation. A gap therefore needs an explicit `GapApproval`
covering **all tracks**. It must have construction-label or human-review
provenance and exact source-time bounds. It is a disposable-silence label,
not a pacing command that can override speech. The entire request is bound to
the SHA256 of the strict serialized analysis, including source fingerprints,
events, reviews, versions and settings. Changing that analysis requires a new
request; changing the preset alone does not invalidate source-time overrides.
This conservative approval requirement is a recorded S06 decision, preserving
the earlier no-negative-model-as-silence contract. No silence certifier or new
listening workflow is introduced. An unattended useful-removal rate on real
interviews has **not** been established.

Only gaps between distinct components of the protected union are considered.
The outermost raw event times identify the adjacent activity. Both boundaries
must consist exclusively of speech with confidence at least 9/10, referring to
one source group with one participant label. Multiple simultaneous boundary
groups, reactions, uncertainty or shared microphones produce an uncertain rule
and preserve the gap. A `same` rule means the same recording-source identity;
it does not claim voice identification. Remaining overlap elsewhere in an
island is protected and cannot be removed or independently attenuated.

## Presets and exact boundaries

These defaults are pacing hypotheses pending later listening calibration:

| Preset | Different-group gap strictly longer than | Nominal residual | Same-group gap strictly longer than | Nominal residual |
|---|---:|---:|---:|---:|
| Tight | 4/5 s | 1/4 s | 3/2 s | 1/2 s |
| Gentle | 6/5 s | 1/2 s | 5/2 s | 9/10 s |

The residual is at least the sum of the actual left tail and right onset
protection. A nominal quarter second therefore retains at least 8/25 s with
the default guards. Extra residual beyond that protection is divided equally
between the two sides. Every proposed removal is intersected with an approval,
then `keep` and `audible` overrides are subtracted globally. Both override types
retain their entire source-time interval; S06 never changes gain.

Removal starts round up and ends round down to absolute project frames. An
empty/subframe candidate is retained. Narrow approvals/overrides can leave more
residual time; they can never enlarge a removal. Multiple approved pieces have
separate reasons. All source ranges are half-open. Complete time before the
first protected island and after the last one survives. With no activity,
continuous protection, ambiguous boundaries or no approvals, the map is the
identity. Unknown/no-activity input never authorizes trimming the recording.

One `SharedTimeMap` governs the video and every audio source. Output positions
derive from integer retained frame counts and rational FPS. The planner does
not accumulate rounded seconds, shift video, use picture candidates, split
words or remove fillers. Output edit-unit boundaries currently mark only
shared removal seams; meaningful turns and group serialization belong to S07.

## Versioned wire records

The existing `Analysis`/`EditPlan` schema remains **v1**, unchanged. The generic
strict codec in `contracts.py` also serializes these new independent v1 records:

- `PlannerRequest`: `schema_version`, `analysis_sha256`, `preset`, ordered
  disjoint/non-touching `approvals`, and source-bound `overrides`.
- `GapApproval`: `approval_id`, rational `start`/`end`, `basis`
  (`construction_label` or `human_review`), and nonempty `evidence`. These are
  global source-clock intervals, never per-microphone permission to delete time.
- `PlanningResult`: `schema_version`, fixed algorithm
  `s06-shared-pauses-1`, the complete request, the complete canonical `plan`,
  and `decisions` for every gap between protected islands.
- `GapDecision`: raw `source_start`/`source_end`, `rule`, `outcome`, `reason`,
  rational `residual_target`, quantized `removed` ranges and matching approval
  IDs. Kept gaps have empty removal/provenance arrays. No-activity and one-island
  cases have no interior-gap decisions.

Every field is required. Rational objects are reduced numerator/denominator
pairs, with no floats. Missing/unknown fields, unknown versions, duplicate JSON
keys and stale analysis bindings fail closed. There are no migrations; a future
change needs an explicit migration or an unsupported-version error. Algorithm
identity fixes the preset values and protection/rule semantics listed above.

The result validator requires every map deletion to have a corresponding
decision and approval, with no deletion outside either interval. The canonical
`EditPlan` additionally enforces protected-content retention, override retention,
shared duration and source identity/origin/tail invariants. This JSON is local
application data, not a cryptographically signed human approval certificate.

Original analysis headers, events, origins, exact sample counts, shared labels,
reviews, shots and source fingerprints are preserved byte-semantically.
Replanning calls no model and needs no runtime beyond the standard library.
Sources with unverified/nonzero origins or unequal exact tails are refused even
for an identity plan. The native sequence's extra frame is not a media frame.
No repair, padding, truncation, stretching or inferred offset is introduced.

## Use and recovery

The callable API is the primary S06 interface. Supply genuinely approved global
source-time gaps; do not generate approvals from missing VAD/reaction events.

```python
from interview_auto_editor.contracts import Analysis, dumps, loads
from interview_auto_editor.planner import (
    PlannerRequest, PlanningResult, analysis_digest, explain, plan_pauses,
)

# analysis is an existing strict Analysis with certified origins/exact coverage.
request = PlannerRequest(1, analysis_digest(analysis), 'tight', (), ())
result = plan_pauses(analysis, request)  # no approvals: keep all time
serialized = dumps(result)
restored = loads(PlanningResult, serialized)
report = explain(restored)
```

`explain()` lists exact rational source/output seconds, source/output frame
ranges, reasons, approval IDs, residual targets and output seams. Reviews retain
their original reasons and source locations; mapped output time is null if
the location was removed. The retained map supplies both coordinates for any
retained point. Integer frames plus exact rational seconds avoid ambiguous
rounded decimal clocks, including fractional FPS.

The preliminary CLI writes one new `PlanningResult` file exclusively:

```powershell
python tools/s06_plan.py --analysis '<private analysis.json>' --request '<private request.json>' --output '<new private planning-result.json>'
```

Exit 0 means a plan with no review records; exit 2 means a complete plan with
mapped reviews; exit 1 means refusal/failure; Ctrl-C exits 130. It does not
overwrite an existing result or either input. Failure before publication leaves
no result; the shared atomic writer handles publication. Error text omits
private paths/content. Requests, plans and `explain()` reports contain source
fingerprints/labels/timecodes and must stay local for real material. S10 will
define the integrated CLI and run-folder recovery contract.

To restore removed time, add a source-time `keep` override on any source covering
the interval and replan with the same analysis. It restores that time on all
tracks. Remove approvals or Keep the full recording to recover the identity
map. Original media references and the unchanged analysis remain in the plan;
S06 has no transformed media/project to undo. A changed analysis must be reviewed
and rebound explicitly rather than silently applying stale silence approvals.

## Evidence and limits

Run the independent exact/synthetic regressions:

```powershell
python -B -m unittest discover -s tools -p test_s06_planner.py -v
```

See [S06_PLANNER_EVIDENCE.json](../fixtures/S06_PLANNER_EVIDENCE.json) and the
[S06 handover](../handovers/S06.md) for measured commands/results. Applicable
G03/G04/G05 evidence includes 500 shared cuts at each of integer/fractional FPS,
five sample grids, off-frame labels, all event kinds, full handles, no activity,
Keep restoration and exact labelled integer-PCM retention. Construction-labelled
regions are not human words, acoustic accuracy scores or Kdenlive output.

The retained S05 human overlap envelope is also checked with the production
planner in an explicitly derived coordinate harness; its synthetic verified
origins never certify the original files. Original real analysis still fails
the origin gate. Held-out audio remains unopened. No useful real removal rate,
pace preference, full-interview/held-out G04/G05, edited Kdenlive output or gain
acceptance is claimed. No new listening is requested; earlier one-audio-file
maximum and no-new-connection preferences remain in force.
