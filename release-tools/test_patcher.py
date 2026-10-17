"""Self-contained format/error-path tests; no firmware required."""
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib
from apply_patch import apply, decode_patch, digest, reconstruct, MAGIC
from build_patch import make_patch


class PatcherTests(unittest.TestCase):
    def setUp(self):
        self.stock = bytes(range(256)) * 8
        self.target = self.stock[:97] + b'changed notes' + self.stock[109:] + b'extra bytes'
        self.meta, self.patch = make_patch(self.stock, self.target, 'TEST', 'TEST.syx', 'test fixture')

    def test_short_equal_and_long_images(self):
        for target in [self.stock[:500], self.stock, self.target]:
            with self.subTest(size=len(target)):
                _, patch = make_patch(self.stock, target, 'TEST', 'TEST.syx', 'test fixture')
                self.assertEqual(reconstruct(self.stock, patch)[1], target)

    def test_wrong_base(self):
        with self.assertRaisesRegex(ValueError, 'Stock firmware'):
            reconstruct(b'\0' * len(self.stock), self.patch)

    def test_corrupt_and_truncated_patch(self):
        for patch in [self.patch[:-1], self.patch[:-1] + bytes([self.patch[-1] ^ 1]), b'bad']:
            with self.subTest(length=len(patch)), self.assertRaises(ValueError):
                reconstruct(self.stock, patch)

    def changed(self, **updates):
        meta, packed = decode_patch(self.patch)
        meta.update(updates)
        header = json.dumps(meta).encode()
        return MAGIC + struct.pack('>I', len(header)) + header + packed

    def test_output_hash_mismatch(self):
        with self.assertRaisesRegex(ValueError, 'Reconstructed firmware'):
            reconstruct(self.stock, self.changed(target_sha256='0' * 64))

    def test_oversize_and_filename(self):
        for change in [{'target_bytes': 99999999}, {'output_filename': '../stock.syx'}, {'output_filename': 'C:stock.syx'}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                reconstruct(self.stock, self.changed(**change))

    def test_bounded_decompression(self):
        with self.assertRaisesRegex(ValueError, 'compressed delta'):
            reconstruct(self.stock, self.changed(target_bytes=10))

    def test_extra_compressed_data(self):
        meta, packed = decode_patch(self.patch)
        packed += zlib.compress(b'trailing')
        meta['delta_sha256'] = digest(packed)
        header = json.dumps(meta).encode()
        with self.assertRaisesRegex(ValueError, 'compressed delta'):
            reconstruct(self.stock, MAGIC + struct.pack('>I', len(header)) + header + packed)

    def test_writes_verified_output_only(self):
        with tempfile.TemporaryDirectory(prefix='.patch-test-', dir=Path.cwd()) as folder:
            root = Path(folder)
            stock, patch, out = root/'stock.syx', root/'test.darp', root/'new.syx'
            stock.write_bytes(self.stock)
            patch.write_bytes(self.patch)
            apply(stock, patch, out)
            self.assertEqual(out.read_bytes(), self.target)
            with self.assertRaises(FileExistsError):
                apply(stock, patch, out)
            self.assertEqual(out.read_bytes(), self.target)
            with self.assertRaises(ValueError):
                apply(stock, patch, stock)
            self.assertEqual(stock.read_bytes(), self.stock)
            out.unlink()
            stock.write_bytes(b'wrong')
            with self.assertRaises(ValueError):
                apply(stock, patch, out)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
