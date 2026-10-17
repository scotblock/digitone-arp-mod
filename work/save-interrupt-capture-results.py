from pathlib import Path
import sys,json,hashlib
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'outputs'))
from digitone_interrupt_capture_checks import checks
result=checks()
paths=[Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'),root/'work/section-3.bin']
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
b=paths[1].read_bytes()
anchors={0x400169b0:'487a03a4',0x400169ba:'4eb94000170c',0x4000173a:'203c407c2000',0x40001740:'2280',0x40001744:'236f00080004',0x40000452:'4ce8ffff000c',0x40000458:'4e73',0x4009bd4c:'203c4009c838',0x4009bd52:'23c0400002fc',0x4009bd58:'7005',0x4009bd5a:'13c0fc04c07f',0x4009ba5c:'203c80000000',0x4009ba62:'81b9fc04c010',0x4009c840:'203c7fffffff',0x4009c846:'c1b9fc04c010',0x4009dc5c:'4e73',0x400eef62:'223c400eef30',0x400eef68:'23c1400002fc',0x400eef86:'23c0400002fc',0x40001dbe:'46c2',0x4009ca12:'6668',0x4009cae4:'4eb9400efcb8',0x40007224:'2039404dc2fc'}
for address,h in anchors.items():
 actual=b[address-0x40000400:address-0x40000400+len(bytes.fromhex(h))]
 assert actual.hex()==h,(hex(address),actual.hex())
result['verified_byte_anchors']={f'{a:08x}':h for a,h in anchors.items()}
result['unchanged_input_sha256']=dict(zip([p.name for p in paths],hashes))
(root/'outputs/Digitone-interrupt-capture-check-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(result['scenarios_passed'],'specification scenarios;',len(anchors),'byte anchors verified; firmware hashes unchanged')
