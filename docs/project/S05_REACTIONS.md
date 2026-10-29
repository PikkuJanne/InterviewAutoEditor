# S05 local reaction and uncertainty evidence

**EXPERIMENTAL. S05 passes G04 on the agreed bounded development examples,
under one shared removal map and the current protected-source attenuation refusal.**
The implemented CPU event path adds positive reaction evidence and uncertainty
to S04. It does not certify silence, alignment, speaker identity or readiness to
edit. No cuts, gain changes, source separation, normalization, denoising, media
repair, camera recognition or project export occur. S06 remains pending.

## Setup and use

Tested platform: CPython 3.12.14, Windows AMD64, FFmpeg/ffprobe 8.1.1.
Install into an isolated environment, then explicitly download the model:

```powershell
.venv/Scripts/python.exe -m pip install --require-hashes -r requirements-s05-win-py312.lock
.venv/Scripts/python.exe tools/s05_prepare_model.py --destination .local/models/yamnet-v1.tflite
```

The lock includes the full S04 set and six additional version/hash-pinned wheels.
Existing NumPy 2.1.3 and ONNX Runtime 1.20.1 stay pinned. YAMNet runs with
ai-edge-litert 2.3.0, one CPU thread and its builtin CPU XNNPACK backend. No
external GPU/NPU delegate or accelerator SDK is supplied. Inference performs no
network operation; model setup is the explicit separate download. S04 continues
to disable ONNX Runtime telemetry. Runtime and model licences/provenance are in
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

