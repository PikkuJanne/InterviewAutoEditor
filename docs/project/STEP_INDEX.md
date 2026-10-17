# Step sequence

One named step per thread. Every step includes its GitHub checkpoint and verbose handover.

| Step | Work | Dependency |
|---|---|---|
| [S00](steps/S00.md) | Bootstrap and preserve existing work | None |
| [S01](steps/S01.md) | Capture Kdenlive 26 reference fixtures | S00 |
| [S02](steps/S02.md) | Prove editable Kdenlive 26 export | S01 |
| [S03](steps/S03.md) | Validate media timing and define exact data contracts | S02 |
| [S04](steps/S04.md) | Implement cached per-participant speech analysis | S03 |
| [S05](steps/S05.md) | Protect laughter overlap and uncertain sounds | S04 |
| [S06](steps/S06.md) | Build the shared pause-removal planner | S05 |
| [S07](steps/S07.md) | Export clear speaker turns and grouped edits | S06 |
| [S08](steps/S08.md) | Apply reversible idle-microphone cleanup | S07 |
| [S09](steps/S09.md) | Account for recorded Zoom picture switches | S08 |
| [S10](steps/S10.md) | Complete the recoverable CLI pipeline | S09 |
| [S11](steps/S11.md) | Build the minimal desktop workflow | S10 |
| [S12](steps/S12.md) | Validate full interviews and calibrate quality | S11 |
| [S13](steps/S13.md) | Verify compatibility and prepare future upgrades | S12 |
| [S14](steps/S14.md) | Package and accept the release candidate | S13 |
| [S15](steps/S15.md) | Integrate publish and close the project | S14 |

Read the exact step brief for deliverables and exit gates. A blocked step is resumed rather than skipped. S15 ends the implementation sequence.
