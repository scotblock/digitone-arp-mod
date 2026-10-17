"""PC-only interruption diagnostic. Completed execution is not recovery safety."""
from pathlib import Path
import json, os, shutil, sys, traceback
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu','work']
from emu import bootstrap as bs, sparse, longrun
from emu.session import Session
from unicorn.m68k_const import UC_M68K_REG_A7, UC_M68K_REG_PC
from E10_storage_probe import record_bytes

original_build=longrun.build
def build(*args,**kwargs):
 kwargs['unblock']=False;kwargs['idle_yield']=1<<60
 return original_build(*args,**kwargs)
longrun.build=build

proof=json.loads(Path('outputs/Digitone-E10-PC-life-copy-cache.json').read_text())
assert proof['passed'];expected_bank=bytes.fromhex(proof['expected_bank'])
syx=Path('work/os144/E09A-PC-path-candidate.syx').resolve()
root=Path('work/E10-update-interrupt').resolve();root.mkdir(exist_ok=True)
paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()))
boot=json.loads(Path('outputs/Digitone-E10-PC-powergood-startup.json').read_text());assert boot['passed'] and boot['stock_powerfail_gate_armed']
snapshot=boot['cases'][0]['ui_snapshot']
srcpaths=bs.FirmwarePaths(str(Path(snapshot).parents[2]),syx.name,paths.devices_dir)
shutil.copytree(srcpaths.sections,paths.sections,dirs_exist_ok=True)
shutil.copytree(srcpaths.overlay,paths.overlay,dirs_exist_ok=True);shutil.copyfile(syx,paths.syx)
with open(srcpaths.card,'rb') as src,open(paths.card,'wb') as dst:
 sparse.make_sparse(dst);sparse.extend(dst,Path(srcpaths.card).stat().st_size)
 while chunk:=src.read(1024*1024):
  if chunk.strip(b'\0'):dst.seek(src.tell()-len(chunk));dst.write(chunk)
os.environ.update(paths.env())
rd=lambda u,a:int.from_bytes(u.mem_read(a,4),'big')
out=dict(PC_only=True,passed=False,explicit_host_entry=True,power_loss_interrupt_emulated=False,cache_contents_host_written=False,writes=[],failure=None)

layout=json.loads(Path('work/os144/PC_ONLY-E10-life-layout.json').read_text());payload=Path('work/os144/PC_ONLY-E10-life-payload.bin').read_bytes()
def verify_code(session):
 for r in layout['regions']:
  if r['base']<layout['base']:continue
  off=r['base']-layout['base'];code=payload[off:off+r['bytes']]
  assert bytes(session.m.uc.mem_read(r['base'],r['bytes']))==code,r['name']
  session.m.install_isa_patches_scoped(code,r['base'])
s=Session(snapshot,syx=str(syx),ddr=0x8000000,audio=True,on_machine=verify_code)
from emu.intfrc import ForcedInterrupts
from emu.pit import interrupt_level
from unicorn import UC_HOOK_MEM_READ
from unicorn.m68k_const import UC_M68K_REG_SR
forced=ForcedInterrupts(s.m,sources=(30,),base=0xfc050000,first_vector=192)
s.sources=s.sources+(forced,)
out.update(explicit_host_entry=False,power_loss_interrupt_emulated=True,events=[],commands=[],failure=None)
u=s.m.uc
# Board input fixture: power-fail pin C2 low; preserve all other GPIO bits.
def pin(u,access,address,size,value,d):
 u.mem_write(0xec09401a,bytes([u.mem_read(0xec09401a,1)[0]&~4]))
u.hook_add(UC_HOOK_MEM_READ,pin,begin=0xec09401a,end=0xec09401a)
finished=[False]
for pc,label in [(0x40002008,'force_store'),(0x40002012,'post_force'),(0x4000202e,'reset_IRQ_stack'),(0x40002034,'lower_IPL'),(0x4000203a,'external_restore'),(0x40001e54,'external_pin_ISR'),(0x40001e2a,'forced_callback_ISR'),(0x400a7b8e,'registered_shutdown'),(0x400a7e8e,'working_cache_gate'),(0x400a7a6c,'raw_32K_writer'),(0x400a800c,'cache_write_complete'),(0x400a8088,'shutdown_terminal')]:
 def entered(u,pc,n,d,label=label):
  row=dict(kind=label,pc=hex(pc),SR=hex(u.reg_read(UC_M68K_REG_SR)),SP=hex(u.reg_read(UC_M68K_REG_A7)),force=hex(rd(u,0xfc050014)))
  if label=='raw_32K_writer':
   sp=u.reg_read(UC_M68K_REG_A7);row.update(sector=rd(u,sp+4),source=hex(rd(u,sp+8)))
  out['events'].append(row)
  if label=='cache_write_complete' and out['commands']:finished[0]=True;s.m.halt_vec=-1;u.emu_stop()
 s.at(pc,entered)
es=s.ev['esdhc']
from E10_powerfail_fixture import PolledCompletionStatus
status=PolledCompletionStatus(es);original_write=es.card.write_data
# Observe actual controller payload, keeping normal native command/DMA flow.
def write_data(idx,arg,data):
 out['commands'].append(dict(command=idx,sector=arg,bytes=len(data)))
 return original_write(idx,arg,data)
