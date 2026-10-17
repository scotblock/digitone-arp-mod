from pathlib import Path
import sys,json,hashlib
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'outputs'))
from digitone_active_writer_checks import checks
result=checks()
paths=[Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'),root/'work/section-3.bin']
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
b=paths[1].read_bytes()
anchors={0x40015bc2:'4879407b00b0',0x4002235e:'23d040507e2c',0x4002239e:'49ec001c',0x400223c6:'06830001611d',0x4001fcc2:'0684000003d0',0x40031c60:'4ef94013a344',0x4013a34a:'216f00080010',0x4013a33a:'206f0004202800104e75',0x40093b72:'207941342150',0x40093b78:'203c00016119',0x400eeb14:'0681407b00cc',0x40094652:'23ca41342150',0x40001d8e:'40c246fc2700',0x40001dbe:'46c2',0x400172a8:'4eb940014678',0x400146c4:'4ef9400d8180',0x400b71a6:'4ef9400d6974',0x400d69e8:'22680034',0x401764f0:'4013a33a',0x401a498c:'400b6d92400b6e7a'}
for address,hexbytes in anchors.items():
 actual=b[address-0x40000400:address-0x40000400+len(bytes.fromhex(hexbytes))]
 assert actual.hex()==hexbytes,(hex(address),actual.hex())
result['verified_byte_anchors']={f'{a:08x}':h for a,h in anchors.items()}
result['unchanged_input_sha256']=dict(zip([p.name for p in paths],hashes))
(root/'outputs/Digitone-active-writer-check-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(result['scenarios_passed'],'specification scenarios;',result['address_cases'],'address cases;',len(anchors),'byte anchors verified; firmware hashes unchanged')
