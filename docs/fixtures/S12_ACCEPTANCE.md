**Historical evidence retained. Current continuation: [attempt 05 feedback](S12_SYNC_FEEDBACK.md); five pairs reported working, pair 2B rejected as unintelligible, source baseline unresolved.**

# S12 acceptance report - attempt 01, 29 October 2026

**Historical attempt 01.** The two-person input is now available. See the
[30 October attempt 02 report](S12_ATTEMPT_02.md) for current availability,
complete analysis, actual native input preparation, diagnostics and long-media
evidence. The measurements and unrun work below describe this earlier checkpoint.

**BLOCKED. Full-interview, held-out and automation-utility acceptance are NOT
RUN. S12 is not complete; S13 has not started.** This checkpoint adds independent
measurement tooling, runs engineering regressions and a two-hour contract/timing
fixture, and rechecks the real-input refusal. It does not waive missing evidence.

Implementation: **f73cd9247abd2c1b71ab9d1bc80398b7afd729c3**. Starting S11
completion checkpoint: **cd6da241f805c94511d6c51b150b399d5bbe5061**. See
[aggregate measurements](S12_ACCEPTANCE.json), [procedure](../project/S12_VALIDATION.md)
and [handover](../handovers/S12.md). Public identifiers describe synthetic inputs
or neutral corpus roles; private paths, source hashes, annotations and jobs stay
in ignored storage.

## Corpus availability and provenance

| Corpus role | Available evidence | Acceptance status |
|---|---|---|
| Complete two-person interview | Unavailable now; owner can provide it next time on this machine | NOT RUN |
| Complete band interview | One registered 34-minute recording, one video/four audio files; fresh read-only intake and saved-analysis planning refusal | BLOCKED: four unverified origins and unequal exact tails |
| Development content | Existing construction labels and bounded owner-reviewed overlap/TTS examples | Retained bounded evidence; no whole-interview claim |
| Independent held-out excerpts | No distinct registered/independently labelled acceptance corpus supplied | NOT RUN; no held-out audio opened or tuned |
| Long timing fixture | Eight generated source contracts, five sample rates, 599 cuts at each of two FPS | PASS for metadata/timing only |
| Full two-hour processing fixture | No two-hour source media decode/inference/picture/export/native run | NOT RUN |

The owner corrected the earlier raw-file description: supplied audio has received
the same volume leveling treatment intended for actual projects. This confirms
the intended processing provenance; do not level, normalize or denoise these
files again. Alignment and exact-tail evidence remain separate and unresolved.
The initial raw-file statement remains historical, superseded evidence. No media
processing, trimming, resampling or origin/status upgrade accompanied this
documentation correction.

## Actual denominators and limits

| Measurement | Observed result | Denominator/scope |
|---|---|---|
| Original preservation | 102 assertions pass; five unchanged sources; twelve sample-exact PCM excerpts | Existing registered source set/excerpts, not all possible recordings |
| Existing human-confirmed development overlap | 200/200 frames retained, zero gain spans, zero independently approved idle intervals | One eight-second envelope at 25 FPS; no precise per-word boundaries |
| Original real audio origins | 4/4 unverified, 4/4 verified offsets null | Fresh intake; original source records equal saved analysis |
| Original exact audio end minus video end | Three at -4/375 s, one at +4/375 s | Four complete WAVs at 192000 Hz; video domain 51092/25 s |
| Original real planning | 2/2 direct plans refused; fresh Application saved-analysis plan refused at planning | Fresh intake and existing fused analysis; no final project published |
| Long constructed content retention | 600/600 intervals per FPS, full exterior handles preserved | Constructed activity/protection intervals, not annotated human words |
| Long timing | 599 shared cuts per FPS; 9600 endpoint/sample-grid checks per FPS; zero cumulative map drift | Exact contract mapping; no rendered A/V measurement |
| Full/held-out word, acknowledgement, laughter loss | NOT RUN, denominator unavailable | No accepted independently labelled full/held-out output |
| Full/held-out deletion approval precision | NOT RUN, denominator unavailable | No independently labelled acceptance removals |
| Full-interview excessive handover coverage | NOT RUN, denominator unavailable | 90% remains a candidate target, not a result |
| Full-interview idle-noise reduction/click quality | NOT RUN, denominator unavailable | No actual accepted real output/listening comparison |
| Full-interview rendered sync/editability | NOT RUN | Real export correctly refuses |
| Manual baseline/assisted correction time | NOT RUN | No timed comparable editing task; approval/review time must be included |
| Repetitive editing effort reduction | NOT RUN | 70% remains a candidate target, not a result |
| New focused owner A/B/utility acceptance | NOT RUN | No valid real source/output pair; no new audio file/connection |

