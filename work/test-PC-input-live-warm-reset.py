"""Actual warm initializer calls and explicitly injected overlap; no reachability claim."""
from pathlib import Path
exec(Path('work/test-PC-input-live-controls.py').read_text().split('\nout=')[0])
from unicorn import UC_HOOK_CODE
report={'PC_only':True,'firmware_modified':False,'resets':[],'limits':['Warm initializer is invoked directly on a recovered startup snapshot; panel/command reachability is not established here.','The input between reset boundaries is an explicit hypothetical preemption, not a demonstrated interrupt/scheduler overlap.','No warm-reset guard or flashable artifact is implemented.']}
pre='work/startup-producer-order-E04_restored/producer-0x4008d3ec.snap'
for phase in ['live','initializing','failed']:
 m=restored(pre);install_inputs(m);u=m.uc;u.mem_write(STATE,u32(P[phase]));phase_writes=[];readiness=[]
 def store(u,access,a,n,v,d):
  if a<STATE+4 and a+n>STATE:phase_writes.append(v)
  if a<0x47be1014 and a+n>0x47be1010:readiness.append(v)
 h=u.hook_add(UC_HOOK_MEM_WRITE,store)
 for cycle in range(3):
  invoke(u,0x400ffed0,[158],count=500000)
  assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and rd(u,STATE)==P[phase]
  assert rd(u,0x47be1010)==1
 u.hook_del(h)
 assert not phase_writes
 report['resets'].append({'incoming_phase':phase,'three_initializer_calls_returned':True,'phase_unchanged':True,'phase_writes':phase_writes,'READY_writes':readiness})
# Pause the native fallback at its actual stock trampoline, READY=0.
m=restored(pre);install_inputs(m);u=m.uc;u.mem_write(STATE,u32(P['live']));stops=[]
def stop(u,pc,n,d):stops.append(pc);u.emu_stop()
h=u.hook_add(UC_HOOK_CODE,stop,begin=0x47be0642,end=0x47be0642)
invoke(u,0x400ffed0,[158],count=500000);u.hook_del(h)
assert stops and rd(u,0x47be1010)==0 and rd(u,STATE)==P['live']
register_ids=list(range(UC_M68K_REG_D0,UC_M68K_REG_D0+8))+list(range(UC_M68K_REG_A0,UC_M68K_REG_A0+8))+[UC_M68K_REG_SR,UC_M68K_REG_PC]
saved={q:u.reg_read(q) for q in register_ids};before=fingerprint(u);hits=[]
for pc in [0x400eb166,0x400eae5c,0x40100252]:u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:hits.append(hex(pc)),begin=pc,end=pc)
packet=0x47fc6000;m.ensure(packet);ch=rd(u,0x41368d2c)&15;u.mem_write(packet,bytes([0x90|ch,64,100]))
u.mem_write(0x47fcff00,struct.pack('>IIII',0xdeadbee0,packet,3,8));u.reg_write(UC_M68K_REG_A7,0x47fcff00);u.reg_write(UC_M68K_REG_SR,0x201f);u.emu_start(0x400eb2d2,0xdeadbee0,count=300000);assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0
report['hypothetical_overlap']={'reset_paused_pc':'0x47be0642','READY':rd(u,0x47be1010),'phase':hex(rd(u,STATE)),'input_routes':hits,'state_changed':fingerprint(u)!=before,'reachability_proven':False}
assert '0x400eb166' in hits and '0x400eae5c' in hits and fingerprint(u)!=before
u.reg_write(UC_M68K_REG_SR,saved[UC_M68K_REG_SR])
for q,v in saved.items():
 if q!=UC_M68K_REG_SR:u.reg_write(q,v)
u.emu_start(saved[UC_M68K_REG_PC],0xdeadbee0,count=500000)
assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and rd(u,STATE)==P['live'] and rd(u,0x47be1010)==1
report['hypothetical_overlap']['reset_resumed_and_returned']=True
report['passed']=True
Path('outputs/Digitone-E04-PC-input-live-warm-reset.json').write_text(json.dumps(report,indent=2));print('PASS repeated warm initializer and negative overlap control',flush=True)

