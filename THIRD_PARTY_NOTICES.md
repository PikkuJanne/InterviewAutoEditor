# S04 model and runtime provenance

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
