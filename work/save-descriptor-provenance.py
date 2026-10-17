from pathlib import Path
import hashlib, struct, json, sys
root = Path(__file__).resolve().parents[1]
out = root / 'outputs'
sys.path.insert(0, str(out))
from digitone_descriptor_provenance_checks import checks
result = checks()
b = (root / 'work/section-3.bin').read_bytes()
base = 0x40000400
anchors = {
    0x400037de: '4eb940005f92',
    0x400039ea: '22d8',
    0x400039ec: '7a14',
    0x40003a04: '2686',
    0x400060d6: '23c0fc0b01b0',
    0x4009ca96: '4eb940003830',
    0x4009cae4: '4eb9400efcb8',
    0x400efc50: '4ef940095d96',
    0x40095d96: '4e75',
}
for addr, expected in anchors.items():
    assert b[addr-base:addr-base+len(expected)//2].hex() == expected, hex(addr)
assert struct.unpack_from('>I', b, 0x4016cfe0-base+3*4)[0] == 8
original = Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes = {original.name: hashlib.sha256(original.read_bytes()).hexdigest(),
          'section-3.bin': hashlib.sha256(b).hexdigest()}
assert hashes[original.name] == '0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
assert hashes['section-3.bin'] == 'ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'
result['static_byte_anchors'] = {f'{addr:08x}': value for addr, value in anchors.items()}
result['receive_channel_3_prime_mask'] = 8
result['unchanged_input_sha256'] = hashes
(out / 'Digitone-descriptor-provenance-check-results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print('PC scenarios:', result['scenarios_passed'], 'static anchors:', len(anchors), 'input hashes unchanged')
