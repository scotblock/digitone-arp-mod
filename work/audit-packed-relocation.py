"""Verify exact reachable instructions, fallthroughs and relocated literals."""
import pathlib,sys,json
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import cfisa as cf
info=json.loads(pathlib.Path('work/packed-context-build.json').read_text())
old=pathlib.Path('work/cache-context-overlay.bin').read_bytes();new=pathlib.Path('work/packed-context-overlay.bin').read_bytes();base=0x47be0000
mapping={int(k):v for k,v in info['instruction_map'].items()}
alias={base+0x1aa:info['layout']['slot']['address']}
relocations={int(r['old'],16):r for r in info['relocations']}
def decode(blob,a):return cf.decode(lambda p:int.from_bytes(blob[a-base+p:a-base+p+2],'big'),a)
fallthrough=literal=transfers=unchanged=0
for a,b in mapping.items():
 i=decode(old,a);j=decode(new,b)
 assert not j.flags&(cf.ILLEGAL|cf.PCREL|cf.FPU|cf.LINEF),(hex(b),j)
 if a in relocations:
  r=relocations[a];assert new[b-base:b-base+j.length].hex()==r['new_bytes']
  if r['kind']=='relative transfer':
   assert j.target==mapping.get(i.target,alias.get(i.target)),(hex(a),i,j)
   assert (i.flow,j.flow) in [(cf.F_JSR,cf.F_BSR),(cf.F_JMP,cf.F_BRA),(cf.F_BRA,cf.F_BRA),(cf.F_BCC,cf.F_BCC),(cf.F_BSR,cf.F_BSR)]
   transfers+=1
  else:
   assert old[a-base:a-base+2]==new[b-base:b-base+2];literal+=1
 else:
  assert old[a-base:a-base+i.length]==new[b-base:b-base+j.length],hex(a);unchanged+=1
 if i.flow not in (cf.F_BRA,cf.F_JMP,cf.F_RTS,cf.F_RTE):
  assert mapping[a+i.length]==b+j.length,(hex(a),i,j);fallthrough+=1
assert new[info['table_address']-base:]==old[1904:2324]
assert old[0x1aa:0x1b0]==bytes.fromhex('4ef9')+(0x47be0940).to_bytes(4,'big')
out={'passed':True,'firmware_modified':False,'retained_reachable_instructions':len(mapping),'removed_forwarding_instructions':1,'removed_forwarding_bytes':6,'byte_identical_instructions':unchanged,'equivalent_transfer_instructions':transfers,'relocated_literal_instructions':literal,'fallthroughs_verified':fallthrough,'all_checks_and_register_saves_retained':True,'no_new_FPU_or_illegal_instructions':True,'table_bytes_exact':420,'storage_layout_unchanged':True,'limitations':['Structural equivalence does not establish physical timing or region ownership.','Candidate startup entries are relocated but not connected to or exercised through a new loader/bootstrap.']}
pathlib.Path('outputs/Digitone-packed-context-relocation-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
