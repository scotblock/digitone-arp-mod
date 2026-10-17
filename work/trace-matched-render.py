"""Stock/full replay from one unchanged prepared snapshot; PC-only probes."""
import pathlib,os
outer=pathlib.Path('work/run-cold-cycle-complete-handoff.py').read_text().split("exec(compile(source,'cold-cycle-complete-handoff','exec'))")[0]
exec(compile(outer,'matched-render-source','exec'))
mode=os.environ.get('MATCHED_RENDER_MODE','stock')
assert mode in ('stock','full')
source=source.replace('outputs/Digitone-cycle-complete-handoff','outputs/Digitone-matched-render-'+mode)
if mode=='stock':
 source=source.replace("MODE='all'","MODE='stock'")
 source=source.replace(" result['PC_runtime_extension_installed']=False", " if MODE=='stock':\n  for site in [0x4009344e,0x40093892]:uc.mem_write(site,stock[site-base:site-base+6])\n result['PC_runtime_extension_installed']=False")
 source=source.replace("  assert bytes(uc.mem_read(site,6))==bytes.fromhex(opcode)+u32(target)","  assert bytes(uc.mem_read(site,6)) in (bytes.fromhex(opcode)+u32(target),stock[site-base:site-base+6])")
a=source.index(' from emu import snapshot\n');b=source.index(' def timed_install(timed):',a)
source=source[:a]+''' checkpoint=pathlib.Path('work/cache-fresh-trace-prepared.snap')
 result['prepared_checkpoint']={'path':str(checkpoint),'sha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest(),'shared_stock_full_start':True,'native_copy_paste_completed':True,'transport_stopped':True,'new_guest_preparation':False}
 if s:s.close()
'''+source[b:]
a=source.index('\ntry:\n session=Session(')+len('\ntry:\n')
b=source.index(' session=enable_timing(session)\n',a)
source=source[:a]+' session=None\n'+source[b:]
probe=r'''
  from unicorn import UC_HOOK_BLOCK
  c=timed.clock;mem=timed.memtime;uc=timed.m.uc
  result['loaded_root_scale']={hex(backing):[[bytes(uc.mem_read(backing+t*0x3d0+0x3cb,1))[0],struct.unpack('b',uc.mem_read(backing+t*0x3d0+0x3ce,1))[0]] for t in range(4)] for backing in [0x407c61e9,0x407b00cc]}
  result['root_scale_fixture']={'old_backing':'0x407c61e9','new_backing':'0x407b00cc','old_root':61,'old_raw_scale':0,'new_root':59,'new_raw_scale':5,'metadata_injection':False,'inherited_native_preparation':True}
  lo,hi=2617*264000,2625*264000
  obs=result['matched_probe']={'mode':PROBE_MODE,'window_core_cycles':[lo,hi],'blocks':[],'data':[],'stores':[],'captures':[],'points':[],'interrupts':[]}
  def active():return lo<=c.cycles<=hi
  def stamp():return {'cycles':c.cycles,'timer_cycles':timed.pits.now-timed._t0,'frames':[list(f) for f in c._frames]}
  def point(label,pc):
   if active():
    e=uc.reg_read(UC_M68K_REG_A3)
    item={**stamp(),'label':label,'pc':hex(pc),'memory_counts':dict(mem.counts),'bus_counts':dict(mem.bus.counts),'queue_clock':rd(uc,0x413360e8),'TX_TCD':bytes(uc.mem_read(timed.ev['ssi0_dma']._tcd(timed.ev['ssi0_dma'].p.tx_chan),32)).hex()}
    if label in ('pitch_entry','acceptance'):item.update(event=hex(e),fields=bytes(uc.mem_read(e,72)).hex())
    obs['points'].append(item)
  previous=c._on_block;uc.hook_del(c.hook)
  def block(uc,pc,size,d):
   if not active():return previous(uc,pc,size,d)
   before=c.cycles;ins=c.instructions;flow=c.flow_cycles
   memory=sum(v for k,v in mem.counts.items() if k.endswith('_stall_cycles'))
   previous(uc,pc,size,d)
   obs['blocks'].append({'cycles':before,'pc':hex(pc),'size':size,'cost':c.cycles-before,'instructions':c.instructions-ins,'fetch_cycles':sum(v for k,v in mem.counts.items() if k.endswith('_stall_cycles'))-memory,'flow_cycles':c.flow_cycles-flow,'frames':[list(f) for f in c._frames]})
  c.hook=uc.hook_add(UC_HOOK_BLOCK,block)
  previous_data=mem.data
  def data(a,n,write):
   if not active():return previous_data(a,n,write)
   before=c.cycles;counts=dict(mem.counts);answer=previous_data(a,n,write)
   if c.cycles!=before:obs['data'].append({'cycles':before,'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'address':hex(a),'size':n,'write':write,'cost':c.cycles-before,'charges':{k:v-counts.get(k,0) for k,v in mem.counts.items() if k.endswith('_stall_cycles') and v!=counts.get(k,0)}})
   return answer
  mem.data=data
  for pc,label in [(0x4009dd80,'acceptance'),(0x4009df9a,'pitch_entry'),(0x4009dfa8,'pitch_output'),(0x4009c838,'render_body_entry'),(0x4009ba1c,'audio_IRQ_body')]:
   timed.at(pc,lambda uc,pc,n,d,label=label:point(label,pc))
  old_raise=c._raise_vector
  def raised(vec,from_instruction=False,level=None):
   before=c.cycles;answer=old_raise(vec,from_instruction=from_instruction,level=level)
   if active():obs['interrupts'].append({**stamp(),'kind':'entry','vector':vec,'taken':answer,'cycle_before':before,'from_instruction':from_instruction})
   return answer
  timed.m.raise_vector=raised
  old_exit=c._exit_frame
  def exited():
   if active() and c._frames:obs['interrupts'].append({**stamp(),'kind':'exit','vector':c._frames[-1][0]})
   return old_exit()
  c._exit_frame=exited
  def stored(uc,access,a,n,value,d):
   if active():obs['stores'].append({**stamp(),'address':hex(a),'size':n,'value':hex(value),'pc':hex(uc.reg_read(UC_M68K_REG_PC))})
  uc.hook_add(UC_HOOK_MEM_WRITE,stored,begin=0x80001000,end=0x80002fff)
'''.replace('PROBE_MODE',repr(mode))
source=source.replace(' s=Session(str(checkpoint)',probe+'\n s=Session(str(checkpoint)')
# Install capture observation after the original freshness observer exists.
source=source.replace(" result['marks']=[]\n import threading,time",''' result['marks']=[]
 previous_sink=s.ev['ssi0_dma'].sink
 def observed_capture(raw):
  previous_sink(raw)
  if active():obs['captures'].append({**stamp(),**result['DMA_captures'][-1],'payload':raw.hex(),'pc':hex(s.m.uc.reg_read(UC_M68K_REG_PC))})
 s.ev['ssi0_dma'].sink=observed_capture
 import threading,time''')
# obs/active/stamp are local to timed_install: expose only these probe handles.
source=source.replace("  c._exit_frame=exited", "  c._exit_frame=exited\n  timed._matched_handles=(obs,active,stamp)")
source=source.replace(" previous_sink=s.ev['ssi0_dma'].sink", " obs,active,stamp=s._matched_handles\n previous_sink=s.ev['ssi0_dma'].sink")
a=source.index(" session.run_ms(700);mark('queued note observation after handoff');")
b=source.index(' now=bytes(session.m.uc.mem_read(RAM,0x20000))',a)
source=source[:a]+" session.run_ms(max(0,2630-session.now_ms()));mark('matching render interval completed')\n"+source[b:]
exec(compile(source,'matched-render-replay','exec'))
