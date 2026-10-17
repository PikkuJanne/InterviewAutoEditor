# Resume S01 only — real inputs still required

S01 — Capture Kdenlive 26 reference fixtures — is **BLOCKED**, with useful
synthetic capture work preserved. Do not begin S02.

- Branch: `codex/kdenlive26-overhaul`.
- S01 implementation commit: `1d81a245a4a5986ecbfe4fff7d341b84d2ebcf78`.
- Latest handover: [docs/handovers/S01.md](handovers/S01.md).
- Durable state: [docs/project/STATE.json](project/STATE.json).
- Selected brief: [docs/project/steps/S01.md](project/steps/S01.md).
- Capture evidence: [docs/fixtures/S01_CAPTURE.md](fixtures/S01_CAPTURE.md).

The installed build is independently confirmed as Kdenlive 26.08.2 rev. d4e87e4.
Three genuine GUI-created, sanitized synthetic projects and media are under
`tests/fixtures/kdenlive-26.08.2/`. The comprehensive two-participant fixture
passed actual open/play/group-edit/undo/save-copy/close/reopen/GUI-render checks,
plus moved-folder opening. The semantic timeline survived; the render preserves
300 video frames and excludes the embedded marker in the measured window. This
is reference evidence, not a product exporter or real-interview acceptance.

**Missing:** the owner's real starter `.kdenlive`, source Zoom MP4, aligned
cleaned participant files and private sample excerpts. Supply their local
project/media-folder location. No unrelated personal storage was searched.
Ignored `.local/S01/private-corpus-index.json` retains capture paths and empty
real-input slots. `.local/S00-inputs.json` records the runtime/install. Actual
production profile, N, starter structure and synchronization assumptions remain
unchecked. The broader GUI fixture matrix and native clip-gain edge evidence
remain pending; see the handover.

At the next chat start, read the handover continuation prompt and execution/GitHub
protocols. Resolve its containing checkpoint and verify live synchronization:

```powershell
git log -1 --format=%H -- docs/handovers/S01.md
python tools/verify_checkpoint.py --repo .
```

Inspect newer work, compare local HEAD with live origin, and verify upstream and
a clean intended worktree. Failed synchronization must be finished on S01 first.
The final chat records the pushed documentation SHA; this file does not embed
its own containing commit. Preserve existing work and failed-attempt evidence.

Resume S01 to obtain/check real inputs and complete its exit gate. No importer,
exporter, audio engine, models, application GUI or S02 work was started.
Commit/push/verify/handover and STOP again at the S01 boundary.
