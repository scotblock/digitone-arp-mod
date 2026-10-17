"""Existing warm/diagnostic guards with the complete nonempty E10 bank watched."""
from pathlib import Path
import json,struct,hashlib,traceback
definitions=Path('work/test-PC-E10-bound-panel-patterns.py').read_text(encoding='utf-8').split('source_paths=paths;root=')[0]
exec(compile(definitions,'E10-reset-definitions','exec'))
from emu.harness import call
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_D0,UC_M68K_REG_PC
proof=json.loads(Path('outputs/Digitone-E10-PC-bound-panel-patterns.json').read_text());assert proof['passed']
result=dict(PC_only=True,cases=[],helpers_host_loaded=False,bank_host_written=False)
tests=[('diagnostic_'+hex(p),0x4009c6d0,[],p,0x76543210) for p in [0,0x434f4c44,0x494e4954,0x4c495645,0x4641494c]]
tests += [(name,pc,args,0x4c495645,0x76543210) for name,pc,args in [('warm_setup',0x4009d0d8,[]),('pool_wrapper',0x4009c5a0,[]),('pool_initializer',0x400ffed0,[158]),('test_exit',0x4009d0ea,[])]]
tests += [('E10_cold_init_refuses_LIVE',native['E10']['entries']['init'],[],0x4c495645,0)]
for name,entry,args,admission,expected in tests:
 session=None;row=dict(name=name,entry=hex(entry),admission_fixture=hex(admission),writes=[]);result['cases'].append(row)
 try:
  session=Session(proof['checkpoints']['reloaded-two-patterns'],syx=str(syx),ddr=0x8000000,on_machine=install)
  u=session.m.uc;stack=0x47fdff00;session.m.ensure(stack);u.mem_write(0x47be2840,struct.pack('>I',admission))
  bank=bytes(u.mem_read(native['E10']['bank'],64));assert bank==b''.join(bytes.fromhex(x) for x in proof['expected_records'])
  spans=[(native['base'],len(payload)),(0x419ebe2c,9216),(0x419f0d70,8),(0x402a0e50,4),(0x40236788,4),(0x41392fa4,4)]
  fingerprint=lambda:hashlib.sha256(b''.join(bytes(u.mem_read(a,n)) for a,n in spans)).hexdigest()
  before=fingerprint()
  def written(u,access,a,n,value,d):row['writes'].append(dict(address=hex(a),size=n,value=value,pc=hex(u.reg_read(UC_M68K_REG_PC))))
  for a,n in spans:u.hook_add(UC_HOOK_MEM_WRITE,written,begin=a,end=a+n-1)
  u.reg_write(UC_M68K_REG_D0,0x76543210);value=call(session.m,entry,args,stack_top=stack,limit=100000)
  assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and value==expected
  assert not row['writes'] and fingerprint()==before
  row.update(passed=True,balanced_return=True,nonempty_bank_and_all_new_storage_unchanged=True)
 except Exception:
  row.update(passed=False,failure=traceback.format_exc());print(row['failure'],flush=True)
 finally:
  if session:session.close()
 print(name,row.get('passed'),flush=True)
result['passed']=all(r.get('passed') for r in result['cases'])
result['limits']=['Stopped native entry calls with explicit admission fixtures; no concurrent input/reset or physical reset is claimed.','Existing diagnostic and warm-reset refusals protect the nonempty E10 bank and copied image in these ten entry cases. Unknown interior/computed bypasses and warm copier replay remain outside this check.']
Path('outputs/Digitone-E10-PC-bound-reset-refusal.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
if not result['passed']:raise SystemExit(1)
