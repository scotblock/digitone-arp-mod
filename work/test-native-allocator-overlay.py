"""Paired native stock/overlay allocation from the same settled stock snapshot."""
import pathlib
exec(pathlib.Path('work/test-native-arp-overlays.py').read_text().split('def run(mode):')[0])
from emu.harness import call
states=[]
for mode in ['stock','overlay']:
 def installed(session):
  if mode=='stock':return
  m=session.m;m.ensure(RAM);uc=m.uc;uc.mem_write(RAM,blob);uc.mem_write(PTR,bytes(0xb74));uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1));m.install_isa_patches_scoped(blob,RAM)
  uc.mem_write(BSS+32,bytes.fromhex('80000080')*128)
  pc=0x400f0626;assert bytes(uc.mem_read(pc,6))==stock[pc-base:pc-base+6];uc.mem_write(pc,bytes.fromhex('4ef9')+u32(layout['allocate_clear']['address']))
 session=Session(paths.gui,syx=str(SYX),ddr=DDR,on_machine=installed)
 try:
  uc=session.m.uc;session.m.ensure(0x47fdff00);call(session.m,0x400f0626,[],stack_top=0x47fdff00,limit=100000)
  assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
  registers={str(r):uc.reg_read(r) for r in [UC_M68K_REG_D0+i for i in range(8)]+[UC_M68K_REG_A0+i for i in range(8)]+[UC_M68K_REG_SR]}
  event=uc.reg_read(UC_M68K_REG_A0)
  states.append({'mode':mode,'registers':registers,'event':hex(event),'stock_pool_sha256':hashlib.sha256(bytes(uc.mem_read(0x4199da94,128*72))).hexdigest(),'candidate':rd(uc,BSS+32+(event-0x4199da94)//72*4) if mode=='overlay' else None})
 finally:session.close()
checks={'registers_and_SR_equal':states[0]['registers']==states[1]['registers'],'stock_pool_equal':states[0]['stock_pool_sha256']==states[1]['stock_pool_sha256'],'candidate_cleared':states[1]['candidate']==0}
pathlib.Path('outputs/Digitone-native-allocator-overlay-results.json').write_text(json.dumps({'checks':checks,'states':states,'firmware_modified':False},indent=2))
assert all(checks.values()),checks
print('PASS paired allocator:',checks)
