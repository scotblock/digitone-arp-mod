"""Observe native admission, stock gates/transport setup and producer entries."""
from pathlib import Path
import json
producer_order_original_read=Path.read_text
def producer_order_source_read(path,*args,**kwargs):
 s=producer_order_original_read(path,*args,**kwargs)
 if path.name=='test-PC-native-cold-admission-startup.py':
  s=s.replace('native-cold-admission-','startup-producer-order-').replace('Digitone-E04-PC-native-cold-admission-startup.json','Digitone-E04-PC-startup-producer-order.json')
 if path.name=='test-PC-cold-permit-boundary.py':
  anchor="  row['admission_boundary_events']=[];"
  addition=r'''
  row['startup_order_events']=[];row['startup_gate_writes']=[];row['producer_entries']=[];row['producer_checkpoints']=[]
  order_stage=['cold']
  def getword(u,a):
   try:return int.from_bytes(u.mem_read(a,4),'big')
   except Exception:return None
  def inputstate(u):
   return {'admission':getword(u,0x47be2840),'READY':getword(u,0x47be1010),'PTR':getword(u,0x47be1000),'receive_gate':getword(u,0x41368d64),'note_gate':getword(u,0x41368d88),'auto_channel':getword(u,0x41368d2c),'test_mode':getword(u,0x402a0e50),'audio_vector':getword(u,0x400002fc),'DIN_vector':getword(u,0x40000270),'panel_vector':getword(u,0x40000268),'DIN_DMA_DADDR':getword(u,0xfc045490),'queue':getword(u,0x419ee22c)}
  saved_points=set();input_hook_ids={}
  def order(u,pc,n,d):
   row['startup_order_events'].append({'stage':order_stage[0],'pc':hex(pc),'instruction_estimate':done,'SR':hex(u.reg_read(UC_M68K_REG_SR)),**inputstate(u)})
   if order_stage[0]=='cold' and pc in [0x4009d0d8,0x4008d31e,0x4008d3dc,0x4008d3ec] and pc not in saved_points:
    saved_points.add(pc);checkpoint=str(root/('producer-'+hex(pc)+'.snap'))
    save(m,checkpoint,extra={'point':hex(pc),'stage':'cold','state':inputstate(u)})
    row['producer_checkpoints'].append({'pc':hex(pc),'path':checkpoint,'state':inputstate(u)})
   if pc==0x4008d3ec:u.hook_del(input_hook_ids[(order_stage[0],pc)])
  def gatewrite(u,access,a,n,v,d):
   if (a<0x41368d68 and a+n>0x41368d64) or (a<0x41368d8c and a+n>0x41368d88):
    row['startup_gate_writes'].append({'stage':order_stage[0],'pc':hex(u.reg_read(UC_M68K_REG_PC)),'address':hex(a),'bytes':n,'value':v,'instruction_estimate':done,'admission':getword(u,0x47be2840),'READY':getword(u,0x47be1010)})
  def producer(u,pc,n,d):
   if len(row['producer_entries'])<100:row['producer_entries'].append({'stage':order_stage[0],'pc':hex(pc),'instruction_estimate':done,**inputstate(u)})
  def observe_input(mm,stage):
   order_stage[0]=stage
   for at in [0x4000053e,0x40000546,0x4008d300,0x4008d308,0x4008d318,0x4009d0d8,0x400ffed0,0x4009c5d8,0x4009c650,0x4008d31e,0x4008d332,0x4008d3dc,0x4008d7ee,0x4008d814,0x4008d820,0x4008d3ee,0x40019476,0x4001947c,0x4008d3ec]:input_hook_ids[(stage,at)]=mm.uc.hook_add(UC_HOOK_CODE,order,begin=at,end=at)
   mm.uc.hook_add(UC_HOOK_MEM_WRITE,gatewrite,begin=0x41368d20,end=0x41368d8b)
   for at in [0x400eb2d2,0x400eb166,0x400eae5c,0x400eaf48,0x400ff3ec,0x40100252]:mm.uc.hook_add(UC_HOOK_CODE,producer,begin=at,end=at)
  observe_input(m,'cold')
'''
  assert anchor in s;s=s.replace(anchor,addition+'\n'+anchor)
 if path.name=='test-PC-ISA-corrected-startup.py':
  # Existing on-machine observer is invoked again for the intro checkpoint.
  old="   install_strict(mm,'intro')"
  assert old in s;s=s.replace(old,old+"\\n   observe_input(mm,'intro')")
 return s
Path.read_text=producer_order_source_read
try:exec(compile(producer_order_source_read(Path('work/test-PC-native-cold-admission-startup.py')),'startup-producer-order','exec'))
finally:Path.read_text=producer_order_original_read
