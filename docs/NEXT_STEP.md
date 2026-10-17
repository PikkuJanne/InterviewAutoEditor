# S02 next — prove editable Kdenlive 26 export

S01 — Capture Kdenlive 26 reference fixtures — is **COMPLETE** after its second
attempt. Execute **S02 only** in the next chat, after verifying this checkpoint.

- Branch: `codex/kdenlive26-overhaul`.
- Relevant unchanged S01 code commit: `1d81a245a4a5986ecbfe4fff7d341b84d2ebcf78`.
- Latest handover: [docs/handovers/S01-attempt-02.md](handovers/S01-attempt-02.md).
- Durable state: [docs/project/STATE.json](project/STATE.json).
- Next brief: [docs/project/steps/S02.md](project/steps/S02.md).
- Evidence: [synthetic capture](fixtures/S01_CAPTURE.md),
  [real-input observations](fixtures/S01_REAL_INPUTS.md).

Kdenlive 26.08.2 rev. d4e87e4 is independently confirmed. Three genuine sanitized
synthetic references exist; the two-participant grouped fixture passed actual
open/play/group-edit/undo/save/reopen/GUI-render checks. A private native starter
created from the owner's supplied MP4/four cleaned WAVs passed play/save/reopen
and save-copy. There was no existing owner project in the supplied media folder.
The ignored corpus index now locates the real starter, original media, mapping,
source hashes and exact private PCM excerpts. Read that index locally; never
copy its names, paths or media into public records.

S01 intake does not certify synchronization. WAVs are stereo 192 kHz/16-bit PCM;
three are 4096 samples shorter than the longest. All native entries cover 51092
frames at 25 FPS, with subframe source-tail differences. Reopen/save grew the
sequence range by one frame while clip entries stayed unchanged. Limited signal
spots have differing subframe correlation peaks. Preserve these findings for
S02/S03; do not silently slide audio, retime picture or discard tails.

S02 builds only the minimal reader/adapter and one manually specified interior
cut, with a new editable project, N named audio tracks, MP4 audio excluded, a
group and guide. Prove G01/G02 in the actual installed application, including
native gain edges and a short GUI render. No automatic speech/pause decisions.
Product compatibility remains EXPERIMENTAL. Broader GUI count/fractional/UNC
matrix evidence remains pending before tested compatibility is declared.

At the next chat start, read the handover, selected brief and execution/GitHub
protocols. Resolve the handover's containing commit and verify live state:

```powershell
git log -1 --format=%H -- docs/handovers/S01-attempt-02.md
python tools/verify_checkpoint.py --repo .
```

Inspect newer work, compare local HEAD with live origin, and verify upstream and
clean intended worktree. A failed sync must be finished on S01 first. The final
chat records the pushed SHA; this file does not embed its own containing commit.

Ready-to-paste prompt:

> Execute S02 only in the existing InterviewAutoEditor checkout on
> codex/kdenlive26-overhaul. Read AGENTS.md, docs/project/STATE.json,
> docs/NEXT_STEP.md, docs/handovers/S01-attempt-02.md, the execution/GitHub protocols
> and docs/project/steps/S02.md. Verify the live checkpoint before editing.
> S01 code is 1d81a245a4a5986ecbfe4fff7d341b84d2ebcf78; resolve the latest
> documentation SHA from Git history. Use the genuine public references and the
> ignored private corpus index. Build the minimal adapter and one manual shared
> interior cut; prove editable native open/play/group-edit/undo/save/reopen/render,
> MP4-audio exclusion and gain-edge behavior. Retain the documented native
> sequence/tail findings. Do not start automatic analysis or S03. Commit, push,
> verify live SHA equality and clean status, inspect exact-SHA CI, provide a
> verbose handover and STOP.
