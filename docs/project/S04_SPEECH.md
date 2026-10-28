# S04 local speech evidence

Compatibility remains **EXPERIMENTAL**, with the unchanged Kdenlive **26.08.2
rev. d4e87e4** adapter. This step adds analysis, not cuts, gain changes, turns,
laughter classification, overlap decisions or project export. VAD probabilities
are model scores, not calibrated content-preservation confidence. A negative
result never certifies disposable silence. S05 must add reaction protection;
S06 must implement the shared planner separately.

## Setup and commands

Use CPython 3.12 on Windows AMD64 and an isolated environment. Tested Python is
3.12.14. Model/runtime pins and full licences are in
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install --require-hashes -r requirements-s04-win-py312.lock
.venv/Scripts/python.exe tools/s04_prepare_model.py --destination .local/models/silero-v5.1.2.onnx
```

Only explicit setup downloads anything. ONNX Runtime telemetry is explicitly
disabled before session creation. Setup pins an immutable upstream revision,
checks 2,327,524 bytes and SHA256
`2623a2953f6ff3d2c1e61740c6cdb7168133479b267dfef114a4a3cc5bdd788f`,
and refuses to overwrite. Analysis checks size/hash and runtime versions even
on cache hits. Missing, modified or unusable models fail visibly; no amplitude
detector replaces the model. Runtime package and model download are separate.

Reuse the explicit local [S03 mapping](S03_CONTRACTS.md), then run:

```powershell
.venv/Scripts/python.exe tools/s04_analyze.py --project '<starter.kdenlive>' --mapping '<private mapping.json>' --ffprobe '<ffprobe.exe>' --ffmpeg '<ffmpeg.exe>' --model .local/models/silero-v5.1.2.onnx --cache .local/speech-cache --report '<new report.json>' --analysis '<new PRIVATE analysis.json>'
```

Optional `--anchor 60 --anchor 1000 --anchor 1900` preserves freshly measured S03
correlation evidence in the enclosing report. Choose valid anchors for the
actual recording; this example is for the known development corpus only.
The callable `analyze(intake, audio_paths, model_path, ffmpeg, cache_dir, ...)`
retains the exact supplied intake, including existing diagnostics/anchors.
The command runs fresh read-only intake; it does not silently import or replace
earlier diagnostic methods. Their historical records remain authoritative.

Exit **2** means complete analysis evidence requiring review, **1** means
failure, **130** means keyboard cancellation. There is no ready-to-edit exit 0.
No project or media is written. Output paths must be new. Each validated output
is published atomically; the optional private contract and summary are separate
files, not a multi-file transaction. If one publication fails, an already
completed file may remain and must be inspected/reused with a new destination.

The summary uses neutral participant IDs and includes per-track events and every
intake extent/tail/origin diagnostic. Full contracts/cache entries contain source
fingerprints and supplied IDs/labels, so **keep them private**. A neutral report
still needs privacy review before publication. Model fingerprints are public;
real source fingerprints must never enter Git or CI logs.

## Signal, state and timing

Analyze each participant file and **each physical PCM channel independently**;
retain all channel evidence using the source's semantic labels and an explicit
`pcm_channel` evidence index. A shared microphone remains inseparable. Opposite
polarity stereo cannot cancel through averaging. The MP4's embedded mix is used
only for optional S03 correlation, never for participant inference or output.

One FFmpeg process per physical channel reads the entire measured WAV extent,
including source tails. A continuous SWR resampler creates temporary 16 kHz
float32 samples with fixed filter size 32, phase shift 10, exact rational phase
and no dither. There is no seeking per chunk, normalization, denoising or source
replacement. Original sample rate, dynamics, layout, count and bytes survive.
Finite resampler overshoot above full scale is passed through unchanged in
temporary buffers; it is never clipped or renormalized. Non-finite samples fail.
Decoded length must agree with the rational resampling count within one 16 kHz
sample; a disagreement fails instead of silently truncating or repairing.

Production IO chunks are 1–65,536 samples (default 8,192) with a two-block queue.
Audio buffering is bounded independently of interview length. Event metadata
grows with activity and uses the existing bounded 8 MiB strict contract limit;
inputs exceeding that limit fail visibly rather than publishing partial data.
FFmpeg stderr is capped at 64 KiB, inactivity at 30 seconds and each channel's
total decode/inference run at max(120 seconds, twice its source duration).
Sources too slow for these limits need an explicit future policy, never a
partial success. Cancellation kills/reaps the decoder; completed track caches
survive, incomplete entries never appear.

Model calls consume 512 samples (32 ms) with 64 previous context samples and
recurrent state `[2,1,128]`. State/context are reset only at source-channel start;
IO boundaries do not reset them. Only the final incomplete window is zero-padded
for inference; its event end is clamped to real decoded/source extent. Original
PCM is never padded. Absolute rational conversions floor starts and ceil ends
onto the source grid. Full final source sample bounds remain recoverable.

Window score >=0.50 emits speech. Score >=0.15 below that, or a non-speech-model
window with absolute peak >=0.0001 (-80 dBFS), emits **uncertainty**. This signal
check is an additional keep-for-review safeguard, not a speech/noise classifier
or fallback. Subthreshold signals may be missed; silence is not certified.
There is no minimum duration filter to discard brief responses. Same-kind runs
within 100 ms coalesce; default protection adds 120 ms before and 200 ms after,
clamped to the full source. Boundaries describe analysis events, not timeline
split proposals. These choices are conservative development settings, not full
interview quality calibration.

The strict v1 `Analysis` keeps the original `Source` records byte-for-field,
retains previous reviews, and adds every intake diagnostic as a canonical
review. The enclosing result retains the complete intake and origin anchors.
Native sequence extent, clip coverage and measured source end remain separate.
Unverified offsets stay null; correlation does not certify alignment. No shift,
stretch, truncation, silence padding or video advancement is performed. Existing
`exact_coverage` plan refusals remain in force.

## Cache and recovery

Per-source identity binds content SHA256, original sample grid/origin/labels,
channel count, complete analysis/protection settings, algorithm/source-module
hash, model hash, pinned runtime/NumPy versions, Python/platform, decoder
version/executable hash and fixed resampler/window/context options. It excludes
local paths, IO chunk size and future pause targets. Replanning should reuse
speech inference; changing protection settings intentionally invalidates it.

Each entry is strict versioned JSON. Hits require model/runtime validation and
rehashing the original source, then cache identity, decoded length, source/event
type/bounds and strict analysis validation. Corrupt entries fail visibly; remove
only the indicated local cache entry after diagnosis and rerun. Sources are
untouched. Completed entries are created atomically and exclusively; concurrent
identical results can be reused, conflicting content fails visibly. Inference
failures and cancellation do not publish incomplete entries.

## Development gate and limitations

The local test generator uses Windows System.Speech, Microsoft David Desktop,
to create a known sentence, “Yes” and “Mm hmm”, then constructs normal, soft
(gain 0.03) and very soft (gain 0.003) cases. TTS audio/voices are never committed.
Construction labels split generated speech at digital silence >100 ms; they
are independent of model predictions. Opposite polarity stereo tests both
physical channels. These are synthetic development samples, not genuine
Kdenlive output or held-out human interview acceptance.

```powershell
New-Item -ItemType Directory -Force .local/S04-development
powershell -File tools/s04_generate_tts.ps1 -Folder .local/S04-development
.venv/Scripts/python.exe tools/s04_build_development_fixture.py --folder .local/S04-development
$env:IAE_S04_MODEL='<local pinned model.onnx>'
$env:IAE_S04_DEVELOPMENT='<local development fixture folder>'
$env:IAE_FFMPEG='<local ffmpeg.exe>'
$env:IAE_FFPROBE='<local ffprobe.exe>'
.venv/Scripts/python.exe -B -m unittest discover -s tools -p 'test_*.py' -v
```

Optional real-model tests explicitly skip without these local assets; they
never download models or depend on private interviews. The S04 checkpoint ran
them with assets present. Chunked versus unchunked boundaries must match with
**zero samples tolerance** on this fixed runtime/decoder, including partial EOF
windows; the allowed decoded-count rounding is a separate resampling check.

Full-source private analysis is read-only engineering integration. Existing
private excerpts are position-selected and **not content-labelled**; no real
word/laughter/overlap retention or subjective listening acceptance is inferred.
VAD alone does not protect all laughter, breaths or acknowledgements. Wider
languages, real soft speakers, held-out content, two-hour stress, clean-install
packaging, S05 reactions and later product gates remain future work.

No new Kdenlive GUI check is required by this analysis-only change. Actual
open/play/group-edit/save/reopen/render evidence remains the unchanged S01/S02
26.08.2 synthetic record; it is not a new S04 application result. The wider GUI
matrix and real alignment/tail export limitations remain open.
