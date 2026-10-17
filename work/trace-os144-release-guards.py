from pathlib import Path
source=Path('work/trace-os144-release-branches.py').read_text().split("exec(compile(s,'trace-release-branches','exec'))")[0]
exec(compile(source,'build-release-guards','exec'))
s=s.replace('Digitone-OS1.44-release-branches.json','Digitone-OS1.44-release-guards.json')
needle="s.at(0x4009363c,writer_entry)"
assert needle in s
s=s.replace(needle,needle+'''
 def cancel_guard(uc,pc,n,d):
  if r.get('delayed_queue_fixture') and 3200<=session.now_ms()<=3260:
   a4=uc.reg_read(UC_M68K_REG_A4);sp=uc.reg_read(UC_M68K_REG_A7)
   r.setdefault('cancel_guard_points',[]).append({'ms':session.now_ms(),'pc':hex(pc),'track_d2':uc.reg_read(UC_M68K_REG_D2),'D6':hex(uc.reg_read(UC_M68K_REG_D6)),'alternate_pattern':hex(rd(uc,0x4138f21c)),'active_pattern':hex(rd(uc,CURRENT)),'guard_a4':hex(a4),'guard_byte':bytes(uc.mem_read(a4,1)).hex(),'stack_words':list(struct.unpack('>6I',uc.mem_read(sp,24)))})
 for pc in [0x40095b66,0x40095b72,0x40095b76,0x40095b88,0x40095ba2]:s.at(pc,cancel_guard)
''')
exec(compile(s,'release-guards','exec'))
