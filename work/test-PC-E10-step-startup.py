"""Actual native copier -> old cold initialization -> E10 -> cache handoff.

Stops at the established stock cache-handoff entry, not full application boot.
"""
from pathlib import Path
import json,struct,hashlib
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from emu.harness import Machine
c=json.loads(Path('work/os144/PC_ONLY-E10-startup-layout.json').read_text());life=c['E10'];PB=c['base'];MB=0x40000400
main=Path('work/os144/PC_ONLY-E10-startup-main.bin').read_bytes();payload=Path('work/os144/PC_ONLY-E10-startup-payload.bin').read_bytes();STACK=0x47bcff00;rows=[]
for case in ['cold_poisoned','wrong_caller','initializer_refusal']:
 m=Machine(ddr=0x8000000);u=m.uc
 for p in range(MB&~4095,MB+len(main),4096):m.ensure(p)
 for p in range(PB,PB+len(payload)+4096,4096):m.ensure(p)
 m.ensure(STACK);u.mem_write(MB,main);u.mem_write(PB,b'\xa7'*(len(payload)+32))
 for r in [dict(name='copier',base=0x4029c4b0,bytes=110)]+c['regions']+[dict(name='cold_seed',base=0x47be3b22,bytes=150)]:
  base=MB if r['base']<PB else PB;data=main if base==MB else payload;raw=data[r['base']-base:r['base']-base+r['bytes']];off=0
  while off<len(raw):
   ins=cfisa.decode(lambda x:int.from_bytes(raw[off+x:off+x+2],'big'),r['base']+off)
   assert ins.length and off+ins.length<=len(raw) and not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(raw[off:off+2],'big')),(r,off,ins)
   off+=ins.length
  m.install_isa_patches_scoped(raw,r['base'])
 seen=[]
 def observe(uc,pc,n,d):
  if pc in [c['bootstrap'],c['entries']['init'],c['E10_bootstrap'],life['entries']['init'],0x40001df4]:seen.append(hex(pc))
  if pc==life['entries']['init']:
   # Poison only data immediately before the actual native initializer runs.
   uc.mem_write(life['state'],b'\xa7'*64);uc.mem_write(life['bank'],b'\xa7'*life['bank_bytes'])
   if case=='initializer_refusal':uc.mem_write(c['state']+280,struct.pack('>I',1))
 u.hook_add(UC_HOOK_CODE,observe)
 ret=0x40000540 if case=='wrong_caller' else 0x4000053e
 u.reg_write(UC_M68K_REG_SR,0x2700);u.reg_write(UC_M68K_REG_A7,STACK);u.mem_write(STACK,struct.pack('>I',ret))
 end=0x47be3b00 if case=='wrong_caller' else 0x40001df4
 u.emu_start(0x4029c4b0,end,count=400000);assert u.reg_read(UC_M68K_REG_PC)==end
 get=lambda p:int.from_bytes(u.mem_read(p,4),'big')
 for r in c['regions']+c['data_regions']:
  assert bytes(u.mem_read(r['base'],r['bytes']))==payload[r['base']-PB:r['base']-PB+r['bytes']],r['name']
 assert bytes(u.mem_read(PB+len(payload),32))==b'\xa7'*32
 if case=='cold_poisoned':
  assert get(life['state'])==0x4d535131 and get(life['state']+4)==0 and get(life['state']+8)==16
  assert get(life['state']+20)==0xffff and get(life['state']+24)==0x80000080
  assert bytes(u.mem_read(life['state']+28,36))==bytes(36)
  assert bytes(u.mem_read(life['bank'],4096))==bytes(4096) and get(c['E10_status'])==1
  assert [get(c['state']+x) for x in [0,4,304,308]]==[0x4d314131,0,2,50]
 elif case=='wrong_caller':assert not seen and get(life['state'])==0 and get(c['E10_status'])==0
 else:
  assert get(c['E10_status'])==0 and get(life['state'])==0 and get(life['state']+56)==0
  assert bytes(u.mem_read(life['bank'],4096))==b'\xa7'*4096 and get(c['state']+280)==1
 rows.append(dict(case=case,passed=True,stop_pc=hex(end),native_calls=seen,exact_code_and_labels_copied=True))
out=dict(PC_only=True,passed=True,cases=rows,payload_bytes=len(payload),extra_bytes_over_E09A=c['extra_bytes_over_E09A'],strict_ColdFire_checked=True,state_initialized_by_native_code=True,firmware_container_created=False,native_project_persistence=False,limits=['This executes the actual copier through cold success and the cache-handoff entry, not the loader or full application/playback.','Data poisoning and the refused-initializer condition are deliberate PC fixtures. Physical cache coherence and expanded RAM ownership remain unverified.'])
Path('outputs/Digitone-E10-PC-step-startup.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
