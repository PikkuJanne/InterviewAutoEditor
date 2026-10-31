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

## Owner-directed workflow revision (S12, 2026-10-31)
- The timed manual/assisted owner exercise and mandatory usefulness/quality sign-off are **retired by owner**. Never request two edits, two saves, elapsed seconds, routine annotation batches or a usefulness score as a delivery prerequisite. Preserve old study copies and evidence; retired is not passed. Unknown timings, subjective usefulness and unsupported 90%/70% claims stay unmeasured.
- Codex owns setup, reproduction, repairs, retries, editor operation and affected validation. Use the ordinary editor workflow; internal approvals, benchmark records and evidence files must not be prerequisites for conservative project generation. Preserve uncertain speech/timing and continue independent work.
- Ask only for an unresolved choice with a meaningful editorial consequence. Use existing decisions first. Supply the existing project, edited timeline timecode, one thing to listen for, plain options and the conservative default. An approved local mute grants no broader detector/safeguard permission.
- S12 closes when normal generation, both complete interviews' applicable technical checks, the authorized full mute, prompt-free recovery and GitHub sync pass. Preserve all other content/timing/editability/recovery requirements. Numerical accuracy/effort claims still require suitable independent evidence; detector predictions cannot be their own answer key.
- Apply these working rules in every later milestone. Stop at the S12/S13 handover in this chat. Lead the owner handover with usable absolute project paths and verified results; keep verbose engineering evidence in the linked handover. State “Nothing needed from Janne” when true, and end with next owner/action, branch, commit and verified push status.
