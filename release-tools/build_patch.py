"""Create a stock-dependent XOR delta, never include either input image."""
from pathlib import Path
import argparse
import json
import struct
import zlib
from apply_patch import MAGIC, LIMIT, HEADER_LIMIT, digest, read_limited, reconstruct


def make_patch(stock, candidate, build, filename, status):
    if not stock or not candidate or max(len(stock), len(candidate)) > LIMIT:
        raise ValueError('Unsupported image size.')
    baseline = stock[:len(candidate)].ljust(len(candidate), b'\0')
    packed = zlib.compress(bytes(a ^ b for a, b in zip(baseline, candidate)), 9)
    meta = {'format': 'digitone-xor-v1', 'build': build, 'device': 'Original Digitone / Digitone Keys',
            'base_os': '1.44', 'status': status, 'source_bytes': len(stock), 'source_sha256': digest(stock),
            'target_bytes': len(candidate), 'target_sha256': digest(candidate),
            'output_filename': filename, 'delta_sha256': digest(packed)}
    header = json.dumps(meta, sort_keys=True, separators=(',', ':')).encode('utf-8')
    if len(header) > HEADER_LIMIT:
        raise ValueError('Header too large.')
    patch = MAGIC + struct.pack('>I', len(header)) + header + packed
    assert reconstruct(stock, patch)[1] == candidate
    return meta, patch


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stock', required=True, type=Path)
    p.add_argument('--candidate', required=True, type=Path)
    p.add_argument('--build', required=True)
    p.add_argument('--status', required=True)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    meta, patch = make_patch(read_limited(args.stock, LIMIT), read_limited(args.candidate, LIMIT),
                             args.build, args.candidate.name, args.status)
    with args.output.open('xb') as stream:
        stream.write(patch)
    print(json.dumps(meta, indent=2))


if __name__ == '__main__':
    main()
