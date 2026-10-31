# S03 intake and exact contracts

The executable schemas are the frozen typed records in
[`contracts.py`](../../interview_auto_editor/contracts.py). Their strict JSON
codec is `dumps(record)` / `loads(Analysis | EditPlan, text)` (pass the individual
class, not a Python union). `MappingManifest` is defined in
[`intake.py`](../../interview_auto_editor/intake.py) and uses the same codec.
These are version **1**, independent of Kdenlive XML. There is no inference or
planner in S03 and the S02 exporter does not consume these plans yet.

## Wire rules and identity

`Header` contains `schema_version=1`, run ID, project SHA256, tool version,
adapter target, explicit setting pairs and model/version pairs. Analysis contains
FPS, source records, sample-based events, frame-based shot candidates and review
records. Plan contains that analysis, **one** shared map, one reason per removed
gap, sample-based gain points, shared output-frame edit-unit boundaries,
source-time overrides, mapped reviews and an explicit tail policy.

Every field is required, including empty arrays. Unknown fields, duplicate JSON
keys, unknown versions/enums, booleans used as integers, floats and implicit
defaults are rejected. Rational quantities use reduced objects such as
`{"numerator":30000,"denominator":1001}` with positive denominator. Times,
confidence and gain are rational; source samples/frames are integers. Paths and
display names belong to the local mapping, not the canonical edit plan.
`source_id` connects records; SHA256 binds content. Two distinct files may have
identical content, for example two silent channels. A fingerprint is not a
participant name or a substitute for the explicit mapping.

Use the strict codec at persistence/consumer boundaries even for directly
constructed records; dataclass annotations alone do not enforce Python types.
The codec applies type checks and cross-record invariants. Corrupt data is
rejected rather than migrated implicitly. There are **no migrations yet**.
Future schema changes need an explicit migration, retained old fixtures and
tests, or a clear unsupported-version diagnostic. Future Kdenlive adapters must
not change the meaning of stored source time.

## Timing and origin

All intervals are half-open `[start,end)`. `SharedTimeMap` stores ordered,
non-overlapping, coalesced retained source frame ranges and derives output
positions from absolute integer bounds. The first source frame and final source
endpoint must survive; removals are interior only. FPS is rational, never
29.97 as a float. Conversion to each source sample grid derives floor/ceil from
absolute times, so rounding is bounded independently of the number of cuts.
Protection rounds outward and removals inward. Inclusive MLT end conversion
stays inside adapters; it is not the canonical interval convention.

Sample bounds, evidence/confidence, protected rational bounds, channel labels
and uncertainty reasons are stored for speech/reaction/uncertainty/turn/overlap
events. Speech, reaction, uncertainty and overlap protection cannot intersect a
removed interval. Picture candidates use video frame indices and cannot
authorize a speech cut or picture shift. Gain points are attenuation only,
source-bound and ordered. Until S08 defines a tested envelope policy, this
contract refuses attenuation on sources with protected events. Turns, overlaps,
shot candidates, gains and overrides are **data types**, not implemented
analysis/cleanup algorithms.

`Source.origin` records the declared source-to-project origin. A zero WAV
timeline origin does not prove waveform alignment. `origin_status` distinguishes
verified/unverified/detected-offset/inconsistent findings; `verified_offset` is
**null** unless verified. A nonzero origin/verified offset or unverified source
cannot authorize a plan. Diagnostic correlation records remain evidence, not
applied offsets. The application never shifts, stretches or resamples originals
to make a validation pass.

The bounded diagnostic uses three or more distinct 4-second source windows
spanning at least half the recording, mono 2 kHz temporary analysis buffers,
±100 ms lag search, normalized peak >=0.65 and separated-peak margin >=0.08.
Positive lag means the participant occurs later than the embedded reference mix.
Its resolution is 0.5 ms. Silence, repeated peaks, search-boundary peaks,
insufficient anchors and inconsistent lags remain review states. The thresholds
are conservative diagnostic choices, not calibrated real-interview acceptance.
Even consistent zero-lag peaks against a cleaned/mixed recording are not an
automatic alignment certificate. The read-only intake therefore leaves WAV
origins uncertified and reports `ready=false`; later explicitly evidenced origin
acceptance is required before planning/export. Non-destructive analysis can
still operate on the inventory and must propagate these review states.

## Three different end measurements

Keep **timeline clip coverage**, **native sequence extent** and **measured source
ends** separate. The observed extra native sequence frame is recorded explicitly;
it does not become a source frame or get silently removed. Exact WAV counts and
full decoded video PTS cadence are authoritative probing observations. Metadata
duration is recorded separately from the video timestamp audit.

