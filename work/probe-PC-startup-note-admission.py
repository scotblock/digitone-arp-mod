"""Handler eligibility on startup snapshots. No transport dispatch inferred."""
from pathlib import Path
import sys,json,struct,traceback
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from emu import snapshot,cfisa
from emu.pit import interrupt_level
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import *
u32=lambda x:struct.pack('>I',x&0xffffffff)
def rd(u,a):return int.from_bytes(u.mem_read(a,4),'big')
def restored(path):
 m=Machine(ddr=0x08000000);snapshot.restore_into(m,path)
 # Install CPU instruction support from the saved executable bytes, without
 # replacing any gate, code, phase or initializer state from the checkpoint.
 m.install_isa_patches_scoped(bytes(m.uc.mem_read(0x40000400,0x28ec00)),0x40000400)
 for base,length in [(0x47be0000,1784),(0x47be3000,474),(0x47be3400,304),(0x47be3600,182),(0x47fa0000,332),(0x47fa0300,280)]:m.install_isa_patches_scoped(bytes(m.uc.mem_read(base,length)),base)
 return m
out={'PC_only':True,'cases':[],'limits':['Complete three-byte packet is passed directly to the actual note handler; upstream USB/DIN/panel transport and concurrent dispatch are not executed.','No note/receive gate is changed. Scratch packet and call stack are fixture inputs.','Pre-initializer controls stop at producer entry, before executing against uninitialized note pools.','Later controls execute the complete handler only after normal stock setup has returned.','Snapshots inherit modeled hardware, not physical device state.']}
for image in ['E04_default','E04_restored']:
 for pc in [0x4009d0d8,0x4008d31e,0x4008d3dc,0x4008d3ec]:
  path=Path('work/startup-producer-order-'+image)/('producer-'+hex(pc)+'.snap')
  if not path.exists():continue
  for full in ([False] if pc==0x4009d0d8 else [False,True]):
   m=restored(path);u=m.uc;channel=rd(u,0x41368d2c)&15;packet=0x47fc6000;stack=0x47fdff00
   m.ensure(packet);m.ensure(stack);u.mem_write(packet,bytes([0x90|channel,64,100]));hits=[]
   def producer(u,at,n,d):
    hits.append(hex(at))
    if not full and at==0x400eae5c:u.emu_stop()
   for at in [0x400eb166,0x400eae5c,0x400eaf48,0x400ff3ec,0x40100252]:u.hook_add(UC_HOOK_CODE,producer,begin=at,end=at)
   item={'image':image,'checkpoint':hex(pc),'full_handler':full,'phase':hex(rd(u,0x47be2840)),'READY':rd(u,0x47be1010),'receive_gate':rd(u,0x41368d64),'note_gate':rd(u,0x41368d88),'channel':channel,'DIN_interrupt_level':interrupt_level(m,156),'queue_before':hex(rd(u,0x419ee22c)),'failure':None}
   try:
    u.mem_write(stack,u32(0xdeadbee0)+u32(packet)+u32(3)+u32(8));u.reg_write(UC_M68K_REG_SR,0x2700);u.reg_write(UC_M68K_REG_A7,stack)
    u.emu_start(0x400eb2d2,0xdeadbee0,count=300000)
    item['end_pc']=hex(u.reg_read(UC_M68K_REG_PC));item['returned']=u.reg_read(UC_M68K_REG_PC)==0xdeadbee0
    item['producer_reached']='0x400eae5c' in hits;item['queue_after']=hex(rd(u,0x419ee22c));item['queue_publisher_reached']='0x40100252' in hits
    assert item['returned'] or (not full and u.reg_read(UC_M68K_REG_PC)==0x400eae5c),item
   except Exception:item['failure']=traceback.format_exc()
   item['native_sites']=hits;out['cases'].append(item);print('PROBE',image,hex(pc),full,item.get('producer_reached'),item.get('queue_publisher_reached'),bool(item['failure']),flush=True)
out['passed']=bool(out['cases']) and all(c['failure'] is None for c in out['cases'])
Path('outputs/Digitone-E04-PC-startup-note-admission-probes.json').write_text(json.dumps(out,indent=2))
if not out['passed']:raise SystemExit(1)
