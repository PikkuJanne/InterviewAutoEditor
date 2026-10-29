# S08 reversible idle-microphone cleanup

Compatibility remains **EXPERIMENTAL**, targeting only the observed Kdenlive
**26.08.2 rev. d4e87e4**, MLT 7.43.0. This adds gain automation to the existing
S07 grouped export; the editable project remains the primary artifact.

## Approval and independent protection

`cleanup.py` defines separate strict v1 `IdleApproval`, `CleanupRequest`,
`GainSpan` and `CleanupResult` records. It intentionally preserves the original
v1 Analysis/EditPlan and its **protected-source attenuation refusal** unchanged.
No migration or reinterpretation of stored gain points occurs. S06 must still
reproduce exactly before S08 can proceed. The S08 request binds the complete S06
result digest, including the original analysis, global approvals, map and overrides.
Changing any of these requires explicit rebinding; a stale cleanup result refuses.

Each cleanup interval needs a source-bound, exact rational `IdleApproval` with
`construction_label` or `human_review` provenance and nonempty evidence. Missing
VAD, low floor, loudness ranking and cross-source correlation cannot create an
approval. This JSON records approval provenance; it is not a signed certificate
or an automatic verifier of human labels. Useful unattended real cleanup is
unproven. No additional model, dependency, network service or telemetry is added.

The fixed `s08-approved-idle-1` policy intersects approvals with retained shared
map segments and S07 edit groups, then subtracts protected intervals. Speech,
reactions, uncertainty and turns preserve at least 120 ms onset/200 ms tail
protection, or their longer existing protection. Explicit overlap protects
**all** microphones. No single-winner selection or per-person separation occurs.
Every shared microphone remains at unity, even with an idle approval. No events
means no cleanup. Leading/trailing sections outside the global protected span
stay fully audible. All source-time `keep` and `audible` overrides restore unity
on every microphone over their interval as a conservative restoration rule.

Approval boundaries round inward to absolute source frames. A further complete
frame stays at unity on both sides for native evaluation/interpolation. Every
group/removal seam gets the same unity margin. Both ramps last at least 200 ms
(at least two frames); there must also be at least one plateau frame. Short
remainders stay audible with a diagnosis. Fixed plateau attenuation is **-36 dB**,
with native dB-linear ramps; no exact mute, adaptive threshold, normalization or
denoising is used. These are conservative development settings, not calibrated
naturalness preferences. No subframe native-gain claim is made.

`validate_cleanup()` strictly reloads and exactly recomputes all spans before
export. The adapter writes the proven S02 entry `volume` effect, using absolute
source-frame keys even on nonzero source in-points. It does not alter the map,
clip boundaries, groups, source bounds, guides, bin originals or video. All MP4
audio remains disabled. Original origin/tail refusals run before cleanup/export.

## Peak and bleed report

`peaks.py` reads original integer PCM at its own sample grid, independently per
physical channel. It audits every retained frame using absolute rational sample
bounds. Buffers are bounded to one native frame per source, at most 384 kHz/eight
channels with FPS at least one. Unsupported bounds fail. Mixed sample rates are
not resampled. Digital silence and opposite-polarity channels cannot disappear
through averaging. Sources are rehashed before/after the audit and before export.

The report gives original/attenuated sums of each source's maximum absolute
physical-channel sample, a **conservative upper bound**, not an exact summed
waveform peak or a loudness score. Export requires the original bound below
**0.95**. This deliberately takes no cancellation credit: attenuating one of two
opposite-phase sources can expose overload. It can refuse a safe real mix; it
never silently changes master gain. Resolve a headroom review explicitly in a
future policy rather than renormalizing cleaned inputs. The headroom is not a
proof of codec or intersample true peaks; the actual synthetic GUI render is
measured separately.

Equal-grid source-frame absolute correlation is reported only as possible
bleed-like evidence. It never classifies a participant as idle or overrides quiet
speech, reactions, uncertainty or overlap. Unequal-rate comparisons are skipped.

## Commands and restoration

The callable API needs only the standard library and existing local probes.
Create explicit approvals from independently reviewed idle labels:

```python
from interview_auto_editor.cleanup import (
    CleanupRequest, IdleApproval, build_cleanup, planning_digest,
)

# result is a strict, reproducible S06 PlanningResult.
request = CleanupRequest(1, planning_digest(result), ())
cleanup = build_cleanup(result, request)  # no approvals: unity everywhere
```

Every wire field is required, including empty arrays. The strict codec rejects
unknown versions/fields, floats, noncanonical rationals, duplicate IDs and stale
bindings. Store records privately for real sources; IDs, hashes, notes and exact
timecodes can identify a recording.

```powershell
python tools/s08_cleanup.py --result '<private planning-result.json>' --request '<private cleanup-request.json>' --output '<new cleanup-result.json>'
python tools/s07_export.py --project '<starter.kdenlive>' --mapping '<private mapping.json>' --result '<private planning-result.json>' --cleanup '<private cleanup-result.json>' --output '<new cleaned.kdenlive>' --ffprobe '<local ffprobe>' --experimental
```

The cleanup command writes exclusively/atomically, with exit 0/2/1/130 for a
result, result requiring review, refusal or cancellation. Export retains its
S07 exit semantics. Audit failure/cancellation creates no new project. Original
sources and input records are unchanged. S10's combined run-folder interface
remains later work.

To restore one interval reproducibly, add a source-time `audible` or `keep`
override to the S06 request, replan, bind a new CleanupRequest to the new result,
and export another new file. Time restoration applies globally. To restore all
gain, remove all IdleApprovals and rebuild; this reproduces the baseline project
byte-for-byte on the synthetic fixture. No inference is needed. In Kdenlive,
bypass the selected clip's Volume effect (or its effect stack) to restore that
clip directly. Bin originals retain full source extents for manual extension.
Never feed the edited output back through the simple-starter reader.

## Evidence and scope

See [S08 evidence](../fixtures/S08_CLEANUP_EVIDENCE.json) and the
[S08 handover](../handovers/S08.md) for final gate status. The
[synthetic construction](../../tests/fixtures/s08-cleanup-26.08.2/construction.json)
has four independent noise-only labels, four protected tone activity intervals
and two overlaps. It retains S07's six groups/233 frames and the one approved
global deletion `[105,172)`. Construction files are not Kdenlive-authored.
Actual native saves, render and restoration have separate provenance.

```powershell
python -B -m unittest discover -s tools -p test_s08_cleanup.py -v
python tools/s08_fixture.py --output '<new synthetic folder>' --ffprobe '<local ffprobe>'
```

The actual 26.08.2 render measures all four noise probes more than 30 dB down,
eight protected source probes within 0.1 dB, thirteen exact picture anchors and
five zero-lag audio anchors. Sixteen native ramp edges have no measured large
sample discontinuity. Tone measurements cannot certify syllable naturalness.
The one local 24.5-second TTS A/B comparison separately preserves **187474/187474**
samples in three constructed utterances, including quiet acknowledgements, with
sample-evaluated policy envelopes. That speech file is not an actual GUI render,
real interview or held-out acceptance. Its human listening status must be read
from the current handover/evidence; measurements cannot substitute for feedback.

The retained eight-second human-confirmed development overlap stays at unity
because it has no independently approved idle labels. This independently checks
the new authorization default and preserves all 200/200 frames; it does not
establish that inference finds every event on every microphone. Original real
origins remain uncertified/null, exact tails unequal and export refused. Private
media/annotations remain local, and held-out/full interviews remain separate.
