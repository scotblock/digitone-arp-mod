from pathlib import Path
source=Path('work/test-PC-resident-storage-extended-runtime.py').read_text()
source=source.replace("'failure':None};s=None", "'failure':None,'pattern_entries':[],'buffer_entries':[],'buffer_allocations':[],'target_copies':[]};s=None")
insert='''  def pattern_entry(u,pc,n,d):
   sp=u.reg_read(UC_M68K_REG_A7);args=struct.unpack('>IIII',u.mem_read(sp,16));report['pattern_entries'].append({'caller':hex(args[0]),'destination_base':hex(args[1]),'source_base':hex(args[2]),'mode':args[3],'sp':hex(sp)})
  def buffer_entry(u,pc,n,d):
   sp=u.reg_read(UC_M68K_REG_A7);args=struct.unpack('>IIII',u.mem_read(sp,16));report['buffer_entries'].append({'caller':hex(args[0]),'source_start':hex(args[1]),'source_end':hex(args[2]),'allocator_arg':hex(args[3]),'sp':hex(sp)})
  def allocated(u,pc,n,d):
   header=u.reg_read(UC_M68K_REG_D0);sp=u.reg_read(UC_M68K_REG_A7);request=rd(u,sp);frame=u.reg_read(UC_M68K_REG_A6);caller=rd(u,frame+4);capacity=u.reg_read(UC_M68K_REG_D2)
   report['buffer_allocations'].append({'caller':hex(caller),'header':hex(header),'request':request,'capacity':capacity,'heap_bounded':0x419f20a0<=header and header+request<=0x429f20a0})
  s.at(0x4000a1a6,pattern_entry);s.at(0x4018ab1a,buffer_entry);s.at(0x401893bc,allocated)
'''
source=source.replace("  for entry,label in",insert+"  for entry,label in")
source=source.replace("report['bulk_calls'][label]+=1", """report['bulk_calls'][label]+=1
    caller=rd(u,sp)
    if caller in [0x4000a4a6,0x4000a4b8,0x4018ab94]:
     a2=u.reg_read(UC_M68K_REG_A2);a4=u.reg_read(UC_M68K_REG_A4);row={'caller':hex(caller),'destination':hex(dest),'other':hex(other),'bytes':size,'a2':hex(a2),'a4':hex(a4),'queue_overlap':overlaps(dest,size)}
     if caller==0x4018ab94:
      matches=[x for x in report['buffer_allocations'] if int(x['header'],16)==a4 and x['caller'] in ['0x4018ab46','0x4018ab7c']]
      row['allocation_match']=bool(matches);row['destination_matches_header']=dest==a4+12
      if matches:row['capacity']=matches[-1]['capacity'];row['fits_allocation_with_terminator']=size+13<=matches[-1]['request'];row['heap_bounded']=matches[-1]['heap_bounded']
     else:
      matches=[x for x in report['pattern_entries'] if int(x['destination_base'],16)==a2];row['entry_match']=bool(matches)
      if matches:row['entry']=matches[-1]
     report['target_copies'].append(row)""")
source=source.replace("s.run_ms(2000);after=rd(u,0x4138f214)","s.run_ms(2000);after=rd(u,0x4138f214)\n for wait in range(8):\n  if after!=before:break\n  s.run_ms(500);after=rd(u,0x4138f214)")
source=source.replace(" assert not any(v['overlaps_queue'] for v in report['DMA'].values())", """ assert not any(v['overlaps_queue'] for v in report['DMA'].values())
 assert before!=after
 assert report['target_copies']
 for row in report['target_copies']:
  if row['caller']=='0x4018ab94':assert row['allocation_match'] and row['destination_matches_header'] and row['fits_allocation_with_terminator'] and row['heap_bounded']
  else:assert row['entry_match']""")
source=source.replace('Digitone-E04-PC-resident-storage-extended-runtime.json','Digitone-E04-PC-copy-pointer-provenance-runtime.json')
exec(compile(source,'copy-pointer-provenance','exec'))
