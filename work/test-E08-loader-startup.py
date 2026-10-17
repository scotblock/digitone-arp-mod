from pathlib import Path
import json
# Reuse the established native-timer startup test, with E08's own loader state.
s=Path('work/test-E07-PC-startup.py').read_text().replace('E07','E08')
s=s.replace('outputs/Digitone-E08-PC-candidate-layout.json','outputs/Digitone-E08-PC-path-layout.json').replace('work/os144/E08-PC-payload.bin','work/os144/E08-PC-layout-payload.bin').replace('work/os144/E08-PC-main.bin','work/os144/E08-PC-layout-main.bin').replace('work/os144/E08-PC-candidate.syx','work/os144/E08-PC-path-candidate.syx')
s=s.replace("['stock_default','stock_restored','E08_default','E08_restored','E08_disabled']","['E08_restored']")
anchor="exec(compile(s,'E08-packaged-startup','exec'))"
extra='''
s=s.replace('machine_out=box)',"machine_out=box,handoff='work/os144/E08-PC-loader-handoff.bin')")
s=s.replace("  sp=m.uc.reg_read(UC_M68K_REG_A7);m.uc.mem_write(sp+4,struct.pack('>I',0x00140000))", "  row['loader_handoff']='work/os144/E08-PC-loader-handoff.bin'\\n  assert bytes(m.uc.mem_read(0x40000400,len(image)))==image")
s=s.replace("  save(m,paths.cold", "  if name.startswith('E08'):\\n   row['M1_after_cold']=[int.from_bytes(m.uc.mem_read(cfg['state']+x,4),'big') for x in [0,4,304,308]]\\n   assert row['M1_after_cold']==[0x4d314131,0,2,50]\\n   assert bytes(m.uc.mem_read(cfg['arena'],cfg['arena_bytes']))==bytes(cfg['arena_bytes'])\\n  save(m,paths.cold")
'''
assert anchor in s;s=s.replace(anchor,extra+'\n'+anchor)
exec(compile(s,'E08-loader-native-startup','exec'))
