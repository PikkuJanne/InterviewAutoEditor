"""Package boundary regressions: archive confinement, integrity, repeatability."""
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
import zipfile

from s14_package import checked, deterministic_zip, digest, put, runtime_files, safe_name, wheel_files


class PackageTests(unittest.TestCase):
    def test_archive_paths_cannot_escape_or_address_windows_devices(self):
        for name in ('../outside', '/outside', 'C:/outside', 'a\\b', 'a/../b', 'a/b.', 'a/b ', '.', 'a/CON.txt'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                safe_name(name)

    def test_hash_pin_and_exclusive_output_refuse_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            put(root, 'file', b'locked')
            checked(root / 'file', digest(root / 'file'))
            with self.assertRaises(ValueError):
                checked(root / 'file', '0' * 64)
            with self.assertRaises(FileExistsError):
                put(root, 'file', b'replacement')
            self.assertEqual((root / 'file').read_bytes(), b'locked')

    def test_runtime_rejects_links_and_filters_development_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / 'runtime.tar.gz'
            with tarfile.open(archive, 'w:gz') as tar:
                for name in ('python/python.exe', 'python/tcl/tcl8.6/init.tcl',
                        'python/Lib/site-packages/private.py', 'python/python.pdb'):
                    item = tarfile.TarInfo(name)
                    item.size = 1
                    tar.addfile(item, io.BytesIO(b'x'))
            runtime_files(archive, root / 'out')
            self.assertEqual({p.relative_to(root / 'out').as_posix() for p in (root / 'out').rglob('*') if p.is_file()},
                {'python.exe', 'tcl/tcl8.6/init.tcl'})
            with tarfile.open(archive, 'w:gz') as tar:
                item = tarfile.TarInfo('python/link')
                item.type = tarfile.SYMTYPE
                item.linkname = '../../outside'
                tar.addfile(item)
            with self.assertRaises(ValueError):
                runtime_files(archive, root / 'links')

    def test_wheels_refuse_collisions_links_and_unsupported_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / 'test.whl'
            for name in ('../outside', 'a.data/scripts/run', 'package/file'):
                with zipfile.ZipFile(archive, 'w') as wheel:
                    wheel.writestr(name, b'x')
                if name == 'package/file':
                    wheel_files(archive, root / 'out')
                    with self.assertRaises(FileExistsError):
                        wheel_files(archive, root / 'out')
                else:
                    with self.assertRaises(ValueError):
                        wheel_files(archive, root / 'out')
            with zipfile.ZipFile(archive, 'w') as wheel:
                item = zipfile.ZipInfo('link')
                item.external_attr = 0o120777 << 16
                wheel.writestr(item, '../../outside')
            with self.assertRaises(ValueError):
                wheel_files(archive, root / 'out')

    def test_zip_is_identical_after_relocation_and_mtime_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            put(root / 'one', 'app/a.py', b'print(1)\n')
            put(root / 'two', 'app/a.py', b'print(1)\n')
            deterministic_zip(root / 'one', root / 'a.zip', 'candidate/')
            deterministic_zip(root / 'two', root / 'b.zip', 'candidate/')
            self.assertEqual(digest(root / 'a.zip'), digest(root / 'b.zip'))
            with self.assertRaises(FileExistsError):
                deterministic_zip(root / 'one', root / 'a.zip')


if __name__ == '__main__':
    unittest.main()
