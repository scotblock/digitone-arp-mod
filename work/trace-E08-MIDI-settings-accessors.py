from pathlib import Path
s=Path('work/trace-E08-MIDI-controls.py').read_text()
s=s.replace('UC_M68K_REG_D3','UC_M68K_REG_D3,UC_M68K_REG_D0',1)
s=s.replace("'writes':[]","'writes':[],'MIDI_handles':[],'parameter_copies':[]")
extra='''
 def returned(u,pc,n,d):
  p=u.reg_read(UC_M68K_REG_D0);vt=rd(u,p)
  data=rd(u,p+0x10)
  row={'phase':phase,'handle':hex(p),'vtable':hex(vt),'getter':hex(rd(u,vt+0x28)),'data_pointer':hex(data),'data':bytes(u.mem_read(data,0xa4)).hex(),'words':[hex(rd(u,p+i*4)) for i in range(17)]}
  if row not in out['MIDI_handles']:out['MIDI_handles'].append(row)
 def copied(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7);p=rd(u,sp+4)
  if len(out['parameter_copies'])<40:out['parameter_copies'].append({'phase':phase,'pointer':hex(p),'track':rd(u,sp+8),'data':bytes(u.mem_read(p,0xa4)).hex()})
 s.at(0x4001dd42,returned);s.at(0x400f3750,copied)
'''
s=s.replace(" out['offers']=[]",extra+" out['offers']=[]")
s=s.replace(" phase='arp_menu';", " for track in ['T2','T3','T4']:\n  phase=track;s.press(s.code('MIDI'));s.tap(s.code(track),hold_ms=100,after_ms=100);s.release(s.code('MIDI'));s.tap(s.code('SYN1'),hold_ms=100,after_ms=200)\n phase='arp_menu';")
s=s.replace('Digitone-E08-MIDI-controls-trace.json','Digitone-E08-MIDI-settings-accessors.json')
s=s.replace("'E08-MIDI-controls-'","'E08-settings-accessors-'")
exec(compile(s,'E08-MIDI-settings-accessors','exec'))
