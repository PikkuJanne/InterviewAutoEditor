# S12 measurement and acceptance procedure

**S12 is BLOCKED at full-interview acceptance.** The available engineering
checks do not complete G01-G09 on real interviews. Compatibility remains
EXPERIMENTAL for Kdenlive 26.08.2 rev. d4e87e4. See the
[acceptance report](../fixtures/S12_ACCEPTANCE.md) for executed measurements and
the [handover](../handovers/S12.md) for the checkpoint and continuation.

## Corpus and review requirements

The recorded local corpus contains one complete interview with four participant
audio files. The owner confirmed that a complete two-person interview is
unavailable at present and described the supplied files as raw files from Zoom.
Record that provenance statement separately from earlier cleaned-input
assumptions. It does not establish a cleaning history, zero waveform offset,
equal tails, annotation accuracy or owner acceptance of edited output. Do not
apply denoising or normalization to resolve the ambiguity.

Required before acceptance:

1. A complete two-person recording: original MP4, the intended participant audio
   files and explicit source mapping in a supported unedited starter.
2. The complete band recording under an actually supported origin/tail contract.
3. Independently labelled held-out excerpts, preferably from a different
   recording, registered before tuning. Different positions in the already
   analyzed development recording are not an independent interview. Existing
   end excerpts remain reserved from label-based tuning; historical full-source
   inference does not make them a fresh test set.
4. Independent protected-content, excessive-handover, global removable-gap and
   source-local idle labels. Missing model detections cannot supply these labels.
   Record the real precision of human timing rather than declaring sample
   accuracy after converting approximate times to rational coordinates.
5. A focused owner A/B check on accepted exported material, at most **one audio
   file**, with cue times. Preserve the no-new-connection preference. The bounded
   S08 listening pass remains valid for its existing TTS comparison only.

No new listening file is prepared until a valid source/output comparison exists.
The owner does not need to author JSON or label a complete interview personally.
Prepare a short review after input requirements are satisfied. Record actual
manual-baseline and assisted correction times on comparable tasks, including
review and approval-entry time; never substitute generated-tone processing time.

## Explicit origin and tail review

An ignored S12 draft review record retains the original fingerprints, measured
sample counts, exact ends, unverified statuses and null offsets. It is a pending
evidence checklist, **not** an Analysis record, accepted contract or certificate.
Neither this record nor the owner's Zoom provenance statement is loaded into
Application as approval.

For each audio file, obtain evidence tied to the actual source bytes: export
provenance about the recording start and absence/presence of trims, shifts and
speed changes; reviewed start/middle/end alignment observations with their
precision; reviewer, date and evidence reference. Correlation diagnostics remain
diagnostics. Preserve their ambiguous outcomes. Only a genuinely reviewed
zero-origin record may declare verified zero; unknown offsets stay null.

The current video ends at 51092/25 seconds. Three audio sources end 4/375 second
earlier and one ends 4/375 second later. Exact sample counts are authoritative.
Approving an origin cannot fix unequal ends. The v1 `exact_coverage` contract
requires every measured source end to equal the shared domain, including identity
output. A reviewer cannot make that true by changing a duration field.

Resolution needs either a different genuinely exact-coverage input set with
documented provenance or an explicitly reviewed, versioned unequal-tail policy
with tests and adapter/native-render evidence for how **every original sample**
and the complete video are represented. Such a policy must retain the current
v1 refusals and give explicit source, coverage and recovery semantics. There is
no implemented policy extension in this checkpoint. Do not trim, pad, shift,
stretch, replace media, hide tail loss or certify a draft to get past the gate.

Reviewed analysis is supplied explicitly through the existing Application or
desktop path. Global gap approvals remain separately bound to that complete
analysis. Idle approvals remain separately bound to the exact picture-refined
planning result. Changes require explicit review/rebinding, or removal of idle
approvals for unity gain. Keep/audible overrides remain on original source time
and apply to all tracks. Existing immutable runs/jobs and failed staging remain
recoverable; do not edit their hashes or repair them in place.

## Independent label measurements

[`tools/s12_evaluate.py`](../../tools/s12_evaluate.py) evaluates reproducible S06
results and optional validated S08 cleanup against separate labels. It changes
no media, plans, origins, approvals or Application/desktop jobs. It does not
decode audio or establish actual native editability, rendered sync, noise
reduction, click quality, correction effort or listening acceptance.

Its strict v1 `EvaluationCorpus` registers recording IDs, development/held-out
partitions, all source fingerprints and a frozen configuration digest. Duplicate
recording IDs and source fingerprints shared between partitions refuse. The
reviewer must ensure different excerpts from one recording keep the same parent
recording identity: byte hashes alone cannot detect related excerpts. Both
partitions must be registered before this acceptance evaluator can run.

