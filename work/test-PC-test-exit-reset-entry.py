from pathlib import Path
exec(Path('work/test-PC-live-reset-overlap.py').read_text().split('results=[]')[0])
m=prepared();u=m.uc;event=call(m,0x400ffff2,[],stack_top=RESETSTACK,limit=10000)
descriptor=bytearray(72);descriptor[4:8]=u32(1);descriptor[0x18]=64;u.mem_write(event,bytes(descriptor));call(m,0x40100252,[event],stack_top=RESETSTACK,limit=10000)
queue=rd(u,0x419ee22c);assert queue
original_flags=rd(u,0x402296f0);u.mem_write(0x402296f0,u32(original_flags&~0x80000));u.mem_write(0x41368d64,u32(3));u.mem_write(LIVE['state']+64*4,u32(0x800000be));u.mem_write(LIVE['pending'],u32(0x47fc8000)+u32(0x800000be))
state=execute_until(m,0x4009d0ea,[],ENTRY,sr=0x201f)
result={'PC_only':True,'entry':'0x4009d0ea','stop_before_initializer_mutation':hex(ENTRY),'original_setup_flags':hex(original_flags),'controlled_setup_flags':hex(original_flags&~0x80000),'controlled_receive_gate':3,'gate_at_reset':rd(u,0x41368d64),'queue_at_entry':hex(queue),'queue_at_reset':hex(rd(u,0x419ee22c)),'pending_key_at_reset':hex(rd(u,LIVE['pending'])),'descriptor_context_at_reset':hex(rd(u,LIVE['state']+64*4)),'SR_at_reset':hex(state[UC_M68K_REG_SR]),'outer_dispatch_preconditions_executed':False,'limits':['Begins directly at the stock test-exit setup helper with controlled queued event, enabled MIDI gate and preparation-bit branch.','Does not execute command admission, registered callback dispatch, producer-stop acknowledgement or actual test-mode device state.']}
assert result['gate_at_reset']==3 and result['queue_at_reset']==result['queue_at_entry'] and result['pending_key_at_reset']=='0x47fc8000' and result['descriptor_context_at_reset']=='0x800000be' and (state[UC_M68K_REG_SR]>>8)&7==0
result['passed']=True;Path('outputs/Digitone-E04-PC-test-exit-reset-entry.json').write_text(json.dumps(result,indent=2));print('PASS controlled actual test-exit-to-reset entry; local branch preserves queued input and metadata')
