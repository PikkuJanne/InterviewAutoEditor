# S11 focused desktop workflow recording

Observed on Windows AMD64, 29 October 2026, using Python 3.12.14 / Tk 8.6,
local FFmpeg/ffprobe 8.1.1 and Kdenlive 26.08.2 rev. d4e87e4. This is a textual
action/observation recording, not a fabricated video or screenshot. Raw UI
observations contained local paths and are not published. Sources are the
existing shareable [S09 synthetic package](../../tests/fixtures/s09-picture-26.08.2/README.md)
and [S10 gap request](../../tests/fixtures/s10-cli-26.08.2/planner-request.json).
Construction provenance remains distinct from actual application operations.

| Action through the desktop | Observed result |
|---|---|
| Launch desktop, inspect high-DPI layout | Project picker, participant table, pacing, records/setup, output, review and controls visible; status/cancel layout corrected during this check. |
| Load synthetic example | Two neutral participant files, explicit p0/p1 identities and original channel labels; reviewed construction records selected. Mapping confirmation remains unchecked. |
| Confirm mapping, opt in to experimental export, enter new private destination | Both opt-ins are visible. No terminal command is needed to configure or run the project. Local tools were already installed and supplied to the process environment. |
| Start Create editable project | Form becomes disabled, indeterminate progress and Preparing local inputs are visible, Cancel remains enabled. Service transaction completes. |
| Inspect completed review | Run complete with review required; origin diagnostics retained. Global source gap [4,7) and shared seam 21/5 seconds are shown, with picture observations. |
| Open copy in Kdenlive | A new sibling editable copy is created; validated run is preserved. A second actual Kdenlive instance opens that copy without repair/missing-media prompts. Original media remain in the bin; one video/two named audio tracks and native Volume spans are visible. |
| Play in Kdenlive | Playback advances to 00:00:09:16 and finishes at 00:00:10:16, the final displayed frame of the 267-frame output. This is visible playback, not a new human content/listening acceptance. |
| Open Keep/Restore; enter source p1, start 4, end 7; Apply | Dialog closes; pending source-time overrides count is 1. UI explicitly requires a NEW destination and reviewed/rebound or cleared cleanup. The completed run is unchanged. |

Computer-use tooling initially rejected the registered Python window with a
same-owner binding error. A private, unchanged copy of the **already installed**
Python runtime executable/DLLs under a distinct process name allowed observed
interaction. No acquired software, dependency, system association or security
setting was changed. That local verification helper is ignored and does not ship.
Kdenlive startup took time while CPU regression tests ran; process creation alone
was not counted as successful opening. The actual project window was observed.

This visible pass preceded final presentation refinements: rational picture
coordinates now display as fractions instead of serialization dictionaries,
diagnostic identities occupy the review column, complete reasons have a detail
dialog, initial size is screen-bounded, and idle close cancels polling callbacks.
The final-code Tk integration test separately drives Start, polls its real worker,
verifies completion/open state and checks the final formatted picture rows.

Automated focused checks additionally exercise six stage cancellations and
explicit unchanged resume, altered-input/repeat refusal, missing/invalid assets,
artifact corruption before review/launch, exact Keep/audible restoration and
stale cleanup refusal followed by explicit unity export. UI mapping tables scroll
and edit at 8/64 rows; these are row-scaling checks, not 64-source media exports.
The unchanged core's 1/2/3/6/8-source export gates remain separate.

No export implementation changed, so a new full group-edit/save/reopen/render
cycle was not required or performed in S11. The prior genuine
[S10 full regression](../../tests/fixtures/s10-cli-26.08.2/PROVENANCE.json)
and actual render are retained and remeasured by the full suite. S11's new
Kdenlive result is explicitly **open/play**, not a relabelled full regression.
Full manifests/desktop jobs contain machine paths and remain ignored/local;
aggregate public evidence contains only reviewed neutral metrics.
