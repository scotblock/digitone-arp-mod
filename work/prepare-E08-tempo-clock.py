from pathlib import Path
p=Path('work/trace-E08-MIDI-track-queue.py').read_text()
p=p.replace("'queue_samples':[]}","'queue_samples':[],'tempo_samples':[]}")
a=p.index(" s.tap(s.code('RECORD'),hold_ms=100,after_ms=100);s.tap(s.code('1')");z=p.index(" out['halted']=",a)
p=p[:a]+''' s.tap(s.code('TEMPO'),hold_ms=70,after_ms=100)
 def sample(label):
  before=rd(s.m.uc,0x80004614);start=s.now_ms();s.run_ms(1000);after=rd(s.m.uc,0x80004614);out['tempo_samples'].append({'label':label,'before':before,'after':after,'delta':(after-before)&0xffffffff,'ms':s.now_ms()-start});mark(label)
 sample('initial')
 s.turn(s.encoder('A'),-60,after_ms=250);sample('tempo_A_minus60')
 s.turn(s.encoder('A'),120,after_ms=250);sample('tempo_A_plus120')
''' +p[z:]
p=p.replace('Digitone-E08-MIDI-track-queue-trace.json','Digitone-E08-tempo-clock-discovery.json')
Path('work/trace-E08-tempo-clock.py').write_text(p)
