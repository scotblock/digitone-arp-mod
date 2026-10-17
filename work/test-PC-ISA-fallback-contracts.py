from pathlib import Path
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
s=Path('work/test-os144-startup-fallback-design.py').read_text()
s=s.replace('ENTRY=0x47f40000','ENTRY=0x47be08a4')
s=s.replace('Digitone-OS1.44-startup-fallback-design-checks.json','Digitone-E04-PC-ISA-fallback-contracts.json')
s=s.replace('for sr in [0x2000,0x2300,0x2700]:','for sr in [0x201f,0x231f,0x271f]:')
s=s.replace('uc.reg_read(UC_M68K_REG_SR)&0x2700==sr','uc.reg_read(UC_M68K_REG_SR)&0x2700==(sr&0x2700)')
s=s.replace("assert all(uc.reg_read(reg)==value for reg,value in preserved.items())", "assert all(uc.reg_read(reg)==value for reg,value in preserved.items())\n   assert uc.reg_read(UC_M68K_REG_SR)==sr\n   out.setdefault('full_SR_checks',[]).append({'mode':mode,'incoming':hex(sr),'returned':hex(uc.reg_read(UC_M68K_REG_SR))})")
s=s.replace("code=a.done()", "assert a.done()==Path('work/os144/fallback-final-payload.bin').read_bytes()[2212:]\ncode=Path('work/os144/PC_ONLY-E04-ISA-corrected-payload.bin').read_bytes()[2212:]")
anchor="   m=machine();uc=m.uc;m.load(code,ENTRY);"
addition=r'''   m=machine();uc=m.uc
   def strict(uc,pc,size,data):
    ins=cfisa.decode(lambda off:int.from_bytes(uc.mem_read(pc+off,2),'big'),pc)
    assert not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF),(hex(pc),ins)
    assert not move_restriction(int.from_bytes(uc.mem_read(pc,2),'big')),hex(pc)
    assert not ins.flags&cfisa.PRIV or uc.reg_read(UC_M68K_REG_SR)&0x2000
   uc.hook_add(UC_HOOK_CODE,strict,begin=ENTRY,end=ENTRY+len(code)-1)
   m.load(code,ENTRY);'''
assert anchor in s;s=s.replace(anchor,addition)
exec(compile(s,'PC-ISA-fallback-contracts','exec'))
