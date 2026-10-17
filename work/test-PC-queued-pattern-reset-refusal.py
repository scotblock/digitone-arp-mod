from pathlib import Path
s=Path('work/test-PC-queued-pattern-retirement.py').read_text()
s=s.replace("['baseline','clear_after_publish','rebind_after_publish']","['warm_setup_refused','pool_wrapper_refused','initializer_refused','diagnostic_exit_refused']")
s=s.replace("if not row['injected'] and mode!='baseline':","if not row['injected'] and mode in ['clear_after_publish','rebind_after_publish']:")
anchor="   def event(label,**fields):row['events'].append({'kind':label,'ms':s.now_ms(),**fields})"
addition='''
   target={'warm_setup_refused':0x4009d0d8,'pool_wrapper_refused':0x4009c5a0,'initializer_refused':0x400ffed0,'diagnostic_exit_refused':0x4009d0ea}[mode]
   base=0x47fb0000;site=0x400a88d6;original=bytes(u.mem_read(site,6));assert original.hex()=='486a00102f06'
   stub=bytes.fromhex('4878009e4eb9')+target.to_bytes(4,'big')+bytes.fromhex('588f')+original+bytes.fromhex('4ef9')+(site+6).to_bytes(4,'big')
   s.m.load(stub,base);s.m.install_isa_patches_scoped(stub,base);u.mem_write(site,bytes.fromhex('4ef9')+base.to_bytes(4,'big'));row['PC_only_guest_stub']={'address':hex(base),'bytes':stub.hex(),'target':hex(target),'displaced':original.hex()}
   def fingerprint():
    return hashlib.sha256(bytes(u.mem_read(0x41a720d0,0x244))+bytes(u.mem_read(0x47be1000,0xb74))+bytes(u.mem_read(0x47be2000,2080))+bytes(u.mem_read(LO,spec['storage_bytes']))+bytes(u.mem_read(0x419afff4,0x200))+bytes(u.mem_read(0x402a0e50,4))+bytes(u.mem_read(0x40236788,4))+bytes(u.mem_read(0x41392fa4,4))).hexdigest()
   guard={'before':None}
   def guard_enter(u,pc,n,d):
    if not builder['active']:return
    guard['before']=fingerprint();guard['sr']=u.reg_read(UC_M68K_REG_SR);guard['regs']=[u.reg_read(x) for x in [UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]]
    event('guard_enter',target=hex(target),phase=hex(rd(u,0x47be2840)),fingerprint=guard['before'])
   def guard_return(u,pc,n,d):
    if not builder['active']:return
    registers=[u.reg_read(x) for x in [UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]]
    assert fingerprint()==guard['before'] and u.reg_read(UC_M68K_REG_SR)==guard['sr'] and registers==guard['regs'];row['injected']=True;event('guard_refused_and_returned',fingerprint_unchanged=True,SR_registers_preserved=True,field=hex(rd(u,0x41a720f0)))
   s.at(target,guard_enter);s.at(base+10,guard_return)
   def reset_body(u,pc,n,d):event('stock_reset_body_entered',pc=hex(pc))
   for pc in [0x47be0642,0x400ffed6,0x4009c5aa]:s.at(pc,reset_body)
'''
assert anchor in s;s=s.replace(anchor,anchor+addition)
s=s.replace("if mode!='baseline':assert row['injected'] and kinds.index('field_fixture')<kinds.index('callback_selected')", "assert row['injected'] and kinds.index('queue_published')<kinds.index('guard_enter')<kinds.index('guard_refused_and_returned')<kinds.index('callback_selected');assert 'stock_reset_body_entered' not in kinds")
s=s.replace('Digitone-E04-PC-queued-pattern-retirement-controls.json','Digitone-E04-PC-queued-pattern-reset-refusal-controls.json')
s=s.replace("'No new firmware or guard is installed.'", "'A temporary 24-byte guest call stub injects a reset request after publication; it calls the existing unchanged PC guard and replays displaced publisher instructions. No firmware or guard binary is changed.'")
exec(compile(s,'queued-native-reset-refusal','exec'))
