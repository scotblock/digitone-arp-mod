from pathlib import Path
exec(Path('work/test-PC-reinitialization-admission.py').read_text().split('\nm=prepared();u=m.uc;state=stage')[0])
manifest=json.loads(Path('work/os144/PC_ONLY-release-reset-overlay.json').read_text());blob=Path('work/os144/PC_ONLY-release-reset-overlay.bin').read_bytes();rows=[]
for phase in [0x4c495645,0x494e4954,0x4641494c]:
 m=prepared();u=m.uc;state=stage(m,0x4008b88a);u.mem_write(0x47be2840,u32(phase))
 m.load(blob,manifest['base']);m.install_isa_patches_scoped(blob,manifest['base'])
 for h in manifest['hooks']:
  assert bytes(u.mem_read(h['site'],h['length'])).hex()==h['stock'],h['name'];u.mem_write(h['site'],bytes.fromhex(h['replacement']))
 before=state_of(m);pool=bytes(u.mem_read(0x419eb92c,0x4000));flags=[rd(u,a) for a in [0x40236788,0x41392fa4]];context_before=bytes(u.mem_read(0x47be1000,0xb74))+bytes(u.mem_read(0x47be2000,2080));initial_sp=u.reg_read(UC_M68K_REG_A7);messages=[];resets=[]
 def printed(u,pc,n,d):
  ptr=rd(u,u.reg_read(UC_M68K_REG_A7)+4);messages.append(bytes(u.mem_read(ptr,7)).split(b'\0')[0].decode())
 h=u.hook_add(UC_HOOK_CODE,printed,begin=0x4000594c,end=0x4000594c)
 rh=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:resets.append(hex(pc)),begin=0x4009d0ea,end=0x4009d0ea)
 u.emu_start(0x4008b88a,0x4008b4ae,count=300000);u.hook_del(h);u.hook_del(rh)
 assert u.reg_read(UC_M68K_REG_PC)==0x4008b4ae and u.reg_read(UC_M68K_REG_A7)==initial_sp
 assert bytes(u.mem_read(0x47be1000,0xb74))+bytes(u.mem_read(0x47be2000,2080))==context_before
 assert state_of(m)==before and bytes(u.mem_read(0x419eb92c,0x4000))==pool and flags==[rd(u,a) for a in [0x40236788,0x41392fa4]] and not resets and messages==['?ERROR']
 rows.append({'phase':hex(phase),'actual_parsed_command_refused':True,'native_print_response':messages,'worker_loop_reached':'0x4008b4ae','stack_balanced':True,'test_flag_queue_pool_context_preserved':True})
Path('outputs/Digitone-E04-PC-release-reset-command.json').write_text(json.dumps({'PC_only':True,'passed':True,'cases':rows,'limits':['Actual parser and post-parse command execution use a controlled packet and diagnostic state; transport/dequeue and arbitrary caller cleanup not proved.']},indent=2));print('PASS native command refusal, response and worker cleanup',len(rows))

