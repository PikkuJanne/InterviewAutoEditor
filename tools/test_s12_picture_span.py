"""Actual stream-order and full-picture-coverage regressions on synthetic video."""
from dataclasses import replace
from fractions import Fraction as F
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from interview_auto_editor.picture import (PictureRequest, analyze_picture,
    validate_picture, window_ranges, coverage_report, inspect_frames, _inspect_full_frames, PIXELS)
from interview_auto_editor.planner import analysis_digest
from interview_auto_editor.probe import fingerprint, run_bounded
from test_s12_coverage import example

ROOT=Path(__file__).resolve().parents[1]
FFMPEG=os.environ.get('IAE_FFMPEG') or shutil.which('ffmpeg')
FFPROBE=os.environ.get('IAE_FFPROBE') or shutil.which('ffprobe')

class SpanTests(unittest.TestCase):
    def test_full_scan_optimization_matches_existing_integer_measurements(self):
        frames=[bytes([v])*PIXELS for v in (40,40,40,190,190,40,190,190,190,190)]
        self.assertEqual(_inspect_full_frames(frames,17),inspect_frames(frames,17))
    def test_full_windows_cover_every_frame_and_report_missing_picture_only(self):
        a=example()
        ranges=window_ranges(a,full_span=True)
        self.assertEqual(set(f for _,r in ranges for f in range(r.start,r.end)),set(range(300)))

    @unittest.skipUnless(FFMPEG and FFPROBE,'Local FFmpeg/ffprobe required')
    def test_audio_first_video_stream_one_full_span_and_partial_refusal(self):
        with tempfile.TemporaryDirectory() as temp:
            video=Path(temp)/'audio-first.mp4'
            run_bounded([FFMPEG,'-v','error','-nostdin','-n','-i',
                ROOT/'tests/fixtures/kdenlive-26.08.2/media-2/zoom-source.mp4',
                '-map','0:a:0','-map','0:v:0','-c','copy',video])
            a=example();a=replace(a,sources=(replace(a.sources[0],sha256=fingerprint(video)),*a.sources[1:]))
            req=PictureRequest(2,analysis_digest(a),'uncertain','construction_label','Synthetic audio-first stream order')
            with patch('interview_auto_editor.picture.FULL_CHUNK',100),patch('interview_auto_editor.picture.MAX_FRAMES',128):
                observed=analyze_picture(a,req,video,FFMPEG,FFPROBE)
                coverage=coverage_report(a,observed)
                self.assertEqual(coverage['observed_frames'],300)
                self.assertEqual(coverage['unobserved_recorded_frame_intervals'],[])
                self.assertEqual(coverage['recorded_frames'],300)
                with self.assertRaises(ValueError):
                    validate_picture(a,replace(observed,windows=observed.windows[:-1]))
            with self.assertRaises(ValueError):
                analyze_picture(a,req,video,FFMPEG,FFPROBE,stream_index=0)

if __name__=='__main__':unittest.main()
