from pathlib import Path
exec(Path('work/test-PC-resident-storage-extended-runtime.py').read_text().split('\ntry:')[0])
from emu.harness import call
from unicorn import UC_HOOK_CODE
r={'PC_only':True,'events':[],'failure':None,'limits':['Direct diagnostic-queue entry is a stopped PC fixture. The normal application caller/eligibility is not recovered.','Execution deliberately stops just after its first published diagnostic event, before its polling/drain loop.']};s=None
try:
 s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x08000000);m=s.m;u=m.uc;stack=0x47fdff00;m.ensure(stack);before=bytes(u.mem_read(LO,spec['storage_bytes']));owner=bytes(u.mem_read(0x41a720d0,0x244));r['phase']=hex(rd(u,0x47be2840))
 def event(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7);r['events'].append({'pc':hex(pc),'return':hex(rd(u,sp)),'D0':hex(u.reg_read(UC_M68K_REG_D0))})
 for pc in [0x4009c5a0,0x4009c6d8,0x400ffff2,0x40100178,0x47be0642,0x4009c5aa]:u.hook_add(UC_HOOK_CODE,event,begin=pc,end=pc)
 def allocated(u,pc,n,d):r['event_address']=hex(u.reg_read(UC_M68K_REG_D0))
 def after_first(u,pc,n,d):r['stopped_after_first_publish']=True;u.emu_stop()
 u.hook_add(UC_HOOK_CODE,allocated,begin=0x4009c6e0,end=0x4009c6e0);u.hook_add(UC_HOOK_CODE,after_first,begin=0x4009c6f8,end=0x4009c6f8)
 call(m,0x4009c6d0,[],stack_top=stack,limit=300000);pcs=[x['pc'] for x in r['events']]
 r.update(end_pc=hex(u.reg_read(UC_M68K_REG_PC)),initializer_entered='0x47be0642' in pcs or '0x4009c5aa' in pcs,caller_continues_after_refused_pool_wrapper='0x4009c6d8' in pcs,allocated_event='0x400ffff2' in pcs,published_event='0x40100178' in pcs,custom_queue_unchanged=bytes(u.mem_read(LO,spec['storage_bytes']))==before,pattern_owner_unchanged=bytes(u.mem_read(0x41a720d0,0x244))==owner)
 assert r['phase']=='0x4c495645' and r.get('stopped_after_first_publish') and not r['initializer_entered'] and r['caller_continues_after_refused_pool_wrapper'] and r['allocated_event'] and r['published_event'] and r['custom_queue_unchanged'] and r['pattern_owner_unchanged'];r['passed']=True
except Exception:r.update(passed=False,failure=traceback.format_exc());print(r['failure'],flush=True)
finally:
 if s:s.close()
Path('outputs/Digitone-E04-PC-diagnostic-reset-refusal-continuation.json').write_text(json.dumps(r,indent=2));print('DIAGNOSTIC CONTINUATION',r.get('passed'),r.get('end_pc'),flush=True)
