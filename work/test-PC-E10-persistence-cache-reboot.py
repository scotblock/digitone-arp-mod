"""Cold restoration after an explicitly invoked stock cache writer.

This proves native bytes can restore; automatic power-fail dispatch is separate.
"""
from pathlib import Path
import json,sys,zlib
sys.path.insert(0,'work')
from E10_storage_probe import record_bytes
proof=json.loads(Path('outputs/Digitone-E10-PC-persistence-explicit-cache-flush.json').read_text())
assert proof['passed'] and proof['records_match']==128
source=Path('work/test-PC-E10-integrated-startup.py').read_text(encoding='utf-8')
for old,new in [('PC_ONLY-E10-startup','PC_ONLY-E10-persistence'),('Digitone-E10-PC-integrated-startup.json','Digitone-E10-PC-persistence-cache-reboot.json')]:
 source=source.replace(old,new)
before="assert bytes(m.uc.mem_read(cfg['E10']['bank'],4096))==bytes(4096)"
after="assert bytes(m.uc.mem_read(cfg['E10']['bank'],4096))==b''.join(record_bytes(i) for i in range(128))"
assert before in source;source=source.replace(before,after)
anchor="exec(compile(source,'E10-direct-MAIN-native-startup','exec'))"
# Adapt only the generated startup program, avoiding replacement collisions
# with the original startup evidence report used by other tests.
extra="source=source.replace('work/os144/PC_ONLY-saved-mirror-valid_first.img',"+repr(Path(proof['card']).as_posix())+").replace('work/E10-startup-','work/E10-persistence-cache-reboot-').replace('generated-E10-startup.py','generated-E10-persistence-cache-reboot.py')\n"
assert anchor in source;source=source.replace(anchor,extra+anchor)
exec(compile(source,'E10-cold-cache-control','exec'))
from emu.snapshot import _load_blob
from emu.harness import PAGE
p=Path('outputs/Digitone-E10-PC-persistence-cache-reboot.json');r=json.loads(p.read_text())
assert r['passed']
b=_load_blob(r['cases'][0]['ui_snapshot']);pages={a:zlib.decompress(v) for a,v in b['pages'].items()}
c=json.loads(Path('work/os144/PC_ONLY-E10-persistence-layout.json').read_text())
def peek(a,n):return bytes(pages.get((a+i)&~(PAGE-1),bytes(PAGE))[(a+i)&(PAGE-1)] for i in range(n))
assert peek(c['E10']['bank'],4096)==b''.join(record_bytes(i) for i in range(128))
fields=[int.from_bytes(peek(c['persistence']['meta']+i,4),'big') for i in range(0,32,4)]
assert fields[0]==0x4d535031 and fields[1]==1 and fields[4]==128
r.update(native_working_cache_cold_restoration_verified=True,record_count=128,bank_host_written=False,diagnostic_record_host_injection=False,preceding_cache_flush_explicitly_invoked=True,automatic_power_fail_persistence_verified=False,persistence_metadata=fields,native_project_persistence=True)
r['limits'].append('The preceding test explicitly called the stock cache writer. This does not establish automatic power-loss dispatch or physical persistence.')
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
print('Cold native restoration of all 128 records after explicit native cache flush.',flush=True)
