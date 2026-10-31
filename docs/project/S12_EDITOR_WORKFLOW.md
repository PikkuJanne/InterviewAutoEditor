# Ordinary local interview editing

Use the prepared Python environment and a simple unedited Kdenlive 26.08.2
starter containing the original Zoom MP4 and one aligned, already cleaned WAV
per participant. From the checkout:

```powershell
.venv/Scripts/python.exe -B -m interview_auto_editor edit --project '<starter.kdenlive>' --output '<new private run folder>'
```

Success prints the absolute `project.kdenlive` path and exits 0. Open an editable
copy using the desktop's Open button; the original run remains recoverable.
The desktop's Create editable project mode uses the same service and defaults.
Legacy CLI commands retain their documented status codes and stricter defaults.

The command discovers the existing local Kdenlive FFmpeg tools and pinned CPU
models. Existing environment variables `IAE_FFPROBE`, `IAE_FFMPEG`,
`IAE_S04_MODEL`, `IAE_S05_MODEL` and `IAE_CACHE` override defaults. Explicit
tool/model/cache flags remain available. Nothing is downloaded. If an asset is
missing, restore the indicated input locally and retry; preserve any incomplete
run and use `--resume` only with unchanged inputs and settings. After a code or
input change, choose a new destination; never rewrite old manifests.

Participant tracks use their source filenames, with stable IDs
`participant_01`, `participant_02`, etc., in starter audio-track order from top
to bottom. An optional existing `--mapping` retains chosen participant names
and shared-microphone labels. This does not infer a person's identity.
Optional `--analysis` reuses an exact source-bound analysis and avoids inference;
the media, mapping, timing and fingerprints are still revalidated. Mapping,
analysis, approval and benchmark files are not required for a new interview.

The original-timing policy keeps unknown source offsets unset, retains every
source sample and marks empty picture after its EOF. The MP4 audio is excluded.
Full leading/trailing sections and uncertain vocal content remain. Source media
are never normalized or denoised again. Shared edits and named participant tracks
remain editable in Kdenlive. A fixed native master fader provides mix headroom.

Automatic pause decisions require measured digital silence on **every channel
of every participant source**, intersected with speech/reaction protection and
the existing conservative pacing/handle rules. This intentionally preserves
nonzero room tone and ambiguous gaps. Detector absence alone cannot authorize
deletion or microphone suppression. Zero safe cuts is a valid outcome. General
noise classification remains conservative: uncertain microphone sounds stay
audible; an explicit editorial mute affects only its selected source.

Repeatable mutes use original source seconds (decimal or exact fractions):

```powershell
.venv/Scripts/python.exe -B -m interview_auto_editor edit --project '<starter.kdenlive>' --output '<new run>' --mute participant_02 100.4 101.8 --mute participant_02 105 106
```

These ordinary editing choices become reversible native Volume keyframes.
One-frame edge fades stay inside the requested interval; the flat interior is
fully silent at supported PCM depths. Source coordinates are mapped through the
same shared time map, including edits crossing clip boundaries. Remove a mute
and regenerate in a new folder, or disable the native effect on an editable
copy. No participant names, recording-specific timecodes or source paths are
embedded in detection logic.

Old jobs can still be read and reviewed without an owner questionnaire. A
changed implementation correctly refuses partial resume; regenerate with the
saved options in a new folder and retain the failed attempt. Genuine missing
sources, stale analyses, incompatible structures, mismatched cleanup bindings,
corrupt artifacts and changed inputs continue to fail visibly.

The timed manual-versus-assisted exercise is **retired by owner**. Missing
manual/assisted seconds, subjective usefulness and independent quality/accuracy
denominators remain unmeasured. Retirement is not a pass. No 90%/70% result is
claimed. The original observations, study copies, approvals and failures remain
recoverable. Compatibility is experimental and limited to the exact validated
Kdenlive build; broader compatibility and release packaging belong to later steps.
