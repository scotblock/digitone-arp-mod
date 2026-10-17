"""Post-dequeue command parsing/comparison and stock diagnostic entry/exit.
Controlled packet and queued-note fixture; no device commands are sent."""
from pathlib import Path
exec(Path('work/test-PC-live-reset-overlap.py').read_text().split('results=[]')[0])
from unicorn import UC_HOOK_MEM_WRITE
exec(Path('work/PC-diagnostic-atomic-fixture.py').read_text())
def queue_note(m,note):
 u=m.uc;e=call(m,0x400ffff2,[],stack_top=RESETSTACK,limit=10000);d=bytearray(72);d[4:8]=u32(1);d[0x18]=note;u.mem_write(e,bytes(d));call(m,0x40100252,[e],stack_top=RESETSTACK,limit=10000);return e
def state_of(m):
 u=m.uc;head=rd(u,0x419ee22c)
 return {'queue':hex(head),'queue_node':bytes(u.mem_read(head,20)).hex() if head else None,'receive_gate':rd(u,0x41368d64),'note_gate':rd(u,0x41368d88),'pending':bytes(u.mem_read(LIVE['pending'],32)).hex(),'descriptor_word':hex(rd(u,LIVE['state']+64*4)),'audio_vector':hex(rd(u,0x400002fc)),'test_flag':rd(u,0x402a0e50)}
results=[]
for diagnostic_entry in [False,True]:
 m=prepared();u=m.uc;events=[queue_note(m,64),queue_note(m,67)];u.mem_write(0x41368d64,u32(3));u.mem_write(0x41368d88,u32(1));u.mem_write(LIVE['state']+64*4,u32(0x800000be));u.mem_write(LIVE['pending'],u32(0x47fc8000)+u32(0x800000be));before=state_of(m);prep_hits=[]
 for pc in [0x4009bcc0,0x4009b3da,0x4009b56e,0x4009b65a]:u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:prep_hits.append(hex(pc)),begin=pc,end=pc)
 if diagnostic_entry:
  u.mem_write(0x402a0e50,u32(1));call(m,0x4008e8b2,[],stack_top=RESETSTACK,limit=1000000)
 entered=state_of(m);u.mem_write(0x402296f0,u32(rd(u,0x402296f0)&~0x80000))
 packet=0x47fc6000;token=0x47fc7000;m.ensure(packet);u.mem_write(packet,b'#EXIT_TEST_MODE\0');u.mem_write(token,bytes(128))
 parsed=call(m,0x4008a474,[packet,0x401e29c0,token],stack_top=RESETSTACK,limit=100000)
 assert parsed==1 and bytes(u.mem_read(token,16))==b'#EXIT_TEST_MODE\0'
 writes=[]
 def written(u,access,a,n,v,d):writes.append({'pc':hex(u.reg_read(UC_M68K_REG_PC)),'address':hex(a),'size':n,'value':v})
 watches=[]
 for lo,hi in [(0x41368d64,0x41368d67),(0x41368d88,0x41368d8b),(0x419ee228,0x419ee23b),(LIVE['state'],LIVE['state']+LIVE['state_bytes']-1)]:watches.append(u.hook_add(UC_HOOK_MEM_WRITE,written,begin=lo,end=hi))
 u.reg_write(UC_M68K_REG_A2,packet);u.reg_write(UC_M68K_REG_D2,token);u.reg_write(UC_M68K_REG_D0,parsed);u.reg_write(UC_M68K_REG_D7,0x21);u.reg_write(UC_M68K_REG_A6,0x47fc9000);u.mem_write(0x47fc9000-0x84,u32(0xffffffff))
 s=execute_until(m,0x4008b4ce,[],ENTRY,sr=0x201f);at_reset=state_of(m)
 for h in watches:u.hook_del(h)
 assert before['queue']==entered['queue']==at_reset['queue'] and before['queue_node']==entered['queue_node']==at_reset['queue_node']
 assert at_reset['receive_gate']==3 and at_reset['note_gate']==1 and at_reset['pending']==before['pending'] and at_reset['descriptor_word']==before['descriptor_word'] and not writes
 assert at_reset['test_flag']==0 and (s[UC_M68K_REG_SR]>>8)&7==0
 results.append({'diagnostic_entry_executed':diagnostic_entry,'events':[hex(e) for e in events],'native_parser_result':parsed,'preparation_calls':prep_hits,'before':before,'after_entry':entered,'before_reset':at_reset,'watched_writes':writes,'SR_at_reset':hex(s[UC_M68K_REG_SR]),'passed':True})
 print('PASS command exit',diagnostic_entry,flush=True)
out={'PC_only':True,'passed':True,'cases':results,'scope':'Actual stock parser and worker post-parse command branch through reset entry; diagnostic entry executed in second case.','limits':['Input packet/queued notes/receive settings/preparation branch are controlled fixtures. Command transport/dequeue, live IRQ scheduler and exact device entry state are not executed.','Exit stops before pool reconstruction; other retained payload owners and hardware transfer shutdown are not certified.']}
Path('outputs/Digitone-E04-PC-diagnostic-command-exit.json').write_text(json.dumps(out,indent=2))
