from pathlib import Path
s=Path('work/test-PC-live-storage-playback.py').read_text()
s=s.replace('from pathlib import Path','from pathlib import Path\nimport json',1)
s=s.replace(" s=original(path,*args,**kwargs)"," s=original(path,*args,**kwargs)\n if path.name=='PC_ONLY-live-capture-layout.json':return json.dumps(json.loads(original(Path('work/os144/PC_ONLY-atomic-storage-layout.json')))['live'])")
s=s.replace('Digitone-E04-PC-live-storage-startup.json','Digitone-E04-PC-atomic-storage-startup.json').replace('Digitone-E04-PC-live-storage-playback.json','Digitone-E04-PC-atomic-storage-playback.json')
s=s.replace('PC_ONLY-live-storage-payload.bin','PC_ONLY-atomic-storage-payload.bin')
s=s.replace("session.m.install_isa_patches_scoped(full[0x3400:0x3530],0x47be3400)", "session.m.install_isa_patches_scoped(full[0x3400:0x3530],0x47be3400);session.m.install_isa_patches_scoped(full[0x3600:0x36b6],0x47be3600)\\n    uc.hook_add(UC_HOOK_CODE,strict,begin=0x47be3600,end=0x47be36b5)")
exec(compile(s,'atomic-copy-startup-playback','exec'))
