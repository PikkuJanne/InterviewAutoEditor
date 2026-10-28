#!/usr/bin/env python3
"""Explicit setup of Google's unchanged YAMNet TFLite; analysis stays offline."""
import argparse
import hashlib
import os
from pathlib import Path
import sys
import tempfile
import urllib.request

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.reactions import MODEL_BYTES, MODEL_SHA256

URL = 'https://storage.googleapis.com/download.tensorflow.org/models/tflite/task_library/audio_classification/android/lite-model_yamnet_classification_tflite_1.tflite'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',required=True,type=Path)
    args=parser.parse_args()
    temporary=None
    try:
        if args.destination.exists():
            parser.exit(1,'Reaction setup refused: destination already exists.\n')
        with urllib.request.urlopen(URL,timeout=60) as response:
            data=response.read(MODEL_BYTES+1)
        if len(data)!=MODEL_BYTES or hashlib.sha256(data).hexdigest()!=MODEL_SHA256:
            parser.exit(1,'Reaction setup refused: upstream size/hash mismatch.\n')
        args.destination.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=args.destination.parent,delete=False) as out:
            temporary=Path(out.name)
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        os.link(temporary,args.destination)
    except OSError:
        parser.exit(1,'Reaction setup failed; inspect network/destination privately.\n')
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)
    print('Pinned YAMNet TFLite installed; size and SHA256 verified.')


if __name__=='__main__':
    main()
