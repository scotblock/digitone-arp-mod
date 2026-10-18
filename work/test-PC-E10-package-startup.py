"""E10 stock-loader handoff through native copier/init/logo/UI."""
from pathlib import Path
import json,sys,zlib,hashlib
exec(Path('work/audit-E04-startup-ISA.py').read_text(encoding='utf-8').split('\nregions=')[0])
cfg=json.loads(Path('work/os144/PC_ONLY-E10-package-full-layout.json').read_text())
loader=json.loads(Path('outputs/Digitone-E10-PC-package-loader.json').read_text());assert loader['passed'] and loader['main_matches'] and loader['candidate_sha256']==cfg['candidate_sha256']
proof=json.loads(Path('outputs/Digitone-E10-PC-auto-powerfail.json').read_text());assert proof['passed']
expected_bank=bytes.fromhex(proof['expected_bank'])
source=Path('work/E10_powerfail_startup_template.py').read_text(encoding='utf-8')
for a,b in [('PC_ONLY-E10-life-payload.bin','PC_ONLY-E10-package-payload.bin'),('PC_ONLY-E10-life-main.bin','PC_ONLY-E10-package-main.bin'),('work/os144/E09A-PC-path-candidate.syx','work/os144/PC_ONLY-E10-package-loader-test.syx'),('work/E10-life-startup-','work/E10-package-startup-'),('outputs/Digitone-E10-PC-life-startup.json','outputs/Digitone-E10-PC-package-startup.json')]:source=source.replace(a,b)
source=source.replace('work/E10-bound-panel-patterns/plusdrive.img',Path(proof['card']).as_posix())
source=source.replace('machine_out=box)',"machine_out=box,handoff='work/os144/PC_ONLY-E10-package-loader-handoff.bin')")
old="  sp=m.uc.reg_read(UC_M68K_REG_A7);m.uc.mem_write(sp+4,struct.pack('>I',0x00140000))"
new="""  row['loader_handoff']='work/os144/PC_ONLY-E10-package-loader-handoff.bin'
  assert bytes(m.uc.mem_read(0x40000400,len(image)))==image
  row['loader_derived_MAIN_exact']=True
"""
assert old in source;source=source.replace(old,new)
old='  save(m,paths.cold'
new="""  assert row['depack_clamps']==0
  assert bytes(m.uc.mem_read(cfg['E10']['bank'],4096))==expected_bank
  assert int.from_bytes(m.uc.mem_read(cfg['E10_status'],4),'big')==1
  row['restored_E10_records_match']=128
  save(m,paths.cold"""
assert old in source;source=source.replace(old,new)
# Model only the stock enable-sense board input, as in the prior setup test.
source=source.replace('from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE','from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ')
fixture="""
  def power_sense(mm):
   def good(u,t,a,n,v,d):u.mem_write(0xec09401e,bytes([u.mem_read(0xec09401e,1)[0]|8]))
   mm.uc.hook_add(UC_HOOK_MEM_READ,good,begin=0xec09401e,end=0xec09401e)
  power_sense(m)
"""
source=source.replace("  row['loader_handoff']=",fixture+"  row['loader_handoff']=",1)
source=source.replace("   held['ev']=ev", "   held['ev']=ev\n   power_sense(mm)")
exec(compile(source,'E10-loader-native-copier-startup','exec'))
from emu.snapshot import _load_blob
from emu.harness import PAGE
p=Path('outputs/Digitone-E10-PC-package-startup.json');r=json.loads(p.read_text());assert r['passed']
b=_load_blob(r['cases'][0]['ui_snapshot']);pages={a:zlib.decompress(v) for a,v in b['pages'].items()}
def peek(a,n):return bytes(pages.get((a+i)&~(PAGE-1),bytes(PAGE))[(a+i)&(PAGE-1)] for i in range(n))
assert peek(cfg['E10']['bank'],4096)==expected_bank
r.update(loader_derived_E10_state=True,native_project_persistence=True,automatic_pattern_binding=True,editor_to_pattern_bank_connected=True,restored_records_match=128,helpers_host_loaded=False,hooks_host_patched=False,firmware_container_created=True,internal_loader_test_only=True,firmware_release_created=False,hardware_ready=False,candidate_sha256=cfg['candidate_sha256'])
r['limits']=['Actual stock loader bootstrap/handoff, native copier and init, then native logo/UI on a private card. Engine handoff/snapshots separate stages; no claim of one uninterrupted machine.','Inherited flash-read shortcut, scoped ColdFire ISA adapters, DSP/peripheral models and synthetic idle scheduler yield remain. No decompression clamp or completion-semaphore satisfaction occurred.','Enable-sense input and loader board strap are model fixtures. Physical cache/RAM/timing, full update receiver and abrupt-loss guarantees are outside this test. Stock power handling is the agreed inherited assumption.']
p.write_text(json.dumps(r,indent=2),encoding='utf-8');print('Loader-derived E10 startup and 128-record restoration pass.',flush=True)
