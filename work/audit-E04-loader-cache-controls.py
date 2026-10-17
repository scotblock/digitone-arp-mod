from pathlib import Path
s=Path('work/validate-os144-E04-loader.py').read_text()
prefix=s.split("exec(compile(s,'E04-packaged-loader-validation','exec'))")[0]
exec(compile(prefix,'construct-E04-loader-trace','exec'))
s=s.replace('Digitone-OS1.44E04-stock-loader-check.json','Digitone-OS1.44E04-loader-cache-controls.json')
# Preserve the primary handoff artifact; this run is a register-write audit.
s=s.replace("bootrom.save_handoff(r,'work/os144/E04-loader-handoff.bin')","bootrom.save_handoff(r,'work/os144/E04-cache-audit-handoff.bin')")
needle=' def boundary(uc,pc,n,d):'
addition='''
 candidates=set()
 for filename,base in [('work/os144/startup-bootstrap-image.bin',0x80000400),('work/os144/startup-updater-image.bin',0x80000400),('work/os144/emulator-E04-main.bin',0x40000400)]:
  raw=Path(filename).read_bytes()
  for offset in range(0,len(raw)-3,2):
   if raw[offset:offset+2]==bytes.fromhex('4e7b') and int.from_bytes(raw[offset+2:offset+4],'big')&0xfff==2:candidates.add(base+offset)
 def control(uc,pc,n,d):
  raw=bytes(uc.mem_read(pc,4))
  if raw[:2]!=bytes.fromhex('4e7b'):return
  ext=int.from_bytes(raw[2:],'big')
  if ext&0xfff!=2:return
  value=uc.reg_read((UC_M68K_REG_A0 if ext&0x8000 else UC_M68K_REG_D0)+((ext>>12)&7))
  out.setdefault('CACR_writes',[]).append({'pc':hex(pc),'value':hex(value),'I_enable':bool(value&0x8000),'I_invalidate':bool(value&0x100),'D_enable':bool(value&0x80000000),'D_invalidate':bool(value&0x1000000),'branch_invalidate':bool(value&0x40000)})
 for pc in candidates:uc.hook_add(UC_HOOK_CODE,control,begin=pc,end=pc)
'''
assert needle in s;s=s.replace(needle,addition+needle)
exec(compile(s,'E04-loader-control-trace','exec'))
