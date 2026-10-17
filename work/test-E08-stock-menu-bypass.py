from pathlib import Path
s=Path('work/trace-E08-MIDI-controls.py').read_text()
s=s.replace("'writes':[]","'writes':[],'sound_lookups':[]")
s=s.replace('UC_M68K_REG_D3','UC_M68K_REG_D3,UC_M68K_REG_D0',1)
anchor=" out['offers']=[]"
extra='''
 original=bytes(s.m.uc.mem_read(0x4003fc3e,4));assert original[:2]==bytes.fromhex('6600')
 s.m.uc.mem_write(0x4003fc3e,bytes.fromhex('4e714e71'))
 out['disposable_menu_guard_bypass']={'site':'0x4003fc3e','original':original.hex()}
 def lookup(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7)
  out['sound_lookups'].append({'phase':phase,'base':hex(rd(u,sp+4)),'requested_index':rd(u,sp+8),'return_pc':hex(rd(u,sp))})
 def looked(u,pc,n,d):
  if out['sound_lookups']:out['sound_lookups'][-1]['sound_handle']=hex(u.reg_read(UC_M68K_REG_D0))
 s.at(0x4001dcf2,lookup);s.at(0x4001dd18,looked)
'''
s=s.replace(anchor,extra+anchor)
a=s.index(" for page in ['SYN1'");z=s.index(" phase='arp_menu'",a)
s=s[:a]+s[z:]
s=s.replace(" out['halted']=s.halted", " phase='arp_mode';s.turn(s.encoder('A'),32,after_ms=400);record(phase)\n out['halted']=s.halted")
s=s.replace('Digitone-E08-MIDI-controls-trace.json','Digitone-E08-stock-menu-bypass.json').replace("'E08-MIDI-controls-'","'E08-menu-bypass-'")
exec(compile(s,'E08-disposable-stock-menu-bypass','exec'))
