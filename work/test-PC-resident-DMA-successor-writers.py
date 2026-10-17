from pathlib import Path
# Reuse workload/snapshot configuration while auditing the actual Python DMA
# execution path, not partial programming writes or the native fast engine.
text=Path('work/test-PC-resident-storage-extended-runtime.py').read_text()
text=text.replace("from emu import edma_sw", "from emu import edma_sw\nold_install_bank=edma_sw.install_bank\ndef traced_bank(*args,**kwargs):\n kwargs['native']=False;return old_install_bank(*args,**kwargs)\nedma_sw.install_bank=traced_bank")
text=text.replace("'failure':None};s=None", "'failure':None,'DMA_executions':{},'DMA_successors':{},'bulk_callers':{},'DMA_link_targets':{}};s=None")
# Eliminate the noisy partial-TCD observer; actual software _run and SSI
# major completion below are the sources of descriptor evidence.
text=text.replace("  for ch in range(64):descriptor(ch,bytes(u.mem_read(0xfc045000+ch*32,32)),'initial live configuration')", "  report['DMA_fast_native_disabled_for_audit']=True")
text=text.replace("  u.hook_add(UC_HOOK_MEM_WRITE,sample,begin=0xfc045000,end=0xfc0457ff)", "  # Partial programming observations deliberately excluded.")
start=text.index("  bank=s.ev.get('edma_sw_bank')");end=text.index("  for pc in [0x400004e8",start)
replacement="""  def executed(channel,td,origin):
   descriptor(channel,struct.pack(edma_sw.TCD_FMT,*td),origin)
   report['DMA_executions'][str(channel)]=report['DMA_executions'].get(str(channel),0)+1
   minor=edma_sw.link_channel(td[6]);major=((td[10]>>8)&63) if td[10]&32 else None
   for kind,target in [('minor',minor),('major',major)]:
    if target is not None:
     key=kind+':'+str(channel)+'->'+str(target);report['DMA_link_targets'][key]=report['DMA_link_targets'].get(key,0)+1
     if target!=channel:descriptor(target,bytes(u.mem_read(0xfc045000+target*32,32)),'linked target concrete configuration')
   if td[10]&16:
    pointer=td[8];raw=bytes(u.mem_read(pointer,32));next_td=struct.unpack(edma_sw.TCD_FMT,raw);key=str(channel)+':'+hex(pointer)+':'+raw.hex()
    report['DMA_successors'].setdefault(key,{'channel':channel,'origin':origin,'pointer':hex(pointer),'readable':True,'aligned':pointer%32==0,'descriptor_overlaps_queue':overlaps(pointer,32),'loaded_next_destination':hex(next_td[5]),'next_ESG':bool(next_td[10]&16),'count':0})['count']+=1
    descriptor(channel,raw,'concrete successor read at execution')
  bank=s.ev['edma_sw_bank'];assert bank._native is None
  for channel in bank.channels.values():
   previous=channel._run
   def run(td,ensure=True,channel=channel,previous=previous):executed(channel.channel,list(td),'software _run before payload');return previous(td,ensure)
   channel._run=run
  audio=s.ev['ssi0_dma'];previous_major=audio._complete_major
  def major(channel,source,dest,biter):
   executed(channel,list(struct.unpack(edma_sw.TCD_FMT,u.mem_read(0xfc045000+channel*32,32))),'SSI actual major completion')
   return previous_major(channel,source,dest,biter)
  audio._complete_major=major
"""
text=text[:start]+replacement+text[end:]
text=text.replace("report['bulk_calls'][label]+=1", "report['bulk_calls'][label]+=1\n    caller=rd(u,sp);canonical=0x40000000+(dest-0x40000000)%0x08000000 if 0x40000000<=dest<0x80000000 else dest\n    key=label+':'+hex(caller);row=report['bulk_callers'].setdefault(key,{'kind':label,'return':hex(caller),'calls':0,'min_destination':hex(canonical),'max_end':hex(canonical+size),'max_bytes':0})\n    row['calls']+=1;row['min_destination']=hex(min(int(row['min_destination'],16),canonical));row['max_end']=hex(max(int(row['max_end'],16),canonical+size));row['max_bytes']=max(row['max_bytes'],size)")
text=text.replace('s.run_ms(1500)','s.run_ms(300)').replace('s.run_ms(2000)','s.run_ms(400)')
text=text.replace(" assert not any(v['overlaps_queue'] for v in report['DMA'].values())", " assert not any(v['overlaps_queue'] for v in report['DMA'].values())\n assert not any(v['descriptor_overlaps_queue'] or not v['aligned'] for v in report['DMA_successors'].values())\n bank=s.ev['edma_sw_bank']\n report['software_DMA_refused']=bank.refused;report['software_DMA_errors']=bank.errors();report['minor_links_ignored']=sum(c.links_ignored for c in bank.channels.values());report['software_DMA_links_followed']=sum(c.links_followed for c in bank.channels.values())")
# Property errors/refused names are verified before report consumption.
text=text.replace("s.run_ms(2000);after=rd(u,0x4138f214)","s.run_ms(400);after=rd(u,0x4138f214)\n for wait in range(8):\n  if after!=before:break\n  s.run_ms(500);after=rd(u,0x4138f214)")
text=text.replace('Digitone-E04-PC-resident-storage-extended-runtime.json','Digitone-E04-PC-resident-DMA-successor-writers.json')
text=text.replace("s.run_ms(400);after=rd(u,0x4138f214)","s.run_ms(400);after=rd(u,0x4138f214)\n for wait in range(8):\n  if after!=before:break\n  s.run_ms(500);after=rd(u,0x4138f214)",1)
exec(compile(text,'actual-DMA-successor-writers','exec'))


