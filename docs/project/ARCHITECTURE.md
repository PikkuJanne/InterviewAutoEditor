# Architecture

Use a local Python core, FFmpeg/ffprobe for decoding/probing, CPU-capable inference and a thin Windows desktop UI over the same callable core as the CLI. Inspect any existing code before replacing it. Prefer a bundled runtime in the user package; do not force a system-wide Python install or a single unnecessary patch version. Choose and lock supported dependencies during implementation based on real compatibility.

Suggested modules (names may be refined with a recorded reason): intake, timing, analysis/speech, analysis/reactions, analysis/video, planner, adapters/kdenlive, reporting, cli, ui. UI does not contain timing or inference logic.

Speech detection candidate: Silero VAD via a local ONNX inference path. Reaction detection candidate: a laughter-capable sound-event model such as YAMNet. Benchmark on cleaned Zoom recordings; do not assume perfect class labels or precision from a generic model. Pin model hashes/licences; models must be present locally after setup. Never fall back silently to aggressive amplitude gating if a model is missing.

Cache analysis by source content fingerprint, decoder options and model/settings versions. Replanning a pause target should not rerun inference. Chunk processing must preserve recurrent state/context at boundaries and produce deterministic results. Keep cancellation cooperative and publish outputs atomically after validation. No hidden remote processing or telemetry.

Native editable Kdenlive clip/effect gain is preferred after the S02 proof. If it cannot provide acceptable edges, choose gain-only derived PCM at original time origin/duration, plus originals in the bin and reproducible envelopes. Record the tradeoff and restore path. Internal microfades can be sample-based; project edit boundaries remain representable in the project frame model. Do not claim sub-frame native support without evidence.

Mix peak analysis is separate from per-track normalization. Preserve source dynamics; apply only a documented master gain reduction if needed to avoid summed overload. Keep user overrides stable by source-time interval IDs.

Use safe XML parsing (no external entities or network loads), structured subprocess argument arrays, bounded reads and no execution of project contents. Treat a .kdenlive file as data. Validate output references, IDs, durations and selected stream audio state before finalizing.

CLI capabilities to implement: inspect, analyze, plan, export, run, compatibility-probe and report/restore as appropriate. Exact syntax is decided in S10 and documented; these are requirements, not already existing commands.
