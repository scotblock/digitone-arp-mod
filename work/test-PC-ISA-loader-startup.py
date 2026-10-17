from pathlib import Path
s=Path('work/test-PC-ISA-corrected-startup.py').read_text()
s=s.replace(",('E04_bad_pointer','work/os144-emulator-E02-engine/plusdrive.img'),('E04_post_stock_bad_magic','work/os144/PC_ONLY-saved-mirror-valid_first.img')",'')
s=s.replace('ISA-corrected-startup-','ISA-loader-startup-')
s=s.replace('Digitone-E04-PC-ISA-startup-checks.json','Digitone-E04-PC-ISA-loader-startup.json')
extra=r'''
from emu import bootrom
from unicorn.m68k_const import UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6
s=s.replace('machine_out=box)',"machine_out=box,handoff='work/os144/E04-loader-handoff.bin')")
old="  sp=m.uc.reg_read(UC_M68K_REG_A7);m.uc.mem_write(sp+4,struct.pack('>I',0x00140000))"
new="""  old_image=Path('work/os144/emulator-E04-main.bin').read_bytes()
  assert bytes(m.uc.mem_read(0x40000400,len(old_image)))==old_image
  regs=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7,UC_M68K_REG_SR,UC_M68K_REG_PC]
  inherited=lambda: {'regs':[m.uc.reg_read(k) for k in regs],'ctlregs':dict(m.ctlregs),'sram_sha256':hashlib.sha256(bytes(m.uc.mem_read(0x80000000,65536))).hexdigest(),'stack':bytes(m.uc.mem_read(m.uc.reg_read(UC_M68K_REG_A7),32)).hex()}
  before=inherited()
  m.uc.mem_write(0x40000400,image)
  assert inherited()==before and bytes(m.uc.mem_read(0x40000400,len(image)))==image
  row['loader_handoff']={'path':'work/os144/E04-loader-handoff.bin','start_pc':hex(box['start_pc']),'original_main_verified':True,'state_preserved_by_overlay':True,'state':before,'changed_bytes':sum(a!=b for a,b in zip(old_image,image))}
  assert int.from_bytes(bytes(m.uc.mem_read(m.uc.reg_read(UC_M68K_REG_A7)+4,4)),'big')==0x00140000"""
assert old in s;s=s.replace(old,new)
s=s.replace('paths.cold,budget=', 'paths.cold,out=paths.gui_raw,budget=')
s=s.replace("  row['passed']=True", "  row['ui_snapshot']=paths.gui_raw\n  row['passed']=True")
'''
anchor="exec(compile(s,'PC-ISA-corrected-startup','exec'))"
assert anchor in s;s=s.replace(anchor,extra+"\n"+anchor)
exec(compile(s,'loader-derived-corrected-overlay','exec'))
