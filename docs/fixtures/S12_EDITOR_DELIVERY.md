# S12 ordinary editor delivery — attempt 09

S12 technical delivery is complete under the owner-directed operating revision.
The timed owner exercise is **retired by owner, not passed**. Manual/assisted
seconds, subjective usefulness/quality and the unsupported 90%/70% targets remain
unmeasured. No old observation, rejection, source or study copy was erased.

Implementation: `0f30418fb789ec24b336355a78d97be2172de28c`; initial ordinary workflow: `3d6f1157665eb64f5b140956a2db8828785abb6c`.
Machine-readable results: [metrics](S12_EDITOR_DELIVERY.json).
Exact procedures, failures and next prompt: [handover](../handovers/S12_ATTEMPT_09.md).

## Delivered behavior

`edit --project '<starter.kdenlive>' --output '<new private folder>'` discovers
existing local tools/models, derives participant mapping and preserves supplied
source timing. It requires no mapping, review, benchmark or annotation JSON.
Desktop Create uses this path. Internal records remain private and reproducible.
Explicit repeated `--mute PARTICIPANT_ID START_SECONDS END_SECONDS` choices are
stored with the run and carried through ordinary export. A Keep/audible interval
on any track prevents a conflicting mute. Sources remain recoverable in the bin.

Only measured digital zero on every channel of every participant can authorize
automatic shared pause removal, still constrained by all existing vocal
protection and handles. Nonzero uncertain room tone is retained. This is a
conservative useful path, not evidence of arbitrary-recording pause precision.
Neither complete real interview supplied such a safe automatic shared cut.

## Actual editor and full-render checks

Kdenlive **26.08.2 rev d4e87e4**, MLT **7.43.0**, FFmpeg **8.1.1**, Qt **6.11.1**,
Windows AMD64. Installed executable hash matches the retained genuine version
dialog/setup evidence. Nothing was installed or updated. Compatibility remains
experimental for this exact build until S13; future builds are not guaranteed.

| Fixture | Participant tracks | Groups / entries | Project frames | Native render seconds | Full audio sample frames |
|---|---:|---:|---:|---:|---:|
| band_001 | 4 | 113 / 565 | 51093 | 676.953 | 392394240 |
| two_person_002 | 2 | 128 / 384 | 47005 | 554.250 | 360998400 |

Both passed genuine GUI open/play, one-frame group move, save, undo, save, close
and fresh reopen. All five/three group members moved together with unchanged
source bounds; undo restored every original output position. Native timecode
serialization of effect keys is normalized when comparing semantics. Both saved
and reopened projects then completed installed Kdenlive `--render` (exit 0),
FFV1 picture with stereo PCM16 at 192000 Hz. This is not a GUI Render-button claim.

Every rendered audio sample agrees with the original-clock participant-only
reference to less than **0.501 PCM16 LSB**, including the declared native mute fades.
No full-scale sample or nonzero sample after the longest real audio EOF occurs.
The fixed reversible native master remains 0.95/N; cleaned sources are not
normalized or denoised again. Output has one video plus N named audio tracks;
the MP4 audio route is disabled. Neither project removes any shared frame.

All 51093/47005 encoded FFV1 picture packets, PTS and durations match the prior
fully source-validated native renders: 51092/47004 recorded frames in original
order plus one marked empty picture frame at real EOF. Prior source comparisons
were at 64x36 gray, not a full-resolution source RGB identity claim. Full audio
tails survive. No picture advance, invented camera image, freeze or audio slide
was introduced.

## Scoped full mute

The two authorized non-vocal events now have actual silent interiors on the
selected participant source. Four diagnostic installed-MLT source-isolated
renders use the actual native-saved filters: target interiors contain exactly
zero values, while adjacent target audio and the other three sources retain
their original clocks and expected samples (maximum unedited normalized error
5.9604644830901776e-09).
The complete mixed render is separately checked against every original sample.
Source-local effect keys survive native editing and reopening. Exact local
source IDs, fade boundaries, edited timecodes and output hashes stay private.

Gain interpolation follows the measured installed native effect, including its
previous-frame amplitude ramp. Explicit five-sample reads across all unity-key
boundaries avoid a prior streaming-block measurement omission. Mathematical
continuity/reference checks are not an independent human click-quality score.
No general idle-mic authority or broader audible-safeguard approval follows.

## Tests, recovery and retained evidence

`python -B -m unittest discover -s tools -p 'test_*.py' -v` with the existing
local tool/model/development paths: **250 tests, zero skips/failures/errors,
432.853 s** on the final implementation bytes. Focused ordinary-workflow tests
also passed (7 tests, 18.798 s). The public suite covers rational timing, mixed
grids, content protection, mandatory seams, EOF, export and recovery. A regression
retains more than 128 mandatory pause seams rather than enforcing the soft
optional-group target at their expense.

A controlled single-channel TTS/overlap/noise case removes 3.68 seconds of known
shared silence and retains its constructed words, reply, overlap and both ends.
An actual installed backend render matches the declared mono-to-stereo/native
gain/time-map reference to 3.901342376932959e-08 normalized. It is synthetic
construction evidence, not independent labels for real detector output or a
native GUI fixture. An earlier anti-phase stereo downmix cancelled the TTS and
was rejected as speech evidence; that failed diagnostic remains retained.

An actual historical saved desktop job was copied, loaded and reviewed; current
equivalent picture observations were regenerated, export cancelled without a
final output, and the same options resumed successfully. Its original hash is
unchanged and no questionnaire is introduced. The final full band generation
also retains its failed first attempt and safe same-options recovery evidence.

Hash retention: 8 original inputs,
44 attempt-08 records/projects,
243 older private artifacts unchanged.
Both original analyses/events and six null measured offsets remain unchanged.
The separate pending audible request retains its exact bytes and conditions.
The frozen held-out registration, five positive excerpt judgments, rejected
timing-unscorable excerpt and no-safe-pause finding remain historical evidence.
There was no held-out tuning, new connection or owner comparison assignment.

## Limits and boundary

G01–G09 applicable technical checks pass with the limits above. Full-corpus
independent word labels, subjective edge-fade quality, arbitrary-recording
precision, owner effort reduction and full real-pipeline peak memory remain
unmeasured. Observed native startup/seeking can take time on full interviews;
no universal performance promise is inferred from one group-budget correction.
G10 compatibility/clean-install work belongs to S13/S14. Stable release, merging
and publishing belong to S15 after S14. S13 has not run in this chat.
G11 is verified live after the documentation checkpoint; see final chat/Git.
