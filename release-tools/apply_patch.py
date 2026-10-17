"""Apply a stock-dependent Digitone delta. Python 3.10+, standard library only."""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import sys
import zlib

MAGIC = b'DARPAT1\n'
LIMIT = 8 * 1024 * 1024
HEADER_LIMIT = 8192


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_limited(path, limit):
    with Path(path).open('rb') as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError('File exceeds the supported size limit: ' + Path(path).name)
    return data


def decode_patch(data):
    if data[:8] != MAGIC or len(data) < 12:
        raise ValueError('Not a supported Digitone patch file.')
    size = struct.unpack('>I', data[8:12])[0]
    if not 0 < size <= HEADER_LIMIT or len(data) <= 12 + size:
        raise ValueError('Invalid patch header length.')
    meta = json.loads(data[12:12 + size].decode('utf-8'))
    if not isinstance(meta, dict) or meta.get('format') != 'digitone-xor-v1':
        raise ValueError('Unsupported patch format.')
    for key in ['source_bytes', 'target_bytes']:
        if type(meta.get(key)) is not int or not 0 < meta[key] <= LIMIT:
            raise ValueError('Invalid patch size field: ' + key)
    for key in ['source_sha256', 'target_sha256', 'delta_sha256']:
        value = meta.get(key)
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('Invalid checksum field: ' + key)
    name = meta.get('output_filename')
    if not isinstance(name, str) or not name.endswith('.syx') or not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-' for c in name):
        raise ValueError('Invalid output filename.')
    packed = data[12 + size:]
    if digest(packed) != meta['delta_sha256']:
        raise ValueError('Patch payload checksum failed. Download it again.')
    return meta, packed


def reconstruct(stock, patch):
    meta, packed = decode_patch(patch)
    if len(stock) != meta['source_bytes'] or digest(stock) != meta['source_sha256']:
        raise ValueError('Stock firmware does not match the required original OS 1.44 file.\n'
                         'Required SHA-256: ' + meta['source_sha256'])
    decoder = zlib.decompressobj()
    delta = decoder.decompress(packed, meta['target_bytes'] + 1)
    if len(delta) != meta['target_bytes'] or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise ValueError('Invalid or oversized compressed delta.')
    padded = stock[:len(delta)].ljust(len(delta), b'\0')
    result = bytes(a ^ b for a, b in zip(padded, delta))
    if digest(result) != meta['target_sha256']:
        raise ValueError('Reconstructed firmware checksum failed; no output written.')
    return meta, result


def apply(stock_path, patch_path, output_path=None):
    stock_path, patch_path = Path(stock_path), Path(patch_path)
    meta, result = reconstruct(read_limited(stock_path, LIMIT), read_limited(patch_path, LIMIT + HEADER_LIMIT + 12))
    output = Path(output_path) if output_path else patch_path.resolve().parent / meta['output_filename']
    if output.resolve() in {stock_path.resolve(), patch_path.resolve()}:
        raise ValueError('Output must be separate from the stock firmware and patch.')
    if output.suffix.lower() != '.syx':
        raise ValueError('Output filename must end in .syx.')
    # Exclusive creation protects existing stock, candidates and user files.
    created = False
    try:
        with output.open('xb') as stream:
            created = True
            stream.write(result)
    except OSError:
        if created:
            output.unlink(missing_ok=True)
        raise
    return meta, output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stock', type=Path, help='Your original Digitone/Digitone Keys OS 1.44 .syx')
    parser.add_argument('--patch', type=Path, help='Downloaded .darp patch')
    parser.add_argument('--output', type=Path, help='New .syx path; existing files are never overwritten')
    args = parser.parse_args()
    try:
        if args.patch is None:
            patches = sorted(Path(__file__).resolve().parent.glob('*.darp'))
            if len(patches) != 1:
                raise ValueError('Specify --patch; exactly one .darp must be beside this tool for automatic selection.')
            args.patch = patches[0]
        if args.stock is None:
            args.stock = Path(input('Paste the path to your ORIGINAL stock OS 1.44 .syx: ').strip().strip('"'))
        meta, output = apply(args.stock, args.patch, args.output)
        print('Created:', output.resolve())
        print('SHA-256:', meta['target_sha256'])
        print('Status:', meta.get('status', 'experimental'))
        print('No device was contacted. This tool only creates a local file.')
        return 0
    except (OSError, ValueError, EOFError, zlib.error) as exc:
        print('Stopped:', exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
