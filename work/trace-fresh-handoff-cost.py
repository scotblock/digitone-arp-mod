"""Exact uninterrupted prefix; scoped timing ablation, never flash output."""
import pathlib,os
outer=pathlib.Path('work/run-cold-cycle-complete-handoff.py').read_text().split("exec(compile(source,'cold-cycle-complete-handoff','exec'))")[0]
exec(compile(outer,'fresh-trace-source','exec'))
mode=os.environ.get('FRESH_TRACE_MODE','trace')
assert mode in ('trace','pitch-fetch-neutral')
source=source.replace("outputs/Digitone-cycle-complete-handoff",'outputs/Digitone-fresh-handoff-'+mode)
source=source.replace("work/cache-native-prepared-handoff.snap",'work/cache-fresh-'+mode+'-prepared.snap')
instrument=r'''
  from unicorn import UC_HOOK_BLOCK
  c=timed.clock;mem=timed.memtime;uc=timed.m.uc
  diag=result['fresh_cost']={'mode':MODE_DIAGNOSTIC,'window_ms':[2619,2625],'blocks':[],'memory':[],'boundaries':[],'removed_fetch_cycles':0,'pitch_active':False,'next_stores':[]}
  def focused():return 2619<=timed.now_ms()<=2625
  def point(label,pc):
   if focused():diag['boundaries'].append({'label':label,'pc':hex(pc),'cycles':c.cycles,'ms':timed.now_ms(),'vectors':[f[0] for f in c._frames],'bus_free':mem.bus.free,'memory_counts':dict(mem.counts)})
  original_fetch=mem.fetch
  def fetch(address,size):
   before,left,free=c.cycles,c.left,mem.bus.free
   answer=original_fetch(address,size)
   cost=c.cycles-before
   if focused() and RAM<=address<RAM+len(blob):
    diag['memory'].append({'kind':'fetch','pc':hex(address),'size':size,'cycles':before,'cost':cost,'bus_free_before':free})
    if MODE_DIAGNOSTIC=='pitch-fetch-neutral' and diag['pitch_active']:
     c.cycles,c.left,mem.bus.free=before,left,free
     diag['removed_fetch_cycles']+=cost
   return answer
  mem.fetch=fetch
  original_data=mem.data
  def data(address,size,write):
   before=c.cycles;answer=original_data(address,size,write)
   if focused():
    pc=uc.reg_read(UC_M68K_REG_PC)
    if RAM<=pc<RAM+len(blob):diag['memory'].append({'kind':'write' if write else 'read','pc':hex(pc),'address':hex(address),'size':size,'cycles':before,'cost':c.cycles-before})
   return answer
  mem.data=data
  previous=c._on_block
  uc.hook_del(c.hook)
  def block(uc,address,size,d):
   observe=focused();before=c.cycles;flow=c.flow_cycles;ins=c.instructions
   memory_before=sum(v for k,v in mem.counts.items() if k.endswith('_stall_cycles'))
   previous(uc,address,size,d)
   if observe:
    stall=sum(v for k,v in mem.counts.items() if k.endswith('_stall_cycles'))-memory_before
    if MODE_DIAGNOSTIC=='pitch-fetch-neutral' and diag['pitch_active'] and RAM<=address<RAM+len(blob):stall=0
    diag['blocks'].append({'pc':hex(address),'size':size,'cycles':before,'cost':c.cycles-before,'fetch_cycles':stall,'instructions':c.instructions-ins,'flow_cycles':c.flow_cycles-flow,'helper':RAM<=address<RAM+len(blob),'vectors':[f[0] for f in c._frames]})
  c.hook=uc.hook_add(UC_HOOK_BLOCK,block)
  def enter(uc,pc,n,d):diag['pitch_active']=True;point('pitch_entry',pc)
  def leave(uc,pc,n,d):point('pitch_output',pc);diag['pitch_active']=False
  timed.at(0x4009df9a,enter);timed.at(0x4009dfa8,leave)
  for pc,label in [(0x4009dd80,'acceptance'),(0x4009dda6,'before'),(0x4009de46,'commit'),(0x4009c838,'render_entry'),(0x4009ba70,'render_return')]:
   timed.at(pc,lambda uc,pc,n,d,label=label:point(label,pc))
  for name,item in layout.items():
   timed.at(item['address'],lambda uc,pc,n,d,name=name:point('helper_'+name,pc))
  waiting={};prior_sink=timed.ev['ssi0_dma'].sink
  def capture(raw):
   prior_sink(raw)
   item=result['DMA_captures'][-1]
   if focused() and not item['all_words_fresh']:
    item['pc']=hex(uc.reg_read(UC_M68K_REG_PC));item['vectors']=[f[0] for f in c._frames]
    for a in range(int(item['start'],16),int(item['start'],16)+item['bytes'],4):waiting.setdefault(a,[]).append(item)
  timed.ev['ssi0_dma'].sink=capture
  def store(uc,access,a,n,value,d):
   if focused():
    for word in range(a,a+n,4):
     for cap in waiting.pop(word,[]):diag['next_stores'].append({'word':hex(word),'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'capture_cycles':cap['cycles'],'store_cycles':c.cycles,'lateness_cycles':c.cycles-cap['cycles']})
  uc.hook_add(UC_HOOK_MEM_WRITE,store,begin=0x80001000,end=0x80002fff)
'''.replace('MODE_DIAGNOSTIC',repr(mode))
needle=" s=Session(str(checkpoint)"
assert needle in source
source=source.replace(needle,instrument+'\n'+needle)
# Exact predecessor workload, but end immediately after the disputed window.
a=source.index(" session.run_ms(700);mark('queued note observation after handoff');")
b=source.index(' now=bytes(session.m.uc.mem_read(RAM,0x20000))',a)
source=source[:a]+" session.run_ms(max(0,2630-session.now_ms()));mark('first fresh timing window completed')\n"+source[b:]
exec(compile(source,'fresh-handoff-cost','exec'))
