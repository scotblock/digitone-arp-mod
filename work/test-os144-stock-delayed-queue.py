from pathlib import Path
source=Path('work/test-os144-stock-sustain-transition.py').read_text().split("exec(compile(s,'stock-sustain-transition','exec'))")[0]
exec(compile(source,'build-sustain-control','exec'))
s=s.replace('Digitone-OS1.44-stock-sustain-transition.json','Digitone-OS1.44-stock-delayed-queue.json')
needle="sp=uc.reg_read(UC_M68K_REG_A7);e=rd(uc,sp+4)"
assert needle in s
s=s.replace(needle,needle+'''
  if rd(uc,e)==0 and 'delayed_queue_fixture' not in r:
   original=rd(uc,sp+8);later=(original+96000000)&0xffffffff
   uc.mem_write(sp+8,u32(later))
   r['delayed_queue_fixture']={'event':hex(e),'generation':generations[e],'publication_ms':session.now_ms(),'before_timestamp':original,'after_timestamp':later,'added_ticks':96000000,'original_fields':list(struct.unpack('>18I',uc.mem_read(e,72))),'original_backing':hex(rd(uc,CURRENT))}
   r['fixtures'].append({'kind':'Delay one actual stock-produced type-0 queued note','modified':'queue publisher timestamp argument in PC RAM only','added_ticks':96000000,'eligibility_and_metadata_injected':False})
''')
s=s.replace("mark('confirmed handoff or bounded failure')","mark('confirmed handoff or bounded failure');session.run_ms(2500);mark('delayed source observation after handoff')")
exec(compile(s,'stock-delayed-queue','exec'))
