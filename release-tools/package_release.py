"""Package only the explicit release allowlist, never firmware or sessions."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile
from apply_patch import decode_patch

ROOT = Path(__file__).resolve().parents[1]


def package(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    assets = []
    for build in ['E08F', 'E09']:
        folder = ROOT / 'patches' / build
        patch = folder / (build + '.darp')
        meta, _ = decode_patch(patch.read_bytes())
        published = json.loads((folder / 'manifest.json').read_text())
        if meta != published['patch_metadata'] or hashlib.sha256(patch.read_bytes()).hexdigest() != published['patch_sha256']:
            raise ValueError('Patch manifest mismatch: ' + build)
        files = {'apply_patch.py': ROOT/'release-tools/apply_patch.py',
                 'Create Firmware.cmd': ROOT/'release-tools/Create Firmware.cmd',
                 build+'.darp': patch, 'manifest.json': folder/'manifest.json',
                 'README.md': folder/'README.md', 'RECOVERY.md': ROOT/'docs/PATCH_RECOVERY.md'}
        target = output / ('Digitone-OS1.44-' + build + '-patch.zip')
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, source in sorted(files.items()):
                # Fixed metadata produces identical packages locally and in CI.
                entry = zipfile.ZipInfo(name, date_time=(2026, 10, 17, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                data = source.read_bytes()
                if source.suffix != '.darp':
                    text = data.decode('utf-8').replace('\r\n', '\n')
                    if source.suffix == '.cmd':
                        text = text.replace('\n', '\r\n')
                    data = text.encode('utf-8')
                archive.writestr(entry, data)
        with zipfile.ZipFile(target) as archive:
            if set(archive.namelist()) != set(files) or archive.testzip() is not None:
                raise ValueError('Archive verification failed.')
        assets.append(target)
    lines = [hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name for p in assets]
    (output/'SHA256SUMS.txt').write_bytes(('\n'.join(lines)+'\n').encode())
    print('\n'.join(lines))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'dist')
    package(parser.parse_args().output)
