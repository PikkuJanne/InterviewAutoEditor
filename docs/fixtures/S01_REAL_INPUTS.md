# S01 private example intake — attempt 02

Observed 17 October 2026. **Initial intake/access PASS; synchronization and
interview quality NOT ACCEPTED.** Public records use neutral corpus IDs. Actual
locations, participant mapping, source hashes, XML, screenshots and recordings
are private and are not published. The owner supplied this example after S01's
first blocked checkpoint.

## Located inputs and genuine starter

Corpus ID `real_starter_001` contains one Zoom MP4 and four cleaned WAVs. There
was no existing `.kdenlive` file in the supplied folder. The agent therefore
assembled a new representative starter in the actual installed Kdenlive
**26.08.2 rev. d4e87e4**, using the originals in place. This is an agent-created
native starter, not a previously edited owner project or exporter output.

The saved starter has one sequence, one video-only MP4 clip, and four separate
named audio tracks (`Participant 01` through `Participant 04`). Every clip starts
at timeline/source zero, with no preceding blank and no interior cuts, clip
effects, speed changes or nested sequences. Participant mapping is explicit in
the ignored index; filename order does not establish speaker identity.

The native profile is 1280x720, progressive, 25/1 FPS, square pixels, 16:9,
colorspace 601. The source reports `bt470bg` matrix/primaries and `bt709`
transfer; no color-conversion claim is inferred from the profile label.
Document version remains 1.1, application property 26.08.2, MLT XML 7.43.0.

## Read-only source observations

| Item | Observed value |
|---|---|
| Source video | H.264, 1280x720; nominal and average metadata 25/1 FPS; 51092 video frames reported; start 0; duration 2043.680000 s |
| Embedded MP4 audio | AAC, stereo, 48 kHz; start 0; duration 2043.690667 s |
| All four participant files | PCM signed 16-bit little-endian WAV, stereo, 192000 Hz; no WAV start timestamp reported |
| Longest participant | 392388608 sample frames; exact duration 2043.690666667 s |
| Other three participants | 392384512 sample frames each; exact duration 2043.669333333 s |
| Difference | 4096 sample frames at 192 kHz = 21.333333333 ms |

These are stream metadata and exact WAV sample counts, not a full packet/frame
timestamp audit or proof that all cleaned files align. Do not assume 48 kHz,
mono audio, identical lengths or a trustworthy cleaned-file timestamp in S03.
All five full source SHA256 values were recorded privately before use and
recomputed afterward: **unchanged**. No normalization, denoising or retiming was
applied. The private starter references the original recordings.

## Actual application evidence and discovered limits

1. Created a new project through the GUI with one video/four audio tracks.
2. Imported the MP4, accepted Kdenlive's native matching-profile creation, then
   imported the four original cleaned WAVs. Inserted the MP4 using its video-only
   bin control; placed each WAV at zero; named and committed the audio labels.
3. Saved the private starter. Read-only XML inspection confirmed exactly five
   uncut timeline entries, zero origins, four names, original source references,
   `set.test_audio=1` on the video chain and `hide=audio` on its track layers.
4. Played the project from 00:01:00:10; observed changing picture, advancing
   timecode and audio meters through 00:01:10:10, then paused. This establishes
   playback, not listening or lip-sync acceptance.
5. Opened the known synthetic reference to close the real project, reopened the
   private starter without missing-media/repair prompts, and saved a new private
   round-trip copy. Original source files remained untouched.

**Track comparison PASS:** profile, ordered track names/types, resolved source
identity, entry bounds, audio/video routing and track filter properties are
equal after reopen/save. IDs and serialization order changed naturally.
**Whole-project equality NOT CLAIMED:** sequence `out` changed from
`00:34:03.640` to `00:34:03.680`, one extra frame, while every clip entry still
has inclusive `out=00:34:03.640`. The entry coverage is 51092 frames / 2043.68 s;
the round-trip sequence range covers 51093 frames / 2043.72 s. This must be
accounted for in S02/S03, rather than accepted as a harmless timing difference.