The new scorer has seven tests covering complete/partial labelled loss,
unlabelled removal, gain on independently labelled content, overlap of idle
labels, unknown denominators, source/split/configuration/analysis bindings,
held-out human-review requirements, strict records and private-safe exclusive
publication. Test partitions use generated identities; their reserved entry is
not a supplied real held-out corpus or acceptance run.

## Long fixture resources

Each row ran in a separate Python process, without competing long processing.
Rates are 16000, 44100, 48000, 96000 and 192000 Hz across eight generated sources.
The fractional duration rounds up to a common exact frame/sample endpoint.

| FPS | Source duration | Source/output/removed frames | Fixture + plan seconds | Total seconds | Peak process working set | Serialized plan bytes |
|---|---|---|---:|---:|---:|---:|
| 25 | 7200 s | 180000 / 20067 / 159933 | 3.905233 | 18.043987 | 39776256 bytes | 972605 |
| 30000/1001 | 7207.2 s | 216000 / 24869 / 191131 | 4.129377 | 19.216787 | 40132608 bytes | 972941 |

The largest single output-grid floor rounding is zero at 25 FPS and 7/120000 s
at fractional FPS, below one sample on its corresponding grid. It is bounded
absolute sample conversion, not accumulating drift. Two origin/tail mutations
are independently refused in each generated case. Total time includes strict
serialization/reload, turn building and checks. Peak working set covers the
whole process. No audio was decoded. These times/memory values are not a
full-interview CPU-inference throughput or resource-limit claim. Existing 8 MiB
contracts, 8192-frame picture budget, probe/decode limits and source bounds still
apply. The fresh real audit took 172.118 s while other checks ran; that is an
intake/refusal audit duration, not end-to-end interview processing time.

## Scenario matrix

All automated rows below run in the configured final suite. PASS means the
stated engineering scope only. Native build/track/FPS expansion belongs to later
steps and is not claimed here.

| Scenario | Engineering evidence | Real/full/native boundary |
|---|---|---|
| Two/three/six/eight or more tracks | S07/S08 media export tests pass at 1/2/3/6/8 audio sources; S12 long metadata uses eight | Actual native retained fixtures have two audio tracks; broader native matrix unrun |
| Silent participant/no activity | S04/S05 zero-audio safeguards, S06 identity, S07 full handles, S08 unity pass | No real silent-person accuracy claim |
| Shared microphone | S06 uncertain boundary, S07 inseparable groups, S08 unity and S09 fallback pass | No individual separation or recognition |
| Soft speech/yes/mm-hm | S04/S05 pinned CPU generated speech and acknowledgements pass | Varied real languages/accents/soft speakers unaccepted |
| Laughter/uncertainty | S05 additive protection, S06 every-event-kind union, S08 protected-source checks pass | Bounded prior human review only; independent full/held-out category labels absent |
| Overlap across turns | S07 raw-activity sweep/groups, S08 all-source veto and retained 200-frame development envelope pass | Whole-interview overlap completeness unmeasured |
| Handling noise/bleed/echo | S05 uncertainty/floor, S08 equal-grid correlation/overload safeguards pass | No automatic idle/silence certificate; real suppression precision unmeasured |
| Long same-source pauses | S06 Tight/Gentle thresholds/guards/approvals/Keep pass | Pace/naturalness calibration unrun |
| Pinned/gallery/camera-off/uncertain video | S09 restore-only fallback tests pass | Real layout recognition/accuracy unmeasured |
| Switch during silence | S09 narrowing of existing approved shared deletion passes | No independent picture clock |
| Speech at 12.00/picture at 12.45 | Exact 20-FPS math and decoder tests preserve all opening speech and original 0.45 s lag | Decoder test, not new native fractional/20-FPS certification |
| Short flashes/motion/edge ambiguity | S09 restore rather than truncate tests pass | No unseen Zoom accuracy claim |
| Fractional FPS/off-frame bounds/mixed rates/stereo | S03-S09 exact-grid, physical-channel and inward/outward rounding pass; S12 long cases pass | Broader fractional-FPS GUI unrun |
| Hundreds of cuts/turns/gains | Existing 500-cut/turn/gain tests and new 599-cut long contracts pass | Full two-hour media/native stress unrun |
| Shifted equal-duration inputs | Actual generated decode/correlation diagnostics and plan/export refusal pass | No shift applied or real alignment inferred |
| Encoder padding | Retained genuine GUI-render remeasurement passes declared padding bounds | Does not excuse original unequal PCM tails |
| Truncated audio/VFR | S03 physical WAV/PTS audits and exact-tail refusals pass | No automatic repair |
| Large source media | Existing complete band files rehashed/audited read-only | Long-media inference/resource/export acceptance unrun |
| Spaces/Unicode/Windows paths/moved package | S03/S07-S11 moved-package, mapping and same-depth edit-copy tests pass | Actual UNC/network publication unrun; integrated relocation/UNC export unsupported |
| Repeat/cancel/recovery/cache/missing assets | S04/S05/S10/S11 stage cancellation, corruption, locks, resume and no-overwrite pass | No power-loss/network/Linux durability certification |
| Unknown project structure | S03 reader and Application compatibility refusal pass | No arbitrary-project support |
| Complete two-person and band edits | Two-person unavailable; band planning refused as expected | Full acceptance NOT RUN |
| Distinct held-out interviews | Frozen split/source/configuration guard tests pass | Actual held-out evaluation NOT RUN |

