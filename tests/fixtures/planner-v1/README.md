# Planner v1 construction fixtures

These JSON records were created by the S06 Python planner from mathematical
source-time labels. They contain no media, real identities or real source hashes,
and were **not produced by Kdenlive**. Fingerprints are deliberate placeholders.
Synthetic verified-zero origins apply only to this construction fixture.

The 30-second, 25 FPS input has two sources at 48 kHz and 44.1 kHz, seven
protected events and independently specified removable intervals. The latter
are source-clock construction labels covering every track, not negative model
predictions. Events include speech, reaction, uncertainty and overlap. Full
leading `[0,2)` and trailing `[111/5,30)` sections must survive.

The fixed v1 snapshots include their complete input analysis, request, plan and
decisions. Tight removes `[80,147)` and `[430,522)`, yielding 591 frames. Gentle
removes `[83,144)` and `[433,519)`, yielding 603 frames. Both retain all seven
events. Gaps beside reaction/uncertainty are conservatively kept. Recompute and
compare using `test_s06_planner.py`; unexpected wire or policy changes require
an explicit version/migration decision, not blind fixture regeneration.

These fixtures validate timing and bounded preservation, not speech recognition,
human pace preferences, real interview acceptance or Kdenlive editability.