The native entry grid is 10.666666667 ms shorter than the longest participant
source and 10.666666667 ms longer than the other three. This capture is not a
sample-exact full-tail export solution. Preserve authoritative originals and
explicitly resolve frame/sample boundaries in S03. Do not slide audio or advance
picture to hide either source offsets or Zoom's recorded switching delay.

Limited read-only correlation against the MP4's embedded mix used 20-second
windows starting at source seconds 60, 1000 and 1900, decoded locally to 16 kHz
mono analysis buffers. Stronger peaks occurred at 0, +10 ms and about -32.69 ms
for different participant/window comparisons; inactive windows cannot supply an
anchor. Noise cleanup, mixed speakers and codec behavior can affect the result.
This is evidence to investigate per-track offsets/drift in S03, not a correction
estimate, per-speaker alignment certificate or acceptable-sync threshold.

The complete synthetic open/play/group-edit/undo/save/reopen/render evidence
remains in [S01_CAPTURE.md](S01_CAPTURE.md). Group edits and renders of the real
interview were **NOT RUN** in this attempt. No subjective content, laughter,
overlap, pause-removal or microphone-cleanup acceptance is claimed.

## Private corpus and exact excerpts

The ignored `.local/S01/private-corpus-index.json` is populated with the source
folder, explicit participant mapping, native starter/round-trip paths, probe and
hash inventory, signal spot checks and sample locations. It records
`input_contract_checked=true` for this initial inspection and separately
`alignment_certified=false`.

Three private 30-second sets cover source ranges [0,30), [1000,1030) and
[2013,2043). Each contains a video-only H.264 excerpt and four stereo WAVs at
their original 192 kHz/16-bit format. The videos are preview re-encodes; source
media remains authoritative. Each WAV contains exactly 5760000 sample frames
and matches the corresponding original PCM range byte-for-byte. These are
time-position samples; speech/laughter/overlap/uncertainty labels and exact video
anchor checks remain for later quality work. The full sources are also indexed
so later checks can select events outside these ranges.

## Validation, failed attempts and privacy

- `python -B -m unittest discover -s tools -p 'test_*.py' -v`: **42 PASS in
  45.408 s**, existing public capture/checkpoint code unchanged from
  `1d81a245a4a5986ecbfe4fff7d341b84d2ebcf78`.
- `python -B .local/S01/validate_private_corpus.py`: **102 assertions PASS**:
  five original hashes, real track structure/routing, track semantic comparison,
  twelve exact PCM excerpt comparisons and required source/sample access.
  This local one-off validator is not a public importer or product test.
- Initial raw-ID comparison **FAIL**: Kdenlive renumbered producers/tractors.
  Comparing resolved track semantics fixed the invalid comparison; the genuine
  one-frame sequence extent change remains explicitly reported.
- First FFmpeg PCM stream-copy excerpts **FAIL** the exact 30-second sample
  count gate because copying stops on packet boundaries. Those files remain
  private as failed evidence. New excerpt files were created by exact source
  sample slicing with Python `wave`; all twelve now pass byte comparisons.
- An optional SciPy-based signal check could not start because SciPy is absent.
  No dependency was installed; existing NumPy 2.3.5 performed the bounded local
  correlation. No inference model, cloud service or transcript was used.

No search of unrelated storage was performed. The predecessor inventory remains
the previously recorded scoped negative finding, not a machine-wide assertion.
Real project XML must never be passed through the synthetic-only sanitizer or
staged publicly. Public CI must continue to use synthetic media only.

## Exit-gate scope

S01's build, genuine small references, real initial input assumptions and private
corpus access are now checked. S01 is complete; S02 is not started. The native
gain-edge proof is explicitly S02 work, and exact offset/drift/tail contracts are
S03 work. The pending 3/6/8-participant GUI, fractional-FPS and supported-UNC
matrix must be completed before broader tested product compatibility. Current
product compatibility remains EXPERIMENTAL and there is no product exporter.
