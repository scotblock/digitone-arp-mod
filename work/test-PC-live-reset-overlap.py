"""Actual helper/initializer instructions; explicit hypothetical preemptions.
These injections do NOT establish reachability through the stock dispatcher.
"""
from pathlib import Path
exec(Path('work/test-PC-live-storage-reset.py').read_text().split('ENTRY=cfg')[0])
from unicorn import UC_HOOK_CODE
ENTRY=cfg['fallback_address'];LIVE=cfg['live'];RESETSTACK=0x47fd7f00
REGS=[UC_M68K_REG_D0+i for i in range(8)]+[UC_M68K_REG_A0+i for i in range(8)]+[UC_M68K_REG_SR,UC_M68K_REG_PC]
def rd(u,a):return int.from_bytes(u.mem_read(a,4),'big')
def prepared():
 m=machine();call(m,ENTRY,[158],stack_top=RESETSTACK,limit=400000);return m
def execute_until(m,entry,args,stop,sr=0x231f):
 u=m.uc;stack=0x47fdff00;u.mem_write(stack,u32(0xdeadbee0)+b''.join(u32(x) for x in args));u.reg_write(UC_M68K_REG_SR,sr);u.reg_write(UC_M68K_REG_A7,stack)
 hits=[]
 def pause(u,pc,n,d):hits.append(pc);u.emu_stop()
 h=u.hook_add(UC_HOOK_CODE,pause,begin=stop,end=stop);u.emu_start(entry,0xdeadbee0,count=100000);u.hook_del(h);assert hits and u.reg_read(UC_M68K_REG_PC)==stop
 return {r:u.reg_read(r) for r in REGS}
def resume(m,state,end):
 u=m.uc;u.reg_write(UC_M68K_REG_SR,state[UC_M68K_REG_SR])
 for r,v in state.items():
  if r not in [UC_M68K_REG_SR,UC_M68K_REG_PC]:u.reg_write(r,v)
 u.emu_start(state[UC_M68K_REG_PC],end,count=100000)
 assert u.reg_read(UC_M68K_REG_PC)==end
results=[]
# Pause a real allocated live event's copy at both interruptible boundaries.
for boundary in ['before_memcpy','after_memcpy']:
 m=prepared();u=m.uc;event=call(m,0x400ffff2,[],stack_top=RESETSTACK,limit=10000);source=0x43220348+64*72;m.ensure(source)
 descriptor=bytearray(72);descriptor[4:8]=u32(1);descriptor[0x18]=64;u.mem_write(source,bytes(descriptor));u.mem_write(LIVE['state']+64*4,u32(0x800000be))
 stop=0x400fbad8 if boundary=='before_memcpy' else LIVE['layout']['live_copy']['address']+18
 state=execute_until(m,LIVE['layout']['live_copy']['address'],[event,source,72],stop)
 assert (state[UC_M68K_REG_SR]>>8)&7<7
 call(m,ENTRY,[158],stack_top=RESETSTACK,limit=400000)
 free_after=rd(u,0x419ee238);assert free_after==event
 resume(m,state,0xdeadbee0)
 slot=0x47be1024+(event-0x419ebe2c)//72*4
 results.append({'control':'hypothetical reset '+boundary,'paused_pc':hex(stop),'incoming_IPL':(state[UC_M68K_REG_SR]>>8)&7,'metadata_after':hex(rd(u,slot)),'event_now_free':free_after==event,'reachability_proven':False})
 assert rd(u,slot)==0
