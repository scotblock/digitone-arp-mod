from pathlib import Path
s=Path('work/test-os144-stock-behavior.py').read_text()
s=s.replace('Digitone-OS1.44-stock-behavior.json','Digitone-OS1.44-stock-pattern-isolation.json')
begin=s.index(' mi=midi.MidiIn();');end=s.index('except BaseException:',begin)
s=s[:begin]+''' mark('initial')
 session.tap(session.code('STOP'),hold_ms=100,after_ms=100)
 session.press(session.code('PTN'));session.run_ms(100);session.tap(session.code('2'),hold_ms=100,after_ms=100);session.release(session.code('PTN'));session.run_ms(300);mark('stopped selected 2')
 old=rd(session.m.uc,CURRENT)
 session.tap(session.code('PLAY'),hold_ms=100,after_ms=200);mark('play')
 session.press(session.code('PTN'));session.run_ms(100);session.tap(session.code('1'),hold_ms=100,after_ms=100);session.release(session.code('PTN'));session.run_ms(200);mark('request 1')
 for i in range(32):
  session.run_ms(250);mark('wait '+str(i))
  if rd(session.m.uc,CURRENT)!=old:break
 r['actual_playing_handoff']=rd(session.m.uc,CURRENT)!=old
 if not r['actual_playing_handoff']:
  session.tap(session.code('STOP'),hold_ms=100,after_ms=200);mark('stop after uncompleted request')
  session.press(session.code('PTN'));session.run_ms(100);session.tap(session.code('1'),hold_ms=100,after_ms=100);session.release(session.code('PTN'));session.run_ms(300);mark('stopped selected 1')
 r['inputs']=session.inputs;r['halted']=session.halted
 r['actual_stopped_handoff']=rd(session.m.uc,CURRENT)!=old
''' +s[end:]
exec(compile(s,'stock-pattern-isolation','exec'))
