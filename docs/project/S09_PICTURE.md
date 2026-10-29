# S09 recorded-picture analysis and shared seams

Compatibility remains **EXPERIMENTAL**. Actual application evidence targets only
**Kdenlive 26.08.2 rev. d4e87e4 / MLT 7.43.0 / Qt 6.11.1** on Windows AMD64.
The editable project remains the primary output. Picture changes never identify
a person, certify silence or create an independent video clock.

## Observations and layout

[`picture.py`](../../interview_auto_editor/picture.py) adds separate strict v1
PictureRequest, PictureAnalysis, Boundary, PictureWindow, PictureMarker and
PictureRefinement records. Canonical Analysis/EditPlan, S06 and S08 schemas and
their invariants are unchanged. Unknown fields/versions, floats, noncanonical
rationals, stale analysis/video/implementation bindings and incomplete coverage
fail closed. No implicit migration exists.

The request binds the complete unchanged audio Analysis digest, with an explicit
whole-input layout label and construction/human-review provenance. Supported
labels are speaker_view, gallery, pinned, camera_off and uncertain. Use uncertain
for mixed or unreviewed layouts. This is recorded review evidence, not automatic
Zoom-layout recognition or a signed certificate. Facial recognition is absent;
even speaker_view does not certify who appears in a picture.

Substantial confident source-group speech runs follow S07's 600 ms duration/join
rules. Different successive recording groups propose inspection windows,
including overlap; they do not infer individual voices within shared microphones.
Windows cover the preceding gap plus a 500 ms left handle, and at least 1.5 s
either side of the new run. Short reactions/acknowledgements/uncertain/shared-mic
events retain review markers without picture-follow cuts.

The local decoder verifies the source fingerprint and full CFR timestamp audit,
then selects absolute video-stream-0 frame numbers in one FFmpeg pass **before**
96x54 area scaling to luma. No seeking, FPS substitution or source conversion.
Absent/nonzero video stream 0, VFR or timing mismatch refuses analysis. Current
bounded support is 1-120 FPS, at most 8192 window frames including overlaps and
120 s per probe/decode. Oversize/partial decode fails instead of silently reducing
coverage. Decode bytes and split images are bounded (about 81 MiB combined at
the maximum); metadata also has the strict codec's 8 MiB bound. Very large/full
interview budgets and stream-selection expansion remain later work.

Adjacent frames with mean luma change >=10/255 and at least 25% of pixels changing
by >=24 become probable-transition candidates. A speaker_view candidate receives
the engineering score 9/10 only with mean >=24/255, changed fraction >=55%, and
at least 500 ms of observed pictures on **each** side differing from their edge
reference by no more than 12 mean luma units. Others receive 1/2. Motion, fades,
lighting and short reactions can confuse this heuristic; these scores are not
calibrated semantic confidence. Layout fallbacks never become high-confidence
speaker assignments. All observations stay available for review.

Saved observations bind input hashes, request, implementation bytes, decoder hash
and decoder version. They can be reused for deterministic refinement/export
without another decode or audio inference. Changing the audio analysis requires
new reviewed bindings; changing picture implementation requires fresh observations.
There is no automatic cache search or model download in this step.

## Restore-only seam policy

`refine_picture_seams(base, picture)` first exactly reproduces S06 and validates
the independent observations. Only a different-group, explicitly approved S06
handover deletion is eligible. It cannot expand that deletion.

When one stable probable transition lies inside the deletion and the whole seam
has observed 500 ms picture handles, the new right edge is that **existing**
source frame. This restores the remaining silence on **every** track. An already
aligned stable right edge is unchanged. Static reviewed speaker_view pictures
also leave an eligible approved seam unchanged. Ambiguous/multiple/brief changes,
short edge fragments, incomplete edge coverage, gallery/pinned/camera-off and
uncertain layout restore the affected handover deletion completely. Existing
recorded brief shots may remain in restored original time; no new short shot is
constructed. Same-group/out-of-scope gaps retain S06's decisions.

The derived global approvals are intersections of original approved deletions
with these smaller deletions, retaining original basis/evidence and deterministic
sub-IDs. Replanning uses the unchanged production S06 policy. An independent
retained-range check forbids losing any previously retained time. Analysis,
protection, all source-time overrides, canonical gain refusal, source identities,
full exterior handles and real origin/exact-tail refusals survive unchanged.

**12.00 s speech / 12.45 s picture:** the opening speech and original .45 s
picture lag survive. Neither a protected onset nor any later video is advanced.
Reviews flag probable boundaries and uncertain/unavoidable delay without
asserting camera identity. There is no fake footage, freeze, face matching,
J/L retiming, per-track deletion, padding, source repair or normalization/denoising.

