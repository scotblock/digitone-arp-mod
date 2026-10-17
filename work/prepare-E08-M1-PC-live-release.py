from pathlib import Path
p=Path('work/test-E08-M1-PC-prototype.py').read_text()
p=p.replace("'clock_samples':[]}","'clock_samples':[],'live_inputs':[]}")
p=p.replace("if kind==4 or (s.profile.transport_state and rd(u,s.profile.transport_state)!=1):", "if kind==4 or (not state['active'].get('live') and s.profile.transport_state and rd(u,s.profile.transport_state)!=1):")
p=p.replace("elif due(now,state['active']['expiry']):", "elif state['active']['expiry'] is not None and due(now,state['active']['expiry']):")
needle="  if kind in [0,1] and v[1]==0 and v[2]==1 and v[4]>=3:"
extra="""  if state['phase']=='UP_live_release' and kind in [0,1] and v[1]==0 and v[11]==2 and v[4]==1:
   raw=bytes(u.mem_read(a,52));note=raw[0x14];on=v[2]==1;held=state.setdefault('held',set())
   out['live_inputs'].append({'ms':s.now_ms(),'note':note,'on':on,'raw':raw.hex()})
   if on:
    held.add(note)
    if state['active'] is None:state['active']={'notes':sorted(held),'index':0,'template':raw,'next':now,'interval':5400000,'gate':1350000,'expiry':None,'live':True}
    else:state['active']['notes']=sorted(held)
    u.mem_write(a+0x10,bytes(4))
   else:
    held.discard(note)
    if not held:
     out['cancellations'].append({'phase':state['phase'],'reason':'native_source_key_release','ms':s.now_ms()});state['active']=None
    elif state['active']:state['active']['notes']=sorted(held)
   return
"""
p=p.replace(needle,extra+needle)
a=p.index(' # Native MIDI input and grid recording create the chord;');z=p.index(" out['MIDI_received']=",a)
p=p[:a]+""" state['phase']='UP_live_release';begin=s.now_ms();startwire=len(out['wire'])
 send([0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100])
 for _ in range(80):
  count=sum(1 for x in out['wire'][startwire:] for i in range(0,len(x['bytes']),3) if x['bytes'][i]&240==144 and x['bytes'][i+2]>0)
  if count>=3:break
  s.run_ms(10)
 assert count>=3,'live arp did not emit three notes'
 s.run_ms(10);release_request=s.now_ms()
 send([0x80|channel,60,0,0x80|channel,64,0,0x80|channel,67,0]);s.run_ms(450)
 out['phases'].append({'phase':'UP_live_release','begin_ms':begin,'release_request_ms':release_request,'end_ms':s.now_ms(),'wire':out['wire'][startwire:],'active_scheduler_at_end':state['active'] is not None,'held_at_end':sorted(state.get('held',[]))});mark('live source release complete')
"""+p[z:]
p=p.replace('Digitone-E08-M1-PC-prototype.json','Digitone-E08-M1-PC-live-release.json')
Path('work/test-E08-M1-PC-live-release.py').write_text(p)
