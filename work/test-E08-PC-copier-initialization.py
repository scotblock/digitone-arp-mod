from pathlib import Path
import sys,json,struct,hashlib
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from emu.harness import Machine
cfg=json.loads(Path('work/os144/E08-PC-install-layout.json').read_text());old=json.loads(Path('outputs/Digitone-E07-PC-candidate-layout.json').read_text());main=Path('work/os144/E08-PC-layout-main.bin').read_bytes();payload=Path('work/os144/E08-PC-layout-payload.bin').read_bytes();PB=0x47be0000;MB=0x40000400;STACK=0x47bcff00;rows=[]
for label,ret in [('cold',0x4000053e),('wrong_caller',0x40000540)]:
 m=Machine(ddr=0x08000000);u=m.uc
 for a in range(MB&~4095,MB+len(main),4096):m.ensure(a)
 for a in range(PB,PB+len(payload)+4096,4096):m.ensure(a)
 m.ensure(STACK);u.mem_write(MB,main);u.mem_write(PB,b'\xa7'*(len(payload)+32))
 # Decoder checks include original copier and all relocated executable regions.
 for r in [dict(name='copier',base=0x4029c4b0,bytes=110)]+cfg['regions']+[dict(name='cold_seed',base=0x47be3b22,bytes=150)]:
  data=main if r['base']<PB else payload;base=MB if r['base']<PB else PB;code=data[r['base']-base:r['base']-base+r['bytes']];off=0
  while off<len(code):
   ins=cfisa.decode(lambda x:int.from_bytes(code[off+x:off+x+2],'big'),r['base']+off);assert ins.length>0 and off+ins.length<=len(code) and not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(code[off:off+2],'big')),(r,off,ins);off+=ins.length
  # Native copier supplies these later; install only generic ISA adapters.
  m.install_isa_patches_scoped(code,r['base'])
 u.reg_write(UC_M68K_REG_SR,0x2700);u.reg_write(UC_M68K_REG_A7,STACK);u.mem_write(STACK,struct.pack('>I',ret));seen=[]
 def observe(uc,pc,n,d):
  if pc in [cfg['bootstrap'],cfg['entries']['init'],cfg['entries']['configure']]:seen.append(hex(pc))
 u.hook_add(UC_HOOK_CODE,observe)
 end=0x40001df4 if label=='cold' else 0x47be3b00
 u.emu_start(0x4029c4b0,end,count=200000)
 assert u.reg_read(UC_M68K_REG_PC)==end
 get=lambda a:int.from_bytes(u.mem_read(a,4),'big')
 # Exact preservation of executable bytes and lookup table after native copying.
 for r in cfg['regions']+cfg['data_regions']:
  assert bytes(u.mem_read(r['base'],r['bytes']))==payload[r['base']-PB:r['base']-PB+r['bytes']],r['name']
 assert bytes(u.mem_read(PB+len(payload),32))==b'\xa7'*32
 if label=='cold':
  assert get(0x47be2840)==0x434f4c44 and get(cfg['state'])==0x4d314131 and get(cfg['state']+4)==0 and get(cfg['state']+8)==0
  assert get(cfg['state']+32)==5400000 and get(cfg['state']+36)==1350000 and get(cfg['state']+40)==0x4138f208 and get(cfg['state']+304)==2 and get(cfg['state']+308)==50
  assert bytes(u.mem_read(cfg['arena'],64))==bytes(64) and len(seen)==3
 else:
  assert get(cfg['state'])==0 and not seen
 rows.append({'case':label,'stop_pc':hex(end),'native_calls':seen,'default_M1_OFF':get(cfg['state']+4)==0,'copied_bytes':len(payload),'exact_native_code_copy':True,'passed':True})
print('PASS cold copier/initialization and wrong-caller exclusion')
Path('outputs/Digitone-E08-PC-copier-initialization.json').write_text(json.dumps({'PC_only':True,'passed':True,'cases':rows,'strict_ColdFire_checked':True,'payload_bytes':len(payload),'additional_copy_bytes':cfg['additional_copy_bytes'],'source_start':hex(cfg['copy_source']),'source_end':hex(cfg['copy_source_end']),'destination_end':hex(cfg['copy_destination_end']),'limits':['Native copier through cold-success initializer reaches the existing stock cache-handoff entry; the subsequent cache/application startup is not executed by this isolated test.','Wrong-caller check proves no M1 initializer call after inherited cold guard rejection; it does not make copier replay safe.','No packed container/loader continuity, physical cache behavior or exclusive RAM ownership proof.']},indent=2))
