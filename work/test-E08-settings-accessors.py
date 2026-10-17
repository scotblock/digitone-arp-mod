from pathlib import Path
import sys,json,struct,hashlib
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from emu.harness import Machine,call
c=json.loads(Path('work/os144/E08-PC-settings-accessors-layout.json').read_text());blob=Path('work/os144/E08-PC-settings-accessors.bin').read_bytes();m=Machine(ddr=0x8000000);u=m.uc;H=0x47bc8000;R=H+0x100;ST=0x47bcff00
for p in [c['base'],H,ST]:m.ensure(p)
u.mem_write(c['base'],blob)
for r in c['regions']:
 code=blob[r['base']-c['base']:r['base']-c['base']+r['bytes']];p=0
 while p<len(code):
  ins=cfisa.decode(lambda off:int.from_bytes(code[p+off:p+off+2],'big'),r['base']+p)
  assert ins.length>0 and p+ins.length<=len(code) and not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(code[p:p+2],'big')),(r['name'],p,ins)
  p+=ins.length
 m.install_isa_patches_scoped(code,r['base'])
put=lambda a,v:u.mem_write(a,struct.pack('>I',v&0xffffffff))
def invoke(which,args):return call(m,c['entries'][which],[x&0xffffffff for x in args],stack_top=ST,limit=3000)
put(H,c['MIDI_vtable']);put(H+16,R);original=bytes([0x5a])*164;u.mem_write(R,original);checks=[];count=0
for mode in range(2):
 for rate in range(8):
  for gate in range(1,100):
   u.mem_write(R,original);assert invoke('write',[H,mode,rate,gate])==1
   want=0xa800|(mode<<10)|(rate<<7)|gate;assert bytes(u.mem_read(R+158,2))==struct.pack('>H',want)
   actual=bytes(u.mem_read(R,164));assert actual[:158]==original[:158] and actual[160:]==original[160:]
   assert invoke('read',[H])==want;count+=1
checks.append('all 1584 valid configurations round-trip in native code; only proposed two-byte slot changes')
for args in [[2,0,50],[0,8,50],[0,0,0],[0,0,100],[-1,0,50],[0,-1,50],[0,0,-1]]:
 before=bytes(u.mem_read(R,164));assert invoke('write',[H]+args)==0 and bytes(u.mem_read(R,164))==before
checks.append('invalid inputs fail before mutation')
for v in [0,0xffff,0xa800,0xa864,0xaf80,0x1234]:
 u.mem_write(R+158,struct.pack('>H',v));assert invoke('read',[H])==0xa932
checks.append('unmarked and invalid saved words resolve to OFF, 1/16, 50%')
put(H,0x4019a6a4);before=bytes(u.mem_read(R,164));assert invoke('read',[H])==0 and invoke('write',[H,1,2,50])==0 and bytes(u.mem_read(R,164))==before
checks.append('synth/other object class rejected rather than clamped or mutated')
put(H,c['MIDI_vtable']);put(H+16,0);assert invoke('read',[H])==0 and invoke('write',[H,1,2,50])==0
assert invoke('read',[0])==0 and invoke('write',[0,1,2,50])==0
checks.append('null handle/data rejected')
out={'PC_only':True,'passed':True,'valid_configurations':count,'checks':checks,'integrated':False,'padding_ownership_proven':False,'project_save_reload_proven':False,'limits':c['limits']}
Path('outputs/Digitone-E08-settings-accessor-tests.json').write_text(json.dumps(out,indent=2));print('Native settings accessors:',count,'configurations passed')
