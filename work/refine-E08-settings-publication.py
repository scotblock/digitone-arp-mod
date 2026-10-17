from pathlib import Path
p=Path('work/build-E08-PC-tempo-M1.py').read_text()
p=p.replace("a=Asm();save(a);a.emit('2f0a');js(a,D)", "a=Asm();save(a);absop(a,'2039',S+320);a.branch('6700','settings_done');absop(a,'2f39',S+316);absop(a,'2f39',S+312);js(a,CONFIG);a.emit('508f');absop(a,'42b9',S+320);a.label('settings_done');a.emit('2f0a');js(a,D)")
p=p.replace("a.emit('7250')","a.emit('7254')").replace("'state_bytes':320","'state_bytes':336")
Path('work/build-E08-PC-tempo-M1.py').write_text(p)
# Contract canaries must follow the complete state extent.
for name in ['work/test-E08-M1-tempo-contracts.py','work/test-E08-M1-relocated-tempo-contracts.py']:
 p=Path(name).read_text().replace('S+320',"S+c['state_bytes']")
 Path(name).write_text(p)
p=Path('work/test-E08-M1-tempo-playback.py').read_text()
a=p.index(' def configure(index,pct):');z=p.index(' configure(2,50);',a)
p=p[:a]+''' def configure(index,pct):
  s.m.uc.mem_write(native['state']+312,struct.pack('>III',index,pct,1));s.run_ms(70)
  assert rd(s.m.uc,native['state']+320)==0 and rd(s.m.uc,native['state']+304)==index and rd(s.m.uc,native['state']+308)==pct
''' +p[z:]
Path('work/test-E08-M1-tempo-playback.py').write_text(p)