## Actual Kdenlive evidence and acoustic measurements

No new Kdenlive open/play/group-edit/save/reopen/render operation occurred in
S12. Exporter, Application, desktop and core policies are unchanged. Exact
installed executable bytes still match the recorded production build; that is
not a fresh GUI operation. Prior genuine native evidence remains separated from
hand-authored construction files in
[S10 provenance](../../tests/fixtures/s10-cli-26.08.2/PROVENANCE.json).

A new explicit remeasurement of the retained S10 actual native/render package
passes **12/12 checks**. It measures 267/267 picture frames matching shared source
frames, one switch at output 105, eight protected tone probes within 0.1 dB,
four onset anchors at zero measured lag, four noise probes at -31.689, -43.766,
-33.858 and -33.836 dB relative to baseline, peak 0.476731, 384 AAC padding
samples and embedded-MP4 marker -227.711 dB. Native groups/guides/gains/routing,
25-frame three-member group movement and Undo match retained actual saves, with
zero sequence-extent delta. These are actual **synthetic artifact** measurements,
not a new GUI session, word-quality score or full-interview acceptance. Existing
S01/S02/S07/S08/S09 artifact remeasurements also remain in the full suite.

## Calibration, gates and disposition

No settings, thresholds, models, dependency pins, native adapter or origin/tail
policy changed. Tight/Gentle remain pacing hypotheses: different-group thresholds
0.8/1.2 s, residuals 0.25/0.5 s; same-group thresholds 1.5/2.5 s, residuals
0.5/0.9 s; minimum onset/tail guards 0.12/0.20 s override nominal residuals.
S08 retains -36 dB, at least 200 ms ramps, unity seam margins and conservative
headroom refusal. No tuning occurred, so no held-out rerun is presented.

| Gate | S12 engineering result | Full-interview exit status |
|---|---|---|
| G01 | Original preservation, references/MP4 exclusion regressions and retained render pass | No real output; not established |
| G02 | Historical actual native files/render remain valid; no new GUI operation | NOT RUN |
| G03 | Exact mapping/long contracts and retained synthetic rendered anchors pass | Real rendered sync NOT RUN |
| G04 | Existing labelled construction/overlap bounds retained; scorer detects injected loss | Full/held-out zero-loss gate NOT RUN |
| G05 | Existing explicit-approval rules and independent-label scorer pass | Actual acceptance denominator absent |
| G06 | Existing protected-gain/headroom tests and synthetic render noise checks pass | Real noise/click/listening gate NOT RUN |
| G07 | Group/turn/overlap/recovery regressions pass | Full-interview practical editability NOT RUN |
| G08 | Original picture timing/fallback regressions pass | Real full-interview picture acceptance NOT RUN |
| G09 | Application/desktop/cancellation/cache/recovery regressions pass; failed real staging retained | Full-interview long processing not established |
| G11 | Verify live local/upstream/remote equality, clean tree and exact-SHA CI at checkpoint | Final chat records actual result |

Final full suite: **231 tests, zero skips, 206.030 s** at the work commit.
Focused final suite: **7 tests, zero skips, 0.936 s**. An earlier full pass also
passed 231 tests in 214.168 s before report-provenance fields were added; the
final run tests those fields too. No failed result is hidden as a pass.

S12 remains blocked on missing complete two-person material, genuine origin/tail
resolution, independent held-out/acceptance labels and actual exported-output
metrics/owner review. Request the missing local material only when available;
do not ask for a connection, repeat the bounded S08 review or declare these
gates complete from synthetic results. Resume S12, not S13.
