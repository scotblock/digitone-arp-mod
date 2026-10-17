from pathlib import Path
import sys,os,json,struct,traceback,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,longrun
from emu.session import Session
from emu.harness import call
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import *
base_build=longrun.build
def build(*a,**kw):kw['unblock']=False;return base_build(*a,**kw)
longrun.build=build
startup=json.loads(Path('outputs/Digitone-E07-PC-startup-comparison.json').read_text());case=next(r for r in startup['cases'] if r['image']=='E07_default');assert case['passed'];cfg=json.loads(Path('outputs/Digitone-E07-PC-candidate-layout.json').read_text());payload=Path('work/os144/E07-PC-payload.bin').read_bytes();syx=Path('work/os144/E07-PC-candidate.syx').resolve();root=Path(case['ui_snapshot']).parents[2];paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
out={'PC_only':True,'cases':[],'limits':['Native stopped-state calls from new candidate startup snapshot. Admission phases are explicit fixtures for diagnostic controls.','Whole diagnostic entry is intentionally disabled, matching the candidate exclusion of diagnostic initialization. No caller success-return contract is invented.','Unknown interior/computed bypasses and live concurrent physical reset behavior remain unproven.']}
tests=[('diagnostic_'+hex(phase),0x4009c6d0,[],phase) for phase in [0,0x434f4c44,0x494e4954,0x4c495645,0x4641494c]]+[(name,pc,args,0x4c495645) for name,pc,args in [('warm_setup',0x4009d0d8,[]),('pool_wrapper',0x4009c5a0,[]),('pool_initializer',0x400ffed0,[158]),('test_exit',0x4009d0ea,[])]]
for name,pc,args,phase in tests:
 row={'name':name,'entry':hex(pc),'phase':hex(phase),'unexpected_entries':[]};out['cases'].append(row);s=None
 try:
  def install(s):
   for r in cfg['regions']:
    if r['base']>=0x47be0000:s.m.install_isa_patches_scoped(payload[r['base']-0x47be0000:r['base']-0x47be0000+r['bytes']],r['base'])
  s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x08000000,on_machine=install);m=s.m;u=m.uc;stack=0x47fdff00;m.ensure(stack);u.mem_write(0x47be2840,struct.pack('>I',phase))
  spans=[(0x47be1000,0xb74),(0x47be2000,2080),(0x47be2860,400),(0x419ebe2c,9216),(0x419f0d70,8),(0x402a0e50,4),(0x40236788,4),(0x41392fa4,4)]
  fingerprint=lambda:hashlib.sha256(b''.join(bytes(u.mem_read(a,n)) for a,n in spans)).hexdigest();before=fingerprint()
  for p in [0x400ffff2,0x40100178,0x4009c6d8,0x47be0642]:
   def observed(u,p,n,d):row['unexpected_entries'].append(hex(p))
   u.hook_add(UC_HOOK_CODE,observed,begin=p,end=p)
  u.reg_write(UC_M68K_REG_D0,0x76543210);result=call(m,pc,args,stack_top=stack,limit=100000)
  assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and result==0x76543210 and not row['unexpected_entries'] and fingerprint()==before
  row.update(passed=True,returned=True,D0_preserved=True,monitored_storage_unchanged=True,no_event_allocation_or_publication=True)
 except Exception:row.update(passed=False,failure=traceback.format_exc());print(row['failure'],flush=True)
 finally:
  if s:s.close()
 print('RESET',name,row.get('passed'),flush=True)
out['passed']=all(r.get('passed') for r in out['cases']);Path('outputs/Digitone-E07-PC-diagnostic-reset-controls.json').write_text(json.dumps(out,indent=2))
if not out['passed']:raise SystemExit(1)
