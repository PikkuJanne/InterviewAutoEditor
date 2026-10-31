# S00 bootstrap inventory and decisions

Observed on 17 October 2026. This record describes bootstrap evidence only.

## Repository and preserved work

The intended workspace initially contained one local background roadmap document
and no `.git` directory, application source, tests, project instructions, state,
handover or media. No applicable parent `AGENTS.md` was found. A name-scoped check
of the immediate projects directory found no other InterviewAutoEditor workspace;
this is not a claim that the whole computer contains no predecessor code.

Live GitHub inspection found public `PikkuJanne/InterviewAutoEditor`, default
branch `main`, at `0c445a400c96b1f85f17fcb0ee8916d283e22d6f`. Its only tracked
file was `LICENSE`; there were no other branches, tags, open pull requests,
Actions workflows, workflow runs or repository rulesets. `main` was reported
unprotected. The historical bundle baseline happened to match; it was not used
to reset anything.

Initialized Git in the existing workspace, fetched the real remote and created
`codex/kdenlive26-overhaul` from `origin/main`. No existing work was reset,
stashed, deleted or overwritten. The original MIT license remains byte-identical
to the baseline (SHA256
`e4ed5c06dbf973cf3af0155de72915214e4c5bc7de211c601816b7e083f1dae3`).

The local background document was retained in place, byte-identical to the
bundle's reference copy (SHA256
`095f9b3a47c67c4cd7f9dd15518168e03b17b85e77340afa3883032cb99b36d6`).
A repository-local `.git/info/exclude` entry keeps it outside the public
checkpoint. No document content was published. There is no existing editor code
in this workspace or on inspected `main` to reuse. The roadmap remains background;
the current user request and accepted bundle specification govern implementation.

## Bundle adoption

Source: InterviewAutoEditor Codex Kdenlive26 bundle, revision 1. Archive SHA256:
`74780ac285331f36c68b8ed5ddddae1d0a3ae25c8cdaf2983c6f8cd260cea59a`.

Read `START_HERE.md` and the overlay `AGENTS.md` before repository mutations.
Extracted outside the repository, checked archive entry containment, and ran
the supplied `VERIFY_BUNDLE.py`: **PASS**, 16 steps, 59 files verified, zero
errors. This establishes bundle integrity, not application correctness.

After inspecting the workspace and live GitHub, preflighted every overlay target:
all 35 paths were absent. Copied those paths only; there were no merge collisions.
Preserved the license and original background document. Added a README explaining
planned behavior, this inventory and the S00 handover/state checkpoint. The ZIP,
bootstrap prompts and background document are not application source and were
not installed into tracked project paths. Future chats use repository state,
without reinstalling the overlay.

The supplied checkpoint helper and local-bare-repository tests are reused.
S00 hardens malformed-state handling with focused regression tests. No audio
engine, adapter implementation, model package or application GUI is introduced.

## Git transport and identity

Requested SSH identity: `git@github.com:PikkuJanne/InterviewAutoEditor.git`.
Both initial SSH ref queries failed with `Permission denied (publickey)`.
The existing GitHub CLI login had repository push permission and a configured
HTTPS credential helper. The permitted equivalent origin is
`https://github.com/PikkuJanne/InterviewAutoEditor.git` for fetch and push.
No SSH keys, credentials or global Git settings were changed.

Repository-local commit identity uses the existing account login and its GitHub
noreply email. Repository-local `core.autocrlf=false` preserves the overlay's LF
text. No stable branch, tag, release or pull request is created or changed by S00.

## Environment and private inputs

- Platform observed: Windows NT `10.0.26300.0`, PowerShell `7.6.5`,
  Git `2.56.0.windows.1`. This is an environment observation, not a supported
  Windows-version claim for a future package.
- GitHub CLI: `2.97.0`.
- Bootstrap Python: `3.12.14`, using the existing bundled runtime. No Python or
  model dependencies were installed. Future product/runtime selection remains open.
- Owner-reported production target: Kdenlive `26.08.2`. The expected installation
  directory and executable exist. Windows executable version fields were empty;
  the application build has **not** been independently confirmed.
- No starter `.kdenlive` project, Zoom MP4 or cleaned participant audio location
  was supplied or found in the intended workspace. No search of unrelated
  personal storage was performed. These inputs are prerequisites for S01.

Machine-specific paths and input availability are recorded in ignored
`.local/S00-inputs.json`. Recheck that file on this machine; its content does not
travel with a clone. Real media stays outside public Git. Ignored cache files and
the preserved background document do not count as uncommitted project work.

## Limits and continuation

S00 establishes planning, preservation and checkpoint tooling only. Kdenlive
open/play/group-edit/undo/save/reopen/render, fixture provenance, timing,
content retention and audio quality checks are **NOT RUN**. Adapter architecture
is specified, not implemented or tested. The compatibility matrix remains
untested for all builds, including 26.08.2 and upcoming releases.

S01 must confirm the actual build, create genuine sanitized fixtures and locate
the private starter/sample inputs. Their absence does not block S00. The S00
handover records actual bootstrap verification and the exact next-thread prompt.
