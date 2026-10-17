from pathlib import Path
s=Path('work/test-PC-parent-destruction-retained-callback.py').read_text()
s=s.replace("[('child_teardown',0x4015141c,0x41a720d0)", "[('live_baseline',None,0x41a720a0),('child_teardown',0x4015141c,0x41a720d0)")
s=s.replace("'entry':hex(entry)","'entry':hex(entry) if entry else None")
s=s.replace("call(m,entry,[target],stack_top=stack,limit=3000000);row['destructor_returned']", "if entry:call(m,entry,[target],stack_top=stack,limit=3000000)\n  else:u.reg_write(UC_M68K_REG_PC,0xdeadbee0)\n  row['destructor_returned']")
needle="   vtable=rd(u,0x41a720d0);row['getter_after']=hex(rd(u,vtable+0x28));call"
replace="""   vtable=rd(u,0x41a720d0);row['getter_after']=hex(rd(u,vtable+0x28))
   def virtual(u,pc,n,d):
    target=u.reg_read(UC_M68K_REG_A0);row['actual_virtual_dispatch_target']=hex(target)
    if target==0xfffffdf8:row['stopped_before_invalid_dispatch']=True;u.emu_stop()
   u.hook_add(UC_HOOK_CODE,virtual,begin=0x4002c1e4,end=0x4002c1e4)
   call"""
assert needle in s;s=s.replace(needle,replace)
s=s.replace("row['completed']=True", "row['completed']=True\n  if mode=='live_baseline':assert row['callback_returned'] and row['conversions'] and row['conversions'][0]['destination']=='0x407ef9f4'\n  else:assert row['destructor_returned'] and row.get('stopped_before_invalid_dispatch') and row['actual_virtual_dispatch_target']=='0xfffffdf8' and not row['conversions']\n  row['expected_observation_verified']=True")
s=s.replace("Path('outputs/Digitone-E04-PC-parent-destruction-retained-callback.json')", "out['passed']=all(c.get('expected_observation_verified',False) for c in out['cases']);Path('outputs/Digitone-E04-PC-parent-destruction-retained-callback.json')")
exec(compile(s,'verified-destructor-virtual-dispatch','exec'))
