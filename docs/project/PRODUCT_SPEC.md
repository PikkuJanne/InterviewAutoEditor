# Product specification

## Objective
Turn Janne's Zoom interview starter project into a tight, editable Kdenlive interview. Janne later trims the beginning/end and removes unwanted statements. The tool handles repetitive pacing and idle microphone cleanup without making those editorial decisions.

## Input contract
- Exactly one source MP4 from Zoom; N cleaned/normalized participant audio files, normally N >= 2. Each file represents a participant recording channel; a shared microphone remains one inseparable group.
- A single unedited sequence with full-length clips at the intended common recording origin. Explicit file-to-participant mapping overrides filename guesses. Empty default Kdenlive tracks may be ignored; linked MP4 audio must be recognized and excluded.
- Read media references from the starter project and validate readability, decoded duration, timestamps, sample rate/channels, frame rate and source identity. Resolve Windows drive/UNC paths, spaces, Unicode and relative paths safely; do not execute media paths or fetch remote media implicitly.
- Equal duration is expected but not proof of synchronization. Diagnose offsets and drift at several anchors. The embedded mix may support analysis only; it never becomes final audible audio. Do not silently stretch, shift or truncate a mismatched participant track.
- Preserve project profile, source quality and channel layout. Analysis copies may be resampled/downmixed. Conditional CFR conversion must preserve original wall-clock mapping and be reported, never merely change an FPS header.
- Reject unsupported edited structures, speed effects, nested timelines and unknown timing-critical features with an actionable message. Do not pretend arbitrary project import is supported.

## Output contract
Write a fresh run folder containing the new project, versioned edit plan, reproducibility manifest, concise review report and any derived assets. Retain originals in the bin and never overwrite source media/project. Exclude original MP4 audio at every relevant producer/track reference; verify by rendering.

The timeline contains one video track and N named participant audio tracks, aligned cuts and grouped edit units. Shortened gaps are shared across all tracks. Gain-only changes do not remove time. The report includes source and output timecodes, reasons, confidence and restore instructions. Originals remain available to extend or restore edits. Package/relink any generated assets reliably.

## Decisions
1. Detect protected speech, reactions, laughter, backchannels and uncertain sounds per participant; retain simultaneous activity.
2. Find global gaps between the union of protected events. Only confident interior gaps may be shortened.
3. Suppress high-confidence idle noise per track without affecting others or suppressing genuine overlap.
4. Form meaningful speaker turns and grouped edit units; a timeline split is independent of who Zoom happens to display.
5. Inspect recorded shot changes near handovers and adjust only within safe removable silence.

Do not select only the loudest microphone or use a negative VAD result as proof that an event is dispensable. Normalized rustling can be loud; laughter can be non-speech. Preserve uncertainty and flag it. Cross-track correlation can support bleed detection but does not overrule a real quiet interruption.

## Pacing defaults to calibrate
Tight: consider different-speaker gaps longer than 0.80 s, with a nominal 0.25 s residual; same-speaker gaps longer than 1.50 s, with about 0.50 s residual only when high confidence. Start with 0.12 s onset and 0.20 s tail protection. Actual residual must be at least the required combined protection: 0.32 s in that example, overriding 0.25 s. Quantize conservatively. These are tunable hypotheses, not validated quality claims. Gentle must preserve more time, using the same safety constraints.

Preserve natural word spacing and meaningful pauses; support source-time Keep overrides. No automatic deletion of fillers, topics, false starts, introductions or endings. Leading/trailing sections outside the protected conversational span remain complete; if activity is uncertain or absent, preserve rather than infer an editorial trim.

## Picture delay
If B starts speaking at 12.00 s and Zoom switches to B at 12.45 s, retain the opening speech and original picture timing. Do not delete B's first words or advance later video frames. When a switch occurs within removable silence, align the seam to existing shots if protection allows. Pinned/gallery/camera-off/uncertain views use conservative fallback. No invented video, freezes or independent retiming in v1.

## Non-goals
Transcription-based editorial deletion, subtitles, multicamera capture, gallery reframing, cloud services, speaker separation from a shared recording, fresh denoising/normalization and a replacement full video editor.

## Completion
A supported project yields a practically useful tight interview with recoverable edits. Tests and representative listening establish content preservation, meaningful cleanup, no new sync defects and working Kdenlive editing. Full release also includes installer/portable package, source, docs, checksums and explicit compatibility evidence.
