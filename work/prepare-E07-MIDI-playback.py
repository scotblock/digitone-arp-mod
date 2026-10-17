from pathlib import Path
s=Path('work/trace-synth-arp-MIDI-lifecycle.py').read_text().replace('E06','E07')
s=s.replace("dest=Path('outputs/Digitone-synth-arp-MIDI-lifecycle.json')", "dest=Path('outputs/Digitone-E07-MIDI-native-playback.json')")
s=s.replace("cases={r['image']:r for r in startup['cases']};", "cases={r['image']:r for r in startup['cases']};cases['E07_mirror_off']=cases['E07_restored'];")
s=s.replace("for name,scenario in [('E07_restored','scale')]:", "for name,scenario in [('E07_restored','scale'),('E07_mirror_off','scale')]:")
s=s.replace("'MIDI_poll':[]", "'MIDI_poll':[],'MIDI_mirror_starts':[]")
anchor='   from unicorn import UC_HOOK_MEM_WRITE'
add='''   row['MIDI_private_state_from_copier']=hex(rd(session.m.uc,cfg['MIDI_state']));assert rd(session.m.uc,cfg['MIDI_state'])==0x53414d31
   if name=='E07_mirror_off':session.m.uc.mem_write(cfg['MIDI_state']+4,bytes(4));row['MIDI_disable_fixture']=True
   def mirror_start(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7);voice,track,ev,note,velocity=[rd(u,sp+i) for i in [4,8,12,16,20]]
    row['MIDI_mirror_starts'].append({'ms':session.now_ms(),'voice':voice,'track':track,'event':hex(ev),'note':note,'velocity':velocity,'eligible':track<4 and rd(u,cfg['MIDI_markers']+track*4)==ev})
   session.at(cfg['MIDI_entries']['ON'],mirror_start)
'''
assert anchor in s;s=s.replace(anchor,add+anchor)
s=s.replace("for r in cfg['components'])", "for r in cfg['components'] if r['name']!='MIDI_private_state_seed')")
anchor="  wav=Path('outputs',"
add='''  row['private_state_hex']=bytes(s.m.uc.mem_read(cfg['MIDI_state'],160)).hex()
  messages=[];stream=b''.join(bytes(x['bytes']) for x in row['wire']);assert len(stream)%3==0,stream.hex()
  active={};ons=[]
  for i in range(0,len(stream),3):
   status,note,velocity=stream[i:i+3];assert status&0xf0 in [0x80,0x90] and note<128 and velocity<128
   key=(status&15,note);on=status&0xf0==0x90 and velocity>0
   if on:assert key not in active,(key,messages);active[key]=True;ons.append(note)
   else:assert key in active,(key,messages);del active[key]
   messages.append({'channel':(status&15)+1,'note':note,'velocity':velocity,'on':on})
  if name=='E07_mirror_off':assert not messages
  else:assert messages and not active and set([60,62,64,65,67,69,71,72])<=set(ons),(messages,active)
  assert all(rd(s.m.uc,cfg['MIDI_records']+v*16)==0 for v in range(8))
  row['MIDI_messages']=messages;row['balanced_note_pairs']=len(ons);row['no_active_mirrored_notes_at_stop']=True;row['dropped_note_ons']=rd(s.m.uc,cfg['MIDI_state']+8);row['mirror_code_host_loaded']=False
'''
assert anchor in s;s=s.replace(anchor,add+anchor)
s=s.replace("f'Digitone-synth-arp-MIDI-{name}-{scenario}.wav'", "f'Digitone-E07-MIDI-native-{name}-{scenario}.wav'")
s=s.replace("'No physical cache, timing, DMA or hardware-ready claim.'", "'Native copying supplies MIDI code and private-state seed; tests install scoped ISA emulation and observations only. No host injects outgoing MIDI packets.','DIN output only; physical timing and USB mirroring remain outside this candidate.','No physical cache, timing, DMA or hardware-ready claim.'")
s += "\non,off=out['cases'];baseline=json.loads(Path('outputs/Digitone-E06-PC-playback-comparison.json').read_text());reference=next(r for r in baseline['cases'] if r['image']=='E06_restored' and r['scenario']=='scale');out['internal_pitches_equal_E06_and_mirror_off']=[x['pitch'] for x in on['pitches']]==[x['pitch'] for x in off['pitches']]==[x['pitch'] for x in reference['pitches']];assert out['internal_pitches_equal_E06_and_mirror_off'];dest.write_text(json.dumps(out,indent=2))\n"
Path('work/test-E07-MIDI-native-playback.py').write_text(s)
