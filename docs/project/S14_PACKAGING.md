# S14 portable candidate build and validation

The builder is offline and uses only reviewed tracked source plus explicitly
provided hash-pinned archives/models/wheels. No system installation, global
execution-policy change, pip invocation or development-venv copy occurs.

Acquire the runtime install-only archive identified by
`third_party/s14-runtime.json` through its exact upstream URL. Verify its size
and SHA256. Retained licensing metadata was extracted from the separately
hash-verified full archive; upstream `PYTHON.json` declares applicable native
links/licences. Obtain the 16 wheels in the S04/S05 inventories using the two
`--require-hashes` locks and explicit setup, and the two models from their
existing exact hash manifests. Downloads are a setup operation; the builder
and the user application never fetch anything.

From a reviewed clean tracked commit, with Python 3.12 and Git:

```powershell
python -B tools/s14_package.py --runtime '<pinned install_only.tar.gz>' --wheels '<all 16 locked wheels>' --speech '<silero_vad.onnx>' --reaction '<yamnet.tflite>' --output '<new candidate output directory>'
```

The runtime is CPython 3.12.16 Windows AMD64 from python-build-standalone
20261026. It intentionally differs from the development Python 3.12.14.
The builder verifies all binary input hashes, refuses unsafe paths, archive
links, file collisions and nonempty/existing output, and includes only the
reviewed tracked application/documentation/notices allowlist in the runnable
ZIP. The complete tracked source ZIP is separate. Neither archive includes
ignored local evidence, sources, caches or recordings.

Outputs are `InterviewAutoEditor-1.0.0-rc.1-windows-x64.zip`, matching
`-source.zip` and `SHA256SUMS.txt`. The runnable ZIP includes source `.py` files,
the full per-file `PACKAGE.json` inventory, binary input hashes/source commit,
model manifests/licences, runtime licence inventory, wheel notices, both locks,
quick start, limitations, recovery and release notes. Kdenlive/FFmpeg are not
copied. No code signing is claimed or required. `-I -B` starts bundled Python
without system/user Python path configuration or new bytecode caches; the
bootstrap supplies package-relative model/Tcl paths and a private per-user cache.
User `IAE_...` tool/model/cache choices retain their documented behavior.
The Microsoft Visual C++ x64 v14 runtime is a separate prerequisite. A fresh
Sandbox exposed the missing `msvcp140.dll` dependency; the launcher now names it
clearly. Its official tested installer is pinned in `third_party/s14-runtime.json`
but not redistributed. Installing that prerequisite can need administrator
permission; the portable app itself does not. No host system DLL is copied.
The first host run also exposed MSIX redirection of a newly created LocalAppData
cache. Run identity now binds the cache's stable absolute logical location.
Cache entry source/model/settings checks and all source/tool/model/code file
fingerprints remain intact. Historical complete runs remain readable; partial
runs from changed implementation bytes still require a fresh destination.

The ZIP uses sorted names, fixed timestamps, regular-file modes and deflate
level 9. Two builds from the same source/binary inputs must have identical
archive hashes on the recorded builder Python/zlib toolchain. This is a
reproducible assembly, not a claim to independently rebuild upstream native
binaries. Source inputs include the actual source commit; a later documentation
checkpoint does not retarget the built artifacts. S15 must rebuild after main
integration and validate the actual release commit, if it differs.

Validation must cover a complete fresh extraction, file inventory, model CPU
inference, Tk creation, no system Python/pip, starter-only normal generation,
missing-input failure/recovery, unchanged inputs, relocation, the desktop and
actual supported editor. A fresh Windows Sandbox/VM is separate evidence from
same-host isolation. Never label a host-only smoke test as a clean machine.
Keep the original complete interviews and their accepted native/render evidence;
rerun affected exporter/media checks if their code or semantics change. The
retired owner exercise/usefulness sign-off remains retired, not passed.

Exact executed checks, failures and limitations belong to
`docs/fixtures/S14_RC_VALIDATION.json` and `docs/handovers/S14.md`. Candidate
archives are local ignored artifacts until the S15 publication step. S14 must
not tag, merge main or publish a stable release.
