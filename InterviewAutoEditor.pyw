"""Windows double-click entry point; uses the installed local Python runtime.

Release runtime bundling/clean-install validation belongs to S14.
"""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
runtime = root / '.venv' / 'Scripts' / 'pythonw.exe'
if runtime.is_file() and Path(sys.prefix).resolve() != runtime.parent.parent.resolve():
    # A file association may select a different system Python. Prefer the
    # project's already prepared runtime; never install/download anything.
    subprocess.Popen([str(runtime), '-B', str(Path(__file__).resolve())], cwd=root, shell=False)
else:
    from interview_auto_editor.desktop import main
    main()
