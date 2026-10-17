import json,sys,struct,hashlib
from pathlib import Path
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from unicorn.m68k_const import UC_M68K_REG_PC
old=Path('work/section-3.bin').read_bytes();new=Path('work/os144/section-3.bin').read_bytes();base=0x40000400
table=old[0x401b107c-base:0x401b107c-base+455];offset=new.find(table)
assert offset>=0 and new.find(table,offset+1)<0
address=base+offset;refs=[];p=new.find(address.to_bytes(4,'big'))
while p>=0:refs.append(hex(base+p));p=new.find(address.to_bytes(4,'big'),p+1)
assert len(refs)==2
rows=[]
for raw in range(-1,35):
 row=None if raw==-1 else list(new[offset+raw*13:offset+(raw+1)*13])
 rows.append({'raw_scale':raw,'pitch_classes':list(range(12)) if row is None else [i for i in range(12) if row[i]],'degree_bytes':row})
mapping={'source':'OS 1.44 extracted membership table; byte-identical to OS1.42 table','address':hex(address),'bytes':455,'operand_references':refs,'sha256':hashlib.sha256(table).hexdigest(),'scales':rows}
Path('outputs/Digitone-OS1.44-scale-map.json').write_text(json.dumps(mapping,indent=2))
info=json.loads(Path('work/packed-context-build.json').read_text());blob=Path('work/os144/packed-context-overlay.bin').read_bytes()
m=Machine(ddr=0x08000000)
for a in [0x47be0000,0x47fdff00]:m.ensure(a)
m.uc.mem_write(0x47be0000,blob);m.install_isa_patches_scoped(blob[:info['code_bytes']],0x47be0000)
checks=0
for row in rows:
 raw=row['raw_scale']
 for root in [0,60,127]:
  word=0x80000000|root|((raw+1)<<7)
  for note in range(128):
   expected=min((n for n in range(128) if (n-root)%12 in row['pitch_classes']),key=lambda n:(abs(n-note),n))
   actual=call(m,info['layout']['quantize']['address'],[note,word],stack_top=0x47fdff00,limit=10000)
   assert m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and actual==expected,(raw,root,note,actual,expected)
   checks+=1
Path('outputs/Digitone-OS1.44-scale-contract.json').write_text(json.dumps({'passed':True,'firmware_modified':False,'quantizer_cases':checks,'roots':[0,60,127],'raw_scale_range':[-1,34],'note_range':[0,127],'oracle':'Nearest legal in-range note; ties resolve downward, using extracted 1.44 membership rows.','scale_table':mapping},indent=2))
print('PASS',checks,'quantizer cases against extracted OS 1.44 scale rows')
