from pathlib import Path
exec(Path('work/test-PC-ui-defer-overlay.py').read_text().split('\nresults=[]')[0])
from unicorn import UC_HOOK_MEM_WRITE
admission_cfg=json.loads(Path('work/os144/PC_ONLY-persistent-admission.json').read_text())
admission_blob=Path('work/os144/PC_ONLY-persistent-admission.bin').read_bytes()
ADDR=admission_cfg['state_address'];PHASE=admission_cfg['phases']
pos=0
while pos<len(admission_blob):
 ins=cfisa.decode(lambda off:int.from_bytes(admission_blob[pos+off:pos+off+2],'big'),admission_cfg['base']+pos)
 assert not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(admission_blob[pos:pos+2],'big')),(hex(admission_cfg['base']+pos),ins.op)
 pos+=ins.length
assert pos==len(admission_blob)
def install(m,phase):
 m.load(admission_blob,admission_cfg['base']);m.install_isa_patches_scoped(admission_blob,admission_cfg['base'])
 m.uc.mem_write(ADDR,u32(phase))
 for hook in admission_cfg['hooks']:
  assert bytes(m.uc.mem_read(hook['site'],hook['length'])).hex()==hook['stock']
  m.uc.mem_write(hook['site'],bytes.fromhex(hook['replacement']))
def native(m,name,args=(),sr=0x201f):
 u=m.uc;regs={r:u.reg_read(r) for r in REGS if r not in [UC_M68K_REG_D0,UC_M68K_REG_SR,UC_M68K_REG_PC,UC_M68K_REG_A7]}
 u.mem_write(0x47fdff00,u32(0xdeadbee0)+b''.join(u32(x) for x in args));u.reg_write(UC_M68K_REG_SR,sr);u.reg_write(UC_M68K_REG_A7,0x47fdff00)
 stores=[]
 def transition_write(u,access,a,n,v,d):
  if a<ADDR+4 and a+n>ADDR:
   stores.append((a,n,(u.reg_read(UC_M68K_REG_SR)>>8)&7))
 h=u.hook_add(UC_HOOK_MEM_WRITE,transition_write)
 try:u.emu_start(admission_cfg['layout'][name]['address'],0xdeadbee0,count=1000)
 finally:u.hook_del(h)
 assert len(stores)<=1 and all(row==(ADDR,4,7) for row in stores),stores
 assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and u.reg_read(UC_M68K_REG_A7)==0x47fdff04 and u.reg_read(UC_M68K_REG_SR)==sr,(name,hex(u.reg_read(UC_M68K_REG_PC)),hex(u.reg_read(UC_M68K_REG_A7)),hex(u.reg_read(UC_M68K_REG_SR)),hex(sr))
 assert all(u.reg_read(r)==v for r,v in regs.items())
 return u.reg_read(UC_M68K_REG_D0)
out={'PC_only':True,'ISA_C_and_MOVE_audit_passed':True,'helper_cases':[],'reset_cases':[]}
m=prepared();install(m,0);u=m.uc
for sr in [0x201f,0x231f,0x271f]:
 for label,value in list(PHASE.items())+[('zero',0),('poison',0xa5a5a5a5),('one_bit_corrupt',PHASE['cold']^1)]:
  u.mem_write(ADDR,u32(value));assert native(m,'claim_cold',sr=sr)==int(label=='cold')
  assert rd(u,ADDR)==(PHASE['initializing'] if label=='cold' else value)
  assert native(m,'claim_cold',sr=sr)==0
  out['helper_cases'].append({'incoming_SR':hex(sr),'initial':label,'single_use_claim':True,'registers_stack_SR_preserved':True})
 for success in [0,1,2]:
  u.mem_write(ADDR,u32(PHASE['cold']));assert native(m,'complete',[success],sr)==0 and rd(u,ADDR)==PHASE['cold']
  assert native(m,'claim_cold',sr=sr)==1
  assert native(m,'complete',[success],sr)==1 and rd(u,ADDR)==PHASE['live' if success==1 else 'failed']
  terminal=rd(u,ADDR);assert native(m,'complete',[1],sr)==0 and native(m,'claim_cold',sr=sr)==0 and rd(u,ADDR)==terminal
  out['helper_cases'].append({'incoming_SR':hex(sr),'completion_argument':success,'terminal_phase':'live' if success==1 else 'failed','replay_denied':True})
