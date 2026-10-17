from pathlib import Path
exec(Path('work/validate-E03-DIN-buffer-interleavings.py').read_text().split('\ntry:\n for enabled')[0])

def input_setup(m):
 for a in [PARSER,RT,RUN,0x418e9f88,0x431f2dd0,0x431f4dd0]+list(range(RING,RING+0x29000,4096)):m.ensure(a)
 m.uc.mem_write(RUN,loop);m.uc.mem_write(PARSER,u32(RING)+u32(RT)+bytes(44));m.uc.mem_write(PARSER+0x24,u32(DQ));m.uc.mem_write(PARSER+0x28,u32(0x4199fefc));m.uc.mem_write(0x418e9f88,bytes(4));m.uc.mem_write(0x4199fefc,bytes(8))
 call(m,0x40001c78,[DQ,0,0x4199fafc,256],stack_top=STACK,limit=1000)
def input_bytes(m,data):
 m.uc.mem_write(MSG,bytes(data));call(m,RUN,[MSG,len(data),PARSER],stack_top=STACK-0x3000,limit=100000)
def input_drain(m):
 n=0
 while int.from_bytes(m.uc.mem_read(DQ+4,4),'big'):
  s=STACK-0x5000;m.uc.mem_write(s,bytes(128));m.uc.reg_write(UC_M68K_REG_A7,s);m.uc.reg_write(UC_M68K_REG_A2,0x401ce294);m.uc.reg_write(UC_M68K_REG_A3,0x40001cba);m.uc.reg_write(UC_M68K_REG_A4,0x40001d6c)
  m.uc.emu_start(0x400e9bfa,0x400e9c72,count=100000);assert m.uc.reg_read(UC_M68K_REG_PC)==0x400e9c72;n+=1
 return n
class Freeze:
 # Coordination state is host-owned test state, not allocated in Digitone RAM.
 def __init__(self,m):self.m=m;self.owner=None;self.active_view=True;self.original=None;self.flash_started=False;self.faulted=False;self.log=[]
 def acquire(self,owner):
  if self.owner is not None:return False
  self.owner=owner;self.original=int.from_bytes(self.m.uc.mem_read(0x419950a4,4),'big');call(self.m,0x400ed8ea,[],stack_top=STACK-0x6000,limit=1000);self.log.append('gate closed before completed-buffer read');return True
 def fault(self,owner):
  assert self.owner==owner;self.faulted=True;self.log.append('unknown failure latched; no reopening')
 def reject(self,owner):
  if self.owner!=owner:return 'wrong_owner'
  if self.flash_started:return 'flash_started_keep_frozen'
  if self.faulted:return 'fault_keep_frozen'
  drained=input_drain(self.m);self.log.append('drained '+str(drained)+' queued DIN frames while frozen')
  if int.from_bytes(self.m.uc.mem_read(PARSER+0x1c,4),'big')==0xf0:return 'partial_frame_keep_frozen'
  if not self.active_view:return 'view_changed_keep_frozen'
  call(self.m,0x400eb524,[self.original],stack_top=STACK-0x6000,limit=1000);self.owner=None;self.log.append('prior gate restored');return 'restored'

