# Release checklist

S14 prepares the release candidate and applicable technical acceptance. The owner-directed S12 revision retires the timed exercise and mandatory subjective usefulness/pace/usability sign-off; retired is not passed, and unknown quality/effort numbers remain unmeasured. S15 performs integration and release after explicit instruction to run S15. Do not publish a stable release during earlier steps.

- All required S00–S14 gates passed with real evidence; no material loss of speech, laughter or synchronization defect remains.
- Actual production Kdenlive 26 build tested; newest stable available 26 build checked if different; exact supported matrix published. Future builds clearly experimental until tested.
- Windows target/architecture confirmed, portable/installer package works on a clean machine, packaged runtime/models/dependencies are reproducible and licensed. No unsupported Windows-version claims.
- README, quick start, input setup, limits, recovery, restoring muted content, troubleshooting, privacy and compatibility update procedure are accurate.
- Dependency locks, model SHA256/licences, third-party notices and SBOM or equivalent inventory included. Record FFmpeg redistribution obligations for the chosen build. No paid code-signing requirement; state unsigned status honestly if applicable.
- No private interview data, credentials, transcripts, absolute private paths or development cache in source/package. Check unpacked assets, not only archive names.
- Release candidate artifact hashes correspond to the validated source commit. If merge integration changes that commit/tree, rerun affected gates and build the final assets from the actual release commit.
- Integrate to main through the permitted normal workflow and honor required reviews. Do not bypass branch protections.
- Confirm v1.0.0 is unused and appropriate; never move or replace an existing tag. Tag the exact accepted main commit. Publish release notes, package, checksums and provenance.
- Verify GitHub tag target and asset hashes, downloading/verifying assets where practical. Distinguish a draft release from a published release.
- Close state with product step completion, actual release tag/URL and implementation commit. If final handover documentation needs a later commit, identify release code SHA and documentation checkpoint SHA separately; do not pretend main HEAD must equal the release tag forever.
- Sync final main and any retained development branch coherently; no leftover uncommitted work. Include a verbose final handover and a maintenance continuation prompt. Do not invent S16 or automatically begin post-release work.
