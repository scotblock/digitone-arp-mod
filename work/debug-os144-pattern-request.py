from pathlib import Path
source=Path('work/test-os144-stock-handoff.py').read_text().split("exec(compile(s,'stock-1.44-handoff','exec'))")[0]
exec(compile(source,'build-stock-handoff','exec'))
s=s.replace('Digitone-OS1.44-stock-handoff.json','Digitone-OS1.44-stock-pattern-request-debug.json')
s=s.replace("range(16)","range(8)")
s=s.replace("r['marks'].append({'label':label", """from emu import panel
 if label in ('stopped pattern 2 selection','pattern request sent','after handoff observation','stopped'):
  panel.write_png(panel.read(session.m,session.profile.fb_back),str(Path('work/os144')/(label.replace(' ','-')+'.png')))
 r['marks'].append({'pattern_region':bytes(session.m.uc.mem_read(0x4138f200,256)).hex(),'label':label""")
exec(compile(s,'pattern-request-debug','exec'))
