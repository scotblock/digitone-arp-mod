from pathlib import Path
previous=Path('outputs/Digitone-E04-PC-restored-arp-DSP.json')
if previous.exists() and not Path('outputs/Digitone-E04-PC-live-MIDI-zero-context.json').exists():
 Path('outputs/Digitone-E04-PC-live-MIDI-zero-context.json').write_bytes(previous.read_bytes())
if previous.exists() and not Path('outputs/Digitone-E04-PC-encoder-dead-zone-control.json').exists():
 Path('outputs/Digitone-E04-PC-encoder-dead-zone-control.json').write_bytes(previous.read_bytes())
s=Path('work/test-PC-ISA-loader-playback.py').read_text()
s=s.replace('Digitone-E04-PC-ISA-loader-startup.json','Digitone-E04-PC-ISA-DSP-loader-startup.json')
s=s.replace('Digitone-E04-PC-ISA-loader-playback.json','Digitone-E04-PC-restored-arp-DSP.json')
s=s.replace('bytes([61])','bytes([62])')
s=s.replace("for case in startup['cases']:","for case in startup['cases'][1:]:")
s=s.replace("[c['image'] for c in startup['cases']]","[c['image'] for c in startup['cases'][1:]]")
start=s.index("   s.tap(s.code('STOP'),hold_ms=100,after_ms=100)")
end=s.index("   r.update(ms=",start)
scenario=r'''   from emu import midi
   import wave
   link=s.ev['dsplink'];r['DSP_before']={'model':type(link).__name__,'booted':link.booted,'renders':link.renders,'pc':hex(link.pc) if link.pc else None}
   # gui-raw is a first-live frame, not proof that the DSP/sound jobs finished.
   for warm in range(10):
    s.run_ms(1000)
    print('warmup',scenario,mode,warm+1,link.booted,link.renders,flush=True)
    if link.booted and link.renders>100:break
   r['warmup']={'ms':s.now_ms(),'booted':link.booted,'renders':link.renders}
   assert link.booted and link.renders>100
   s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
   s.tap(s.code('T1'),hold_ms=100,after_ms=100)
   s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('SYN1'),hold_ms=100,after_ms=100);s.release(s.code('FUNC'));s.run_ms(200)
   # Toggle through the documented FUNC+NOTE action, avoiding idle encoder dead zone.
   s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('KEYBOARD'),hold_ms=100,after_ms=100);s.release(s.code('FUNC'));s.run_ms(200)
   s.turn(3,16,after_ms=200)
   from emu import panel
   frame=panel.read(s.m,s.profile.fb_front)
   if frame:panel.write_png(frame,'outputs/Digitone-E04-PC-restored-arp-menu-'+scenario+'-'+mode+'.png',scale=4)
   s.tap(s.code('NO'),hold_ms=100,after_ms=100)
   s.tap(s.code('RECORD'),hold_ms=100,after_ms=100)
   s.tap(s.code('1'),hold_ms=100,after_ms=100)
   s.tap(s.code('RECORD'),hold_ms=100,after_ms=100)
   s.tap(s.code('PLAY'),hold_ms=100,after_ms=500)
   r['sequencer_configuration']='Guest panel: RECORD, step 1, RECORD, PLAY; no sequence/event RAM injection.'
   r['arp_configuration']='Guest panel: T1, FUNC+SYN1, FUNC+KEYBOARD to toggle arp, encoder C +16 (range); no event or eligibility injection.'
   mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,)
   setting=0x41368d64;old=rd(s.m.uc,setting);s.m.uc.mem_write(setting,struct.pack('>I',old|3));channel=rd(s.m.uc,0x41368d2c)&15
   r['MIDI_input_fixture']={'address':hex(setting),'before':hex(old),'after':hex(old|3),'channel':channel}
   def send(data):
    for i,byte in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*0.00032,byte)
    mi.received+=len(data);s.run_ms(20)
   send([0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100])
   s.run_ms(2000)
   send([0xb0|channel,64,127])
   send([0x80|channel,60,0,0x80|channel,64,0,0x80|channel,67,0])
   s.run_ms(500)
   send([0xb0|channel,64,0]);s.run_ms(300)
   send([0x90|channel,62,100]);s.run_ms(500);send([0x80|channel,62,0]);s.run_ms(300)
   s.tap(s.code('STOP'),hold_ms=100,after_ms=200)
   r['DSP_after']={'booted':link.booted,'renders':link.renders,'pc':hex(link.pc) if link.pc else None,'error':str(link.error) if link.error else None}
   r['MIDI_delivery']={'received':mi.received,'delivered':mi.delivered,'interrupts':mi.raised}
   r['audio_nonzero_bytes']=sum(x!=0 for x in s.pcm)
   with wave.open('outputs/Digitone-E04-PC-restored-'+scenario+'-'+mode+'.wav','wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(s.pcm)
'''
# Outer scenario variable would shadow the scenario string above: rename the text.
s=s[:start]+scenario+s[end:]
s=s.replace("   r['passed']=True","   assert r['audio_nonzero_bytes']>0 and r['DSP_after']['booted'] and r['DSP_after']['renders']>r['DSP_before']['renders']\n   assert mi.received==mi.delivered\n   r['passed']=True")
exec(compile(s,'restored-live-arp-DSP','exec'))
