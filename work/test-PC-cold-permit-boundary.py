"""Passive loader-derived startup trace; marker is fixture data, not integration."""
from pathlib import Path
import json
boundary_original_read=Path.read_text
def boundary_source_read(path,*args,**kwargs):
 s=boundary_original_read(path,*args,**kwargs)
 if path.name=='test-PC-atomic-storage-startup.py':
  s=s.replace('atomic-storage-startup-','cold-permit-boundary-').replace('Digitone-E04-PC-atomic-storage-startup.json','Digitone-E04-PC-cold-permit-boundary.json')
 if path.name=='test-PC-ISA-corrected-startup.py':
  anchor="  install_strict(m,'cold')"
  addition=r'''
  row['admission_boundary_events']=[];row['admission_word_writes']=[];row['cold_marker_fixture_only']=True
  def boundary(uc,pc,size,data):
   sp=uc.reg_read(UC_M68K_REG_A7)
   try:value=int.from_bytes(uc.mem_read(0x47be2840,4),'big')
   except Exception:value=None
   try:ret=hex(int.from_bytes(uc.mem_read(sp,4),'big'))
   except Exception:ret=None
   event={'pc':hex(pc),'SR':hex(uc.reg_read(UC_M68K_REG_SR)),'SP':hex(sp),'stack_return':ret,'admission_word':hex(value) if value is not None else None,'estimated_instructions':done}
   if pc==0x4029c518:
    assert event['stack_return']=='0x4000053e' and value==0
    assert bytes(uc.mem_read(0x47be0000,len(payload)))[:0x1000]==payload[:0x1000]
    # Marker measures lifetime only. No native admission helper is installed.
    uc.mem_write(0x47be2840,struct.pack('>I',0x434f4c44));event['fixture_marker_seeded']=True
   elif pc==0x400ffed0:
    event['initializer_argument']=int.from_bytes(uc.mem_read(sp+4,4),'big')
    assert value==0x434f4c44 and event['stack_return']=='0x4009c5aa' and event['initializer_argument']==158
   row['admission_boundary_events'].append(event)
  for at in [0x400004e8,0x4029c4b0,0x4029c518,0x40001df4,0x4000053e,0x40000542,0x40000546,0x4009d0d8,0x4009c5ae,0x4009c5a0,0x400ffed0,0x4009c5aa,0x4009c5d8,0x4009c650]:
   m.uc.hook_add(UC_HOOK_CODE,boundary,begin=at,end=at)
  def wordwrite(uc,access,a,n,v,data):
   if a<0x47be2844 and a+n>0x47be2840:row['admission_word_writes'].append({'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'address':hex(a),'size':n,'value':v})
  m.uc.hook_add(UC_HOOK_MEM_WRITE,wordwrite,begin=0x47be2800,end=0x47be2843)
'''
  assert anchor in s;s=s.replace(anchor,addition+'\n'+anchor)
 return s
Path.read_text=boundary_source_read
try:exec(compile(boundary_source_read(Path('work/test-PC-atomic-storage-startup.py')),'passive-cold-permit-boundary','exec'))
finally:Path.read_text=boundary_original_read
result_path=Path('outputs/Digitone-E04-PC-cold-permit-boundary.json')
result=json.loads(result_path.read_text())
for row in result['cases']:
 assert row['passed']
 assert len([e for e in row['admission_boundary_events'] if e['pc']=='0x4029c518'])==1
 assert len([e for e in row['admission_boundary_events'] if e['pc']=='0x400ffed0'])==1
 assert row['admission_word_writes']==[{'pc':'0x4029c4c2','address':'0x47be2840','size':4,'value':0}]
 row['cold_marker_survives_to_initializer']=True
result_path.write_text(json.dumps(result,indent=2))
