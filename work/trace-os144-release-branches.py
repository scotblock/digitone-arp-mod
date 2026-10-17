from pathlib import Path
source=Path('work/trace-os144-delayed-release.py').read_text().split("exec(compile(s,'trace-stock-release','exec'))")[0]
exec(compile(source,'build-release-trace','exec'))
s=s.replace('Digitone-OS1.44-delayed-release-trace.json','Digitone-OS1.44-release-branches.json')
needle="for label,reg in [('producer',UC_M68K_REG_A2)"
assert needle in s
s=s.replace(needle,"""def writer_entry(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);f=r.get('delayed_queue_fixture')
  if f and rd(uc,sp+4)==int(f['event'],16) and generations[int(f['event'],16)]==f['generation']:
   r.setdefault('invalidation_calls',[]).append({'ms':session.now_ms(),'return_to':hex(rd(uc,sp)),'arguments':[hex(rd(uc,sp+4)),rd(uc,sp+8)],'stack':list(struct.unpack('>20I',uc.mem_read(sp,80))),'before_fields':list(struct.unpack('>18I',uc.mem_read(rd(uc,sp+4),72))),**state(uc)})
 s.at(0x4009363c,writer_entry)
 def consumer_branch(uc,pc,n,d):
  f=r.get('delayed_queue_fixture');e=uc.reg_read(UC_M68K_REG_A3)
  if f and e==int(f['event'],16) and generations[e]==f['generation']:
   r.setdefault('consumer_branches',[]).append({'ms':session.now_ms(),'pc':hex(pc),'D0':hex(uc.reg_read(UC_M68K_REG_D0)),'D1':hex(uc.reg_read(UC_M68K_REG_D1)),'fields':list(struct.unpack('>18I',uc.mem_read(e,72)))})
 for pc in [0x4009d480,0x4009d570,0x4009d760,0x4009d762,0x4009d766,0x4009d76a,0x4009d76c,0x4009d7d8,0x4009d7de]:s.at(pc,consumer_branch)
 """+needle)
exec(compile(s,'trace-release-branches','exec'))
