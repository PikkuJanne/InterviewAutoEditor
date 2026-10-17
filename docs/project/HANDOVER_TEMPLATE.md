# Sxx handover — descriptive step title

Template only. Replace fields with actual evidence. Do not commit this template as a completed handover.

## Outcome and scope
Step ID/title; COMPLETE or BLOCKED; what works now in ordinary language; which planned work remains. Explain any deviation and why.

## Starting state
Repository, branch, starting commit, actual Kdenlive/application/document/MLT versions where relevant, platform and how prior state was verified. Public handovers must not expose private local paths or participant names.

## Changes and reasoning
List meaningful files/components and resulting behavior. Explain important design choices, alternatives rejected for a concrete reason and compatibility implications. Include dependency/model changes and provenance.

## Validation evidence
For every relevant gate: exact command or manual procedure, input fixture ID, tested commit, expected behavior, observed result and evidence path. Distinguish PASS, FAIL and NOT RUN. List actual GUI open/play/edit/save/reopen/render checks separately from automated XML/timing tests. Explain failures fixed and concrete remaining risks. Summarize routine checks without hiding missing evidence.

## Content and synchronization checks
Report speech/laughter/overlap retention and pause/noise results when relevant. Report A/V anchors and duration checks. State source preservation and original MP4 audio exclusion evidence. If this step does not involve media, say not applicable.

## Git and CI
Implementation commit: actual full SHA.
Checkpoint branch and handover path: actual values.
Checkpoint commit: resolve from Git history for this file; final chat includes actual SHA after commit/push.
Live synchronization: verify at checkpoint; record actual results in final chat. Next thread re-verifies.
CI: exact tested SHA, run URLs/status or not configured/not applicable. Do not claim green CI before it has run.
Worktree and untracked/private files: clean status and exclusions; no secret values or private filenames.

## Artifacts and usage
What can be run now; exact verified commands; locations of generated results and restoration instructions. Use public-safe paths in Git and provide local absolute paths privately in chat only when useful.

## Remaining limitations and blockers
Separate expected scope limits from defects and unavailable evidence. State the precise smallest required user action if any. Do not ask the user to repeat checks Codex can perform.

## Next thread
Exact next step ID/title and its prerequisites. Include a ready-to-paste prompt that names the repo, branch, current implementation SHA, handover path, state and next-step files, the one step to execute, its scope and the instruction to commit/push/verify/handover/STOP. If blocked, the prompt resumes this same step.

## Pause
State explicitly that this thread stops here. No background execution of the next step.