A source at least one frame shorter than clip coverage is a truncation error.
Any other nonzero source-end difference, positive or negative, requires explicit
tail reconciliation. There is no end tolerance that silently drops samples.
Version 1's only plan tail policy is `exact_coverage`: every measured source end
must equal the shared map domain. This intentionally rejects the current real
corpus for export while retaining all its tails in the inventory. Supporting
unequal ends later requires an explicit, tested policy/contract extension. S03
does not introduce automatic silence padding, picture freezes or media repair.

## Safe reader and setup

Python **3.12 or later** is required for this core; S03 was run with 3.12.14.
It uses the standard library and the existing local FFmpeg/ffprobe 8.1.1;
no dependency or model was installed. Set `IAE_FFPROBE` and `IAE_FFMPEG` for the
real-tool tests, or put the executables on PATH. Missing tools fail visibly;
integration tests explicitly skip when these variables/PATH are absent.

The bounded 8 MiB UTF-8 XML reader rejects DTD/entities, alternate encodings,
duplicate IDs/properties, unresolved references, unknown processing structures,
edits/offsets, active effects, proxies, nested timelines and unregistered builds.
All bin chain resources must resolve. Relative paths use the saved project root
or project directory; mappings use the mapping file directory. Literal local
paths with spaces/Unicode are supported. Exact-reference relocation pairs are
explicit relinks; media is not copied or modified. URLs and drive-relative paths
are refused. UNC access requires explicit opt-in and remains untested.

The reader recognizes the observed 26.08.2/document-1.1 structure. Fractional
millisecond serialization is accepted only within half a millisecond of a unique
frame at a rate below 1000 FPS; integer frame serialization is exact. This is
automated parser coverage, not a fractional-FPS GUI support claim. Product
compatibility remains **EXPERIMENTAL**. The S02 exporter is unchanged.

Probes use argument arrays without a shell, local file/pipe protocols, bounded
disk-spooled output, time limits and private-safe errors. Full video frame PTS
are compared with absolute expected times, rather than trusting nominal/average
FPS. Missing timestamps, count/duration inconsistency and decoder errors fail
closed. RIFF chunk boundaries, physical WAV size and PCM frame alignment are
checked before trusting counts. RF64/non-PCM WAVs need future explicit support.
Probe limits are 120 seconds and 64 MiB per process (diagnostic windows have a
smaller output limit); reaching a limit reports failure, never a partial audit.

The parser precautions follow Python's
[XML security guidance](https://docs.python.org/3/library/xml.html#xml-vulnerabilities).
The probe interface follows the official
[ffprobe documentation](https://ffmpeg.org/ffprobe.html). Neither documentation
is evidence of Kdenlive editability; that remains the S01/S02 actual-application
record and future required GUI matrix.

## Read-only command

Create a local mapping JSON (do not publish actual names/paths):

```json
{
  "schema_version": 1,
  "participants": [
    {
      "resource": "media-2/participant-01.wav",
      "source_id": "participant_01",
      "display_name": "Participant 01",
      "channel_labels": ["participant_01"]
    },
    {
      "resource": "media-2/participant-02.wav",
      "source_id": "participant_02",
      "display_name": "Participant 02",
      "channel_labels": ["participant_02"]
    }
  ],
  "relocations": []
}
```

For this example put the mapping beside the public starter fixture. Prefer an
ignored private mapping with appropriate explicit resources for actual work.

```powershell
python tools/s03_inspect.py --project tests/fixtures/kdenlive-26.08.2/starter-2.kdenlive --mapping '<local mapping.json>' --ffprobe '<local ffprobe executable>' --report '<new report.json>'
```

Optional diagnostics add `--ffmpeg '<local ffmpeg executable>' --anchor 0
--anchor 4 --anchor 8` for a 12-second synthetic input. Select suitable distinct
windows for longer material. No audio is sent to a service. The report replaces
all source IDs with neutral IDs and omits names, paths and content hashes, but
still requires review before publication. Canonical analysis records contain
source hashes and are **private when real inputs are used**.

Exit 0 means no review/error diagnostics; exit 2 means a complete report needs
review; exit 1 means inspection failed. Uncertified WAV origins currently make
ordinary intake return 2 by design. The report is created exclusively; existing
files and all media/project inputs are never overwritten. This is an S03 setup
command, not the final S10 CLI contract.
