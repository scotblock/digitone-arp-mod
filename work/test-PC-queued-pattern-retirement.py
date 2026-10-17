from pathlib import Path
exec(Path('work/test-PC-resident-storage-extended-runtime.py').read_text().split('\ntry:')[0])
results={'PC_only':True,'cases':[],'limits':['Field clear/rebind at publication is an explicit host fixture between stock queue publication and worker consumption; not naturally scheduled reset/rebind or timing evidence.','Actual stock producer, queue publisher, callback consumer and cleanup run in the existing PC engine.','No new firmware or guard is installed.']}
for mode in ['baseline','clear_after_publish','rebind_after_publish']:
 row={'mode':mode,'events':[],'injected':False,'failure':None};results['cases'].append(row);s=None;builder={'active':False};descriptor_ids=set()
 try:
  def install(s):
   u=s.m.uc
   for a,n in [(0x47be0000,1784),(0x47be3000,474),(0x47be3400,304),(0x47be3600,182),(0x47fa0000,332),(0x47fa0300,280),(0x47fa0600,492),(0x47fa0900,594),(spec['base'],spec['bytes'])]:s.m.install_isa_patches_scoped(bytes(u.mem_read(a,n)),a)
   def event(label,**fields):row['events'].append({'kind':label,'ms':s.now_ms(),**fields})
   def start(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7);obj=rd(u,sp+4);builder['active']=obj==0x41a720d0
    if builder['active']:event('builder',destination=hex(rd(u,sp+8)))
   def done(u,pc,n,d):builder['active']=False
   s.at(0x4002f80c,start);s.at(0x4002f884,done)
   def published(u,pc,n,d):
    if not builder['active']:return
    slot=u.reg_read(UC_M68K_REG_A2);descriptor=rd(u,slot)
    if not descriptor or rd(u,descriptor)!=0x41a720d0:return
    descriptor_ids.add(descriptor);event('queue_published',slot=hex(slot),descriptor=hex(descriptor),retained_destination=hex(rd(u,descriptor+4)),field=hex(rd(u,0x41a720f0)),manager=hex(rd(u,slot+8)),invoke=hex(rd(u,slot+12)))
    if not row['injected'] and mode!='baseline':
     replacement=0 if mode=='clear_after_publish' else 0x407f29f4
     u.mem_write(0x41a720f0,struct.pack('>I',replacement));row['injected']=True;event('field_fixture',replacement=hex(replacement),descriptor_unchanged=rd(u,descriptor+4)==0x407ef9f4)
   s.at(0x400a88d6,published)
   def callback(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7);slot=rd(u,sp+4);descriptor=rd(u,slot)
    if descriptor and rd(u,descriptor)==0x41a720d0 and rd(u,descriptor+4)==0x407ef9f4:
     descriptor_ids.add(descriptor);event('callback_selected',slot=hex(slot),descriptor=hex(descriptor),destination=hex(rd(u,descriptor+4)),owner_field=hex(rd(u,0x41a720f0)))
   s.at(0x4002c1d2,callback)
   def clone(u,pc,n,d):
    ptr=u.reg_read(UC_M68K_REG_D0)
    if ptr and rd(u,ptr)==0x41a720d0 and rd(u,ptr+4)==0x407ef9f4:
     descriptor_ids.add(ptr);event('descriptor_clone',descriptor=hex(ptr),retained_destination=hex(rd(u,ptr+4)))
   s.at(0x4002c25a,clone)
   def convert(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7)
    if rd(u,sp)==0x4002c1f4:event('native_conversion',destination=hex(rd(u,sp+4)),source=hex(rd(u,sp+8)),owner_field=hex(rd(u,0x41a720f0)))
   s.at(0x4000a1a6,convert)
   def retire(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7);op=rd(u,sp+12)
    if op==3:
     descriptor=rd(u,rd(u,sp+4))
     if descriptor in descriptor_ids:event('manager_destroy',descriptor=hex(descriptor))
   s.at(0x4002c1fe,retire)
   def freed(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7);ptr=rd(u,sp+4)
    if ptr in descriptor_ids:
     event('descriptor_free',descriptor=hex(ptr));descriptor_ids.remove(ptr)
   s.at(0x400e96cc,freed)
  s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x08000000,on_machine=install);s.run_ms(200);queue_before=bytes(s.m.uc.mem_read(LO,spec['storage_bytes']))
  for key in ['KEYBOARD','T1','1','T2','5','PLAY']:s.tap(s.code(key),hold_ms=100,after_ms=200)
  s.run_ms(600)
  assert s.halted is None
  kinds=[x['kind'] for x in row['events']];assert 'queue_published' in kinds and 'callback_selected' in kinds and 'native_conversion' in kinds and 'descriptor_free' in kinds
  assert kinds.index('queue_published')<kinds.index('callback_selected')<kinds.index('native_conversion')
  selected=next(x for x in row['events'] if x['kind']=='callback_selected')['descriptor'];completion=next(i for i,x in enumerate(row['events']) if x['kind']=='descriptor_free' and x['descriptor']==selected);assert kinds.index('native_conversion')<completion
  if mode!='baseline':assert row['injected'] and kinds.index('field_fixture')<kinds.index('callback_selected')
  assert all(x['destination']=='0x407ef9f4' for x in row['events'] if x['kind']=='native_conversion')
  assert bytes(s.m.uc.mem_read(LO,spec['storage_bytes']))==queue_before
  row.update(passed=True,halted=s.halted,queue_unchanged=True,model_ms=s.now_ms())
 except Exception:row.update(passed=False,failure=traceback.format_exc());print(row['failure'],flush=True)
 finally:
  if s:s.close()
 print('QUEUED CONTROL',mode,row.get('passed'),flush=True)
results['passed']=all(x['passed'] for x in results['cases']);Path('outputs/Digitone-E04-PC-queued-pattern-retirement-controls.json').write_text(json.dumps(results,indent=2))
if not results['passed']:raise SystemExit(1)

