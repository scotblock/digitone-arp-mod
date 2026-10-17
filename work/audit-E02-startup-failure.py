from pathlib import Path
import sys,json,struct,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from emu import snapshot
from unicorn.m68k_const import *
port=json.loads(Path('work/os144/helper-port.json').read_text());build=json.loads(Path('outputs/Digitone-OS1.44E02-build.json').read_text());captures=json.loads(Path('outputs/Digitone-OS1.44-caller-state-capture.json').read_text())
blob=Path('work/os144/packed-context-overlay.bin').read_bytes();main=Path('work/os144/emulator-E02-main.bin').read_bytes();RAM,PTR,BSS,STACK=0x47be0000,0x47be1000,0x47be1004,0x47fdff00
u32=lambda v:struct.pack('>I',v&0xffffffff)
r={'scope':'Final E02 machine code in isolated PC calls on a stock-captured stopped state; no device operations','cases':[],'limitations':['Timers, IRQ producers and DMA do not advance during these calls. No real fault exception/unwind, cache coherence or global RAM ownership proof.'],'failure':None}
def machine():
 m=Machine(ddr=0x08000000);snapshot.restore_into(m,captures['caller_states'][0]['path']);m.ensure(RAM);m.ensure(STACK)
 m.uc.mem_write(0x40000400,main);m.install_isa_patches_scoped(main,0x40000400)
 m.uc.mem_write(RAM,blob);m.install_isa_patches_scoped(blob[:1784],RAM)
 m.uc.mem_write(PTR,u32(BSS-0x14100));m.uc.mem_write(BSS,struct.pack('>III',0x534c4332,2,0xb70)+bytes([0xa5])*(0xb70-12))
 return m
try:
 for mode in ['ready','not_ready','bad_magic','bad_version','bad_size','null_pointer','bad_argument','reentry']:
  m=machine();uc=m.uc
  uc.mem_write(RAM-16,b'\x6d'*16);uc.mem_write(BSS+0xb70,b'\x7e'*16)
  uc.mem_write(BSS+12,u32(0 if mode=='not_ready' else 1))
  if mode.startswith('bad_') and mode!='bad_argument':uc.mem_write(BSS+{'bad_magic':0,'bad_version':4,'bad_size':8}[mode],u32(0))
  if mode=='null_pointer':uc.mem_write(PTR,u32(0))
  before=bytes(uc.mem_read(PTR,0xb74));entry=port['layout']['reset']['address']
  if mode in ['ready','not_ready','reentry']:
   call(m,entry,[158],stack_top=STACK,limit=300000)
   assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
   assert bytes(uc.mem_read(BSS,16))==struct.pack('>IIII',0x534c4332,2,0xb70,1)
   assert bytes(uc.mem_read(BSS+16,0xb70-16))==bytes(0xb70-16)
   if mode=='reentry':
    uc.mem_write(BSS+16,b'\x99'*(0xb70-16));call(m,entry,[158],stack_top=STACK,limit=300000)
    assert bytes(uc.mem_read(BSS+16,0xb70-16))==bytes(0xb70-16)
   outcome='stock initializer returned; contexts cleared; ready published'
  else:
   uc.mem_write(STACK,u32(0xdeadbee0)+u32(157 if mode=='bad_argument' else 158));uc.reg_write(UC_M68K_REG_SR,0x2700);uc.reg_write(UC_M68K_REG_A7,STACK)
   uc.emu_start(entry,0x47be0640,count=300000)
   assert uc.reg_read(UC_M68K_REG_PC)==0x47be0640
   assert bytes(uc.mem_read(PTR,0xb74))==before
   outcome='interrupt-masked infinite failure loop; not stock fallback'
  assert bytes(uc.mem_read(RAM,len(blob)))==blob
  assert bytes(uc.mem_read(RAM-16,16))==b'\x6d'*16 and bytes(uc.mem_read(BSS+0xb70,16))==b'\x7e'*16
  r['cases'].append({'mode':mode,'passed':True,'outcome':outcome});print('PASS',mode,flush=True)
 # Execute final appended copier, not a rebuilt assembly fixture.
 m=machine();uc=m.uc;uc.mem_write(RAM,b'\xa5'*len(blob));uc.mem_write(PTR,b'\xa5'*0xb74)
 call(m,int(build['copier_address'],16),[],stack_top=STACK,limit=300000)
 assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
 assert bytes(uc.mem_read(RAM,len(blob)))==blob
 assert bytes(uc.mem_read(PTR,4))==u32(BSS-0x14100)
 assert bytes(uc.mem_read(BSS,16))==struct.pack('>IIII',0x534c4332,2,0xb70,0)
 assert bytes(uc.mem_read(BSS+16,0xb70-16))==bytes(0xb70-16)
 r['copier']={'passed':True,'source_bytes':len(blob),'copier_bytes':build['copier_bytes'],'ready_after_copy':0,'stock_displaced_call_returned':True}
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc();print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E02-startup-failure-review-checks.json').write_text(json.dumps(r,indent=2))
