# Validation and acceptance

## Mandatory gates
| ID | Gate |
|---|---|
| G01 | Original project/media unchanged; all output references resolve; linked MP4 audio absent from audible output |
| G02 | Kdenlive 26 actual open/play/group edit/save/reopen/render succeeds without repair or missing media |
| G03 | Shared exact time map, duration conservation and no cumulative drift; rendered anchors within one project frame of validated source baseline |
| G04 | Zero lost annotated words, acknowledgements and laughter; protected intervals never cut or muted |
| G05 | All automated deletions in labelled acceptance excerpts lie inside approved removable intervals |
| G06 | Idle-noise suppression measured; no new clicks, truncated syllables or mix overloads |
| G07 | Turns/groups support synchronized ripple removal; genuine overlap remains editable |
| G08 | Picture-delay cases introduce no speech loss, new lip-sync defects or accidental short flashes |
| G09 | Cancellation, recovery, missing assets, repeated runs, caches and moved/relinked output work safely |
| G10 | Exact compatibility matrix and a clean-install package check are complete |
| G11 | Local and live GitHub SHA match; intended worktree is clean; required CI passes |

Quality claims apply to the measured corpus. Candidate targets are 90% of independently labelled excessive handover gaps and 70% less repetitive editing effort. They remain unmeasured/unclaimed without suitable evidence and never justify sacrificing G04/G05. The timed owner exercise and mandatory usefulness sign-off are **retired by owner**, not passed. Missing manual/assisted seconds and subjective usefulness stay null; they are not delivery prerequisites.

## Scenario matrix
Two/three/six/eight or more tracks; silent participant; shared microphone; soft speech; varied accents/languages present in real work; short yes/mm-hm; multi-track laughter; overlap across a turn boundary; normalized handling noise; bleed/echo; long same-speaker pauses; pinned/gallery/camera-off video; delayed switches during silence and during speech; no detected activity.

Timing/files: actual production FPS plus fractional FPS; hundreds of cuts; off-frame boundaries; mixed sample rates and stereo files; shifted equal-duration audio; encoder padding; deliberately truncated audio; VFR; large file; spaces and Unicode; Windows drive and supported UNC paths; repeated runs and moved folders; unknown project structure.

Use deterministic synthetic tests for timing and public CI. Use private labelled excerpts for content retention and tuning. Keep held-out acceptance excerpts distinct from tuning data. Final checks include one complete two-person interview, one complete band interview and a two-hour stress fixture. Review all automated edits on the labelled excerpts, then targeted flagged moments and start/middle/end anchors on full interviews.

## Human review budget
Codex obtains repeatable technical and actual editor/render evidence and reuses still-matching prior observations. Routine listening assignments, annotation batches, duplicate comparison projects, timed repetitions and mandatory sign-offs are retired from normal delivery. Ask only for an unresolved editorial decision that materially changes an edit; give the existing playable project, edited timecode, options and conservative default. Unavailable subjective/independent evidence stays explicitly unmeasured and limits claims. Do not ask for existing media, a new comparison package, upload or connection.

## Evidence format
Record fixture ID, source provenance/consent status, exact versions, commit, configuration/model hashes, commands, pass/fail, timing/retention metrics and evidence path. Public evidence uses synthetic/anonymized identifiers and sanitized logs. Do not publish private recordings or transcripts with the report.
