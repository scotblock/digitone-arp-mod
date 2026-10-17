from pathlib import Path
p=Path('work/test-E08-M1-PC-prototype.py').read_text()
p=p.replace("'prototype_kind':'Host-assisted PC scheduler feeding native guest MIDI task; not a machine-code patch'", "'prototype_kind':'Native ColdFire scheduler, consumer and retirement hooks; host configuration/input fixtures only'")
p=p.replace("'clock_samples':[]}","'clock_samples':[],'native_helper_observations':[]}")
p=p.replace("def rd(u,a):", "native=json.loads(Path('work/os144/E08-PC-native-M1-layout.json').read_text());native_blob=Path('work/os144/E08-PC-native-M1-code.bin').read_bytes()\nfrom emu.harness import call as native_call\n\ndef rd(u,a):")
a=p.index(' s.m.ensure(ARENA)');z=p.index(' mo=midi.MidiOut(',a)
p=p[:a]+''' for address in [native['base'],native['state'],native['arena'],0x47be7f00]:s.m.ensure(address)
 s.m.uc.mem_write(native['base'],native_blob)
 for r in native['regions']:
  s.m.install_isa_patches_scoped(native_blob[r['base']-native['base']:r['base']-native['base']+r['bytes']],r['base'])
 for h in native['hooks']:
  assert bytes(s.m.uc.mem_read(h['site'],h['length'])).hex()==h['original'],h
  s.m.uc.mem_write(h['site'],bytes.fromhex(h['replacement']))
 regs=list(range(UC_M68K_REG_D0,UC_M68K_REG_D0+8))+list(range(UC_M68K_REG_A0,UC_M68K_REG_A0+8))+[UC_M68K_REG_SR,UC_M68K_REG_PC]
 saved={reg:s.m.uc.reg_read(reg) for reg in regs}
 native_call(s.m,native['entries']['init'],[s.profile.transport_state],stack_top=0x47be7f00,limit=30000)
 s.m.uc.reg_write(UC_M68K_REG_SR,saved[UC_M68K_REG_SR])
 for reg,value in saved.items():
  if reg!=UC_M68K_REG_SR:s.m.uc.reg_write(reg,value)
 assert rd(s.m.uc,native['state'])==0x4d314131
 out['native_initialization_executed']=True
 def queue_observe(u,pc,n,d):
  a=u.reg_read(UC_M68K_REG_A2)
  if a==native['arena']:return
  v=[rd(u,a+i*4) for i in range(13)]
  if state['phase'] in ['OFF','UP_release','UP_stop'] and v[0] in [0,1] and v[1]==0 and v[2]==1 and v[4]>=3:
   assert v[7]>0
   u.mem_write(a+0x1c,struct.pack('>I',v[7]*8))
   out['captures'].append({'phase':state['phase'],'ms':s.now_ms(),'notes':list(u.mem_read(a+20,v[4])),'native_base_gate':v[7],'source_gate_fixture_multiplier':8})
 s.at(0x400f40b4,queue_observe)
 def observe(u,pc,n,d):
  if len(out['native_helper_observations'])<100:out['native_helper_observations'].append({'phase':state['phase'],'pc':hex(pc),'ms':s.now_ms(),'active':rd(u,native['state']+8),'count':rd(u,native['state']+16)})
 for entry in [native['entries']['emit'],native['entries']['retire']]:s.at(entry,observe)
''' +p[z:]
p=p.replace("state={'phase':'setup','active':None}","state={'phase':'setup'}")
p=p.replace("state['phase']=phase;state['active']=None;begin=", "state['phase']=phase;s.m.uc.mem_write(native['state']+4,struct.pack('>I',0 if phase=='OFF' else 1));begin=")
p=p.replace("'active_scheduler_at_end':state['active'] is not None", "'active_scheduler_at_end':rd(s.m.uc,native['state']+8)!=0,'native_counters':[rd(s.m.uc,native['state']+i) for i in [48,52,56,60]],'arena_busy_at_end':rd(s.m.uc,native['state']+280)")
needle=" out['MIDI_received']=mi.received"
extra=""" state['phase']='UP_live_release';begin=s.now_ms();startwire=len(out['wire']);live_inputs_before=mi.delivered
 send([0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100])
 for _ in range(80):
  count=sum(1 for x in out['wire'][startwire:] for i in range(0,len(x['bytes']),3) if x['bytes'][i]&240==144 and x['bytes'][i+2]>0)
  if count>=3:break
  s.run_ms(10)
 assert count>=3,'native live arp did not emit three notes'
 s.run_ms(10);release_request=s.now_ms()
 send([0x80|channel,60,0,0x80|channel,64,0,0x80|channel,67,0]);s.run_ms(450)
 out['phases'].append({'phase':'UP_live_release','begin_ms':begin,'release_request_ms':release_request,'end_ms':s.now_ms(),'wire':out['wire'][startwire:],'active_scheduler_at_end':rd(s.m.uc,native['state']+8)!=0,'native_counters':[rd(s.m.uc,native['state']+i) for i in [48,52,56,60]],'arena_busy_at_end':rd(s.m.uc,native['state']+280),'native_held_count_at_end':rd(s.m.uc,native['state']+16)});mark('native live release complete')
 for h in native['hooks']:assert bytes(s.m.uc.mem_read(h['site'],h['length'])).hex()==h['replacement']
 for r in native['regions']:assert bytes(s.m.uc.mem_read(r['base'],r['bytes']))==native_blob[r['base']-native['base']:r['base']-native['base']+r['bytes']]
 out['native_code_preserved']=True;out['native_state_final']=bytes(s.m.uc.mem_read(native['state'],320)).hex()
"""
p=p.replace(needle,extra+needle).replace('Digitone-E08-M1-PC-prototype.json','Digitone-E08-M1-native-playback.json')
Path('work/test-E08-M1-native-playback.py').write_text(p)
