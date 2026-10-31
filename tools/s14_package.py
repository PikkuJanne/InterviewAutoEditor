"""Offline, hash-locked Windows AMD64 portable candidate builder.

Inputs are acquired explicitly before invocation. Never copies a development
venv or executes downloaded archives/wheels. Output is exclusive and immutable.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = 'InterviewAutoEditor-1.0.0-rc.1-windows-x64'
STAMP = (2026, 10, 31, 0, 0, 0)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def checked(path, expected):
    if digest(path) != expected:
        raise ValueError('Build input checksum mismatch: ' + Path(path).name)
    return Path(path)


def safe_name(name):
    p = PurePosixPath(name)
    if (not name or '\\' in name or ':' in name or p.is_absolute()
            or not p.parts or '..' in p.parts or any(x.endswith(('.', ' ')) for x in p.parts)
            or any(re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', x) for x in p.parts)):
        raise ValueError('Unsafe archive member')
    return p


def put(root, name, data):
    path = root.joinpath(*safe_name(name).parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(data)


def runtime_files(archive, destination):
    with tarfile.open(archive, 'r:gz') as tar:
        for item in tar:
            p = safe_name(item.name)
            if item.isdir():
                continue
            if not item.isfile() or p.parts[0] != 'python':
                raise ValueError('Runtime archive must contain regular python/ files')
            name = PurePosixPath(*p.parts[1:])
            # Remove development tools, unrelated packages and build/debug caches.
            if (name.suffix in ('.pdb', '.pyc', '.lib', '.h') or '__pycache__' in name.parts
                    or name.parts[0] in ('include', 'libs', 'Scripts')
                    or str(name).startswith(('Lib/site-packages/', 'Lib/ensurepip/', 'Lib/test/', 'Lib/idlelib/'))):
                continue
            put(destination, str(name), tar.extractfile(item).read())


def wheel_files(archive, destination):
    with zipfile.ZipFile(archive) as wheel:
        for item in wheel.infolist():
            p = safe_name(item.filename)
            if item.is_dir():
                continue
            if (item.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Wheel symlink refused')
            if p.parts[0].endswith('.data'):
                if len(p.parts) < 3 or p.parts[1] not in ('purelib', 'platlib', 'data'):
                    raise ValueError('Unsupported wheel data scheme')
                target = destination.parents[1] if p.parts[1] == 'data' else destination
                p = PurePosixPath(*p.parts[2:])
            else:
                target = destination
            put(target, str(p), wheel.read(item))


def deterministic_zip(directory, output, prefix=''):
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for p in sorted(directory.rglob('*')):
            if p.is_file():
                info = zipfile.ZipInfo(prefix + p.relative_to(directory).as_posix(), STAMP)
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, p.read_bytes(), compresslevel=9)


def build(runtime, wheels, speech, reaction, output):
    lock = json.loads((ROOT / 'third_party/s14-runtime.json').read_text())
    checked(runtime, lock['runtime']['sha256'])
    models = ((speech, 'silero_vad.onnx', lock['models']['silero']),
              (reaction, 'yamnet.tflite', lock['models']['yamnet']))
    for path, _, sha in models:
        checked(path, sha)
    entries = json.loads((ROOT / 'third_party/s04-runtime-inventory.json').read_text())['wheels']
    entries += json.loads((ROOT / 'third_party/s05-runtime-inventory.json').read_text())['additional_wheels']
    for entry in entries:
        checked(wheels / entry['wheel'], entry['sha256'])
    if subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT).strip():
        raise ValueError('Commit reviewed tracked source before building')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    output.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / NAME
        root.mkdir()
        runtime_files(runtime, root / 'runtime')
        for entry in entries:
            wheel_files(wheels / entry['wheel'], root / 'runtime/Lib/site-packages')
        for path, name, _ in models:
            put(root, 'models/' + name, path.read_bytes())
        for name in tracked:
            if not name:
                continue
            if name.startswith('interview_auto_editor/') and name.endswith('.py'):
                dest = 'app/' + name
            elif name.startswith('third_party/') or name in ('LICENSE', 'THIRD_PARTY_NOTICES.md',
                    'requirements-s04-win-py312.lock', 'requirements-s05-win-py312.lock',
                    'docs/COMPATIBILITY.md') or name.startswith('docs/project/') and name.endswith('.md'):
                dest = name
            else:
                continue
            put(root, dest, (ROOT / name).read_bytes())
        for source, dest in [('packaging/portable.py', 'app/portable.py'),
            ('packaging/InterviewAutoEditor.cmd', 'InterviewAutoEditor.cmd'),
            ('packaging/InterviewAutoEditor-cli.cmd', 'InterviewAutoEditor-cli.cmd'),
            ('docs/QUICKSTART.md', 'QUICKSTART.md'), ('docs/RELEASE_NOTES_RC1.md', 'RELEASE_NOTES.md')]:
            put(root, dest, (ROOT / source).read_bytes())
        inventory = {'schema_version': 1, 'candidate': NAME, 'source_commit': commit,
            'platform': 'Windows AMD64; only recorded Windows 11 build tested',
            'signed': False, 'runtime': lock['runtime'],
            'wheels': [{'file': e['wheel'], 'sha256': e['sha256']} for e in entries],
            'models': lock['models'], 'external_prerequisite': 'Separately installed Kdenlive and its FFmpeg/ffprobe; no binaries redistributed',
            'external_cpp_prerequisite': lock['external_cpp_prerequisite'],
            'files': {p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob('*')) if p.is_file()}}
        put(root, 'PACKAGE.json', (json.dumps(inventory, indent=2, sort_keys=True) + '\n').encode())
        deterministic_zip(root, output / (NAME + '.zip'), NAME + '/')
        # Complete tracked source snapshot, independently reviewable/rebuildable.
        source = Path(temporary) / 'source'
        source.mkdir()
        for name in tracked:
            if name:
                put(source, name, (ROOT / name).read_bytes())
        deterministic_zip(source, output / (NAME + '-source.zip'))
    artifacts = {p.name: digest(p) for p in sorted(output.glob('*.zip'))}
    (output / 'SHA256SUMS.txt').write_text(''.join(f'{sha}  {name}\n' for name, sha in artifacts.items()), encoding='ascii')
    print(json.dumps({'source_commit': commit, 'artifacts': artifacts}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('runtime', 'wheels', 'speech', 'reaction', 'output'):
        p.add_argument('--' + arg, type=Path, required=True)
    build(**vars(p.parse_args()))
