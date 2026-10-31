# InterviewAutoEditor Windows candidate

This unsigned **1.0.0-rc.1** portable candidate runs locally on Windows AMD64.
Use the exact tested Kdenlive **26.08.2 rev d4e87e4** installation. Other
installations remain experimental until tested. See `docs/COMPATIBILITY.md`.
This candidate is prepared for S14 validation; see the checkpoint evidence for
the actual acceptance result. Stable publication belongs to S15.

## Start

1. Install Kdenlive separately from [the official download](https://kdenlive.org/en/download/).
   InterviewAutoEditor does not install, update or redistribute Kdenlive/FFmpeg.
   Its normal Windows installation supplies `bin/ffmpeg.exe` and `bin/ffprobe.exe`.
2. Windows must also have the **Microsoft Visual C++ x64 v14 runtime**. If
   `--self-check` says it is missing, install the
   [official prerequisite](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)
   under Microsoft's terms. This separate installer can require administrator
   permission. The exact tested installer URL/hash/version is in
   `third_party/s14-runtime.json`; it is not included in this ZIP. The observed
   host 14.44.35211 and clean-test 14.51.36247 runtimes are recorded separately.
3. Compare the ZIP's SHA256 with `SHA256SUMS.txt`, then extract the **whole** ZIP
   into a new writable folder. Do not run it inside Explorer's ZIP view. Keep
   all runtime, app, model and notice files together. Once the prerequisites are
   present, the portable app needs no system Python, pip, administrator launch,
   execution-policy changes or model download.
4. Double-click `InterviewAutoEditor.cmd`. Choose the unedited starter, check
   participant filenames/names, confirm that mapping, and choose a new private
   output folder **outside the extracted application folder**. Select Create
   editable project and Tight/Gentle, then Start. No timed exercise, usefulness
   score, annotation batch or approval JSON is required.
5. Open **Local setup** if Kdenlive is in a different location. Select its
   Kdenlive, ffprobe and ffmpeg executables. The two inference models are already
   bundled. Missing assets fail visibly; processing never downloads replacements.
6. On completion choose **Open copy in Kdenlive**. Save manual editing in that
   copy. The complete run and original sources remain available for recovery.

Input is a simple unedited starter with one original Zoom MP4 and N aligned,
already cleaned participant **PCM WAV** files. One file may represent a shared
microphone. Linked MP4 audio is recognized and excluded. Unsupported edited
structures and timing overrides refuse with a diagnostic.

## Command line

From PowerShell in the extracted folder:

```powershell
.\InterviewAutoEditor-cli.cmd --self-check
.\InterviewAutoEditor-cli.cmd edit --project 'D:\Interviews\starter.kdenlive' --output 'D:\Interviews\new-run'
```

The self-check verifies all packaged file hashes, both CPU model invocations and
Tk creation. `PACKAGE.json` identifies the source commit and every unpacked
file. It is an integrity inventory, not a digital signature or guarantee against
a maliciously replaced inventory. Use the separately supplied archive checksum.

For a nonstandard tool location add `--ffprobe`, `--ffmpeg` and optionally
`--target-kdenlive`. `IAE_FFPROBE`, `IAE_FFMPEG` and `IAE_KDENLIVE` are local
environment alternatives; the last selects the desktop's editor. Model/cache
overrides use `IAE_S04_MODEL`, `IAE_S05_MODEL`, `IAE_CACHE`. The default cache is
`%LOCALAPPDATA%\InterviewAutoEditor\cache`. Keep the app and all outputs local.
The CLI's ordinary `edit` succeeds with exit 0 and prints `project.kdenlive`.
Legacy `report` returns 2 for a verified complete historical run; this is a
documented status, not corruption. Other legacy/probe statuses are in the CLI
and compatibility guides included under `docs/project/`.

## Recovery and troubleshooting

- **Missing source/tool:** restore that asset at its original path. Preserve the
  incomplete run. Repeat the identical command with `--resume`, or choose Resume
  saved job in the desktop. Resume checks source, code, tool, model, settings and
  artifact identities. Changed inputs/code require a **new output folder**.
- **Cancel:** the current operation stops cooperatively; no partial final project
  is published. Completed caches and private staging survive. Resume unchanged
  options; never hand-edit manifests to bypass a refusal.
- **Already existing output:** use a new folder. The application never overwrites
  a complete run or original starter. `report --run 'D:\Interviews\new-run'`
  verifies saved run artifacts; it does not revalidate current media.
- **Startup/model error:** run `--self-check`. Re-extract a verified archive into
  a new folder if a file is missing/corrupt. Do not install random runtime/model
  versions. If Windows blocks an unsigned file, follow your organization's normal
  review process; this product does not change security settings or require paid
  signing. Launch failures can also mean a missing system dependency; preserve
  the exact diagnostic for support.
- **Missing media after moving:** preserve run manifests; use Kdenlive's normal
  relink dialog on a separate editable copy. Generated relative references depend
  on directory depth. A report alone cannot repair or certify a moved recording.
- **Restore a cut/mute:** originals remain in the bin. Extend or move all grouped
  clips together; disable/edit native Volume on the affected clip. For repeatable
  source-time changes regenerate in a new folder with Keep/audible overrides or
  without the explicit mute. See `docs/project/S12_EDITOR_WORKFLOW.md` and
  `S11_DESKTOP.md`. Do not modify the immutable validated run.
- **Remove app:** close it and remove its extracted folder. Outputs, originals
  and the cache are separate. No registry install, service or global policy is
  changed. Delete a private cache only when its reuse is no longer wanted.

## Expected limits

Automatic pauses require exact digital silence on every participant channel,
plus all content/handle safeguards. Quiet room tone and uncertain noises stay.
Zero safe cuts is a valid outcome. Explicit mutes are reversible source-local
choices; no detector result grants wider mute authority. Sources are never
renormalized, denoised, stretched or independently shifted. Unknown offsets stay
unknown; recorded Zoom picture switches retain their timing during speech.
Full leading/trailing sections and audio past picture EOF remain, with explicit
empty-picture markers. Native groups coalesce optional boundaries toward 128;
mandatory shared seams and full semantic cues survive.

Only the exact measured Windows/Kdenlive row is tested. No broader Windows,
future editor, arbitrary project, subjective quality, 90% accuracy or 70% effort
claim is made. The owner exercise is retired, not passed. Local processing has
no cloud inference or hidden downloads. Reports can contain private paths and
recording information: keep runs/caches/screenshots out of public Git/support
uploads. Share only deliberately sanitized synthetic reproductions.

Licences and component provenance are included in `THIRD_PARTY_NOTICES.md`,
`third_party/`, the runtime's `LICENSE.txt` and wheel `.dist-info` notices. The
application's MIT licence is unchanged. Kdenlive/FFmpeg remain separate software
with their own licences and installation terms.
