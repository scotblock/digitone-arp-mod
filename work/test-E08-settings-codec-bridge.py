from pathlib import Path
import sys,json,struct
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from emu.harness import Machine,call
c=json.loads(Path('work/os144/E08-PC-settings-codec-bridge-layout.json').read_text());blob=Path('work/os144/E08-PC-settings-codec-bridge.bin').read_bytes();m=Machine(ddr=0x8000000);u=m.uc;R=0x47bc8000;F=R+0x200;BACK=R+0x400;ST=0x47bcff00
main=Path('work/os144/E07-PC-main.bin').read_bytes()
for p in range(0x40000000,0x40000400+len(main),0x100000):m.ensure(p)
u.mem_write(0x40000400,main);m.install_isa_patches_scoped(main,0x40000400)
for p in [R,ST,c['base']]:m.ensure(p)
u.mem_write(c['base'],blob)
for r in c['regions']:
 code=blob[r['base']-c['base']:r['base']-c['base']+r['bytes']];p=0
 while p<len(code):
  i=cfisa.decode(lambda off:int.from_bytes(code[p+off:p+off+2],'big'),r['base']+p);assert i.length>0 and p+i.length<=len(code) and not i.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(code[p:p+2],'big')),(r,p,i);p+=i.length
 m.install_isa_patches_scoped(code,r['base'])
def invoke(entry,args):return call(m,entry,args,stack_top=ST,limit=30000)
raw=bytearray(164)
for i in range(41):struct.pack_into('>H',raw,i*2,(i%4)*256)
raw[8:10]=bytes(2);raw[24:26]=bytes(2);raw[162:164]=bytes.fromhex('1234')
u.mem_write(R,bytes(raw));u.mem_write(F,bytes([0x55])*172);assert invoke(c['stock_entries']['encode'],[F,R,0])==1
baseline_file=bytes(u.mem_read(F,172));u.mem_write(BACK,bytes(164));assert invoke(c['stock_entries']['decode'],[BACK,F,0])==1;baseline_back=bytes(u.mem_read(BACK,164));checks=[]
for mode in range(2):
 for rate in range(8):
  for gate in [1,25,50,99]:
   word=0xa800|(mode<<10)|(rate<<7)|gate
   u.mem_write(R,bytes(raw));u.mem_write(R+158,struct.pack('>H',word));u.mem_write(F,bytes([0x55])*172)
   assert invoke(c['entries']['encode'],[F,R,0])==1
   encoded=bytes(u.mem_read(F,172));assert encoded[:166]==baseline_file[:166] and encoded[168:]==baseline_file[168:] and encoded[166:168]==struct.pack('>H',word)
   u.mem_write(BACK,bytes(164));assert invoke(c['entries']['decode'],[BACK,F,0])==1
   restored=bytes(u.mem_read(BACK,164));assert restored[:158]==baseline_back[:158] and restored[160:]==baseline_back[160:] and restored[158:160]==struct.pack('>H',word)
checks.append('64 valid configurations survive actual stock encode/decode with bridge; all stock fields match baseline')
word=0xad32;u.mem_write(R+158,struct.pack('>H',word));invoke(c['stock_entries']['encode'],[F,R,0]);assert bytes(u.mem_read(F+166,2))==bytes(2)
checks.append('stock control erases tag: bridge is necessary')
for word in [0,0xffff,0xa800,0xa864,0x1234]:
 u.mem_write(F,baseline_file);u.mem_write(F+166,struct.pack('>H',word));u.mem_write(BACK,bytes([0x5a])*164);assert invoke(c['entries']['decode'],[BACK,F,0])==1 and bytes(u.mem_read(BACK+158,2))==bytes(2)
checks.append('legacy/malformed serialized tail resets extension to unmarked OFF defaults')
before=bytes(u.mem_read(BACK,164));assert invoke(c['entries']['decode'],[BACK,0,0])&255==0 and bytes(u.mem_read(BACK,164))==before
checks.append('stock decode failure does not mutate extension')
out={'PC_only':True,'passed':True,'checks':checks,'codec_bridge_integrated':False,'full_project_save_reload_proven':False,'hardware_ready':False,'limits':['Actual stock MIDI preset conversion executes; the full project filesystem save/load route is not yet joined.','This is a private extension proposal, not a globally certified padding or lifetime claim.']}
Path('outputs/Digitone-E08-settings-codec-bridge-tests.json').write_text(json.dumps(out,indent=2));print('Native stock codec bridge checks passed')
