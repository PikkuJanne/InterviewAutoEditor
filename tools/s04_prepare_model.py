#!/usr/bin/env python3
"""Explicit one-time model setup; speech analysis itself is offline."""
import argparse
import hashlib
from pathlib import Path
import sys
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.speech import MODEL_SHA256

REVISION = '6478567951ae5c9979ad7b234185b5515f4be7a1'
URL = f'https://raw.githubusercontent.com/snakers4/silero-vad/{REVISION}/src/silero_vad/data/silero_vad.onnx'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True, help='New local ONNX file; never overwritten.')
    args = parser.parse_args()
    try:
        if args.destination.exists():
            parser.exit(1, 'Model setup refused: destination already exists.\n')
        with urllib.request.urlopen(URL, timeout=60) as response:
            data = response.read(2327525)
        if len(data) != 2327524 or hashlib.sha256(data).hexdigest() != MODEL_SHA256:
            parser.exit(1, 'Model setup refused: upstream size/hash mismatch.\n')
        # Reuse exclusive atomic publication for binary data via Latin-1 is
        # deliberately avoided: model bytes must remain byte-identical.
        import os
        import tempfile
        args.destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=args.destination.parent, delete=False) as out:
                temporary = Path(out.name)
                out.write(data)
                out.flush()
                os.fsync(out.fileno())
            os.link(temporary, args.destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    except (OSError, ValueError):
        parser.exit(1, 'Model setup failed; check network and local destination privately.\n')
    print('Pinned Silero v5.1.2 model installed; SHA256 verified. See THIRD_PARTY_NOTICES.md.')


if __name__ == '__main__':
    main()
