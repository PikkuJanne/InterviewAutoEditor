# Next step: S01 only

S00 — Bootstrap and preserve existing work — has passed its technical gate.
The next chat should execute **S01 — Capture Kdenlive 26 reference fixtures**
only, after verifying the live S00 Git checkpoint. S01 has not started.

- Branch: `codex/kdenlive26-overhaul`.
- Implementation commit: `32cdc719e943378e004e4759dd233109876349a0`.
- Latest handover: [docs/handovers/S00.md](handovers/S00.md).
- Durable state: [docs/project/STATE.json](project/STATE.json).
- Selected brief: [docs/project/steps/S01.md](project/steps/S01.md).
- Public inventory: [docs/project/BOOTSTRAP_INVENTORY.md](project/BOOTSTRAP_INVENTORY.md).

Read the handover's exact continuation prompt and the execution/GitHub protocols.
Resolve the final S00 documentation checkpoint with
`git log -1 --format=%H -- docs/handovers/S00.md`, then compare current HEAD
with live `origin` using `python tools/verify_checkpoint.py --repo .`.
The final chat records the actual pushed SHA; this file does not embed its own
containing commit. A failed sync overrides this next-step selection: resume S00
until the checkpoint is synchronized. Preserve any newer work; do not reset.

S01 prerequisites: independently confirm the reported Kdenlive 26.08.2 build,
create genuine sanitized fixtures, and locate a real starter project, Zoom MP4
and cleaned aligned participant audio. No input media locations are supplied yet.
The executable exists but application tests remain NOT RUN. Machine-local
paths/runtime and input availability are in ignored `.local/S00-inputs.json`.

Do not reinstall the bundle or begin audio-engine/GUI implementation.
