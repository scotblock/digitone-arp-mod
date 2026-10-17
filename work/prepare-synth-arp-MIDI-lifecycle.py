from pathlib import Path
s=Path('work/test-E06-PC-playback.py').read_text()
s=s.replace("for name,scenario in [('stock_restored','ordinary'),('E06_restored','ordinary'),('stock_restored','scale'),('E06_restored','scale'),('E06_disabled','ordinary')]:", "for name,scenario in [('E06_restored','scale')]:")
s=s.replace("dest=Path('outputs/Digitone-E06-PC-playback-comparison.json')", "dest=Path('outputs/Digitone-synth-arp-MIDI-lifecycle.json')")
s=s.replace("if '--resume' in sys.argv:out['cases']=[r for r in json.loads(dest.read_text())['cases'] if r['scenario']=='ordinary' and r.get('passed')]", '')
s=s.replace("'failure':None};", "'failure':None,'voice_starts':[],'voice_state_writes':[],'MIDI_poll':[],'output_channels':[],'wire':[]};")
anchor='   def arp_fixture(u,pc,n,d):'
add='''   from unicorn import UC_HOOK_MEM_WRITE
   def voice_started(u,pc,n,d):
    frame=u.reg_read(UC_M68K_REG_A6);ev=u.reg_read(UC_M68K_REG_A3)
    row['voice_starts'].append({'ms':session.now_ms(),'event':hex(ev),'track':u.reg_read(UC_M68K_REG_D2),'voice':rd(u,frame-0x80),'pitch':u.reg_read(UC_M68K_REG_D0)>>16,'raw_event':bytes(u.mem_read(ev,72)).hex(),'SR':hex(u.reg_read(UC_M68K_REG_SR))})
   session.at(0x4009e934,voice_started)
   def voice_write(u,access,address,size,value,d):
    if len(row['voice_state_writes'])<10000:row['voice_state_writes'].append({'ms':session.now_ms(),'pc':hex(u.reg_read(UC_M68K_REG_PC)),'address':hex(address),'size':size,'value':hex(value)})
   session.m.uc.hook_add(UC_HOOK_MEM_WRITE,voice_write,begin=0x80005434,end=0x80005434+160-1)
   session.at(0x400f4c7e,lambda u,pc,n,d:row['MIDI_poll'].append(session.now_ms()))
   row['output_channels']=[rd(session.m.uc,0x41368d30+i*4) for i in range(4)]
   mo=midi.MidiOut(lambda data:row['wire'].append({'ms':session.now_ms(),'bytes':list(data)}));mo.install(session.m);mo.attach(session.m,session.ips);session.sources=session.sources+(mo,)
'''
assert anchor in s;s=s.replace(anchor,add+anchor)
s=s.split("ordinary={r['image']")[0]+"\nout['passed']=all(r.get('passed') for r in out['cases']);dest.write_text(json.dumps(out,indent=2));\nif not out['passed']:raise SystemExit(1)\n"
s=s.replace("f'Digitone-E06-PC-{name}-{scenario}.wav'", "f'Digitone-synth-arp-MIDI-{name}-{scenario}.wav'")
Path('work/trace-synth-arp-MIDI-lifecycle.py').write_text(s)
