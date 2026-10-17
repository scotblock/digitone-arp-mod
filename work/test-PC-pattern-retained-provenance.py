from pathlib import Path
source=Path('work/test-PC-resident-storage-extended-runtime.py').read_text()
start=source.index('  for ch in range(64):');end=source.index('  for pc in [0x400004e8',start);source=source[:start]+source[end:]
source=source.replace("'failure':None};s=None","'failure':None,'retained_construction':[],'retained_callbacks':[],'pattern_entries':[]};s=None")
insert='''  def constructed(u,pc,n,d):
   sp=u.reg_read(UC_M68K_REG_A7);args=struct.unpack('>III',u.mem_read(sp,12));report['retained_construction'].append({'caller':hex(args[0]),'object':hex(args[1]),'retained_destination':hex(args[2]),'sp':hex(sp),'a6':hex(u.reg_read(UC_M68K_REG_A6))})
  def callback(u,pc,n,d):
   sp=u.reg_read(UC_M68K_REG_A7);slot=rd(u,sp+4);descriptor=rd(u,slot);report['retained_callbacks'].append({'caller':hex(rd(u,sp)),'slot':hex(slot),'descriptor':hex(descriptor),'source_object':hex(rd(u,descriptor)),'retained_destination':hex(rd(u,descriptor+4)),'sp':hex(sp)})
  def pattern(u,pc,n,d):
   sp=u.reg_read(UC_M68K_REG_A7);args=struct.unpack('>IIII',u.mem_read(sp,16));descriptor=u.reg_read(UC_M68K_REG_A2)
   report['pattern_entries'].append({'caller':hex(args[0]),'destination':hex(args[1]),'source':hex(args[2]),'descriptor':hex(descriptor),'descriptor_destination':hex(rd(u,descriptor+4)),'caller_a6':hex(u.reg_read(UC_M68K_REG_A6))})
  s.at(0x4002f80c,constructed);s.at(0x4002c1d2,callback);s.at(0x4000a1a6,pattern)
'''
source=source.replace('  for entry,label in',insert+'  for entry,label in')
source=source.replace("s.run_ms(2000);after=rd(u,0x4138f214)","s.run_ms(2000);after=rd(u,0x4138f214)\n for wait in range(8):\n  if after!=before:break\n  s.run_ms(500);after=rd(u,0x4138f214)")
source=source.replace(" assert not any(v['overlaps_queue'] for v in report['DMA'].values())", " assert before!=after\n assert report['pattern_entries']\n assert all(x['destination']==x['descriptor_destination'] for x in report['pattern_entries'])")
source=source.replace('Digitone-E04-PC-resident-storage-extended-runtime.json','Digitone-E04-PC-pattern-retained-provenance-runtime.json')
exec(compile(source,'retained-pattern-provenance','exec'))
