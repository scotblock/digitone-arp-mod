from pathlib import Path
exec(Path('work/test-PC-release-reset-controls.py').read_text().split('\np=0')[0])
defer_cfg=json.loads(Path('work/os144/PC_ONLY-deferred-release-overlay.json').read_text());defer_blob=Path('work/os144/PC_ONLY-deferred-release-overlay.bin').read_bytes()
def install_deferred(m):
 m.load(defer_blob,defer_cfg['base']);m.install_isa_patches_scoped(defer_blob,defer_cfg['base']);m.ensure(defer_cfg['count']);m.uc.mem_write(defer_cfg['count'],bytes(defer_cfg['storage_bytes']))
 for h in defer_cfg['hooks']:
  assert bytes(m.uc.mem_read(h['site'],h['length'])).hex()==h['previous'],h['name'];m.uc.mem_write(h['site'],bytes.fromhex(h['replacement']))
def fresh():
 m=restored('work/startup-producer-order-E04_restored/producer-0x4008d3ec.snap');install_inputs(m);install_release(m);install_deferred(m);return m
pos=0
while pos<len(defer_blob):
 ins=cfisa.decode(lambda off:int.from_bytes(defer_blob[pos+off:pos+off+2],'big'),defer_cfg['base']+pos)
 assert not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(defer_blob[pos:pos+2],'big')),(hex(defer_cfg['base']+pos),ins.op)
 pos+=ins.length
assert pos==len(defer_blob)
r={'PC_only':True,'ISA_passed':True,'boolean_controls':[],'queue_controls':[]}
for phase in [0,0x434f4c44,0x494e4954,0x4641494c]:
 for incoming in [0,1,127,0xffffff00]:
  m=fresh();u=m.uc;u.mem_write(STATE,u32(phase));u.reg_write(UC_M68K_REG_D0,incoming);before=watched(u);saved=regs(u);invoke(u,0x400f0580,[1,60,32],count=2000)
  assert u.reg_read(UC_M68K_REG_D0)==1 and regs(u)[1:]==saved[1:] and u.reg_read(UC_M68K_REG_SR)==0x201f and watched(u)==before
  r['boolean_controls'].append({'phase':hex(phase),'incoming_D0':hex(incoming),'refusal_result':1,'other_registers_SR_storage_preserved':True})
m=fresh();u=m.uc;u.mem_write(STATE,u32(P['initializing']));before=watched(u)
for i in range(4):invoke(u,0x400eabb4,[1,60,32],count=5000)
assert rd(u,defer_cfg['count'])==1 and bytes(u.mem_read(defer_cfg['entries'],12))==struct.pack('>III',1,60,32) and watched(u)==before
r['queue_controls'].append({'duplicate_exact_releases_coalesce':True,'no_original_note_storage_mutation':True})
for note in range(31):invoke(u,0x400eabb4,[1,note,32],count=5000)
assert rd(u,defer_cfg['count'])==32
invoke(u,0x400eabb4,[1,100,32],count=5000);assert rd(u,defer_cfg['count'])==32 and rd(u,defer_cfg['error'])==1
invoke(u,0x47fa0044,[1],count=10000);assert u.reg_read(UC_M68K_REG_D0)==0 and rd(u,STATE)==P['initializing'] and rd(u,defer_cfg['count'])==32
r['queue_controls'].append({'capacity':32,'overflow_latches_error_and_prevents_LIVE':True})
for phase in ['initializing','live','failed']:
 m=fresh();u=m.uc;u.mem_write(STATE,u32(P[phase]));invoke(u,0x47fa0044,[1],count=10000)
 assert rd(u,STATE)==P['live' if phase=='initializing' else phase] and u.reg_read(UC_M68K_REG_D0)==int(phase=='initializing')
 r['queue_controls'].append({'phase':phase,'empty_completion_dispatch_correct':True})
m=fresh();u=m.uc;u.mem_write(STATE,u32(P['initializing']));invoke(u,0x47fa0044,[0]);assert rd(u,STATE)==P['failed'] and u.reg_read(UC_M68K_REG_D0)==1
r.update(passed=True,original_failure_completion_preserved=True);Path('outputs/Digitone-E04-PC-deferred-release-controls.json').write_text(json.dumps(r,indent=2));print('PASS refusal boolean, bounded/coalesced queue and completion dispatch')
