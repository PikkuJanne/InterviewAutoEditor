# S12 measurement and acceptance procedure

**Current production policy:** the explicit schema-2 original-timing path is
implemented. It preserves null offsets, every source ending and marked empty
picture coverage. See [the policy](S12_ORIGINAL_TIMING.md) and
[current production evidence](../fixtures/S12_PRODUCTION_COVERAGE.md). Historical
prerequisite/proposal paragraphs below describe the earlier gate; they are not a
current claim that production export is unavailable. Original schema-1 requests,
registration, rejected review and failed runs remain intact.

**S12 is BLOCKED at full-interview acceptance.** The available engineering
checks do not complete G01-G09 on real interviews. Compatibility remains
EXPERIMENTAL for Kdenlive 26.08.2 rev. d4e87e4. See the
[current production audit](../fixtures/S12_PRODUCTION_COVERAGE.md) for executed
measurements and the [handover](../handovers/S12_ATTEMPT_07.md) for the checkpoint
and continuation. The [previous gate audit](../fixtures/S12_GATE_AUDIT.md) and
earlier handover retain the historical refusals and reviews.

## Corpus and review requirements

The recorded local corpus now contains a complete band interview with four
participant audio files and a distinct complete two-person interview with two
audio files. The new folder was supplied on 30 October 2026. The owner corrected
the earlier raw-file description: supplied audio
files have received the same volume leveling treatment intended for actual
projects. Treat them as already leveled inputs; do not level, normalize or
denoise them again. This confirms the intended processing provenance, while
waveform alignment, equal tails, annotation accuracy and edited-output acceptance
still need their own evidence. Do not ask for the already supplied two-person
folder again. Both inputs have private source inventories and complete read-only
Application analysis runs. The new input has an actual Kdenlive-created starter
and separate native round-trip copy. Processing-history clarification for the new
WAVs is separate from baseline/tail approval; record the actual reply status.

Required before acceptance:

1. The available complete two-person recording has original MP4, intended audio,
   explicit mapping and a supported unedited native starter. Source-clock/tail
   acceptance and edited-output validation remain pending.
2. The available complete band recording needs an actually supported reviewed
   source-clock/tail contract before edited-output validation.
3. Independently labelled held-out excerpts, preferably from a different
   recording, registered before tuning. The new two-person recording is registered
   as held-out before inference, with frozen code/model/settings evidence. It has
   now undergone full engineering inference without tuning; human-labelled
   acceptance remains unrun. Different positions in the already
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

Product pace/naturalness acceptance needs a valid source/output comparison.
The owner separately requested one source-sync review: the original Zoom reference
and supplied track at unchanged timing. That diagnostic file is now prepared; it
does not authorize product export, source alignment, cuts or idle attenuation.
The owner does not need to author JSON or label a complete interview personally.
Prepare a short review after input requirements are satisfied. Record actual
manual-baseline and assisted correction times on comparable tasks, including
review and approval-entry time; never substitute generated-tone processing time.

## Explicit origin and tail review

An ignored S12 draft review record retains the original fingerprints, measured
sample counts, exact ends, unverified statuses and null offsets. It is a pending
evidence checklist, **not** an Analysis record, accepted contract or certificate.
Neither this record nor the owner's volume leveling provenance statement is loaded into
Application as approval.

For each audio file, obtain evidence tied to the actual source bytes: export
provenance about the recording start and absence/presence of trims, shifts and
speed changes; reviewed start/middle/end alignment observations with their
precision; reviewer, date and evidence reference. Correlation diagnostics remain
diagnostics. Preserve their ambiguous outcomes. Only a genuinely reviewed
zero-origin record may declare verified zero; unknown offsets stay null.

The band video ends at 51092/25 seconds. Three audio sources end 4/375 second
earlier and one ends 4/375 second later. Exact sample counts are authoritative.
Approving an origin cannot fix unequal ends. The v1 `exact_coverage` contract
requires every measured source end to equal the shared domain, including identity
output. A reviewer cannot make that true by changing a duration field.

Resolution needs either a different genuinely exact-coverage input set with
documented provenance or an explicitly reviewed, versioned unequal-tail policy
with tests and adapter/native-render evidence for how **every original sample**
and the complete video are represented. Such a policy must retain the current
v1 refusals and give explicit source, coverage and recovery semantics. The offline v2 coverage preview and scoped synthetic native EOF proof are now
available; there is still no production planning/export policy extension. Do not trim, pad, shift,
stretch, replace media, hide tail loss or certify a draft to get past the gate.

