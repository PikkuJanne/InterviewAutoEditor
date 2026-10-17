# Kdenlive 26 and future compatibility policy

## Primary target
Kdenlive 26.x is the product target, not a generic older XML template. In S01 record Janne's exact installed 26.x.y, platform, bundled MLT/Qt/FFmpeg information where available, and the project document version/schema features observed in files saved by that build. Do not invent a patch number or treat application version, document version and MLT version as interchangeable.

At release, verify the actual production build and the latest stable available 26.x build if different. If promising a wider range, test its oldest supported build as well. Do not claim all 26.x patches solely from testing one build. Older pre-26 support is outside the initial goal unless the user requests it.

## Adapter boundary
Keep analysis and the canonical edit plan independent of Kdenlive. Use a registry of format adapters selected by observed document structure/capabilities and tested version information. The parser reports unsupported timing-critical structures before mutation. Keep effect IDs, sequence/bin references, clip group serialization, guides, track wiring, audio-disable rules and time conversion inside the adapter.

Use genuine saved-project fixtures for each tested format/build. Do not hard-code a presumed document version (such as 1.1) from historical documentation. Compare semantic structure after opening and saving; volatile IDs, dates, paths and UI state should not cause meaningless byte-equality failures. Preserve known harmless metadata; do not blindly copy unknown references into a rebuilt timeline.

## Compatibility states
| State | Meaning | Export behavior |
|---|---|---|
| Tested | Required round-trip and render evidence exists for the declared build/platform | Normal export |
| Experimental | Recognized structure but no complete evidence for this build | Explicitly labelled opt-in export to a new copy, plus required review |
| Unsupported | Unknown/unsafe structure or a demonstrated failing capability | Analysis/report may run; project export stops with a precise reason |

A future version with a familiar schema is not automatically rejected solely because its version starts with 27 or later, nor automatically accepted as tested. Classify it using structure and evidence. Do not rewrite its document-version string to pretend it is older. Never silently downgrade a newer project or overwrite it.

## Regression fixtures
Cover a starter project, video-only use of MP4, 2/3/6/8 participant tracks, linked input audio, two aligned cuts, group deletion, overlap, one guide, native gain edges, and any chosen derived-PCM fallback. Include Windows paths, relative paths and fractional frame rates. Record fixture provenance, creation build, sanitization and source hash.

For each declared version: open -> play -> edit a group -> undo -> save as a copy -> close -> reopen -> render -> compare semantic timeline and A/V anchors. MLT-only rendering and headless tests do not replace actual Kdenlive interaction. If the environment cannot run the GUI, report NOT RUN and retain the gate.

## New-version maintenance
Provide an on-demand compatibility probe command and a documented procedure. Add fixtures for a new stable version, compare schema/features, implement a new adapter or capability handling if needed, and repeat the round trip. A prerelease/nightly can be a non-blocking canary when available. Its absence does not block v1. Do not create scheduled jobs or recurring tasks unless separately requested.

Update docs/COMPATIBILITY.md with exact versions, status, commit, evidence and known limitations. Changes to the exporter require regression on the primary 26 build. Keep edit-plan schema migrations explicit so cached plans remain useful as Kdenlive changes.

Future-proofing means replaceable adapters, portable plans, evidence and safe failure. It cannot guarantee unknown future formats.
