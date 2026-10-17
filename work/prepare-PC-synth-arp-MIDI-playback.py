from pathlib import Path
s=Path('work/trace-synth-arp-MIDI-lifecycle.py').read_text()
s=s.replace("dest=Path('outputs/Digitone-synth-arp-MIDI-lifecycle.json')", "dest=Path('outputs/Digitone-PC-synth-arp-MIDI-playback.json')")
s=s.replace("'MIDI_poll':[]", "'MIDI_poll':[],'MIDI_mirror_starts':[]")
anchor="   from unicorn import UC_HOOK_MEM_WRITE"
add='''   mc=json.loads(Path('work/os144/PC_ONLY-synth-arp-MIDI-layout.json').read_text());mb=Path('work/os144/PC_ONLY-synth-arp-MIDI-code.bin').read_bytes();tail=Path('work/os144/PC_ONLY-synth-arp-MIDI-tail.bin').read_bytes()
   session.m.ensure(mc['base']);session.m.ensure(mc['state']);session.m.uc.mem_write(mc['base'],mb);session.m.uc.mem_write(mc['state'],bytes(mc['state_bytes']));session.m.uc.mem_write(mc['state'],struct.pack('>II',0x53414d31,1))
   for r in mc['regions']:session.m.install_isa_patches_scoped(mb[r['base']-mc['base']:r['base']-mc['base']+r['bytes']],r['base'])
   session.m.uc.mem_write(mc['tail']['base'],tail);session.m.install_isa_patches_scoped(tail,mc['tail']['base'])
   for h in mc['hooks']:
    assert bytes(session.m.uc.mem_read(h['site'],h['length'])).hex()==h['previous'],hex(h['site'])
    session.m.uc.mem_write(h['site'],bytes.fromhex(h['replacement']))
   def mirror_start(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7);voice,track,ev,note,velocity=[rd(u,sp+i) for i in [4,8,12,16,20]]
    row['MIDI_mirror_starts'].append({'ms':session.now_ms(),'voice':voice,'track':track,'event':hex(ev),'note':note,'velocity':velocity,'eligible':track<4 and rd(u,mc['markers']+track*4)==ev})
   session.at(mc['base']+0x300,mirror_start)
'''
assert anchor in s;s=s.replace(anchor,add+anchor)
s=s.replace("for r in cfg['components'])", "for r in cfg['components'] if r['name']!='arp_degree_tail_hook')")
anchor="  wav=Path('outputs',"
add='''  row['private_state_hex']=bytes(s.m.uc.mem_read(0x47be5c00,160)).hex()
  messages=[];stream=b''.join(bytes(x['bytes']) for x in row['wire']);assert len(stream)%3==0,stream.hex()
  active={};ons=[]
  for i in range(0,len(stream),3):
   status,note,velocity=stream[i:i+3];assert status&0xf0 in [0x80,0x90] and note<128 and velocity<128
   key=(status&15,note);on=status&0xf0==0x90 and velocity>0
   if on:assert key not in active,(key,messages);active[key]=True;ons.append(note)
   else:assert key in active,(key,messages);del active[key]
   messages.append({'channel':(status&15)+1,'note':note,'velocity':velocity,'on':on})
  assert messages and not active and set([60,62,64,65,67,69,71,72])<=set(ons),(messages,active)
  assert all(rd(s.m.uc,0x47be5c20+v*16)==0 for v in range(8))
  expected_tail=Path('work/os144/PC_ONLY-synth-arp-MIDI-tail.bin').read_bytes();assert bytes(s.m.uc.mem_read(0x47be0c00,len(expected_tail)))==expected_tail
  row['MIDI_messages']=messages;row['balanced_note_pairs']=len(ons);row['no_active_mirrored_notes_at_stop']=True;row['dropped_note_ons']=rd(s.m.uc,0x47be5c08)
'''
assert anchor in s;s=s.replace(anchor,add+anchor)
s=s.replace("f'Digitone-synth-arp-MIDI-{name}-{scenario}.wav'", "f'Digitone-PC-synth-arp-MIDI-{name}-{scenario}.wav'")
s=s.replace("'No physical cache, timing, DMA or hardware-ready claim.'", "'Native mirror code, state and hooks are host-installed in a disposable PC overlay. Actual guest voice decisions generate MIDI via the unmodified stock DIN transmitter; no host injects output packets.','USB output and native startup/placement integration remain unimplemented.','No physical cache, timing, DMA or hardware-ready claim.'")
Path('work/test-PC-synth-arp-MIDI-playback.py').write_text(s)
