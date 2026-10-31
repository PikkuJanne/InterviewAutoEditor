# InterviewAutoEditor 1.0.0

Unsigned Windows AMD64 portable release for conservative, editable Kdenlive
interviews. Download the complete portable ZIP, matching source ZIP,
`SHA256SUMS.txt` and `PROVENANCE.json` from the `v1.0.0` GitHub release.

- One unedited Zoom MP4 plus N aligned, already cleaned participant PCM WAV
  files becomes a new editable project: one video track, N named audio tracks,
  aligned grouped cuts and original media available for recovery. MP4 audio
  is excluded. Keep the immutable run and edit a separate Kdenlive copy.
- Local CPU inference with bundled CPython 3.12.16, Tk 8.6.15, 16 hash-locked
  wheels and unchanged Silero VAD/YAMNet models. No system Python, pip, cloud
  inference or hidden downloads. Licences, component hashes and file inventory
  are included. Upstream native binaries are pinned, not independently rebuilt.
- Shared pause removal requires exact silence on every participant channel
  and all protection checks. Quiet room tone, uncertain sounds, laughter,
  acknowledgements and overlap remain. Zero safe cuts is a valid result.
- Explicit source-local mutes remain reversible native effects. Full leading
  and trailing coverage, unknown offsets and original Zoom picture-switch
  timing survive. Sources are not renormalized, denoised or independently shifted.
- Journalled cancellation, exact-options resume, local caches and source-time
  Keep/audible overrides preserve recovery. A changed input/code identity needs
  a new destination; historical complete runs stay readable.

Tested editor: **Kdenlive 26.08.2 rev d4e87e4 / Windows 11 NT10.0.26300 /
AMD64**, MLT 7.43.0, Qt 6.11.1, FFmpeg 8.1.1. The official release index was
rechecked on 2026-10-31 and still lists 26.08.2 as latest stable. No blanket
26.x/future support. Package-clean Sandbox NT10.0.26100 passes setup/CPU/desktop;
its editor target remains EXPERIMENTAL. See `docs/COMPATIBILITY.md`.

Kdenlive with FFmpeg/ffprobe and the official Microsoft Visual C++ x64 v14
runtime are separate prerequisites. They are not installed or redistributed
by this ZIP. No paid signing or global execution-policy change is required.
The archive is unsigned; download reputation/SmartScreen is unqualified.

Known limits: simple unedited one-MP4/PCM-WAV starters only. Alignment is not
certified from equal file lengths. Missing camera footage cannot be recreated.
On small screens maximize the desktop; lower optional Keep/Restore controls
can remain clipped. CLI source-time overrides and native Kdenlive restoration
remain available. Broader Windows, DPI, accessibility, track-count/FPS GUI
coverage and arbitrary edited projects are unqualified.

Both complete interviews retain their accepted native-edit/full-render proof;
technical evidence does not establish general corpus accuracy or subjective
usefulness. The timed owner exercise and mandatory usefulness sign-off are
**retired by owner, not passed**. Unknown seconds, quality and 90%/70% targets
remain unmeasured. No broader cut/mute authority follows from this release.

Follow `QUICKSTART.md` for setup, ordinary generation, recovery and restoration.
Real media, transcripts, run reports and private paths must stay private.
The app's original MIT licence is unchanged.
