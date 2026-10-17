from pathlib import Path
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
cfg=json.loads(Path('work/os144/PC_ONLY-live-storage-layout.json').read_text());image=Path('work/os144/PC_ONLY-live-storage-main.bin').read_bytes();payload_new=Path('work/os144/PC_ONLY-live-storage-payload.bin').read_bytes()
for address,length in cfg['regions']:
 data=image if address<0x47000000 else payload_new;load=0x40000400 if address<0x47000000 else 0x47be0000;p=address
 while p<address+length:
  ins=cfisa.decode(lambda off:int.from_bytes(data[p-load+off:p-load+off+2],'big'),p)
  assert not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(data[p-load:p-load+2],'big')),(hex(p),ins.op)
  p+=ins.length
 assert p==address+length
s=Path('work/test-os144-startup-fallback-design.py').read_text();s=s[s.index("out={'PC_only'"):]
exec(Path('work/audit-E02-startup-failure.py').read_text().split('\ntry:\n for mode')[0])
old_machine=machine
def machine():
 m=old_machine();uc=m.uc;m.load(image,0x40000400);m.load(payload_new,0x47be0000);m.install_isa_patches_scoped(payload_new[cfg['fallback_address']-RAM:cfg['fallback_address']-RAM+cfg['fallback_bytes']],cfg['fallback_address']);m.install_isa_patches_scoped(payload_new[0x3000:0x3000+cfg['live']['bytes']],RAM+0x3000)
 uc.mem_write(PTR,u32(0x47bccf04));uc.mem_write(BSS,struct.pack('>III',0x534c4332,2,0xb70)+bytes([0xa5])*(0xb70-12));uc.mem_write(cfg['state'],bytes([0xa5])*cfg['state_bytes']);uc.mem_write(cfg['state']-16,bytes([0x6d])*16);uc.mem_write(cfg['state']+cfg['state_bytes'],bytes([0x7e])*16)
 return m
ENTRY=cfg['fallback_address'];TRAMP=0x47be0642;EXPECTED=0x47bccf04;code=payload_new[ENTRY-RAM:ENTRY-RAM+cfg['fallback_bytes']]
s=s.replace('Digitone-OS1.44-startup-fallback-design-checks.json','Digitone-E04-PC-live-storage-reset.json').replace('for sr in [0x2000,0x2300,0x2700]:','for sr in [0x201f,0x231f,0x271f]:').replace('uc.reg_read(UC_M68K_REG_SR)&0x2700==sr','uc.reg_read(UC_M68K_REG_SR)==sr')
anchor="   # Compare the actual initializer's pool writes/return against its stock trampoline on the same capture."
extra="""   cleared=mode in ['valid','unready','pointer_changes_during_stock','header_changes_during_stock']
   assert bytes(uc.mem_read(cfg['state'],cfg['state_bytes']))==bytes([0 if cleared else 0xa5])*cfg['state_bytes']
   assert bytes(uc.mem_read(cfg['state']-16,16))==bytes([0x6d])*16 and bytes(uc.mem_read(cfg['state']+cfg['state_bytes'],16))==bytes([0x7e])*16
   assert bytes(uc.mem_read(RAM+0x3000,cfg['live']['bytes']))==payload_new[0x3000:0x3000+cfg['live']['bytes']]
"""
assert anchor in s;s=s.replace(anchor,extra+anchor)
exec(compile(s,'live-storage-reset-contracts','exec'))
# Actual early copier into deliberately dirty RAM, stopping at stock continuation.
m=machine();uc=m.uc;uc.mem_write(RAM,bytes([0xa5])*len(payload_new));uc.reg_write(UC_M68K_REG_SR,0x2710);uc.reg_write(UC_M68K_REG_A7,STACK);uc.emu_start(0x4029c4b0,0x40001df4,count=100000)
assert uc.reg_read(UC_M68K_REG_PC)==0x40001df4 and bytes(uc.mem_read(RAM+0x3000,cfg['live']['bytes']))==payload_new[0x3000:0x3000+cfg['live']['bytes']]
assert bytes(uc.mem_read(cfg['state'],cfg['state_bytes']))==bytes(cfg['state_bytes']) and int.from_bytes(uc.mem_read(0x47be1010,4),'big')==0
assert bytes(uc.mem_read(ENTRY,cfg['fallback_bytes']))==code
dest=Path('outputs/Digitone-E04-PC-live-storage-reset.json');r=json.loads(dest.read_text());r['cold_copier']={'live_code_copied_exactly':True,'reset_code_copied_exactly':True,'extra_storage_zeroed':True,'ready_still_zero':True};r['strict_static_checks']=True
# Dirty state between successive real stock-initializer calls; no host clear.
m=machine();uc=m.uc
for j in range(3):
 uc.mem_write(cfg['state'],bytes([0x91+j])*cfg['state_bytes']);call(m,ENTRY,[158],stack_top=STACK,limit=400000)
 assert bytes(uc.mem_read(cfg['state'],cfg['state_bytes']))==bytes(cfg['state_bytes']) and int.from_bytes(uc.mem_read(0x47be1010,4),'big')==1
r['three_reinitializations_clear_extra_storage']=True;dest.write_text(json.dumps(r,indent=2));print('PASS actual copier and three repeated stock initializer/reset calls')