Google's unchanged classification TFLite v1 is **4,126,810 bytes**, SHA256
`10c95ea3eb9a7bb4cb8bddf6feb023250381008177ac162ce169694d05c317de`.
The download URL is mutable, so exact size/hash are mandatory: it cannot silently
upgrade. The [manifest](../../third_party/yamnet-model.json) separately pins the
upstream reference-code revision and class-map/licence hashes. All 521 class
names were compared with the label list attached to the model and match.
The [official classification model card](https://github.com/tensorflow/tfhub.dev/blob/81fdea8ffa53b5acbd66a012d17fb8f9602c714b/assets/docs/google/models/yamnet/classification/tflite/lite/1.md)
describes this quantized, upstream-retrained Relu6 variant. It is not numerically
equivalent to the original floating-point YAMNet; its own bytes were benchmarked.
The additional runtime/notice burden and broad 975 ms fields are tradeoffs for
the measured laughter evidence missing from speech-only positive detection.

Reuse the explicit local [S03 mapping](S03_CONTRACTS.md):

```powershell
.venv/Scripts/python.exe tools/s05_analyze.py --project '<starter.kdenlive>' --mapping '<private mapping.json>' --ffprobe '<ffprobe.exe>' --ffmpeg '<ffmpeg.exe>' --speech-model '<pinned silero.onnx>' --reaction-model '<pinned yamnet.tflite>' --cache .local/fused-cache --report '<new summary.json>' --analysis '<new PRIVATE fused-analysis.json>'
```

Optional `--anchor` arguments preserve freshly measured S03 diagnostic evidence;
the callable `reactions.analyze(speech_result, ...)` retains the exact supplied
S04 result/intake and all earlier observations. Exit 2 means evidence written
requiring review, 1 failure, 130 cancellation. There is no ready-to-edit exit 0.
Both models remain mandatory even on cache hits. Missing/corrupt models fail
visibly before probing, with no amplitude-only fallback. Output destinations
must be new; each is published exclusively and atomically. The two output files
are separate publications, so one completed file can survive a later failure.

Private contracts/caches/manifests contain source hashes, supplied IDs/labels and
local references. Keep them local. Summaries use neutral participant IDs and
omit source hashes/paths, but still require privacy review before publication.
Full reaction/uncertainty sample bounds and potential-overlap bounds are included
for review. They are evidence windows, not suggested timeline split points.

## Positive evidence and fusion

Each physical PCM channel is decoded independently over the complete measured
source extent using S04's continuous 16 kHz SWR path. No channel averaging can
cancel opposite-polarity stereo. The original media and its complete tails stay
unchanged. Shared microphone labels stay on one source/group; neither physical
channels nor model classes identify individual people inside that recording.

The unchanged TFLite contains waveform feature extraction and the classifier:
15,600 input samples (975 ms, including the STFT receptive field), 521 output
scores. Inference advances 7,680 samples (480 ms), preserving overlapping full
receptive fields. New samples at EOF get one final padded analysis window,
clamped to the real source endpoint. Original audio is never padded. Audio
buffers and the decoder queue are bounded independently of recording length.
Absolute source-grid start/end conversions round outward; default protection is
120 ms before and 200 ms after. No minimum event duration discards responses.

Maximum score across Laughter/Baby laughter/Giggle/Snicker/Belly laugh/Chuckle,
indices 13-18, >=0.10 adds `reaction`. Otherwise a score >=0.03 from the declared
vocal/oral/crowd classes adds `uncertainty`. The exact class indices/settings are
in the implementation/cache identity. Scores are uncalibrated model outputs,
not confidence that content may safely be removed. Broad receptive fields can
overprotect surrounding silence, and two benchmark laughter clips had no
reaction hit. These thresholds were fixed before the supplementary benchmark;
no fitting/training on the evaluation clips was performed.

Each channel also accumulates a bounded 1 dB histogram of 32 ms RMS blocks.
Its 10th percentile is an **empirical floor**, not a verified noise-only sample.
Digital silence, cleaned audio and continuous speech can bias it. Signal runs
above four times the conservative upper floor edge, and at least 0.000001 RMS,
add uncertainty with score zero. Quantized signal-run metadata is capped at
200,000 entries; overflow fails visibly. Floor/contrast never delete or weaken
S04 evidence. The existing S04 peak safeguard also remains intact.

Fusion retains every original S04 event and review unchanged, appending reaction
and uncertainty. Cross-source raw activity intersections add two source-bound
`overlap` records with score zero and an uncertified-simultaneity reason.
Physical channels are unioned within each source first. Noise/bleed can cause
potential overlap; it is not asserted to be genuine simultaneous speech.
Correlation, loudness and the empirical floor cannot suppress a quiet response.
Declared origins are used only to describe possible intersections; no origin,
verified offset, drift, native sequence extent or exact source end is repaired.

The full intake remains attached. Existing reviews, S01 historical correlations,
S03 anchors, null unverified offsets, native extent deltas and exact tails remain
authoritative. V1 `exact_coverage` export refusal remains unchanged. No new
Kdenlive GUI operation is implied; actual editability evidence remains S01/S02
on 26.08.2 rev. d4e87e4, with compatibility EXPERIMENTAL.

## Cache and recovery

Reaction caches are separate from reusable S04 caches. Identity binds the full
source record/channel count, source and decoder implementation hashes, decoder
version/executable hash, model/runtime/Python/platform, settings, CPU backend,
window/hop/class indices and floor method. It excludes local paths, IO chunk
size and future pause targets. Replanning does not require event inference.

Hits still validate model/runtime, source bytes/grid, strict schema, event bounds,
labels/channels, decoded length, floor count and source identity. Corrupt entries
fail; inspect and remove only the diagnosed derived entry to recompute.
Cancellation and source changes cannot publish an incomplete current entry;
completed entries survive. Decoder termination/reaping and private-safe errors
reuse S04. Strict final v1 analysis validation/8 MiB bounds remain mandatory.

## Development evidence and gate scope

[S05_EVENT_EVIDENCE.json](../fixtures/S05_EVENT_EVIDENCE.json) records measured
results with explicit denominators. The benchmark command accepts only a
`development` manifest; a `held_out` manifest is refused before model/media use:

```powershell
.venv/Scripts/python.exe tools/s05_benchmark.py --manifest '<private development manifest.json>' --speech-model '<silero.onnx>' --reaction-model '<yamnet.tflite>' --ffmpeg '<ffmpeg.exe>' --report '<new report.json>'
```

The local ESC-50 supplementary benchmark uses official fixed-revision folds 1-2:
16 laughter, 16 breathing, 16 keyboard and 16 wood-creak clips. Category labels
are upstream human clip labels, **not exact event boundaries or cleaned Zoom**.
Its CC BY-NC 3.0 audio and per-clip attribution remain local for noncommercial
development evaluation; no dataset audio is redistributed or bundled. Folds 3-5
contain 24 reserved laughter clips whose audio was not downloaded/opened. Unknown
AudioSet/pretraining overlap means these are not a proven model-naive test set.

YAMNet versus Silero positive detection and fused protected fractions are reported
separately. A hit anywhere in a clip cannot establish zero lost laughter. Noise
is heavily overprotected; no aggregate accuracy, precision, disposable-silence
or useful pause-removal result is claimed. Unchanged S04 construction labels
measure generated words/acknowledgements only; they are not human acceptance.

The owner's three original excerpt sets have time-position labels only. A short
ignored annotation pack received initial phone listening feedback. The user
corrected provisional sound descriptions; approximate review windows and the
uncertain vocal origin remain explicit in local records. Those windows are fully
protected, but required positive speech/reaction/overlap categories are incomplete.
Candidate selection is explicitly model-assisted, **not ground truth**. A second
21-second development review pack provided an interview speech candidate, a two-source
microphone preview and an explicitly external development laughter example. Each
source channel in the microphone preview remains sample-exact; its declared
common origin remains uncertified. No gain or source-media change is applied.
The end excerpt is reserved from label-based tuning; full-source engineering
inference does not make it an independent interview or constitute acceptance.
Human timing precision must be recorded honestly; converting
seconds outward onto exact source samples does not make the original annotation
sample-precise. Held-out listening/acceptance must stay separate, with a
distinct interview preferred. The new observations and explicit overlap
confirmation below close the bounded S05 development gate. Full-interview,
held-out and later gain-policy acceptance remain untested. Do not start S06
in this thread.

## Phone delivery history and resumed development review

The user reported that inline audio, local references and the private Page file
links were unusable on their phone. Successful upload receipts and Page read-back
did not establish phone accessibility. Do not repeat those delivery claims.

The user limited future listening checks to **one audio file maximum**, selected
**no new connection and pause listening**, and later resumed by returning to
the computer and supplying feedback on the existing clips on 29 October 2026.
That feedback supersedes the listening pause for this review. The one-file and
no-new-connection preferences remain. No new audio is requested or delivered;
keep the existing private assets and observations for recovery.

A single 23-second private audition composite was prepared locally, with the
three development sections separated by one-second silence. Its source cues
remain unchanged; it is a review aid, not an edited interview or timing repair.
A direct public development sample URL was also checked at the HTTP level, but
neither route was verified on the user's phone. Later computer feedback does
not retroactively establish successful phone delivery.

The new direct-user observations confirm private speech, two distinct voices
with laughter, and external development laughter plus an end vocal event. Raw
comments and source-bound mappings remain ignored/local. Exact word,
laughter-onset, gasp-onset and overlap boundaries were not supplied; no transcript
or individual speaker identity is inferred.

Five of six conservative observation/channel envelopes are fully inside current
protection. The speech envelope covers the entire preview on both channels.
Both external vocal envelopes are fully protected without a positive speech-VAD
hit. The conservative suffix containing the end vocal event has S04 protection
`59/75` and fused protection `1`. Its unspecified onset means this is an envelope
coverage measurement, not a precise gasp-duration or classification score.

The two-source preview's combined timeline envelope is fully protected. One
source's broad observation envelope includes an uncovered opening; no vocal
content was labelled there, so no lost speech is established. The private
laughter's exact onset/source remain unknown. The user then explicitly confirmed
that the two voices overlap in the reviewed preview. No precise overlap bounds
or original-alignment certificate follows from that answer. No additional clip
is needed or asked for. Do not fit labels to detector boundaries.

Four private preview-channel mappings were rechecked sample-exact, the external
file matches its pinned development source, and all 102 original corpus
assertions pass again. Production code, settings, event protection and media
remain unchanged. Keep held-out acceptance unopened and separate.

## Bounded S05 G04 completion

Evaluate the **entire** already reviewed two-source preview as a conservative
group envelope, chosen independently of model predictions. Its protected union
covers every instant. One shared removal map therefore preserves all samples
on both sources throughout the envelope, including the human-confirmed overlap
and laughter wherever they occur. The existing contract also refuses attenuation
on either protected source. This proves bounded preservation without inventing
word boundaries or assigning the laughter to a particular microphone.

An explicitly derived contract harness crops the existing event coordinates
into an eight-second test domain. It is not a new planner/export or a repaired
real inventory. All **198** possible interior one-frame deletions at 25 FPS are
rejected specifically for intersecting protected content. Both mute and half-gain
attempts on each source are rejected (**4** refusals); two unity-gain controls
are accepted. Synthetic verified-zero origins exist only inside that harness;
every actual source origin, null offset, tail and review stays unchanged.

The individual-source full-preview protected fractions remain `1027/1600` and
`1`; the earlier five-of-six channel-envelope diagnostic remains intact. Shared
timeline protection with no attenuation is the preservation guarantee. No
per-microphone completeness, detector precision or useful silence-removal rate
is claimed. A later gain policy must independently retain the confirmed content.

Reported separately: six earlier uncertainty/noise channel observations, four
new speech/external-vocal channel envelopes and one whole-preview overlap group
envelope are fully protected. All sixteen construction-labelled S04 speech/
acknowledgement regions remain protected in the existing benchmark. These are
different units, not a pooled accuracy score. External laughter/end-vocal
protection includes an example without a positive speech-VAD hit.

**S05 COMPLETE for this bounded labelled-development gate.** Exact human timing,
per-voice attribution, full interviews, held-out acceptance, later gains and
actual edited output remain separate limitations/gates. No further S05 listening
is required. S06 remains pending for a later explicitly selected thread.
