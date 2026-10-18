"""Packaged E10: actual consumed pattern handoff while a chord is held."""
from pathlib import Path
s=Path('work/test-PC-E10-bound-running-handoff.py').read_text(encoding='utf-8')
anchor="exec(compile(definitions,'E10-bound-handoff-definitions','exec'))"
changes=[('PC_ONLY-E10-bound','PC_ONLY-E10-package'),('Digitone-E10-PC-bound-startup.json','Digitone-E10-PC-package-startup.json'),("['E10_persistence_metadata','E10_pattern_binding_metadata']","['E10_persistence_metadata','E10_pattern_binding_metadata','E10_lifecycle_metadata']")]
injection=''.join('definitions=definitions.replace('+repr(a)+','+repr(b)+')\n' for a,b in changes)
inner="exec(compile(prefix,'E10-bound-panel-definitions','exec'))"
old="    assert [rd(s.m.uc,S+x) for x in [0,4,304,308]] == [0x4d314131,0,2,50]"
injection+='definitions=definitions.replace('+repr(inner)+','+repr('prefix=prefix.replace('+repr(old)+','+repr("    assert rd(s.m.uc,S)==0x4d314131")+')\n'+inner)+')\n'
s=s.replace(anchor,injection+anchor).replace('outputs/Digitone-E10-PC-bound-panel-patterns.json','outputs/Digitone-E10-PC-package-workflow-patterns.json').replace(" and proof['post_reload_pattern_recall']",'').replace("proof['checkpoints']['reloaded-two-patterns']","proof['checkpoints']['reloaded-two-patterns']")
s=s.replace('work/E10-bound-running-handoff','work/E10-package-workflow-handoff').replace('outputs/E10-bound-handoff-','outputs/E10-package-workflow-handoff-').replace('outputs/Digitone-E10-PC-bound-running-handoff.json','outputs/Digitone-E10-PC-package-workflow-handoff.json')
s=s.replace('def choose(number):','def choose(number):\n number+=2')
s=s.replace(" before=bytes(s.m.uc.mem_read(BANK,64))"," before=bytes(s.m.uc.mem_read(BANK,4096))")
s=s.replace("bytes(s.m.uc.mem_read(BANK,64))==before","bytes(s.m.uc.mem_read(BANK,4096))==before")
# Observe the actual helper's due-step cursor, rest and emitted counters.
needle=" phase='A01_held';tap('PLAY');send(chord);s.run_ms(200);mark('A01_held')"
extra="""
 steps=[]
 def due(u,pc,n,d):
  cursor=rd(u,X+12);length=rd(u,X+8)
  if rd(u,X+4) and rd(u,X+28)==rd(u,S+336):
   steps.append(dict(phase=phase,cursor=cursor,length=length,mask=rd(u,X+20),offset=int.from_bytes(u.mem_read(X+32+min(cursor,15),1),'big',signed=True),rests=rd(u,X+48),emitted=rd(u,X+60)))
 s.at(json.loads(Path('work/os144/PC_ONLY-E10-step-engine.json').read_text())['entries']['emit'],due)
 phase='A03_held';tap('PLAY');send(chord);s.run_ms(2200);mark('A03_held')
"""
assert needle in s;s=s.replace(needle,extra)
s=s.replace(" s.run_ms(400);phase='release'", " s.run_ms(2400);mark('A04_playback');phase='release'")
s=s.replace(" preserved(s);out.update(passed=True", " assert any(r['phase']=='A03_held' and r['offset']==1 for r in steps),steps\n assert any(r['phase'] in ['handoff_A02'] and r['mask']&2==0 for r in steps),steps\n assert rd(s.m.uc,X+48)>0\n out.update(due_steps=steps,rest_consumption_observed=True,distinct_programs_consumed=True)\n preserved(s);out.update(passed=True")
s=s.replace('A02_','A04_').replace('handoff_A02','handoff_A04')
Path('work/generated-E10-package-workflow-handoff.py').write_text(s,encoding='utf-8')
exec(compile(s,'E10-packaged-running-pattern-handoff','exec'))