`configuration_digest(result)` binds the selected preset, declared header
settings/model versions/tool version and every core Python module's bytes.
It does not verify installed model/runtime bytes; existing analysis/run checks
must do that. Freeze the digest after development calibration and **before**
held-out evaluation. A changed configuration refuses. Any later calibration
requires a new recorded freeze and genuinely fresh acceptance material rather
than relabelling the observed held-out data as unseen.

`EvaluationLabels` binds recording ID, split, complete analysis digest and
independent evidence. Label kinds are word, acknowledgement, laughter, overlap,
uncertainty, removable_gap, handover_gap and idle_noise. Every label has an ID,
source, rational half-open start/end, basis and evidence. Global gap labels use
source `all`; content/idle labels use the actual participant source ID. Excessive
handover labels are independently judged candidates, not gaps selected by the
planner. Held-out interview labels require `human_review` basis; construction
labels belong to engineering/development cases.

Measurements include complete retained/audible label counts by content kind,
summed labelled/retained source seconds, deletion duration inside independent
removable labels, the number of excessive-handover labels actually shortened,
and retained labelled idle source seconds intersecting planned attenuation.
Content source seconds are summed annotation durations, so overlapping content
labels can count the same time more than once. Idle intervals are unioned per
source to avoid double counting. Overlap labels check unity on all microphones.
Planned attenuation includes ramps; it is **not measured noise reduction**.
Empty denominators remain null; no labels or no deletions do not mean 100%.
All reports retain `acceptance: NOT_ESTABLISHED` because other gates are external.

```powershell
.venv/Scripts/python.exe -B tools/s12_evaluate.py --result '<private refined PlanningResult.json>' --labels '<private independent labels.json>' --corpus '<private frozen corpus.json>' --cleanup '<optional matching cleanup-result.json>' --output '<new private measurements.json>'
```

Omit `--cleanup` for unity gain. Exit 2 means measurements requiring review,
1 means refusal. Output is exclusive/atomic; no overwrite. Unknown fields,
versions, duplicate JSON keys, floats, stale labels, changed configuration,
wrong partitions and tampered cleanup refuse. Real labels/corpus/measurements
contain identities or timecodes and remain private. A well-formed JSON evidence
string is not an independent verification of the supplied annotation.

## Long timing fixture

[`tools/s12_timing.py`](../../tools/s12_timing.py) constructs a source-clock
contract representing eight generated sources at five sample rates, 600 activity
intervals and 599 independently constructed global gaps. It plans, round-trips
the strict result, builds turns, checks every protected interval and both exterior
handles, duration conservation, 9600 output endpoint/sample-grid combinations,
the exact final map endpoint and separate unverified-origin/unequal-tail refusals.

```powershell
.venv/Scripts/python.exe -B tools/s12_timing.py --fps 25 --output '<new timing-25.json>'
.venv/Scripts/python.exe -B tools/s12_timing.py --fps 30000/1001 --output '<new timing-fractional.json>'
```

The 25 FPS domain is exactly 7200 seconds. The fractional domain rounds **up** to
a frame/sample endpoint common to all source rates: 7207.2 seconds, not a falsely
exact two hours. Source IDs/fingerprints/origins are constructed; they never
certify private media. Windows peak working set is the measured whole Python
process, including fixture construction; planning time also includes construction.
Total time includes strict serialization/reload, turn construction, invariants
and refusal checks. Run each process separately for these resource measurements.
These are metadata/timing stress results, not full two-hour decode/inference,
picture-budget, peak-audit, Kdenlive GUI or media-size acceptance.

## Applicable regressions and gate boundary

Use the existing prepared environment, local pinned CPU models and development
fixture; no dependency/model downloads are needed. Set `IAE_FFMPEG`,
`IAE_FFPROBE`, `IAE_S04_MODEL`, `IAE_S05_MODEL` and `IAE_S04_DEVELOPMENT` to the
existing assets, then run:

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s tools -p test_s12_quality.py -v
.venv/Scripts/python.exe -B -m unittest discover -s tools -p 'test_*.py' -v
```

The scenario matrix in the acceptance report distinguishes automated checks,
remeasurement of historical actual GUI artifacts and new native operations.
No exporter/core algorithm changes in this checkpoint require a new exporter
regression. Actual full-interview open/play/group-edit/save/reopen/render and
owner acceptance remain required when valid full-interview output exists.
The 90% gap and 70% effort targets are unmeasured on acceptance interviews.
S12 remains selected; S13-S15 remain pending.
