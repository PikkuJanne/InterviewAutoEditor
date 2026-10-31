# InterviewAutoEditor 1.0.0-rc.1

Unsigned Windows AMD64 portable release candidate; **not a stable release**.
The exact build/acceptance record is in the S14 handover and package inventory.

- Bundled relocatable CPython 3.12.16, Tk, 16 hash-locked CPU inference wheels,
  unchanged Silero VAD v5.1.2 and Google YAMNet classification TFLite v1. No
  system Python or runtime network/model download. External prerequisites can
  need administrator setup; the portable app itself runs as an ordinary user.
- Thin desktop and CLI generate a new editable Kdenlive timeline with one video
  and N named participant audio tracks. MP4 audio is excluded. Grouped edits,
  original media and native reversible gain effects remain editable.
- Shared pause removal is conservative: exact multichannel/all-participant
  digital silence plus protected content and exterior handles. Ambiguous audio,
  overlap, laughter, reactions and unknown offsets remain preserved. No new
  normalization/denoising or independent audio/video retiming.
- Recoverable private runs, repeatable scoped source-time mutes, explicit
  source-time Keep/audible choices, local caches and safe same-input resume.
- Exact compatibility row: Kdenlive 26.08.2 rev d4e87e4 on measured Windows 11
  AMD64/NT 10.0.26300. Latest stable matched this patch at the S13 check. Unknown
  targets are experimental; unsafe structures refuse. No promised version range.

Kdenlive and its FFmpeg/ffprobe, plus Microsoft's Visual C++ x64 v14 runtime,
are explicit separate prerequisites. No editor/decoder or additional Microsoft
installer/system DLL is copied into this archive. All app/runtime/model hashes, source commit,
licences/notices and a complete tracked source archive accompany the candidate.
The dependency/model versions remain fixed; the standalone CPython patch differs
from the development runtime and receives its own package validation.

Known limits: simple unedited one-MP4/PCM-WAV starters only; uncertain room tone
is not automatically deleted; full input-origin correctness is not inferred;
missing camera footage cannot be recreated. Broader Windows/editor builds,
subjective usefulness and numerical accuracy/effort targets are unmeasured.
The old timed owner exercise/usefulness sign-off is retired, not passed.

Follow `QUICKSTART.md` for startup, recovery and restoration. S15 alone owns
stable integration, tag and publication after the S14 checkpoint is accepted.
