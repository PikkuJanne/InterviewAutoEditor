# S02 — editable export proof

S02 technical gates **G01/G02 PASS**, bounded to the synthetic manual-cut proof
below, on 17 October 2026. Product compatibility remains **EXPERIMENTAL**.
The implementation commit is recorded in the S02 handover; resolve the fixture
record's containing commit from Git. This is not interview-quality acceptance.

## Build and provenance

Actual application: **Kdenlive 26.08.2, revision d4e87e4**, Windows NT
10.0.26300.0 / AMD64, MLT 7.43.0, Qt6Core DLL 6.11.1.0, bundled FFmpeg 8.1.1.
The installed executable SHA256 was rechecked and equals S01's
`7a5bbf2e7764514a863fad756fe2195779475804706a8a74e73ab922def1d352`.
No software, model or dependency was installed.

The source is S01's genuine GUI-created `starter-2.kdenlive` and its existing
public generated test-pattern/tone media. There are no recorded people. The new
`s02-manual-cut.kdenlive` is **adapter-generated**, not claimed as GUI-created.
`s02-native-roundtrip.kdenlive` is a sanitized copy of the actual native save
after the observed editing checks. `s02-gui-render.mp4` was rendered using
Kdenlive's GUI, MP4-H264/AAC preset, full project. Raw projects and failed
attempts remain ignored locally. See
[s02-PROVENANCE.json](../../tests/fixtures/kdenlive-26.08.2/s02-PROVENANCE.json).

## Implemented boundary

`tools/s02_kdenlive_adapter.py` is a small Python proof tool, kept separate from
the future canonical plan/timing API. `read()` is its adapter-selection boundary.
It recognizes the observed exact build/document shape (26.08.2 / document 1.1),
integer FPS, one simple unedited sequence, native dual-playlist tracks, one MP4
video and variable distinct participant WAVs at zero with equal **clip-grid**
coverage. Explicit source-file-to-display-name mapping is required.

It rejects unknown builds, fractional FPS pending its GUI proof, ambiguous roots,
missing/local-URL resources, DTD/entities, duplicate IDs/properties, edited
entries, active effects/custom transitions, speed/nested sources, unequal clip
extents and nonzero source origins. Empty default tracks and linked audio of the
same MP4 are recognized and omitted from the output sequence. Public tests use
deliberate structural mutations for these cases; they are not GUI provenance.

Export requires `--experimental`, a new output filename and one strictly interior
half-open integer-frame cut. One retained map controls every track. MP4 chains
including bin references get `audio_index=-1`, `astream=-1` and
`set.test_audio=1`; video track playlists hide audio. The output keeps full source
media in the bin, uses N named audio tracks, creates one group per retained unit
and a guide at the seam. Source files/projects are never overwritten. No audio
is normalized, denoised, independently shifted or time-stretched.

This S02 tool does not probe/certify decoded source tails or drift, support an
arbitrary edited project, create the final run-folder/manifest API, or make
automatic speech/pause decisions. S03 and later steps retain those scopes.

## Exact manual experiment

At 25 FPS, source coverage is `[0,300)`. Manually remove `[100,125)` — source
4.00–5.00 seconds — from **all three tracks**. Retain `[0,100)` at output zero and
`[125,300)` at output frame 100. Output is 275 frames / 11 seconds. Leading and
trailing source frames remain present. The cut is an arbitrary synthetic timing
experiment; it is not a claim that the interval is silence or approved speech
removal (it intersects part of a synthetic tone). No real interview was cut.

On Participant 01's first entry only, a native Volume envelope uses frames
`0=0;35=0;45=-60;55=-60;65=0;99=0` dB. This exercises 400 ms ramps over an active
tone. Gain does not remove time or affect Participant 02.

## Actual application observations

The agent operated the installed application through the computer-use skill:

1. Open adapter output: PASS, no repair or missing-media prompt; one V and two
   named A tracks, two aligned units and the guide were visible.
2. Select Participant 01: PASS, Volume appeared in its native effect stack with
   six keyframes; the envelope was visible and selectable on the clip.
3. Delete the first group: PASS, its video and both audio clips disappeared
   together; Undo restored all three and the gain envelope.
4. Move second group: PASS using native Edit Duration, Position 00:00:04:00 to
   00:00:05:00; all three clips moved together. Undo restored the shared seam.
   Two earlier direct drag attempts only selected the group and did not move it.
5. Play: PASS, observed changing picture/source counter and output timecode
   (00:00:03:01 to 00:00:08:08) and active meters across the seam, then paused.
   This is visual playback evidence, not subjective listening acceptance.
6. Save As a new native copy: PASS. Open the unchanged starter to close it, then
   reopen the saved copy: PASS, no missing-media/repair prompt; cuts/gain retained.
7. GUI render: PASS, full-project duration shown as 00:00:11:00; job completed in
   12 seconds. Actual encoded video is 275 frames / 11.000 s, stereo 48 kHz AAC
   duration 11.008 s (384 decoded padding samples).
8. Open the sanitized public native copy: PASS, no missing-media/repair prompt.
   Public XML resources resolve relative to the package. Render preferences set
   after the captured save were not written over that captured file.