r={'PC_only':True,'cases':[],'failure':None,'design':'Host-owned freeze transaction around unchanged stock received-image action; no firmware helper or image modification.','limits':['Acquisition is scheduled while no input writer is executing; real interrupt-level quiescence is a required integration precondition, not proven here.','Only recovered DIN queues/partial framing are covered; USB/other producer drain coverage is incomplete.','Earlier registry/heap/display/project-save/lock/thread/flash fixtures remain.','Post-write failures stay frozen; safe hardware recovery/rollback is not supplied by this prototype.']}
try:
 for name in ['success_queued','success_partial','bad_checksum','incomplete','prior_gate_disabled','view_changed','partial_on_reject','unknown_exception','flash_error']:
  m=make();t=time.time();stream=[bytes(p) for p in packets]
  if name in ['bad_checksum','prior_gate_disabled','view_changed','partial_on_reject']:
   stream[100]=changed_packet(100)
  if name=='incomplete':stream=stream[:-1]
  for p in stream:m.uc.mem_write(MSG,p);call(m,0x400eaac8,[MSG,len(p),8],stack_top=STACK,limit=100000);consume(m)
  input_setup(m)
  if name=='prior_gate_disabled':call(m,0x400ed8ea,[],stack_top=STACK,limit=1000)
  f=Freeze(m);owner='update-view-1'
  frozen=bytes(m.uc.mem_read(DATA,len(wire)));receive_state=bytes(m.uc.mem_read(STATE,32))
  if name in ['success_queued','bad_checksum','incomplete','prior_gate_disabled','view_changed']:
   for p in [bytes(packets[0]),changed_packet(1)]:input_bytes(m,p)
   queued=int.from_bytes(m.uc.mem_read(DQ+4,4),'big');assert queued==2
  else:queued=0
  if name in ['success_partial','partial_on_reject']:input_bytes(m,bytes(packets[0][:-1]));assert int.from_bytes(m.uc.mem_read(PARSER+0x1c,4),'big')==0xf0
  # Queue entries and the partial frame above predate freeze acquisition.
  assert f.acquire(owner) and not f.acquire('second-owner') and f.reject('wrong-owner')=='wrong_owner'
  # Owner reacquisition and out-of-owner cleanup must not reopen the gate.
  assert int.from_bytes(m.uc.mem_read(0x419950a4,4),'big')==0
  if name=='unknown_exception':
   try:raise RuntimeError('modeled unexpected action failure')
   except RuntimeError:f.fault(owner)
   result=f.reject(owner);assert result=='fault_keep_frozen' and f.owner==owner and int.from_bytes(m.uc.mem_read(0x419950a4,4),'big')==0
  else:
   # Use retained stock context for completed cases. Incomplete case has no queued job: invoke same action with a view fixture.
   if name=='incomplete':context=0x47f1c000;m.uc.mem_write(context,u32(VIEW)+u32(CTRL)+bytes(4))
   else:
    entry=int.from_bytes(m.uc.mem_read(MAN+0x2c,4),'big');context=int.from_bytes(m.uc.mem_read(entry,4),'big')
   stopped=[]
   def boundary(uc,pc,n,d):
    if pc==0x400fcb2a:f.flash_started=True
    if pc in [0x40100504,0xdeadbee0]:stopped.append(pc);uc.emu_stop()
   hooks=[m.uc.hook_add(UC_HOOK_CODE,boundary,begin=a,end=a) for a in [0x400fcb2a,0x40100504,0xdeadbee0]]
   if name=='flash_error':
    m.forced_flash_errors=0
    def fail(uc,pc,n,d):
     if sum(x[0]=='program' for x in m.actions)==1:m.forced_flash_errors+=1;uc.reg_write(UC_M68K_REG_D0,0xffffffff)
    hooks.append(m.uc.hook_add(UC_HOOK_CODE,fail,begin=0x400fd402,end=0x400fd402))
   # Drain queued input after freeze. For successful partial-frame case finish it during the frozen interval.
   drained=input_drain(m)
   if name=='success_partial':input_bytes(m,bytes(packets[0][-1:]));drained+=input_drain(m)
   assert bytes(m.uc.mem_read(DATA,len(wire)))==frozen and bytes(m.uc.mem_read(STATE,32))==receive_state
   m.uc.mem_write(STACK,u32(0xdeadbee0)+u32(context));m.uc.reg_write(UC_M68K_REG_SR,0x2000);m.uc.reg_write(UC_M68K_REG_A7,STACK);m.uc.emu_start(0x400c9536,0xdeadbee0,count=10000000)
   pc=m.uc.reg_read(UC_M68K_REG_PC)
   for h in hooks:m.uc.hook_del(h)
   if name.startswith('success') or name=='flash_error':
    assert pc==0x40100504 and f.flash_started;assert f.reject(owner)=='flash_started_keep_frozen';result='success_keep_frozen' if name!='flash_error' else 'stock_ignored_flash_error_keep_frozen'
    expected=wire[8:8+int.from_bytes(wire[:4],'big')];assert m.flash[0x80000:0x80000+len(expected)]==expected
    if name=='flash_error':assert m.forced_flash_errors==1 and sum(x[0]=='program' for x in m.actions)>1
   else:
    assert pc==0xdeadbee0 and not m.actions;code=m.uc.reg_read(UC_M68K_REG_D0);assert code==(2 if name=='incomplete' else 3)
    if name=='view_changed':f.active_view=False
    result=f.reject(owner)
    if name=='partial_on_reject':
     assert result=='partial_frame_keep_frozen';input_bytes(m,bytes(packets[0][-1:]));input_drain(m);result=f.reject(owner);assert result=='restored'
    elif name=='view_changed':assert result=='view_changed_keep_frozen'
    else:assert result=='restored'
   assert bytes(m.uc.mem_read(DATA,len(wire)))==frozen
  gate=int.from_bytes(m.uc.mem_read(0x419950a4,4),'big')
  if result=='restored':assert gate==(0 if name=='prior_gate_disabled' else 1)
  else:assert gate==0
  # Demonstrate reception can restart following a safe pre-write restoration.
  restart=False
  if result=='restored' and gate:
   input_bytes(m,bytes(packets[0]));input_drain(m);assert m.uc.mem_read(STATE,1)[0]==1;restart=True
  assert bytes(m.uc.mem_read(0x40000400,0x18fc00))==stock[:0x18fc00]
  r['cases'].append({'name':name,'queued_before_freeze':queued,'result':result,'final_gate':gate,'normal_reception_can_restart':restart,'program_calls':sum(x[0]=='program' for x in m.actions),'freeze_log':f.log,'seconds':time.time()-t});print('PASS',name,result,flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc();print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-receive-freeze-design-checks.json').write_text(json.dumps(r,indent=2))