S08 cleanup must be rebuilt and rebound to the **refined** S06 result. Old cleanup
is refused. Export runs the existing S08 exact-span reproduction and conservative
headroom audit against the new shared map/S07 groups, retaining native unity
margins, protected events, overlap vetoes, shared-mic unity and restoration rules.
No new idle approval is created from a picture observation.

## API, commands and restoration

```python
from dataclasses import replace
from interview_auto_editor.picture import refine_picture_seams
from interview_auto_editor.cleanup import build_cleanup, planning_digest

refinement = refine_picture_seams(base_result, picture_analysis)
refined_result = refinement.result
# Reuse independently reviewed idle labels; rebind to the exact derived result.
cleanup = build_cleanup(refined_result, replace(old_cleanup.request,
    planning_sha256=planning_digest(refined_result)))
```

Preliminary commands write one new strict result exclusively/atomically. These
are S09 tools; S10's integrated recoverable pipeline has not been implemented.

```powershell
python tools/s09_picture.py analyze --analysis '<private analysis.json>' --request '<private picture-request.json>' --video '<source.mp4>' --ffmpeg '<local ffmpeg>' --ffprobe '<local ffprobe>' --output '<new picture-analysis.json>'
python tools/s09_picture.py refine --result '<base S06 result.json>' --picture '<picture-analysis.json>' --output '<new picture-refinement.json>'
python tools/s07_export.py --project '<starter.kdenlive>' --mapping '<private mapping.json>' --result '<base S06 result.json>' --picture '<picture-analysis.json>' --cleanup '<rebound S08 cleanup.json>' --output '<new picture-cleaned.kdenlive>' --ffprobe '<local ffprobe>' --experimental
```

`analyze` may run on uncertified sources because it is read-only; refinement and
export still refuse their original origins/tails. The refinement file contains
the derived S06 result in `result`; extract that typed result for S08's existing
cleanup command/API. Export accepts the **base** result plus picture observations
and recomputes the refinement itself. Without `--picture`, existing S07/S08
export behavior/bytes remain unchanged. Picture exports return review exit 2;
refusal/failure is 1 and Ctrl-C 130. Failed/cancelled decoding publishes no partial
record. Inputs/media are untouched; completed separate outputs remain reusable.

Markers include exact rational source and output locations, kind, confidence and
reason. Removed locations have null output time; the native guide is placed at
the following shared seam with that null preserved in its text. New guides merge
with S07 guides sharing a frame. Reports, requests, notes, hashes and timecodes
may identify real material and must stay local. No new connection is used.

Omit picture observations to recover the original S06 pacing. Add source-time
Keep/audible and replan/rebind both picture and cleanup requests as needed to
restore an interval globally. Remove global approvals for identity time; remove
idle approvals for unity gain. Full bin originals stay available. Never use an
edited output as a simple starter.

## Evidence and limits

[S09 evidence](../fixtures/S09_PICTURE_EVIDENCE.json),
[actual provenance](../../tests/fixtures/s09-picture-26.08.2/PROVENANCE.json) and
[render measurements](../../tests/fixtures/s09-picture-26.08.2/render-validation.json)
keep construction, actual GUI and exact timing evidence distinct.

The independent synthetic switch at source frame 138 lies in the all-track
silence label [4,7) seconds. S06 removes [105,172); S09 narrows it to [105,138),
restoring 34 frames. Output is 267 frames/10.68 s, with six N+1 groups and four
S08 gain spans. All 267 actual GUI-rendered pictures match their shared source
frames; exactly one visible switch occurs at output 105. Eight protected tone
probes stay within 0.1 dB, four audio onset anchors have zero measured lag, four
noise probes are over 30 dB down and peak is 0.476731. This does not establish
subjective word quality or accuracy on unseen Zoom layouts.

The exact 20-FPS 12.00/12.45 fixture is separately decoded and tested: speech
samples from 12-15 s survive and the .45 s original picture lag remains exact.
That 20-FPS file is a decoder/math test, **not** a Kdenlive GUI fixture. Fractional
FPS and variable-track tests are likewise automated evidence only.

Actual 26.08.2 opens, plays, moves all three members of the final group 25 frames,
undoes, saves, closes by opening another project, reopens and renders. Native
timing/groups/guides/gain semantics survive with zero sequence-extent delta.
Compatibility is still EXPERIMENTAL. Original real origins remain unverified/null,
tails unequal and planning/export refused. Retained bounded development overlap
and original files are rechecked; private picture tuning, held-out/full interview
acceptance, wider builds/layouts and broader GUI track/FPS matrix are NOT RUN.
No new listening file is requested; the one-file/no-new-connection preference
and existing S08 human listening scope remain intact.
