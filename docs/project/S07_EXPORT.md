# S07 speaker turns and grouped export

S07's implementation connects reproducible S06 pause plans to an experimental
Kdenlive 26.08.2 export. **S07's applicable G02/G03/G07 gates pass on the
synthetic development fixture in actual 26.08.2 rev. d4e87e4.** Native saves and
the GUI render have separate provenance from construction files. Product
compatibility remains EXPERIMENTAL.

## Turn structure

`interview_auto_editor/turns.py` derives recording-source groups, not human voice
identity. It validates the strict v1 PlanningResult and exactly recomputes it
from its analysis/request before adding structure. S06 analysis, approvals,
decisions, protection, reviews, overrides and the shared map stay unchanged.
The derived EditPlan uses the existing v1 `edit_units` field; no schema migration,
inference, gain processing or new removal decision is introduced.

Algorithm `s07-source-group-turns-1` joins confident (at least 9/10) speech on a
single labelled source across gaps of at most 3/5 second. A run lasting at least
3/5 second supplies a structural turn. Shorter runs get backchannel cues without
picture fragmentation. Reactions, uncertainty, low-confidence speech and shared
microphone events retain source-bound cues; shared microphones never become
individual speakers. These thresholds are conservative implementation settings,
not accepted real-interview pace or speaker-recognition results.

Different substantial source-group turns propose a boundary midway through a
retained gap. If that point was removed, the existing shared seam supplies the
boundary. A sweep of **raw** confident event intervals records simultaneous
source activity; joining within-source gaps cannot invent overlap. Overlap at
least 3/5 second proposes outward frame-rounded start/end boundaries. Explicit
overlap events also retain their boundaries and cues. This is source activity
metadata, not proof against acoustic bleed or new human overlap ground truth.

All pause seams are mandatory. Optional structural boundaries must be at least
1/2 second from every existing boundary, including the output ends. Subthreshold
overlap/backchannels still have guides and retain all original media. A split
never deletes time or independently changes the picture. No decorative
transitions, word-level cuts, shot analysis or camera retiming are added.

## Export and recovery

`interview_auto_editor/adapters/export.py` is the new adapter integration; the
historical S02 manual proof tool is preserved. It uses the S03 fail-closed reader,
then validates starter fingerprint, exact adapter target/FPS/domain, complete
source-to-path bindings and names. It rehashes media, probes exact PCM counts,
audits full video PTS and checks fingerprints again before publication. XML is
bounded on read/write. Export is an atomic, exclusive new-file operation.

Each output unit intersects exactly one retained map segment. The resulting
source in/out frames and output position are identical on one video and N audio
tracks. Each unit is one native Normal group containing all N+1 clips. Guides
combine cues sharing a frame and include exact source-clock intervals. Every
MP4 chain, including bin references, disables audio. Native track routing hides
video-track audio, and linked MP4/default tracks are excluded. No gain effects
are introduced. Complete source producers remain in the bin with original
extents, allowing extension/restoration. Full exterior handles survive.

The existing unverified/null/nonzero-origin and unequal exact-tail refusals run
before export, including identity output. The observed extra native sequence
frame is reported separately and never becomes a source frame. Original real
inputs still refuse planning/export. No source shifting, stretching, padding,
truncation, denoising, normalization or source replacement occurs.

```powershell
python tools/s07_export.py --project '<starter.kdenlive>' --mapping '<private mapping.json>' --result '<private S06 result.json>' --output '<new output.kdenlive>' --ffprobe '<local ffprobe>' --experimental
```

The mapping is the existing strict S03 MappingManifest. Explicit relocation
export is not implemented; nonempty relocation pairs fail. Exit 0 means exported
without reviews, 2 means exported with retained reviews, 1 refusal/failure, and
130 keyboard cancellation. Errors and stdout omit private content/paths. Full
plans, cue guides and projects can contain private identities and must stay
local. S10's integrated run-folder/recovery interface remains later work.

Restore removed time by adding source-time Keep to the S06 request and replanning,
then export to another new file. Keep applies globally. Keep full source coverage
or remove approvals to recover an identity map. Replanning/export needs no model
inference. Bin originals and source bytes remain available; manually edited
output is not accepted as a new simple starter.

## Fixtures and validation

The self-contained [synthetic package](../../tests/fixtures/s07-turns-26.08.2/construction.json)
contains a hand-relinked native S01 starter, adapter output, strict planning
result, local relative mapping and generated tones/test-picture video. It has no
recorded people. The relinked starter and exported file are **not newly authored
by Kdenlive**. `tools/s07_fixture.py` reproduces the construction into a new
directory; it never claims GUI provenance. It drops inherited native cached file
hashes for newly constructed sources; canonical measured SHA256 bindings remain
mandatory. The native-roundtrip and ripple-extracted files are sanitized actual
application saves; the GUI-render MP4 came from Kdenlive. See
[provenance](../../tests/fixtures/s07-turns-26.08.2/PROVENANCE.json).

Source coverage is 300 frames at 25 FPS. Two generated source groups have
activity `[1,3)`, `[7,9)` and `[2,4)`, `[8,10)` seconds, so there are two exact
one-second overlaps. The independent all-participant silent label is `[4,7)`.
S06 removes `[105,172)` source frames, preserving every activity/protection
interval and both exterior handles. Output is **233 frames / 9.32 seconds**.
The six groups start at output frames **0, 50, 75, 105, 133, 158**, with end 233.
Each overlap is available on its own aligned group with both sources retained.

```powershell
python -B -m unittest discover -s tools -p test_s07_export.py -v
python tools/s07_fixture.py --output '<new synthetic folder>' --ffprobe '<local ffprobe>'
```

Tests cover 1/2/3/6/8 audio tracks, grouping/routing, raw overlap, backchannel
coalescing, shared microphones, no activity, Keep restoration, source/provenance
refusals, original preservation, native extent reporting, CLI no-overwrite and
byte-exact reproduction from a moved package with spaces/Unicode. Five hundred
alternating turns at 25 and 30000/1001 FPS exercise exact structural coordinates;
S06's separate 500-deletion/frame/sample-grid regressions remain in force.

See [S07 evidence](../fixtures/S07_EXPORT_EVIDENCE.json) and the
[handover](../handovers/S07.md) for exact executed checks and gate status.
Actual 26.08.2 revision d4e87e4 passed open, play, group ripple extraction,
movement and undo, save, close, reopen and GUI render. Removing the first overlap
group shifted all later clips exactly 25 frames on every track; Undo restored
it. The final group moved one second on all tracks and was undone. Reopened
overlap selection still selected three clips. Native timing/groups/guides match;
this capture's sequence extent delta is zero, separate from the retained
S01/S02 one-frame findings. The sanitized public native copy also opens.

All ten [render checks](../../tests/fixtures/s07-turns-26.08.2/render-validation.json)
pass: 233 video frames, 13 picture anchors with exact source-frame mapping,
seven audio anchors at zero measured lag, both source tones in both overlaps,
997 Hz embedded MP4 marker below -50 dB (approximately -227.746 dB in the silent
probe), and 128 AAC padding samples beyond the 447360 mapped source samples.
This is visual playback and measured synthetic preservation, not subjective
human listening acceptance. `tools/s07_validate_render.py` remeasures the actual
GUI artifact; it does not manufacture application evidence.
Full interviews, held-out acceptance, 3/6/8-track GUI, fractional-FPS GUI and later
gain cleanup remain unaccepted. No private/held-out audio is included here.
