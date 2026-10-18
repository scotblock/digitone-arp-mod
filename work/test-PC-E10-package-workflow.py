"""Packaged E10: native two-pattern editing, project save and recall."""
from pathlib import Path
s=Path('work/test-PC-E10-bound-panel-patterns.py').read_text(encoding='utf-8')
for a,b in [('PC_ONLY-E10-bound','PC_ONLY-E10-package'),('Digitone-E10-PC-bound-startup.json','Digitone-E10-PC-package-startup.json'),('E10-bound-panel-patterns','E10-package-workflow'),('Digitone-E10-PC-bound-panel','Digitone-E10-PC-package-workflow'),('outputs/E10-bound-','outputs/E10-package-workflow-'),("['E10_persistence_metadata','E10_pattern_binding_metadata']","['E10_persistence_metadata','E10_pattern_binding_metadata','E10_lifecycle_metadata']")]:s=s.replace(a,b)
anchor="exec(compile(prefix,'E10-bound-panel-definitions','exec'))"
old="    assert [rd(s.m.uc,S+x) for x in [0,4,304,308]] == [0x4d314131,0,2,50]"
s=s.replace(anchor,'prefix=prefix.replace('+repr(old)+','+repr("    assert rd(s.m.uc,S)==0x4d314131")+')\n'+anchor)
s=s.replace("BANK=native['E10']['bank'];","BANK=native['E10']['bank']+64;")
s=s.replace('def choose(number):','def choose(number):\n number+=2')
s=s.replace("rd(s.m.uc,BM+8)==0","rd(s.m.uc,BM+8)==2").replace("rd(s.m.uc,BM+8)==1","rd(s.m.uc,BM+8)==3")
s=s.replace('A01','A03').replace('A02','A04')
s=s.replace("s.press(s.code('MIDI'));tap('T1');s.release(s.code('MIDI'));s.run_ms(150)","selection=rd(s.m.uc,rd(s.m.uc,rd(s.m.uc,0x419f0de0)+0x40)+8)\n  if selection<4:tap('MIDI')\n  tap('T1');s.run_ms(150)")
s=s.replace(" s.close();out['limits']=", " s.close();out['packaged_loader_state']=True;out['test_patterns']=['A03','A04'];out['limits']=")

# Restored card already has slot 002: accept overwrite, then the naming dialog.
s=s.replace("mark('save_name');tap('YES',2000)","mark('save_name');tap('YES',500);tap('YES',2000)")
s=s.replace("resume='--resume-load' in sys.argv", "resume_save='--resume-save' in sys.argv\nresume='--resume-load' in sys.argv or resume_save")
s=s.replace("prior['checkpoints']['load-selected'] if resume", "prior['checkpoints']['two-patterns-edited' if resume_save else 'load-selected'] if resume")
a=s.index(" if not resume:\n  s.run_ms(1000)");b=s.index("  # The same ordinary Save Project As",a)
s=s[:a]+" if not resume or resume_save:\n  if not resume_save:\n"+''.join(' '+line+'\n' for line in s[a+len(" if not resume:\n"):b].splitlines())+s[b:]
s=s.replace("if not resume:tap('GLOBAL')", "if not resume or resume_save:tap('GLOBAL')")

rest_setup="""  # Explicitly set A04 step 2 as a rest using the native step cursor/rest controls.
  phase='A04_native_rest';choose(2);tap('SYN1');open_steps()
  for _ in range(16):
   if rd(s.m.uc,X+16)==0:break
   s.turn(5,-16,after_ms=80)
  s.turn(5,16,after_ms=100)
  assert rd(s.m.uc,X+16)==1
  if rd(s.m.uc,X+20)&2:s.turn(7,16,after_ms=150)
  s.turn(5,-16,after_ms=100)
  second=fields();second_record=valid_record(1)
  assert second[2]==0xfffd
  out.update(expected_fields=[first,second],expected_records=[first_record.hex(),second_record.hex()])
  checkpoint('two-patterns-edited');mark('A04_rest_programmed')
"""
s=s.replace("  # The same ordinary Save Project As",rest_setup+"  # The same ordinary Save Project As")

Path('work/generated-E10-package-workflow.py').write_text(s,encoding='utf-8')

exec(compile(s,'E10-package-native-workflow','exec'))
