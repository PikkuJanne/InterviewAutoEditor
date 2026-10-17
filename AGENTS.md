# InterviewAutoEditor project instructions

These instructions govern development after this overlay is adopted into the InterviewAutoEditor repository. They do not authorize unrelated changes. Follow current user instructions and higher-priority instructions first.

## Required operating mode
- ONE named step per thread, S00–S15. Complete the selected step and its checkpoint, provide a VERBOSE handover, then STOP. Do not continue to the next step automatically, even if it appears easy.
- A step is the unit in docs/project/steps/, not each command or internal task. Do not repeatedly ask permission for ordinary reversible work within the authorized step.
- At every thread start, inspect Git and read docs/project/STATE.json, docs/NEXT_STEP.md, the latest handover, the selected step brief, and EXECUTION_PROTOCOL.md. The original ZIP is a bootstrap, not current state.
- Keep local work and GitHub synchronized at each checkpoint. Read GITHUB_WORKFLOW.md. Do not claim success until the live remote branch SHA equals local HEAD and tracked work is clean. If unavailable, report SYNC BLOCKED and stay on the same step.
- Never reset, discard, overwrite or force-push the user's work. Inspect and reconcile changes. Preserve existing repository instructions and licence.
- Do not spawn sub-agents unless the user explicitly requests delegation.

## Product requirements
- Optimize for Kdenlive 26.x. Record and test the exact patch build; isolate format/version details in adapters. Future versions are tested, experimental or unsupported, never automatically guaranteed.
- Input: one unedited Zoom MP4 plus N aligned cleaned audio files in a simple Kdenlive starter project. N is variable. Output: a NEW editable .kdenlive project, one video and N named audio tracks.
- Exclude the MP4 audio from output. Do not renormalize or denoise cleaned participant files again.
- Separate global pause removal, participant audibility, speaker-turn structure and recorded-picture analysis.
- Apply each removed duration to ALL tracks with one shared time map. Preserve words, laughter, acknowledgements, overlap and uncertain vocal events. Preserve full leading and trailing sections.
- Create useful aligned cuts and edit groups. Do not split every word. Keep original source media recoverable.
- Never advance the video or slide audio to conceal Zoom's picture-switch delay during speech. Missing camera footage cannot be reconstructed from one speaker-view file.
- Use local processing and CPU-capable inference. Keep real interview media, transcripts, names, private paths and credentials out of public Git, CI logs and releases.

## Required evidence and finish
- A plausible XML file or MLT render is not proof that Kdenlive can edit it. Record open/play/group-edit/save/reopen/render evidence from the actual supported version.
- Add focused tests for timing, content preservation, export and recovery. Never invent test results or claim a fixture was produced by Kdenlive when it was hand-authored.
- Keep editable project export as the primary deliverable. A flattened MP4 is not a substitute.
- Every step updates state, NEXT_STEP and a handover under docs/handovers/. Explain changed behavior, exact validation, untested items, risks, Git status and next prompt.
- Stable release work occurs in S15 after S14 acceptance. Respect repository review and protection requirements. Do not require paid signing; accurately describe unsigned builds.