print('PASS native persistent state transitions',len(out['helper_cases']),flush=True)
# Actual native reset/fallback: include valid READY and feature/header failure.
# Global write hook tests interval overlap, including a write starting before it.
for phase in [PHASE['initializing'],PHASE['live'],PHASE['failed'],0]:
 for failure in ['none','unready','bad_magic','null_pointer','bad_argument']:
  m=prepared();install(m,phase);u=m.uc;canary=u32(0x6d6d6d6d);u.mem_write(ADDR-4,canary);u.mem_write(ADDR+4,canary)
  if failure=='unready':u.mem_write(0x47be1010,u32(0))
  if failure=='bad_magic':u.mem_write(0x47be1004,u32(0))
  if failure=='null_pointer':u.mem_write(0x47be1000,u32(0))
  touched=[]
  def watch(u,access,a,n,v,d):
   if a<ADDR+4 and a+n>ADDR:touched.append({'pc':hex(u.reg_read(UC_M68K_REG_PC)),'address':hex(a),'bytes':n})
  h=u.hook_add(UC_HOOK_MEM_WRITE,watch)
  call(m,ENTRY,[157 if failure=='bad_argument' else 158],stack_top=RESETSTACK,limit=400000)
  u.hook_del(h);assert not touched and rd(u,ADDR)==phase and bytes(u.mem_read(ADDR-4,4))==canary and bytes(u.mem_read(ADDR+4,4))==canary
  assert native(m,'claim_cold')==0 and rd(u,ADDR)==phase
  out['reset_cases'].append({'phase':hex(phase),'failure':failure,'actual_initializer_returned':True,'overlapping_writes':touched,'admission_preserved_and_no_cold_regrant':True})
print('PASS native reset storage lifetime',len(out['reset_cases']),flush=True)
# Existing copier overwrites candidate word with payload zero. This does not
# create COLD, but also demonstrates persistence cannot span recopy.
m=prepared();install(m,PHASE['live']);u=m.uc
original_payload=Path('work/os144/PC_ONLY-atomic-storage-payload.bin').read_bytes()
original_main=Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes()
offset=ADDR-0x47be0000
assert original_payload[offset:offset+4]==bytes(4)
assert original_main[0x4029c5b0-0x40000400+offset:0x4029c5b0-0x40000400+offset+4]==bytes(4)
u.reg_write(UC_M68K_REG_SR,0x2710);u.reg_write(UC_M68K_REG_A7,RESETSTACK);u.emu_start(0x4029c4b0,0x40001df4,count=100000)
assert u.reg_read(UC_M68K_REG_PC)==0x40001df4 and rd(u,ADDR)==0 and native(m,'claim_cold')==0
out['recopy']={'actual_copier_executed':True,'word_becomes_zero':True,'cold_not_regranted':True,'live_value_not_preserved_across_recopy':True}
out['passed']=True
out['limits']=admission_cfg['limits']+['Candidate word is in the existing payload extent and outside known reset clears. Actual reset runs are bounded coverage, not global RAM ownership.','A zero payload does not authorize cold entry: trusted initial cold seeding and its ordering remain to integrate.','Single-word exact matching detects tested corruption, not arbitrary writes of the valid COLD value.']
Path('outputs/Digitone-E04-PC-persistent-admission.json').write_text(json.dumps(out,indent=2))
# Reuse established native route checks, replacing their constant selector with
# actual persistent reads. Only case setup seeds state; guest chooses branches.
s=Path('work/test-PC-ui-defer-overlay.py').read_text();s=s[s.index('\nresults=[]'):]
s=s.replace("[('audio',True),('audio',False),('ordinary',True),('null',True)]","[('audio',v) for v in list(PHASE.values())+[0,0xa5a5a5a5,PHASE['cold']^1]]+[('ordinary',PHASE['live']),('null',PHASE['live'])]")
s=s.replace('denied=kind==\'audio\' and live','denied=kind==\'audio\' and live!=PHASE[\'cold\']')
s=s.replace("'compiled_live_control':live","'persistent_state':hex(live)")
s=s.replace('guardcfg','admission_cfg').replace('len(blob)','len(admission_blob)')
s=s.replace('Digitone-E04-PC-ui-defer-overlay-tests.json','Digitone-E04-PC-persistent-admission-routes.json')
s=s.replace("'persistent_latch_installed':False","'persistent_latch_in_disposable_fixture':True").replace('Compiled live constant is selected by test setup; no native persistent latch/startup admission.','Tests seed persistent states; helpers read guest RAM. Startup seed/provenance not implemented.')
exec(compile(s,'persistent-admission-native-routes','exec'))
