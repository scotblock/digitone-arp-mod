"""Native copier and full cold startup with persistence code installed."""
from pathlib import Path
import json,sys,zlib
source=Path('work/test-PC-E10-integrated-startup.py').read_text()
for old,new in [('PC_ONLY-E10-startup-layout.json','PC_ONLY-E10-persistence-layout.json'),('PC_ONLY-E10-startup-full-layout.json','PC_ONLY-E10-persistence-full-layout.json'),('PC_ONLY-E10-startup-main.bin','PC_ONLY-E10-persistence-main.bin'),('PC_ONLY-E10-startup-payload.bin','PC_ONLY-E10-persistence-payload.bin'),('Digitone-E10-PC-integrated-startup.json','Digitone-E10-PC-persistence-startup.json')]:source=source.replace(old,new)
anchor="exec(compile(source,'E10-direct-MAIN-native-startup','exec'))"
extra="source=source.replace('work/os144/PC_ONLY-saved-mirror-valid_first.img','work/E10-storage-save-load/plusdrive.img').replace('work/E10-startup-','work/E10-persistence-startup-').replace('generated-E10-startup.py','generated-E10-persistence-startup.py')\n"
assert anchor in source;source=source.replace(anchor,extra+anchor);exec(compile(source,'E10-persistence-full-startup','exec'))
from emu.snapshot import _load_blob
from emu.harness import PAGE
p=Path('outputs/Digitone-E10-PC-persistence-startup.json');r=json.loads(p.read_text());case=r['cases'][0];b=_load_blob(case['ui_snapshot']);pages={a:zlib.decompress(v) for a,v in b['pages'].items()}
c=json.loads(Path('work/os144/PC_ONLY-E10-persistence-layout.json').read_text());meta=c['persistence']['meta']
def peek(a,n):return bytes(pages.get((a+i)&~(PAGE-1),bytes(PAGE))[(a+i)&(PAGE-1)] for i in range(n))
fields=[int.from_bytes(peek(meta+i,4),'big') for i in range(0,32,4)]
assert fields[0]==0x4d535031 and fields[1]==1 and fields[3]>=1 and fields[4]==0,fields
assert peek(c['E10']['bank'],4096)==bytes(4096)
r.update(persistence_helpers_host_loaded=False,persistence_hooks_host_patched=False,native_cold_capture_executed=True,persistence_metadata=fields,limits=r['limits']+['The input working cache is the previously verified zero-extension cache. Named-file load/cache preservation is tested in the next scenario.'])
r['native_project_persistence']=True
p.write_text(json.dumps(r,indent=2));print('Native cold project capture reached, defaults remain empty; UI up.')
