from pathlib import Path
s=Path('work/test-PC-live-storage-startup.py').read_text()
s=s.replace('PC_ONLY-live-storage','PC_ONLY-atomic-storage').replace('live-storage-startup-','atomic-storage-startup-').replace('Digitone-E04-PC-live-storage-startup.json','Digitone-E04-PC-atomic-storage-startup.json')
s=s.replace("  s=s.replace(\"s=s.replace(\\\",('E04_bad_pointer','work/os144-emulator-E02-engine/plusdrive.img'),('E04_post_stock_bad_magic','work/os144/PC_ONLY-saved-mirror-valid_first.img')\\\",'')\",'')",'')
s=s.replace("len(out['cases'])==4","len(out['cases'])==2")
s=s.replace('(0x47be3000,0x47be31d9)','(0x47be3000,0x47be31d9),(0x47be3600,0x47be36b5)')
s=s.replace('mm.install_isa_patches_scoped(payload[0x3000:0x31da],0x47be3000)', 'mm.install_isa_patches_scoped(payload[0x3000:0x31da],0x47be3000);mm.install_isa_patches_scoped(payload[0x3600:0x36b6],0x47be3600)')
exec(compile(s,'atomic-copy-startup','exec'))
