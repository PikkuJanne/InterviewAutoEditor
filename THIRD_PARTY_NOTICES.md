# Model and runtime provenance

## S14 portable candidate

The candidate bundles unchanged model bytes and the 16 locked S04/S05 wheels
listed below, with their complete wheel metadata/notices. `PACKAGE.json` is the
per-file SHA256 inventory, including every native DLL/PYD and model. Exact
wheel source bytes are pinned by both locks and the S04/S05 inventories.
No development virtualenv, ESC-50 audio, TTS voices or private recording is
bundled. The application's original MIT licence is unchanged.

The new portable CPython **3.12.16** runtime is Astral
[python-build-standalone release 20261026](https://github.com/astral-sh/python-build-standalone/releases/tag/20261026),
Windows x86_64 MSVC. [The package lock](third_party/s14-runtime.json) pins the
install-only archive and the full upstream archive used to retrieve licensing
metadata. `third_party/python-runtime/PYTHON.json` retains the original
component/link/licence inventory; `third_party/python-runtime/licenses/`
retains all supplied notices (a superset including non-Windows components).
The runtime's own `LICENSE.txt` and Tcl/Tk notices are also retained. Its native
binaries are unmodified; omitted development/pip/debug files are documented
in the lock. The CPython source/build scripts remain available through the
upstream release. This differs from the development interpreter and is tested
separately. Python, Tcl/Tk, OpenSSL, libffi, SQLite, bzip2, lzma and compression
notices are preserved; exact applicable upstream licences are in that metadata.
Microsoft VC runtime DLLs retain their upstream bytes/copyright; the associated
[Microsoft runtime terms](https://visualstudio.microsoft.com/license-terms/vs2022-cruntime/)
are retained in `third_party/python-runtime/Microsoft-Visual-Cpp-Runtime.txt`.
The model runtime also needs Microsoft's separately installed Visual C++ x64
v14 prerequisite (`msvcp140.dll`). The tested official installer version/hash
is recorded in the S14 lock, but neither that installer nor a copied system
DLL is redistributed. Microsoft's
[redistribution terms](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files)
are separate from permission to install/use its official prerequisite.

**No Kdenlive or FFmpeg binary is redistributed.** The candidate invokes the
user's separate local installation. Its tested decoder is Kdenlive's FFmpeg
8.1.1 build. FFmpeg licensing depends on the actual configuration, including
optional GPL components; see [FFmpeg's upstream licence description](https://www.ffmpeg.org/legal.html).
Do not describe every FFmpeg build as LGPL or copy its binaries into a release
without the corresponding notices/source/distribution review. Selecting an
external installed decoder avoids that binary redistribution in this candidate.
Kdenlive remains a separately installed editing prerequisite.

The historical S04/S05 paragraphs below describe the original source-development
checkpoints. Their "not bundled" statements apply to those earlier checkpoints;
the S14 candidate inventory above describes current binary packaging.

S04 uses **Silero VAD v5.1.2**, upstream revision
`6478567951ae5c9979ad7b234185b5515f4be7a1`, unchanged ONNX bytes, under the
MIT licence. The exact source URL, SHA256, size, interface and licence hash are
in [the model manifest](third_party/silero-vad-model.json); the full upstream
[MIT notice](third_party/silero-vad-LICENSE) is retained. The
[upstream wrapper](https://github.com/snakers4/silero-vad/blob/6478567951ae5c9979ad7b234185b5515f4be7a1/src/silero_vad/utils_vad.py)
documents its recurrent state and context. This implementation calls ONNX
directly; it does not install PyTorch, torchaudio or the Silero Python package.
This is an intentionally fixed tested model, not a claim to use the latest model.

The tested runtime is CPython **3.12.14**, Windows AMD64, **onnxruntime 1.20.1**
with only CPUExecutionProvider, **NumPy 2.1.3**, sequential execution and one
inter/intra-op thread. The complete transitive wheel set has version and SHA256
pins in [requirements-s04-win-py312.lock](requirements-s04-win-py312.lock) and
[the runtime inventory](third_party/s04-runtime-inventory.json). These wheel
hashes target Windows AMD64/CPython 3.12 only. Other builds need explicit locks
and tests; changing installed versions causes visible analysis refusal.

| Component | Version | Licence / retained notice |
|---|---|---|
| ONNX Runtime | 1.20.1 | [MIT](third_party/onnxruntime-LICENSE); [bundled third-party notices](third_party/onnxruntime-ThirdPartyNotices.txt) |
| NumPy | 2.1.3 | [BSD-3-Clause and bundled binary notices](third_party/numpy-LICENSE.txt), including OpenBLAS, LAPACK and GCC runtime exceptions |
| coloredlogs | 15.0.1 | [MIT](third_party/coloredlogs-LICENSE.txt) |
| flatbuffers | 24.3.25 | [Apache-2.0](third_party/flatbuffers-LICENSE.txt) |
| humanfriendly | 10.0 | [MIT](third_party/humanfriendly-LICENSE.txt) |
| mpmath | 1.3.0 | [BSD](third_party/mpmath-LICENSE) |
| packaging | 24.2 | [Apache-2.0 OR BSD-2-Clause](third_party/packaging-LICENSE); [Apache text](third_party/packaging-LICENSE.APACHE), [BSD text](third_party/packaging-LICENSE.BSD) |
| protobuf | 5.29.3 | [BSD-3-Clause](third_party/protobuf-LICENSE) |
| pyreadline3 | 3.5.6 | [BSD-derived notice](third_party/pyreadline3-LICENSE.md) (Windows dependency) |
| sympy | 1.13.3 | [BSD and bundled notices](third_party/sympy-LICENSE) |

The installed Kdenlive-bundled **FFmpeg 8.1.1** is used as a local executable,
without redistribution in S04. Its version and executable SHA256 bind cache
identity. No FFmpeg binary, model, wheel, runtime, voice, interview media or
generated development audio is committed here. Future packaging must retain
the actual bundled dependency notices and review the chosen FFmpeg build's
redistribution requirements; this source-level inventory is not a release SBOM
or a clean-install acceptance result.

Model setup is an explicit network operation. Analysis, inference and cache
reuse contain no network calls or model download. Analysis sessions explicitly
disable ONNX Runtime telemetry. All source media, derived analysis buffers,
reports and caches are local. The project [MIT licence](LICENSE)
is unchanged.

## S05 YAMNet and additional CPU runtime

S05 uses Google's unchanged **YAMNet classification TFLite v1**, Apache-2.0,
4,126,810 bytes, SHA256
`10c95ea3eb9a7bb4cb8bddf6feb023250381008177ac162ce169694d05c317de`.
Exact download/interface/licence/class-map hashes are in
[yamnet-model.json](third_party/yamnet-model.json). The Google download URL is
mutable; mandatory hash/size verification prevents automatic upgrades. Reference
code and vocabulary are pinned to TensorFlow Models revision
`a6e25e28dc8433dde6c1319186a41e6d81a03f2d`; this is separate from the prebuilt
model's release identity. No local conversion or training was performed.
The prebuilt classification variant uses upstream quantization and Relu6
retraining, as documented in its
[fixed model card](https://github.com/tensorflow/tfhub.dev/blob/81fdea8ffa53b5acbd66a012d17fb8f9602c714b/assets/docs/google/models/yamnet/classification/tflite/lite/1.md).
The retained [Apache notice](third_party/yamnet-LICENSE) and
[521-class map](third_party/yamnet-class-map.csv) accompany the adapter. The map
matches all names in the model's attached label list. See the
[official reference](https://github.com/tensorflow/models/tree/a6e25e28dc8433dde6c1319186a41e6d81a03f2d/research/audioset/yamnet).

The [S05 hash lock](requirements-s05-win-py312.lock) includes the S04 runtime lock
and six additional Windows AMD64/CPython 3.12 wheels. The
[additional inventory](third_party/s05-runtime-inventory.json) binds exact wheel
bytes and retained notices. YAMNet inference uses **ai-edge-litert 2.3.0**, one
CPU thread with its builtin CPU XNNPACK backend; no external hardware delegates
or GPU/NPU SDKs are supplied. Standalone local Interpreter inference has no
network calls in this implementation. S04 still explicitly disables ONNX
Runtime telemetry. No claim of a LiteRT telemetry-disable API is made.

| Added component | Version | Licence / retained notice |
|---|---|---|
| ai-edge-litert | 2.3.0 | [Apache-2.0 wheel notice](third_party/s05-ai_edge_litert-LICENSE) |
| backports.strenum | 1.2.8 | [MIT](third_party/s05-backports_strenum-LICENSE) |
| colorama | 0.4.6 | [BSD-3-Clause](third_party/s05-colorama-LICENSE.txt) |
| ml_dtypes | 0.5.3 | [Apache-2.0](third_party/s05-ml_dtypes-LICENSE); [Eigen/MPL-2.0 notice](third_party/s05-ml_dtypes-LICENSE.eigen) |
| tqdm | 4.67.1 | [MPL-2.0 and MIT portions](third_party/s05-tqdm-LICENCE) |
| typing_extensions | 4.15.0 | [PSF-2.0 and accompanying notice](third_party/s05-typing_extensions-LICENSE) |

These are source-development dependency notices, not a completed redistribution
audit/SBOM or clean-install release package. Review actual packaged native
libraries and transitive notices before S14/S15 redistribution; no wheel/model
binary is committed or distributed at this checkpoint.

Supplementary model comparison uses local copies of the
[official ESC-50 dataset](https://github.com/karolpiczak/ESC-50/tree/33c8ce9eb2cf0b1c2f8bcf322eb349b6be34dbb6),
revision `33c8ce9eb2cf0b1c2f8bcf322eb349b6be34dbb6`, under its declared
**CC BY-NC 3.0** terms, for noncommercial development evaluation only. Original
per-clip attributions, hashes, audio and metadata remain ignored/local. No
dataset audio is bundled or republished; this is not a commercially redistributable
product fixture. Clip labels are weak category labels, not precise private Zoom
event annotations. AudioSet/pretraining overlap is unknown. Reserved folds are
kept separate from development and no held-out acceptance result is claimed.
