# Next: S08 — apply reversible idle-microphone cleanup

**S07 is complete on applicable synthetic and retained bounded development
fixtures. S08 remains pending and was not started.** Compatibility is EXPERIMENTAL.

- Branch: `codex/kdenlive26-overhaul`.
- S07 implementation/evidence: `ffb83e1a3ce07edabe99ce3ed8bdbe500d46c912`.
- Initial S07 core: `24f29902a255269bfd98bdb8adaca6d2e3909b37`.
- Handover: [S07.md](handovers/S07.md).
- State: [STATE.json](project/STATE.json).
- Next brief: [S08.md](project/steps/S08.md).
- Export guide: [S07_EXPORT.md](project/S07_EXPORT.md).
- Evidence: [S07_EXPORT_EVIDENCE.json](fixtures/S07_EXPORT_EVIDENCE.json).
- Actual GUI provenance: [PROVENANCE.json](../tests/fixtures/s07-turns-26.08.2/PROVENANCE.json).
- Render measurements: [render-validation.json](../tests/fixtures/s07-turns-26.08.2/render-validation.json).

S07 derives substantial recording-source turns and overlap boundaries while
retaining brief backchannels as cues. Every edit unit is one native group with
one video and all N audio clips. One unchanged S06 map controls every track.
Strict reproducibility, explicit all-track gap approvals, source-time Keep and
audible overrides, protected content, shared microphones, full exterior handles
and original bin sources remain intact. Canonical contracts stay v1.

Final full implementation suite: **140 tests, zero skips, 113.045 seconds** with
existing local CPU models, development assets and FFmpeg/ffprobe. Coverage includes
1/2/3/6/8 audio tracks, 500 turns at integer/fractional FPS, recovery, provenance,
exclusive output, relocation and actual-GUI-render remeasurement.

Actual **Kdenlive 26.08.2 rev. d4e87e4**, MLT 7.43.0, Qt 6.11.1 passed open/play/
group ripple extraction and movement/undo/save/close/reopen/GUI render. The
sanitized native copy also opened. Removing a 25-frame overlap group shifted all
later video/audio clips together. Native timing/groups/guides match, with zero
sequence extent change in this capture. Prior S01/S02 one-frame findings remain.

The synthetic output has six groups and 233 frames. All ten render checks pass:
13 picture anchors map to exact source frames; seven audio anchors have zero
measured lag; both sources remain in both one-second overlaps; the embedded
MP4 marker is about -227.746 dB in the silent probe. AAC adds 128 padding samples.
These are measured synthetic/visual GUI checks, not subjective real-interview
listening, original-alignment certification or held-out acceptance.

Retained human-confirmed development overlap survives 200/200 frames. The
original corpus again passes 102 assertions: five unchanged originals and twelve
sample-exact excerpts. Actual original origins remain unverified/null and tails
unequal; real planning/export still refuses. No gains, normalization/denoising,
source repair, per-track removal or camera retiming was introduced.

Initial automatic GUI launches were not targetable; the user opened the app and
S07 continued. A first construction open warned about inherited stale native
WAV cache hashes. It was aborted, construction metadata corrected, and all GUI
checks repeated successfully. Both failures are retained in provenance/handover.
No current S07 blocker or further user action remains.

S08 must independently validate any attenuation policy against protected speech,
reactions, uncertainty, shared microphones and overlap. Current protected-source
attenuation refusal is not permission to weaken protection silently. Preserve
source-time audible overrides and exact full coverage. Keep private data local,
held-out/full-interview acceptance separate, the one-audio-file maximum and
no-new-connection preference. Changed export needs actual Kdenlive regression.

Verify the containing checkpoint before editing:

```powershell
git log -1 --format=%H -- docs/handovers/S07.md
python tools/verify_checkpoint.py --repo .
```

The closing chat records final local/live equality, clean upstream/worktree and
exact-SHA CI after normal push. Absent workflows/checks means **CI not configured**.
A failed sync overrides continuation and requires resuming S07.

Ready-to-paste next-thread prompt:

> Execute S08 only in InterviewAutoEditor on codex/kdenlive26-overhaul. Read
> AGENTS.md, STATE.json, NEXT_STEP.md, docs/handovers/S07.md, execution/GitHub
> protocols, S03–S07 contracts/guides and the S08 brief. S07 implementation and
> actual GUI evidence are ffb83e1a3ce07edabe99ce3ed8bdbe500d46c912. Verify the
> containing checkpoint, live SHA equality, clean upstream/worktree and exact-SHA
> CI first. Implement reversible idle-microphone cleanup within S08, preserving
> all speech/reactions/uncertainty/overlap, shared microphones, source-time audible
> and Keep overrides, explicit global gap approvals, the one shared map, grouped
> edits, full exterior handles/bin originals and existing real-origin/tail
> refusals. Do not renormalize/denoise, repair sources, remove time per track or
> retime the camera. Validate any new gain policy independently; obtain actual
> Kdenlive 26.08.2 rev. d4e87e4 evidence for changed export. Keep private data
> local, held-out acceptance separate and compatibility EXPERIMENTAL. Complete
> S08 gates, commit/push/verify, provide a verbose handover and STOP. No S09.

Paused after S07. The next thread should execute S08 only.
