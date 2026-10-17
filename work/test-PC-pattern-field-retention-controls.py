from pathlib import Path
exec(Path('work/test-PC-resident-storage-extended-runtime.py').read_text().split('\ntry:')[0])
from emu.harness import call
from unicorn import UC_HOOK_CODE
result={'PC_only':True,'cases':[],'failure':None,'limits':['Stopped native routine controls on a restored snapshot; state changes are deliberate PC fixtures, not naturally scheduled rebindings.','No exception unwind, physical DMA/cache/timing, or actual release of the permanent project backing is tested.']}
s=None
try:
 s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x08000000);m=s.m;u=m.uc;owner=0x41a720d0;old=0x407ef9f4;stack=0x47fdff00;fixture=0x47fc0100;m.ensure(stack);m.ensure(fixture);owner_saved=bytes(u.mem_read(owner,0x244));queue_saved=bytes(u.mem_read(LO,spec['storage_bytes']))
 new=call(m,0x400e96c0,[0x3000],stack_top=stack,limit=2000000);descriptor=call(m,0x400e96c0,[8],stack_top=stack,limit=2000000);assert 0x419f20a0<=new and new+0x3000<=0x429f20a0;assert descriptor
 conversions=[]
 def conversion(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7);conversions.append({'destination':hex(rd(u,sp+4)),'source':hex(rd(u,sp+8))})
 u.hook_add(UC_HOOK_CODE,conversion,begin=0x4000a1a6,end=0x4000a1a6)
 for label,entry,args,expected in [('null_specific_bind',0x4002c1a0,[owner,0],old),('conditional_disabled',0x40153060,[owner,0,new],old),('conditional_replacement',0x40153060,[owner,1,new],new),('specific_replacement',0x4002c1a0,[owner,new],new),('explicit_clear',0x40153078,[owner],0)]:
  u.mem_write(owner,owner_saved);call(m,entry,args,stack_top=stack,limit=2000000);assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and rd(u,owner+32)==expected
  result['cases'].append({'name':label,'field':hex(expected),'returned':True,'passed':True})
 for label,entry,args in [('retained_callback_after_clear',0x40153078,[owner]),('retained_callback_after_rebind',0x4002c1a0,[owner,new])]:
  u.mem_write(owner,owner_saved);u.mem_write(new,b'\xa5'*0x3000);u.mem_write(descriptor,struct.pack('>II',owner,old));u.mem_write(fixture,struct.pack('>I',descriptor));call(m,entry,args,stack_top=stack,limit=2000000);field=rd(u,owner+32);prior=len(conversions)
  call(m,0x4002c1d2,[fixture],stack_top=stack,limit=3000000);assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and len(conversions)==prior+1 and conversions[-1]['destination']==hex(old);assert bytes(u.mem_read(new,0x3000))==b'\xa5'*0x3000;assert rd(u,descriptor+4)==old
  result['cases'].append({'name':label,'owner_field_at_consume':hex(field),'native_conversion':conversions[-1],'descriptor_retains_old_pointer':True,'new_buffer_untouched':True,'passed':True})
 assert bytes(u.mem_read(LO,spec['storage_bytes']))==queue_saved;result.update(passed=True,queue_unchanged=True,test_buffer=hex(new),descriptor=hex(descriptor))
except Exception:result.update(passed=False,failure=traceback.format_exc());print(result['failure'],flush=True)
finally:
 if s:s.close()
Path('outputs/Digitone-E04-PC-pattern-field-retention-controls.json').write_text(json.dumps(result,indent=2));print('CONTROLS',result['passed'],len(result['cases']),flush=True)
if not result['passed']:raise SystemExit(1)