es.card.write_data=write_data
try:
 # Enter a further unsaved change through actual native panel controls.
 def tap(key,wait=120):s.tap(s.code(key),hold_ms=80,after_ms=wait)
 def combo(key):
  s.press(s.code('FUNC'));s.run_ms(80);tap(key);s.release(s.code('FUNC'));s.run_ms(120)
 s.run_ms(200);tap('STOP')
 root_ptr=rd(u,0x419f0de0);selection=rd(u,rd(u,root_ptr+0x40)+8)
 if selection<4:tap('MIDI')
 tap('T1');s.press(s.code('PTN'));s.run_ms(80);tap('1',80);s.release(s.code('PTN'));s.run_ms(150)
 tap('SYN1');combo('SYN2');X=layout['E10']['state']
 if not rd(u,X+56):s.turn(4,16,after_ms=150)
 assert rd(u,X+56)==1
 before=bytes(u.mem_read(layout['E10']['bank'],4096))
 paused=[False]
 def cleared(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7);ret=rd(u,sp)
  out.setdefault('update_callers',[]).append(dict(ret=hex(ret),pc=hex(pc),header=hex(rd(u,0x40555ee4))))
  if pc!=0x400852a6 or paused[0] or not layout['lifecycle']['base']<=ret<layout['lifecycle']['base']+0x400:return
  paused[0]=True
  out['interrupt_point']=dict(pc=hex(pc),return_to=hex(ret),SR=hex(u.reg_read(UC_M68K_REG_SR)),header=bytes(u.mem_read(0x40555ee4,4)).hex())
  s.m.halt_vec=-2;u.emu_stop()
 s.at(0x400852a6,cleared)
 s.at(0x400852b4,cleared)
 u.ctl_remove_cache(0x40085268,0x400852cc)
 s.turn(6,16,after_ms=200)
 assert paused[0] and rd(u,0x40555ee4)==0
 s.halted=None;s.m.halt_vec=None

 expected_bank=bytes(u.mem_read(layout['E10']['bank'],4096));assert expected_bank!=before
 out['all_mirror_records_complete_at_interrupt']=all(bytes(u.mem_read(0x40555ff4+0x240200+i*0xa00+0x940,32))==expected_bank[32*i:32*i+32] for i in range(128))
 out.update(native_unsaved_edit=True,expected_bank=expected_bank.hex(),previous_bank=before.hex())
 pending,selected=rd(u,0x402369e0),rd(u,0x402369e4)
 out.update(pending_bank=pending,selected_bank=selected,registered_callback=hex(rd(u,0x40528598)),ready_byte=u.mem_read(0x4139420c,1)[0],initial_PC=hex(s.pc),initial_SR=hex(u.reg_read(UC_M68K_REG_SR)),external_vector_level=interrupt_level(s.m,66),reset_stack_flag=rd(u,0x402296f8))
 assert rd(u,0x40528598)==0x400a7b8e and pending in [0,1] and pending!=selected
 assert rd(u,0x40000000+66*4)==0x40001e54
 out['synthetic_idle_scheduler_yield_disabled']=True
 assert s.m.raise_vector(66,level=7)
 s.pc=u.reg_read(UC_M68K_REG_PC)
 for i in range(250):
  s.run_ms(20)
  if i%25==0:print('progress',i,hex(s.pc),len(out['commands']),out['events'][-1:] if out['events'] else [],flush=True)
  if finished[0] or s.halted:break
 es.card.flush();out['CC_TC_acknowledgements']=status.acks;out.update(finished=finished[0],halted=s.halted,final_PC=hex(s.pc),forced_fired=dict(forced.fired),card=paths.card)
 dest=rd(u,0x401c2de0+pending*4)*512
 with open(paths.card,'rb') as f:
  f.seek(dest);out['new_bank_magic']=f.read(4).hex()
  matches=[]
  for i in range(128):
   f.seek(dest+0x110+0x240200+i*0xa00+0x940);matches.append(f.read(32)==expected_bank[32*i:32*i+32])
  f.seek(rd(u,0x401c2de0+selected*4)*512);out['old_bank_magic']=f.read(4).hex()
 out['records_match']=sum(matches)
 assert finished[0] and forced.fired[30]==1
 out.update(execution_completed=True,recovery_passed=False,unsaved_recovery_guaranteed=False,both_bank_magics_invalid=out['new_bank_magic']!='434f4b49' and out['old_bank_magic']!='434f4b49')
 assert out['both_bank_magics_invalid']
 out['passed']=True
except Exception:
 out.update(passed=False,failure=traceback.format_exc());print(out['failure'],flush=True)
finally:
 s.close()
 out['limits']=['One PC-only level-7 interruption after the native COKI clear in E10 editor synchronization. Native panel edit and registered callback dispatch; no writer call frame or firmware changes. Harness stop marker is cleared before injecting the external interrupt.','INTC2 source 30 uses the existing generic forced-interrupt model. eMMC command and DMA completion are immediate in this engine. Test stops after cache-loop completion, before final power-latch behavior. No physical power decay, timing or energy reserve is modeled.']
 Path('outputs/Digitone-E10-PC-update-interrupt.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Interruption scenario completed:',out.get('execution_completed'),'; recovery not guaranteed.',flush=True)
if not out.get('passed'):raise SystemExit(1)
