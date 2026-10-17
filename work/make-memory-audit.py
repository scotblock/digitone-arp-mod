import pathlib
s=pathlib.Path('work/measure-cache-sensitivity.py').read_text()
s=s.replace("ssi=session.ev['ssi0_dma'];sink=ssi.sink",'''# Data-cache occupancy observation: counts costs but does not alter scheduling.
  from unicorn import UC_HOOK_MEM_READ
  data_cache=RoundRobinCache();dirty=set();data_records={};data_totals=collections.Counter()
  rec['data_cache_windows']=[]
  def memory(uc,access,addr,n,value,d):
   clock=getattr(session,'clock',None)
   if clock is None:return
   frame=next((f for f in clock._frames if f[0]==191),None)
   current=data_records.setdefault(frame[1],collections.Counter()) if frame else None
   cached=0x40000000<=addr<0x48000000
   changes=collections.Counter(accesses=1)
   if not cached:changes['uncached_accesses']=1
   else:
    for line in range(addr//16,(addr+n-1)//16+1):
     index=line%128;row=data_cache.tags[index];write=access==17
     if line in row:changes['hits']+=1
     else:
      changes['fills']+=1
      slot=row.index(None) if None in row else data_cache.next[index]
      evicted=row[slot]
      if evicted in dirty:changes['dirty_evictions']+=1;dirty.remove(evicted)
      row[slot]=line;data_cache.next[index]=(slot+1)%4
     if write:dirty.add(line)
   data_totals.update(changes)
   if current is not None:current.update(changes)
  uc.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,memory,begin=0x40000000,end=0x7fffffff)
  rec['_data_records']=data_records;rec['_data_totals']=data_totals
  ssi=session.ev['ssi0_dma'];sink=ssi.sink''')
s=s.replace("try:\n  session.run_ms(20)",'''original_exit=session.clock._exit_frame
 def exit_frame():
  if session.clock._frames and session.clock._frames[-1][0]==191:
   frame=session.clock._frames[-1];counts=rec['_data_records'].pop(frame[1],collections.Counter())
   rec['data_cache_windows'].append(dict(start_cycles=frame[1],wall_cycles=session.clock.cycles-frame[1],**counts))
  return original_exit()
 session.clock._exit_frame=exit_frame
 try:
  session.run_ms(20)''')
s=s.replace("finally:session.close();persist()","finally:\n  rec['data_access_totals']=dict(rec.pop('_data_totals',{}));rec.pop('_data_records',None)\n  session.close();persist()")
pathlib.Path('work/measure-memory-sensitivity.py').write_text(s)
