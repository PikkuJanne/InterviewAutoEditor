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

Quality claims apply to the measured corpus. Candidate targets: automatically shorten at least 90% of labelled excessive handover gaps and reduce repetitive editing effort by 70%. Measure denominators and manual correction time. These targets never justify sacrificing G04/G05 and are not claimed results.

## Scenario matrix
Two/three/six/eight or more tracks; silent participant; shared microphone; soft speech; varied accents/languages present in real work; short yes/mm-hm; multi-track laughter; overlap across a turn boundary; normalized handling noise; bleed/echo; long same-speaker pauses; pinned/gallery/camera-off video; delayed switches during silence and during speech; no detected activity.

Timing/files: actual production FPS plus fractional FPS; hundreds of cuts; off-frame boundaries; mixed sample rates and stereo files; shifted equal-duration audio; encoder padding; deliberately truncated audio; VFR; large file; spaces and Unicode; Windows drive and supported UNC paths; repeated runs and moved folders; unknown project structure.

Use deterministic synthetic tests for timing and public CI. Use private labelled excerpts for content retention and tuning. Keep held-out acceptance excerpts distinct from tuning data. Final checks include one complete two-person interview, one complete band interview and a two-hour stress fixture. Review all automated edits on the labelled excerpts, then targeted flagged moments and start/middle/end anchors on full interviews.

## Human review budget
Prepare a short A/B comparison with timecodes for pace and naturalness, and a focused final acceptance review. Automate repeatable checks. Do not demand broad manual testing after every coding step. Actual listening/GUI evidence that the environment cannot obtain remains explicitly NOT RUN; ask only for that precise necessary action.

## Evidence format
Record fixture ID, source provenance/consent status, exact versions, commit, configuration/model hashes, commands, pass/fail, timing/retention metrics and evidence path. Public evidence uses synthetic/anonymized identifiers and sanitized logs. Do not publish private recordings or transcripts with the report.