The new two-person video ends at 47004/25 seconds, with one WAV ending 4/375
second earlier and one 4/375 second later. Fixed-anchor diagnostics additionally
find a 32.5 ms lag on ten reliable anchors for one source; only two anchors are
reliable for the other. These are reference-mix diagnostics, not applied offsets
or zero-origin certificates. The
[source-clock/end-coverage proposal](S12_SOURCE_COVERAGE_PROPOSAL.md) gives exact
potential shared endpoints and explicitly marked empty EOF coverage. It is
accepted as an empty-ending preference, with exact offline previews and synthetic
representation proof. Baseline review and production integration remain pending;
v1 does not accept it.

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

Attempt 02 separately runs actual two-hour generated-media analysis and identity
export with two silent mono sources and 64x36 video. Both models decode all
115200000 samples per source, and the final export retains all 180000 frames.
This complements the eight-source/599-cut metadata cases; it does not establish
two-hour dialogue, high-resolution throughput or long native/render acceptance.
The initial missing-opt-in export refusal and failed staging remain intact.
Recovery uses explicit opt-in in a new run with saved analysis. Cold-run resource
values lost before the harness failure remain unknown. See the current report
for measured export resources and limitations.

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

## Attempt 03 offline coverage boundary

The owner confirms leveling-only timing provenance for the new recording and
accepts the marked empty ending. [s12_coverage.py](../../tools/s12_coverage.py)
records strict v2 coverage-only reviews/previews, with actual private bindings.
They preserve the original v1 Analysis and cannot authorize origin, cuts or gain
changes. Do not load them as Application/desktop EditPlans. Existing v1 exact
coverage and origin refusals stay intact. Production coverage integration still
needs separate implementation/testing after baseline evidence is reviewed.

The new native synthetic N2/192 kHz mono case proves a marked blank picture
frame and preservation of partial EOF audio under a fixed channel-conversion
reference. Raw mono unity and pixel identity are explicitly false, and the
extra native extent frame is separate from rendered duration. This is not real
stereo, fractional-FPS GUI, productive editing or held-out acceptance. It does
not change the frozen core/inference configuration or existing job identities.
See the current report for exact evidence, failed assumptions and remaining gates.

## Requested source-sync review (attempt 04)

One private 62.12-second A/B video is prepared, with six model-assisted early/
mid/late pairs. Exact selection/cues/source bindings and media remain local.
At the attempt-04 checkpoint the app-panel request returned queued, with playback
and feedback unconfirmed. Attempt 05 below records actual owner feedback. Bind replies to the existing source-bound selection
and its real precision. Do not infer a full-recording certificate, verified zero,
independent content/gap/idle labels or productive utility from bounded sync review.
The original 32.5 ms/insufficient-anchor diagnostics remain intact. Do not prepare
a second comparison or add a connection. See the current review report for QA.

## Attempt 05 review rejection and contradictory evidence

Actual owner feedback reports five numbered pairs work and B2 unintelligible.
Treat B2 as rejected/unscorable for timing, preserve both raw replies privately,
and do not turn five qualitative positives into a full-recording certificate.
Native PCM and continuous-versus-guarded resampling reproduce B2 exactly; AAC
matches closely. No gross conversion corruption is detected, but actual source
intelligibility and perceived cause remain unestablished. Preserve the failed
model-selected sample rather than replacing it to improve a measured outcome.

Additional diagnostics at all six previously selected review windows retain an
early -10 ms versus later +32.5 ms inconsistency for source 1 and three +32.5 ms
offsets for source 2. Preserve earlier thirteen-anchor records; no drift, zero,
cause or origin certificate follows. A reliable correlation can coexist with
unintelligible audio. Pending exact-analysis-bound audible preservation of B2
is separate from approvals and grants no export authority. No second review
file, fitting, offset repair, deletion or idle gain approval is introduced.


## Attempt 06 binding and preservation audit

The [current gate audit](../fixtures/S12_GATE_AUDIT.md) separates new engineering
checks from G01–G09 real acceptance. Eight original media files and all audited
pre-existing S12/used-cache files match before/after. Frozen core/model inventory,
both complete analyses, six original unverified/null audio origins, feedback,
fidelity, contrary diagnostics, immutable jobs and failed runs remain unchanged.
Thirty-three focused regressions pass; they do not supply missing independent
labels, reviewed source baseline or real-output acceptance.

Pending request codec/digest/window checks pass; executable planning still refuses
the original origins for both presets. Metadata-only changed-analysis and other-
recording bindings refuse. Fifteen saved job input records reference no pending
request. It stays unapplied/unrebound, with zero gap/idle approvals. No implicit
certification follows from a matching digest, faithful PCM or five qualitative
positives. Different analysis/refined cleanup requires explicit matching reviewed
bindings. No second comparison, repair, broad replay request or connection.

Production EOF integration still needs explicit implementation/tests and actual
native evidence after actual baseline review. The known stream-0-only decoder
and 8192-frame picture budget remain; the held-out MP4's video stream 1 is not
silently substituted. All full/held-out acoustic/sync/editability/effort/owner
utility gates stay unrun; repeated audits cannot replace them. Resume S12 only.
