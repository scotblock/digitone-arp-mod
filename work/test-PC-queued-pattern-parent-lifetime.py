from pathlib import Path
s=Path('work/test-PC-queued-pattern-retirement.py').read_text()
s=s.replace("for mode in ['baseline','clear_after_publish','rebind_after_publish']:","for mode in ['baseline']:")
s=s.replace("def event(label,**fields):row['events'].append({'kind':label,'ms':s.now_ms(),**fields})", """def ownership(u):
    ctrl=rd(u,0x419f0de4)
    return {'lifetime_counter':(rd(u,0x419f0d70)<<32)|rd(u,0x419f0d74),'parent':hex(rd(u,0x419f0de0)),'control':hex(ctrl),'strong':rd(u,ctrl+4) if ctrl else None,'weak':rd(u,ctrl+8) if ctrl else None,'owner_vtable':hex(rd(u,0x41a720d0))}
   def event(label,**fields):row['events'].append({'kind':label,'ms':s.now_ms(),'ownership':ownership(u),**fields})
   event('restored_start')
   def release(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7);arg=rd(u,sp+4)
    if arg==0x419f0de4:event('global_parent_release',caller=hex(rd(u,sp)))
   s.at(0x40146456,release)
   def teardown(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7)
    if rd(u,sp+4) in [0x41a720a0,0x41a720d0]:event('owner_teardown',entry=hex(pc),caller=hex(rd(u,sp)))
   for pc in [0x40152a1c,0x40152bae,0x4015141c]:s.at(pc,teardown)
   from unicorn import UC_HOOK_MEM_WRITE
   def counter_write(u,access,a,n,v,d):event('lifetime_counter_write',address=hex(a),size=n,value=v,reported_pc=hex(u.reg_read(UC_M68K_REG_PC)))
   u.hook_add(UC_HOOK_MEM_WRITE,counter_write,begin=0x419f0d70,end=0x419f0d77)""")
s=s.replace("row.update(passed=True,halted=s.halted,queue_unchanged=True,model_ms=s.now_ms())", """assert not any(x['kind'] in ['global_parent_release','owner_teardown','lifetime_counter_write'] for x in row['events'])
  assert len({json.dumps(x['ownership'],sort_keys=True) for x in row['events']})==1
  row.update(passed=True,halted=s.halted,queue_unchanged=True,model_ms=s.now_ms(),ownership_stable=True)""")
s=s.replace('Digitone-E04-PC-queued-pattern-retirement-controls.json','Digitone-E04-PC-queued-pattern-parent-lifetime.json')
exec(compile(s,'queued-parent-lifetime','exec'))
