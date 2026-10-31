# Sources and baseline

User requirements accepted 17 October 2026: exact Zoom workflow; one MP4 with its audio excluded; N already-cleaned aligned audio files; tight pauses, clean speaker boundaries, idle-track suppression preserving laughter; manual start/end trim; account for Zoom picture-switch delay. Follow-up: optimize for Kdenlive 26 and future versions where feasible; keep GitHub in sync; pause after every step with a verbose new-thread handover.

Repository observed 17 October 2026: main at 0c445a400c96b1f85f17fcb0ee8916d283e22d6f, one LICENSE file, one initial commit, no implementation found on main. This is a dated observation; recheck at S00 and inspect local predecessor code.

Official technical references checked 17 October 2026:
- https://docs.kdenlive.org/en/project_and_asset_management/file_management/project_files.html — project XML, media references and version changes.
- https://github.com/KDE/kdenlive/blob/master/dev-docs/fileformat.md — development format reference; recheck the appropriate version/tag during implementation.
- https://www.mltframework.org/docs/mltxml/ — MLT serialization semantics.
- https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0062314 — recorded picture layouts and speaker-view behavior.
- https://github.com/snakers4/silero-vad — candidate speech detector.
- https://www.tensorflow.org/tutorials/audio/transfer_learning_audio — candidate audio-event detection including laughter.

The compatibility layer, numerical starting settings and quality targets are project design decisions, not guarantees stated by these sources. Confirm actual tools, versions and APIs from official sources during each implementation step. The Word roadmap in the bundle's reference folder is background; this bundle's Kdenlive 26 policy and one-step execution instructions are the current operational specification.