# A pre-reset input snapshot cannot reappear after the clear; matching stack
# addresses alone do not bring it back. Binding fails open with word zero.
m=prepared();u=m.uc;pattern=0x407fd414;inp=0x47fc8000;src=0x43220348+64*72;m.ensure(inp);m.ensure(src)
u.mem_write(pattern+0x3cb,b'\x3e');u.mem_write(pattern+0x3ce,b'\0');u.reg_write(UC_M68K_REG_A2,pattern);u.reg_write(UC_M68K_REG_A6,inp+0x30);u.reg_write(UC_M68K_REG_D2,0);u.reg_write(UC_M68K_REG_D3,64)
state=execute_until(m,LIVE['layout']['noteon_capture']['address'],[],0x400eaf50);assert rd(u,LIVE['pending'])==inp
call(m,ENTRY,[158],stack_top=RESETSTACK,limit=400000);assert bytes(u.mem_read(LIVE['pending'],32))==bytes(32)
u.mem_write(inp,struct.pack('>IIII',0,64,100,1));u.reg_write(UC_M68K_REG_A2,inp);u.reg_write(UC_M68K_REG_A4,src);u.reg_write(UC_M68K_REG_SR,0x231f);u.reg_write(UC_M68K_REG_A7,0x47fdff00);u.emu_start(LIVE['layout']['descriptor_bind']['address'],0x400ff484,count=10000)
assert rd(u,LIVE['state']+64*4)==0
results.append({'control':'pending input across full reset','stale_snapshot_reappears':False,'reachability_proven':False})
# While the real reset has ready=0, entry hooks refuse new metadata. Their
# displaced stock writes still happen, illustrating the gate's exact scope.
m=prepared();u=m.uc;state=execute_until(m,ENTRY,[158],0x47be0642);assert rd(u,0x47be1010)==0
u.mem_write(pattern+0x3cb,b'\x3e');u.mem_write(pattern+0x3ce,b'\0');u.reg_write(UC_M68K_REG_A2,pattern);u.reg_write(UC_M68K_REG_A6,inp+0x30);u.reg_write(UC_M68K_REG_D2,0);u.reg_write(UC_M68K_REG_D3,64);u.reg_write(UC_M68K_REG_SR,0x231f);u.reg_write(UC_M68K_REG_A7,0x47fcff00);u.emu_start(LIVE['layout']['noteon_capture']['address'],0x400eaf50,count=10000)
assert bytes(u.mem_read(LIVE['state'],LIVE['state_bytes']))==bytes(LIVE['state_bytes']) and bytes(u.mem_read(inp,8))==struct.pack('>II',0,64)
resume(m,state,0xdeadbee0);assert rd(u,0x47be1010)==1
results.append({'control':'capture while real reset ready=0','metadata_blocked':True,'displaced_stock_writes_still_execute':True,'reset_returns_and_reenables':True,'reachability_proven':False})
# A separate producer mutation between byte-copy and metadata-read pairs old
# descriptor bytes with a newer word in the current copy wrapper.
m=prepared();u=m.uc;event=call(m,0x400ffff2,[],stack_top=RESETSTACK,limit=10000);m.ensure(source);u.mem_write(source,bytes(descriptor));u.mem_write(LIVE['state']+64*4,u32(0x800000be))
state=execute_until(m,LIVE['layout']['live_copy']['address'],[event,source,72],LIVE['layout']['live_copy']['address']+18)
new_descriptor=bytearray(descriptor);new_descriptor[0x18]=65;u.mem_write(source,bytes(new_descriptor));u.mem_write(LIVE['state']+64*4,u32(0x80000341));resume(m,state,0xdeadbee0)
slot=0x47be1024+(event-0x419ebe2c)//72*4;assert bytes(u.mem_read(event,72))==bytes(descriptor) and rd(u,slot)==0x80000341
results.append({'control':'descriptor replacement after bytes copied','old_bytes_with_new_context':True,'paused_IPL':(state[UC_M68K_REG_SR]>>8)&7,'reachability_proven':False})
out={'PC_only':True,'firmware_changed':False,'controls':results,'passed':True,'interpretation':'Reset prevents stale metadata reuse, but full reset returns a live allocation to the free list. Copy serialization is required if a producer can rewrite its descriptor during this interval. No injected preemption is established as stock-reachable.'}
Path('outputs/Digitone-E04-PC-input-reset-overlap.json').write_text(json.dumps(out,indent=2));print('PASS',len(results),'machine-code boundary controls; two hypothetical hazards reproduced')
