from pathlib import Path
s=Path('work/probe-PC-startup-settled-MIDI.py').read_text()
s=s.replace('Digitone-E04-PC-startup-producer-order-startup.json','Digitone-E04-PC-input-live-startup-startup.json')
s=s.replace('Digitone-E04-PC-startup-settled-MIDI-probes.json','Digitone-E04-PC-input-live-settled-MIDI.json')
s=s.replace('(0x47fa0300,280)', '(0x47fa0300,280),(0x47fa0600,492)')
s=s.replace("  s.run_ms(100)","  s.run_ms(100)\n  assert rd(s.m.uc,0x47be2840)==0x4c495645")
s=s.replace("  assert r['published']==bool(r['receive_gate']&1),r", "  assert r['published']==bool(r['receive_gate']&1),r\n  assert all(e['phase']=='0x4c495645' for e in r['events'])")
exec(compile(s,'input-live-settled-MIDI','exec'))
