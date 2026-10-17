"""Reboot a separate copy of the native-save probe card; observe, never seed."""
from pathlib import Path
import json,sys
sys.path.insert(0,'work')
from E10_storage_probe import record_bytes
proof=json.loads(Path('outputs/Digitone-E10-PC-storage-native-save-load.json').read_text());assert proof['passed']
exec(compile(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0],'E10-cold-probe-ISA-definitions','exec'))
from unicorn.m68k_const import UC_M68K_REG_A5,UC_M68K_REG_D3
cfg=json.loads(Path('outputs/Digitone-E09A-PC-path-layout.json').read_text())
probes=[]
def cold_probe_install(mm,stage):
 def decoded(u,pc,n,d):
  offset=u.reg_read(UC_M68K_REG_D3)
  assert offset%0xa00==0;slot=offset//0xa00;assert slot<128
  address=u.reg_read(UC_M68K_REG_A5)+offset;raw=bytes(u.mem_read(address+0x940,32))
  probes.append(dict(stage=stage,slot=slot,address=hex(address),matches=raw==record_bytes(slot),actual=raw.hex()))
 mm.uc.hook_add(UC_HOOK_CODE,decoded,begin=0x4000e960,end=0x4000e960)
source=Path('work/generated-E09A-startup.py').read_text()
source=source.replace('work/os144/PC_ONLY-saved-mirror-valid_first.img','work/E10-storage-save-load/plusdrive.img')
source=source.replace('work/E09A-startup-','work/E10-storage-cold-')
source=source.replace('outputs/Digitone-E09A-PC-startup-comparison.json','outputs/Digitone-E10-PC-storage-cold-startup.json')
source=source.replace('machine_out=box)',"machine_out=box,handoff='work/os144/E09A-PC-loader-handoff.bin')")
source=source.replace("  sp=m.uc.reg_read(UC_M68K_REG_A7);m.uc.mem_write(sp+4,struct.pack('>I',0x00140000))", "  assert bytes(m.uc.mem_read(0x40000400,len(image)))==image")
source=source.replace('  done=0;timer=',"  cold_probe_install(m,'cold')\n  done=0;timer=")
source=source.replace("   held['ev']=ev", "   held['ev']=ev\n   cold_probe_install(mm,'intro')")
exec(compile(source,'E10-storage-cold-startup','exec'))
p=Path('outputs/Digitone-E10-PC-storage-cold-startup.json');r=json.loads(p.read_text())
r.update(diagnostic_record_host_injection=False,code_overlay=False,loader_derived_E09A_state=True,serialized_candidate_observations=probes,all_128_slots_observed={x['slot'] for x in probes}==set(range(128)),all_observed_records_match=bool(probes) and all(x['matches'] for x in probes))
r['limits'].append('The unchanged firmware ignores this extension; observations test serialized storage survival, not E10 sequence restoration. No candidate bytes or helper instructions are seeded during cold startup.')
p.write_text(json.dumps(r,indent=2));assert r['passed']
print('Cold startup passed; candidate observations:',len(probes),'matching:',sum(x['matches'] for x in probes),flush=True)
