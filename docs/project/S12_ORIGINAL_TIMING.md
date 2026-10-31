# S12 original timing and unequal endings

The production `export` / `run` path now accepts an explicit schema-2
`PlannerRequest`. It preserves supplied source clocks and uses the
`original_timing_with_gaps_v2` EditPlan policy. Schema 1 remains unchanged: it
still requires verified origins and exactly equal coverage.

The original rejection is on the normal path: `cli.main` calls
`Application.run`, which reads `PlannerRequest` and calls `Application.plan` /
`plan_pauses`. The planner constructs `EditPlan` before making decisions. Its
schema-1 origin check rejects the unchanged unverified audio; even a verified
origin cannot satisfy the subsequent unequal-tail check. The fix is an explicit
policy in that same planner/contract/adapter path. Legacy commands retain their
schema-1 default; the ordinary `edit` command selects schema 2 without a request file.

Schema 2 does **not** certify an unknown origin or turn an unset measured offset
into zero. It places each original source at the starter's original zero, keeps
the Analysis record unchanged and refuses nonzero source placement. Every
original sample remains addressable. The shared frame domain ends at
`ceil(max(source duration) * fps)`; a participant or picture stops at its own
EOF. Missing picture is a blank with a native timeline guide. No source is
trimmed, stretched, shifted, levelled or frozen to fill coverage. The final
partial audio frame remains included; padding to the project frame boundary is
empty coverage, not invented recording.

An approved global removal still uses **one** source/output map for picture and
all participant tracks. Keep/audible overrides are in original source time.
Gap approval and participant idle-microphone approval remain separate and bound
to the exact Analysis and refined result. A positive sync judgment grants
neither. Schema-1 approvals are not silently migrated or rebound.

Use the normal command with a new destination and an explicitly reviewed v2
request. The request has the same fields as v1 apart from `schema_version: 2`;
the supplied analysis digest must match its exact unchanged Analysis. See
[CLI usage](S10_CLI.md). Real requests, commands, hashes and approvals are kept
in private run ledgers. Exit code 2 means completion requiring review, not an
alignment certificate.

## Kdenlive representation

The adapter shares one timeline media producer per original source rather than
opening another decoder at every aligned group boundary. Source clips carry
`eof=continue`; explicit playlist blanks represent missing coverage. The MP4's
audio remains disabled. Turn groups retain source bounds and a shared map.
The native timeline shows coverage and approved-seam guides; detailed model
turn/picture observations remain in the private report.

Already levelled participant media are kept byte-for-byte. Their unity sum can
overload a mix. V2 therefore uses the same fixed **native master fader** rule for
every N-track project: linear `0.95 / N`, or `20 log10(0.95 / N)` dB. This is a
reversible output mix setting, not a second source-normalization pass or a
held-out fit. Relative microphone levels stay unchanged. Any approved
participant gain automation remains separately constrained. Planned headroom
does not substitute for measuring the actual render.

V2 preserves a starter's native profile reference. If it names a local profile
file, Application hashes it as an input and the adapter checks its dimensions,
rate, scan, aspect and colour-space fields against the inline project profile.
A changed or inconsistent profile refuses. This lets the actual installed
Kdenlive renderer select the original custom profile instead of falling back to
an empty/default profile.

## Complete recorded-picture observation

PictureRequest version 2 scans the selected **actual video stream**, including
an audio-first MP4 whose picture is absolute stream 1. It covers the full
recorded video with bounded overlapping windows and disk-spooled gray frames;
the overall v2 limit is 1,000,000 frames. Per-window limits remain. The union of
observed intervals and the explicit unobserved complement are in the report.
Missing recorded observation refuses refinement; missing picture after real
video EOF is reported separately. Version 1 retains historical bounded
handover-only semantics.

Integer picture-change rules and thresholds are unchanged. Full-span window
selection and stream routing fix observation coverage; they are not calibration
on held-out content.

## Verification and limits

`tools/test_s12_production_coverage.py` exercises the normal CLI for equal
endings, audio first and picture first, including the last real sample/frame,
explicit blanks, shared removals/restoration and stale approval rejection.
`tools/test_s12_picture_span.py` covers an actual synthetic audio-first MP4,
full-span coverage, incomplete-observation rejection and equivalence of the
optimized calculation to the original integer measurements.

Current real results belong in the
[production audit](../fixtures/S12_PRODUCTION_COVERAGE.md). Synthetic checks,
project-file checks, actual Kdenlive actions and human listening are separate
evidence. Neither zero automatic removals nor missing independent labels proves
90% pause automation or 70% effort reduction. The timed owner exercise is retired
by owner; see the revised S12 brief and current handover for applicable completion
checks. Unknown accuracy, timing offsets and subjective usefulness stay unset.
