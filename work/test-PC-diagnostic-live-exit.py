from pathlib import Path
exec(Path('work/test-PC-diagnostic-command-exit.py').read_text().split('\nresults=[]')[0])
results=[]
for preparation in [False,True]:
 m=prepared();u=m.uc;u.mem_write(0x41368d64,u32(3));u.mem_write(0x41368d88,u32(1));u.mem_write(0x402a0e50,u32(1));call(m,0x4008e8b2,[],stack_top=RESETSTACK,limit=1000000)
 msg=0x47fc5000;m.ensure(msg);channel=rd(u,0x41368d2c)&15;events=[];publications=[]
 def published(u,pc,n,d):publications.append(rd(u,u.reg_read(UC_M68K_REG_A7)+4))
 h=u.hook_add(UC_HOOK_CODE,published,begin=0x40100252,end=0x40100252)
 for note in [64,67]:
  u.mem_write(msg,bytes([0x90|channel,note,100]));call(m,0x400eb2d2,[msg,3,8],stack_top=RESETSTACK,limit=2000000)
  event=publications[-1];assert bytes(u.mem_read(event+0x18,1))==bytes([note]) and rd(u,event+4)==1
  events.append({'event':hex(event),'note':note,'track':rd(u,event+8),'context':hex(rd(u,0x47be1024+(event-0x419ebe2c)//72*4))})
 u.hook_del(h);assert len(publications)==2;before=state_of(m)
 flags=rd(u,0x402296f0);u.mem_write(0x402296f0,u32(flags|0x80000 if preparation else flags&~0x80000));prep=[]
 for pc in [0x4009bcc0,0x4009b3da,0x4009b56e,0x4009b65a]:u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:prep.append(hex(pc)),begin=pc,end=pc)
 packet=0x47fc6000;token=0x47fc7000;u.mem_write(packet,b'#EXIT_TEST_MODE\0');u.mem_write(token,bytes(128));parsed=call(m,0x4008a474,[packet,0x401e29c0,token],stack_top=RESETSTACK,limit=100000);assert parsed==1
 u.reg_write(UC_M68K_REG_A2,packet);u.reg_write(UC_M68K_REG_D2,token);u.reg_write(UC_M68K_REG_D0,parsed);u.reg_write(UC_M68K_REG_D7,0x21);u.reg_write(UC_M68K_REG_A6,0x47fc9000);u.mem_write(0x47fc9000-0x84,u32(0xffffffff));state=execute_until(m,0x4008b4ce,[],ENTRY,sr=0x201f);after=state_of(m)
 assert before['queue']==after['queue'] and before['queue_node']==after['queue_node'] and after['receive_gate']==3 and after['note_gate']==1
 assert prep==(['0x4009bcc0','0x4009b3da','0x4009b56e','0x4009b65a'] if preparation else [])
 assert all(rd(u,int(e['event'],16)+4)==1 and bytes(u.mem_read(int(e['event'],16)+0x18,1))==bytes([e['note']]) for e in events)
 queue_head=rd(u,0x419ee22c);assert rd(u,queue_head+8)==publications[0] and rd(u,queue_head+12)==publications[1] and rd(u,publications[0]+0x44)==publications[1]
 resume(m,state,0x4009c5aa);rebuilt=state_of(m)
 assert rebuilt['queue']=='0x0' and rd(u,0x419ee238)==publications[0] and rd(u,0x47be1010)==1 and all(rd(u,0x47be1024+(e-0x419ebe2c)//72*4)==0 for e in publications)
 results.append({'preparation_bit_set':preparation,'actual_preparation_calls':prep,'events_generated_by_stock_MIDI_handler':events,'before_command_exit':before,'before_reset':after,'SR_before_reset':hex(state[UC_M68K_REG_SR]),'queued_chain_verified_before_reset':True,'after_real_initializer_return':rebuilt,'free_head_after_reset':hex(rd(u,0x419ee238)),'same_event_returned_to_free_pool':True,'context_ready_after_reset':True,'passed':True});print('PASS native diagnostic-entry -> two notes -> parsed exit -> actual reset',preparation,flush=True)
Path('outputs/Digitone-E04-PC-diagnostic-live-exit.json').write_text(json.dumps({'PC_only':True,'passed':True,'cases':results,'limits':['Complete packets supplied after receive transport/dequeue boundary; no real concurrent task/IRQ/peripheral execution.','Native diagnostic entry, note handler, parser, command comparison, preparation calls and full pool initializer execute; stop at the setup wrapper return before its remaining setup calls.','Receive settings and setup bit are controlled fixtures on a captured initialized emulator state.']},indent=2))
