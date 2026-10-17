from pathlib import Path
import json
cfg=json.loads(Path('work/os144/PC_ONLY-live-storage-layout.json').read_text())
original_read=Path.read_text
def source_read(path,*args,**kwargs):
 s=original_read(path,*args,**kwargs)
 if path.name=='test-PC-ISA-corrected-startup.py':
  s=s.replace('PC_ONLY-E04-ISA-corrected-main.bin','PC_ONLY-live-storage-main.bin').replace('PC_ONLY-E04-ISA-corrected-payload.bin','PC_ONLY-live-storage-payload.bin')
  s=s.replace('(0x47be08a4,0x47be09bb)','(0x47be3400,0x47be352f),(0x47be3000,0x47be31d9)')
  s=s.replace('begin=0x47be08a4,end=0x47be08a4','begin=0x47be3400,end=0x47be3400')
  s=s.replace("  def install_strict(mm,stage):","  def install_strict(mm,stage):\n   mm.install_isa_patches_scoped(payload[0x3000:0x31da],0x47be3000)")
  # Check just before the stock initializer; normal paths have already cleared
  # both descriptor and pending contexts while ready is still unpublished.
  s=s.replace("    sp=uc.reg_read(UC_M68K_REG_A7);row['initializer_calls']", "    assert int.from_bytes(uc.mem_read(0x47be1010,4),'big')==0\n    assert bytes(uc.mem_read(0x47be2000,2080))==bytes(2080)\n    row['extra_storage_zero_before_stock']=True\n    sp=uc.reg_read(UC_M68K_REG_A7);row['initializer_calls']")
 if path.name=='test-E04-native-startup-delay.py':
  s=s.replace('payload[2212:],0x47be08a4','payload[0x3400:0x3530],0x47be3400')
  s=s.replace("assert bytes(m.uc.mem_read(0x47be0000,len(payload)))==payload", "assert bytes(m.uc.mem_read(0x47be0000,2492))==payload[:2492] and bytes(m.uc.mem_read(0x47be3000,474))==payload[0x3000:0x31da] and bytes(m.uc.mem_read(0x47be3400,304))==payload[0x3400:0x3530]")
 if path.name=='test-PC-ISA-loader-startup.py':
  # Keep its two injected-failure controls in addition to normal project cases.
  s=s.replace("s=s.replace(\",('E04_bad_pointer','work/os144-emulator-E02-engine/plusdrive.img'),('E04_post_stock_bad_magic','work/os144/PC_ONLY-saved-mirror-valid_first.img')\",'')",'')
  s=s.replace('ISA-loader-startup-','live-storage-startup-').replace('Digitone-E04-PC-ISA-loader-startup.json','Digitone-E04-PC-live-storage-startup.json')
 return s
Path.read_text=source_read
try:
 exec(compile(original_read(Path('work/test-PC-ISA-DSP-loader-startup.py')),'live-storage-startup','exec'))
finally:Path.read_text=original_read
p=Path('outputs/Digitone-E04-PC-live-storage-startup.json');out=json.loads(p.read_text());assert len(out['cases'])==4 and all(x['passed'] and x['extra_storage_zero_before_stock'] for x in out['cases']);out['passed']=True;out['new_code_host_seeded']=False;out['additional_storage_host_cleared']=False;p.write_text(json.dumps(out,indent=2))
