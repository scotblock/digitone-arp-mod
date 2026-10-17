"""Integrate tested M1 controls into a distinct internal PC package layout.

E08C denotes this controls-integration experiment, not a hardware release.
The older E08 loader artifacts and E07 user build are preserved.
"""
from pathlib import Path
import hashlib
import json
import struct

PB, MB, SOURCE = 0x47be0000, 0x40000400, 0x4029c5b0
sha = lambda b: hashlib.sha256(b).hexdigest()
folder = Path('work/os144')
base = json.loads((folder / 'E08-PC-install-layout.json').read_text())
combined = json.loads(Path('outputs/Digitone-E08-PC-path-layout.json').read_text())
verified = json.loads(Path('outputs/Digitone-E08-M1-controls-verification.json').read_text())
assert verified['passed']
main = bytearray((folder / 'E08-PC-layout-main.bin').read_bytes())
payload = bytearray((folder / 'E08-PC-layout-payload.bin').read_bytes())
old_size = len(payload)
regions, data_regions = [], []
parts = {}
for name in ['settings-accessors', 'settings-codec-bridge', 'M1-controls']:
    path = folder / f'E08-PC-{name}.bin'
    raw = path.read_bytes()
    assert sha(raw) == verified['artifact_sha256'][str(path)], name
    cfg = json.loads((folder / f'E08-PC-{name}-layout.json').read_text())
    parts[name] = cfg
    if name == 'settings-codec-bridge':
        for stock, trampoline in [(0x400081f6, 0x47be6e00), (0x4000818a, 0x47be6e20)]:
            old = b'\x4e\xb9' + struct.pack('>I', stock)
            assert raw.count(old) == 1
            raw = raw.replace(old, b'\x4e\xb9' + struct.pack('>I', trampoline))
    offset = cfg['base'] - PB
    assert offset >= old_size
    end = offset + len(raw)
    if len(payload) < end:
        payload.extend(bytes(end - len(payload)))
    payload[offset:end] = raw
    regions.extend(cfg['regions'])
    if name == 'M1-controls':
        first, last = cfg['data_range']
        data_regions.append({'name': 'M1_control_labels_and_rates', 'base': first, 'bytes': last-first})

hooks = list(parts['M1-controls']['hooks'])
for stock, target, trampoline in [(0x400081f6, 0x47be5a00, 0x47be6e00),
                                  (0x4000818a, 0x47be5b80, 0x47be6e20)]:
    original = bytes(main[stock-MB:stock-MB+8])
    code = original + b'\x4e\xf9' + struct.pack('>I', stock+8)
    off = trampoline-PB
    assert payload[off:off+len(code)] == bytes(len(code))
    payload[off:off+len(code)] = code
    regions.append({'name': f'codec_stock_trampoline_{stock:x}', 'base': trampoline, 'bytes': len(code)})
    hooks.append({'site': stock, 'target': target, 'length': 8,
                  'original': original.hex(),
                  'replacement': (b'\x4e\xf9' + struct.pack('>I', target) + b'\x4e\x71').hex()})

for hook in hooks:
    off = hook['site']-MB
    assert main[off:off+hook['length']].hex() == hook['original'], hook
    main[off:off+hook['length']] = bytes.fromhex(hook['replacement'])
assert len(payload) % 4 == 0 and PB+len(payload) <= 0x47c00000
main[0x4029c4be-MB:0x4029c4c2-MB] = struct.pack('>I', len(payload)//4)
main[SOURCE-MB:] = payload

def merge_hooks(old):
    merged = {hook['site']: hook for hook in old}
    merged.update({hook['site']: hook for hook in hooks})
    return list(merged.values())

limits = [
    'Internal PC controls-integration package; not an installable hardware release.',
    'Physical RAM ownership, cache coherence and timing remain unverified.',
    'M1 only. Pattern isolation, reset/copy lifetimes and other MIDI tracks need broader coverage.'
]
new = {**base, 'regions': base['regions']+regions,
       'data_regions': base['data_regions']+data_regions,
       'hooks': merge_hooks(base['hooks']), 'bytes': len(payload),
       'payload_bytes': len(payload), 'additional_copy_bytes': len(payload)-base['old_payload_bytes'],
       'copy_longwords': len(payload)//4, 'copy_source_end': SOURCE+len(payload),
       'copy_destination_end': PB+len(payload), 'code_bytes': base['code_bytes']+sum(r['bytes'] for r in regions),
       'main_sha256': sha(main), 'payload_sha256': sha(payload),
       'controls_integrated': True, 'controls_baseline_payload_bytes': old_size,
       'new_controls_hooks': hooks, 'controls_extension_bytes': len(payload)-old_size,
       'installable_firmware_produced': False, 'limits': limits}
# All state additions use the final 12 bytes of the existing, natively cleared
# 336-byte M1 record. No added host initializer or warm-state snapshot is used.
assert base['state_bytes'] == 336
assert base['state']+336 <= base['arena']
new['new_state_offsets'] = {'pending_tagged_word': 324, 'binding_pointer_cookie': 328, 'binding_word_cookie': 332}
full = {**combined, **new,
        'regions': combined['regions']+regions,
        'components': combined['components']+regions+data_regions,
        'candidate': None, 'candidate_sha256': None,
        'hardware_ready': False, 'PC_only': True}
(folder / 'E08C-PC-layout-main.bin').write_bytes(main)
(folder / 'E08C-PC-layout-payload.bin').write_bytes(payload)
(folder / 'E08C-PC-install-layout.json').write_text(json.dumps(new, indent=2))
Path('outputs/Digitone-E08C-PC-path-layout.json').write_text(json.dumps(full, indent=2))
print(f'Integrated PC layout: {len(payload)} copied bytes, {len(payload)-old_size} added; state remains 336 bytes.')