## Measurements and semantic comparison

[s02-render-validation.json](../../tests/fixtures/kdenlive-26.08.2/s02-render-validation.json)
contains **11 passing checks** from `tools/s02_validate_render.py`:

- All compared timeline semantics match: profile, track names, source entries,
  output positions, stream routing, entry gain, groups and guide.
- **Whole-project semantic equality is false:** native sequence extent changes
  from 275 to 276 frames. This is separately asserted and retained, matching
  S01's real-project finding. It is not a changed clip entry or extra rendered
  video frame; GUI rendering yields exactly the 275-frame clip map.
- Eight picture anchors, including both seam sides and final source frame 299,
  best-match their mapped original frame at offset zero. RGB MAE is 1.615–2.746
  after the GUI H264 encode.
- Four audio anchor windows include onsets/ends before and after the cut. Their
  best lag is zero samples on a 48-sample search grid over ±3840 samples; the
  direct-position error also passes. This is bounded synthetic evidence, not
  sample-exact AAC identity or real lip-sync certification.
- The MP4-only 997 Hz contamination marker is **63.085 dB down**. Both participant
  tones remain present after the cut, at about 0.244 amplitude.
- Native plateau measures **−60.008 / −60.011 dB** relative to restored level.
  Descending probes measure −13.986 and −43.998 dB; ascending probes measure
  −43.961 and −13.943 dB. Adjacent-sample deltas within 10 ms of the four gain
  boundaries peak at 0.010558 normalized amplitude, below the 0.04 proof bound.
  This is a numerical synthetic discontinuity check, not a subjective no-click
  or protected-syllable claim.
- All source-media manifest hashes remain unchanged. The private S01 validation
  was also repeated: 102 assertions; five originals unchanged and twelve exact
  PCM excerpts still match. Only neutral results are public.

## Audio-gating representation decision

Use **native per-entry Volume keyframes** for the currently proven frame-grid
gain representation. No derived PCM fallback is needed for this S02 400 ms ramp
experiment. Filters must be attached to playlist entries with
`mlt_service=volume` and `kdenlive_id=volume`, as observed in a Volume effect added
through the GUI. Originals remain unchanged and removing the entry effect
restores source gain.

This does not establish sample/subframe native envelopes or accept every future
idle-microphone edge. S08 must test the chosen real envelopes and listening
requirements, and use gain-only PCM if those requirements cannot be met natively.
No fallback audio was generated in S02.

## Failures retained and corrected

- The first two adapter attempts placed a volume filter on a producer chain.
  Kdenlive serialized it but did not show it as an editable clip effect. This
  failed the native-editability expectation. A genuine GUI-added effect exposed
  entry-based serialization; the final output was regenerated and all required
  GUI checks/render repeated. Failed projects remain ignored locally.
- The first linked-audio unit-test mutation duplicated native filter IDs. The
  parser correctly rejected it; the mutation was corrected and the test passed.
- The first render validator used a constant single-tone plateau as its first
  lag anchor. Periodicity selected a spurious −3600-sample minimum despite tiny
  zero-position error. It was an invalid anchor, not evidence of drift. Replacing
  it with an onset/end window produced zero lag; the original failing report
  remains local. The unchanged GUI render passed the corrected measurements.

## Reproduce and recover

From the repository with Python 3.9+ (the observed runtime is Python 3.12.14):

```powershell
python -B -m unittest discover -s tools -p 'test_*.py' -v
python tools/s02_validate_render.py --project tests/fixtures/kdenlive-26.08.2/s02-manual-cut.kdenlive --roundtrip tests/fixtures/kdenlive-26.08.2/s02-native-roundtrip.kdenlive --render tests/fixtures/kdenlive-26.08.2/s02-gui-render.mp4 --media tests/fixtures/kdenlive-26.08.2/media-2 --ffmpeg '<existing ffmpeg executable>' --report '<new local JSON path>'
```

Open `s02-native-roundtrip.kdenlive` for the actual native-saved editable example.
Use Save As for changes. Keep `media-2` alongside it. The MP4 is secondary test
evidence, not the primary output. Rebuild or extend clips from full sources in
the bin to restore the removed interval; remove Volume to restore gain. The
uncut genuine starter and original media remain unchanged.

For a fresh proof export, create a local JSON object mapping the absolute paths
of the two public participant WAVs to `Participant 01` / `Participant 02`, then:

```powershell
python tools/s02_kdenlive_adapter.py --project tests/fixtures/kdenlive-26.08.2/starter-2.kdenlive --output '<new local project.kdenlive>' --cut 100 125 --names '<local mapping.json>' --experimental --gain-edge-proof
```

The gain option is an explicitly synthetic proof envelope, not production noise
cleanup. Exact frame/sample/source-tail contracts and alignment remain S03.
The recorded 192 kHz tail differences, subframe correlation observations and
uncertified real alignment in [S01_REAL_INPUTS.md](S01_REAL_INPUTS.md) remain
unchanged. Broader GUI count, fractional-FPS, UNC and future-build evidence is
still pending. S02 does not widen compatibility to all 26.x or future versions.
