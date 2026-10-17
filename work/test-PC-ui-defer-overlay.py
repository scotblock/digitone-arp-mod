from pathlib import Path
exec(Path('work/test-PC-real-parent-restore-refusal.py').read_text().split('\nfor when,stop in')[0])
from emu import cfisa
guardcfg=json.loads(Path('work/os144/PC_ONLY-ui-defer-overlay.json').read_text());blob=Path('work/os144/PC_ONLY-ui-defer-overlay.bin').read_bytes();pos=0
while pos<len(blob):
 ins=cfisa.decode(lambda off:int.from_bytes(blob[pos+off:pos+off+2],'big'),guardcfg['base']+pos);assert not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(blob[pos:pos+2],'big'));pos+=ins.length
assert pos==len(blob)
def install(m,live):
 code=bytearray(blob)
 for addr in guardcfg['mode_immediate_bytes']:code[addr-guardcfg['base']]=int(live)
 m.load(bytes(code),guardcfg['base']);m.install_isa_patches_scoped(bytes(code),guardcfg['base'])
 for hook in guardcfg['hooks']:
  assert bytes(m.uc.mem_read(hook['site'],hook['length'])).hex()==hook['stock'];m.uc.mem_write(hook['site'],bytes.fromhex(hook['replacement']))

def unrelated(m,O,H):
 u=m.uc;B=call(m,0x400e96c0,[0x50],stack_top=RESETSTACK,limit=100000);call(m,0x400e52e6,[B,0x401dfe30],stack_top=RESETSTACK,limit=100000);BH=H+0x40;u.reg_write(UC_M68K_REG_A0,BH);call(m,0x400e43fc,[O,B],stack_top=RESETSTACK,limit=100000);return B,BH,rd(u,BH+4)
results=[]
for route in ['retained','explicit']:
 for kind,live in [('audio',True),('audio',False),('ordinary',True),('null',True)]:
  for recursive in [False,True]:
   m,M,TASK,H,A,P,O,PP,C,app,cbs=fixture(recursive);u=m.uc;requested=P;RH=H;RC=C
   if kind=='ordinary':requested,RH,RC=unrelated(m,O,H)
   elif kind=='null':requested=0;RH=H+0x40;RC=0;u.mem_write(RH,bytes(8))
   if route=='retained':call(m,0x401774c0,[O+0x8c,RH],stack_top=RESETSTACK,limit=100000)
   else:call(m,0x400e562a,[PP,M],stack_top=RESETSTACK,limit=100000)
   before=state_of(m);ref_before=bytes(u.mem_read(O+0x84,16));count_before=rd(u,RC+4) if RC else 0;rb=registry(u,app);regs=saved(u);install(m,live);body=[];guard=[]
   h=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:body.append(pc),begin=0x400e7e7e,end=0x400e7e7e)
   h2=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:guard.append(pc),begin=guardcfg['base'],end=guardcfg['base']+len(blob)-1)
   # Execute real outer manager around restoration; explicit selection uses
   # its actual shared helper. No host changes PC or result to choose denial.
   if route=='retained':
    PH=H+0x80;u.reg_write(UC_M68K_REG_A0,PH);call(m,0x400e43fc,[app,PP],stack_top=RESETSTACK,limit=100000);fn=0x400e6352;args=[M,PH,0];end=0x400e64ae
   else:fn=0x400e47e6;args=[O,RH];end=0x400e4846
   regs=saved(u);u.mem_write(0x47fdff00,u32(0xdeadbee0)+b''.join(u32(x) for x in args));u.reg_write(UC_M68K_REG_SR,0x201f);u.reg_write(UC_M68K_REG_A7,0x47fdff00);u.emu_start(fn,0xdeadbee0,count=500000);assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0
   u.hook_del(h);u.hook_del(h2);balanced(u,regs);after=state_of(m)
   denied=kind=='audio' and live;assert bool(guard)==(not (route=='retained' and kind=='null'))
   if denied:
    assert ref_before==bytes(u.mem_read(O+0x84,16)) and rd(u,RC+4)==count_before and before==after and not body
    if route=='retained':assert registry(u,app)['entries']==rb['entries']+[PP] and rd(u,PP+0x2c)==M
    else:assert registry(u,app)==rb and u.reg_read(UC_M68K_REG_D0)==0
   else:
    assert bytes(u.mem_read(O+0x84,8))==u32(requested)+u32(RC)
    if route=='retained':assert bytes(u.mem_read(O+0x8c,8))==bytes(8)
    assert len(body)==int(kind=='audio') and (before['audio_vector']!=after['audio_vector'])==bool(body)
    assert all(before[k]==after[k] for k in before if k!='audio_vector')
   assert rd(u,M+8)==(TASK if recursive else 0) and rd(u,M+4)==0
   results.append({'route':route,'kind':kind,'compiled_live_control':live,'recursive':recursive,'guard_instructions_executed':bool(guard),'protected_audio_deferred_or_refused':denied,'audio_entry_body_count':len(body),'native_register_stack_mutex_and_ref_checks':True,'host_branch_or_return_injection':False,'retained_state_and_application_setup_controlled':True});print('PASS overlay',route,kind,live,recursive,flush=True)
Path('outputs/Digitone-E04-PC-ui-defer-overlay-tests.json').write_text(json.dumps({'PC_only':True,'passed':True,'native_guard_in_disposable_overlay':True,'persistent_latch_installed':False,'ISA_C_custom_MOVE_checks_pass':True,'cases':results,'limits':['Compiled live constant is selected by test setup; no native persistent latch/startup admission.','Code is loaded at a fixture-only address, not certified executable placement.','Parent uses stock settings base-constructor prefix; complete settings construction and all entry routes remain unproven.','No firmware container or existing raw candidate modified.']},indent=2))
