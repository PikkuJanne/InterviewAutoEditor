"""Portable launcher. Uses only packaged Python and explicit local assets."""
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))


def configure():
    for key, path in {
        'IAE_S04_MODEL': ROOT / 'models/silero_vad.onnx',
        'IAE_S05_MODEL': ROOT / 'models/yamnet.tflite',
        'IAE_CACHE': Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'InterviewAutoEditor/cache',
    }.items():
        os.environ.setdefault(key, str(path))
    # Tcl's compiled build directory is not a portable runtime location.
    os.environ['TCL_LIBRARY'] = str(ROOT / 'runtime/tcl/tcl8.6')
    os.environ['TK_LIBRARY'] = str(ROOT / 'runtime/tcl/tk8.6')
    editor = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Kdenlive/bin/kdenlive.exe'
    if editor.is_file():
        os.environ.setdefault('IAE_KDENLIVE', str(editor))


def verify():
    manifest = json.loads((ROOT / 'PACKAGE.json').read_text(encoding='utf-8'))
    expected = manifest['files']
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()}
    if actual != set(expected) | {'PACKAGE.json'}:
        raise ValueError('Package file list differs. Extract a fresh candidate into a new folder.')
    for name, digest in expected.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Package checksum differs. Extract a fresh candidate into a new folder.')
    return manifest


def main():
    configure()
    if sys.argv[1:] == ['--self-check']:
        manifest = verify()
        from interview_auto_editor.speech import SileroCPU
        from interview_auto_editor.reactions import YamnetCPU, WINDOW
        import tkinter as tk
        speech = SileroCPU(ROOT / 'models/silero_vad.onnx')
        reaction = YamnetCPU(ROOT / 'models/yamnet.tflite')
        assert 0 <= speech.probability([0.0] * 512) <= 1
        assert len(reaction.scores([0.0] * WINDOW)) == 521
        window = tk.Tk()
        window.withdraw()
        patch = window.tk.call('info', 'patchlevel')
        window.destroy()
        print(json.dumps({'package_verified': True, 'source_commit': manifest['source_commit'],
            'python': sys.version.split()[0], 'tk': patch, 'models_cpu_inference': 'passed',
            'system_python_required': False}))
        return 0
    if sys.argv[1:] == ['--desktop']:
        from interview_auto_editor.desktop import main as desktop
        desktop()
        return 0
    from interview_auto_editor.cli import main as cli
    return cli(sys.argv[1:])


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception:
        if sys.argv[1:] == ['--desktop']:
            import tkinter.messagebox
            tkinter.messagebox.showerror('InterviewAutoEditor',
                'Startup failed. Run InterviewAutoEditor-cli.cmd --self-check. '
                'See QUICKSTART.md for local setup and recovery.')
        else:
            print('Portable startup failed. Verify the archive checksum and extract a fresh copy. '
                  'See QUICKSTART.md.', file=sys.stderr)
        raise SystemExit(1)
