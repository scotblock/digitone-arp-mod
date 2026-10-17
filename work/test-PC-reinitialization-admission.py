"""Policy admission on actual native command state; no firmware guard installed.
Also demonstrate why returning zero from the initializer does not abort setup.
"""
from pathlib import Path
exec(Path('work/test-PC-diagnostic-command-exit.py').read_text().split('\nresults=[]')[0])
import sys,hashlib
sys.path.insert(0,'work')
from digitone_reinitialization_policy import ReinitializationPolicy
results=[]
def live_policy():
 p=ReinitializationPolicy();t=p.begin_boot();p.initializer_entry(t);p.finish_boot(stock_complete=True,context_complete=True,mode_is_normal=True);return p
def stage(m,stop):
 u=m.uc;u.mem_write(0x41368d64,u32(3));u.mem_write(0x41368d88,u32(1));u.mem_write(0x402a0e50,u32(1));call(m,0x4008e8b2,[],stack_top=RESETSTACK,limit=1000000);queue_note(m,64);queue_note(m,67);u.mem_write(0x402296f0,u32(rd(u,0x402296f0)&~0x80000));u.mem_write(LIVE['pending'],u32(0x47fc8000)+u32(0x800000be))
 packet=0x47fc6000;token=0x47fc7000;m.ensure(packet);u.mem_write(packet,b'#EXIT_TEST_MODE\0');u.mem_write(token,bytes(128));parsed=call(m,0x4008a474,[packet,0x401e29c0,token],stack_top=RESETSTACK,limit=100000);assert parsed==1
 u.reg_write(UC_M68K_REG_A2,packet);u.reg_write(UC_M68K_REG_D2,token);u.reg_write(UC_M68K_REG_D0,parsed);u.reg_write(UC_M68K_REG_D7,0x21);u.reg_write(UC_M68K_REG_A6,0x47fc9000);u.mem_write(0x47fc9000-0x84,u32(0xffffffff));return execute_until(m,0x4008b4ce,[],stop,sr=0x201f)
m=prepared();u=m.uc;state=stage(m,0x4008b88a);p=live_policy()
def fingerprint():
 return {'stock':state_of(m),'context_hash':hashlib.sha256(bytes(u.mem_read(0x47be1000,0xb74))+bytes(u.mem_read(LIVE['state'],LIVE['state_bytes']))).hexdigest(),'pool_hash':hashlib.sha256(bytes(u.mem_read(0x419eb92c,0x3000))).hexdigest(),'CPU':[u.reg_read(r) for r in REGS]}
before=fingerprint();called=[]
decision=p.run_operation('diagnostic_exit',lambda:(called.append(True),resume(m,state,ENTRY)))
assert not decision.allowed and not called and before==fingerprint() and before['stock']['test_flag']==1
results.append({'kind':'whole-operation policy denial at actual command pre-mutation boundary','PC':hex(u.reg_read(UC_M68K_REG_PC)),'decision':decision.reason,'queue_flags_handler_metadata_pool_and_CPU_preserved':True,'native_rejection_continuation_executed':False})
# Negative control: an early zero-return at the initializer is ignored by the
# actual setup caller, after command and setup flags have already changed.
m=prepared();u=m.uc;state=stage(m,ENTRY);sp=u.reg_read(UC_M68K_REG_A7);ret=rd(u,sp);u.reg_write(UC_M68K_REG_D0,0);u.reg_write(UC_M68K_REG_A7,sp+4);u.emu_start(ret,0x400982d8,count=10000)
assert ret==0x4009c5aa and u.reg_read(UC_M68K_REG_PC)==0x400982d8 and rd(u,0x402a0e50)==0
results.append({'kind':'initializer-only zero-return negative control','caller_return':hex(ret),'continues_to_setup_call':hex(u.reg_read(UC_M68K_REG_PC)),'diagnostic_flag_already_cleared':True,'zero_return_aborts_whole_setup':False,'return_injected_for_negative_control':True})
Path('outputs/Digitone-E04-PC-reinitialization-admission.json').write_text(json.dumps({'PC_only':True,'passed':True,'native_guard_installed':False,'cases':results,'limits':['Policy denial is host-model admission on a paused native command fixture; it is not a firmware branch or completed native rejection path.','The early initializer return is deliberately injected to test caller behavior.','Callback/app selection veto, request cleanup/status feedback, other computed callers and physical behavior remain unimplemented.']},indent=2));print('PASS pre-mutation denial preserves native state; initializer-only zero return fails to abort setup')
