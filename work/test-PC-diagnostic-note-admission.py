from pathlib import Path
exec(Path('work/test-PC-live-reset-overlap.py').read_text().split('results=[]')[0])
exec(Path('work/PC-diagnostic-atomic-fixture.py').read_text())
results=[]
for gate in [0,1]:
 m=prepared();u=m.uc;u.mem_write(0x41368d64,u32(3));u.mem_write(0x41368d88,u32(gate));u.mem_write(0x402a0e50,u32(1));call(m,0x4008e8b2,[],stack_top=RESETSTACK,limit=1000000)
 packet=0x47fc6000;m.ensure(packet);channel=rd(u,0x41368d2c)&15;u.mem_write(packet,bytes([0x90|channel,64,100]));hits=[]
 for pc in [0x400eb166,0x400eae5c,0x400ff3ec,0x40100252,0x40100178]:
  u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:hits.append(hex(pc)),begin=pc,end=pc)
 call(m,0x400eb2d2,[packet,3,8],stack_top=RESETSTACK,limit=2000000)
 assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0
 queue=rd(u,0x419ee22c);published=bool(queue)
 results.append({'controlled_note_permission':gate,'channel':channel,'test_flag':rd(u,0x402a0e50),'audio_vector':hex(rd(u,0x400002fc)),'handler_hits':hits,'queue':hex(queue),'published':published,'returned':True})
 assert published==bool(gate),(gate,hits,hex(queue))
 print('PASS diagnostic note admission',gate,published,flush=True)
Path('outputs/Digitone-E04-PC-diagnostic-note-admission.json').write_text(json.dumps({'PC_only':True,'passed':True,'cases':results,'limits':['Native wrapper called with a controlled complete MIDI packet after actual diagnostic entry; receiver transport/dequeue and concurrent scheduling are not run.','Initialized stock state is a retained emulator snapshot, not a physical device dump.']},indent=2))
