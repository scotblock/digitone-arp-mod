from pathlib import Path
import sys,json,hashlib
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'outputs'))
from digitone_writer_interleaving_checks import checks
result=checks()
paths=[Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'),root/'work/section-3.bin']
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
b=paths[1].read_bytes()
anchors={0x400efe94:'21400004',0x400effca:'116a00070018',0x40034bb4:'135003ce',0x40034bca:'135003cb',0x40034d00:'135003ce',0x40034d16:'135003cb',0x40035356:'114103ce',0x40035368:'114103cb'}
for address,hexbytes in anchors.items():
 actual=b[address-0x40000400:address-0x40000400+len(bytes.fromhex(hexbytes))]
 assert actual.hex()==hexbytes,(hex(address),actual.hex())
result['verified_instruction_bytes']={f'{a:08x}':h for a,h in anchors.items()}
result['unchanged_input_sha256']=dict(zip([p.name for p in paths],hashes))
(root/'outputs/Digitone-writer-interleaving-check-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(result['scenarios_passed'],'specification scenarios pass; 8 instruction anchors verified; input hashes unchanged')
