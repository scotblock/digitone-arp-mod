"""Actual native helpers load the named file and emit save/cache records.

Input diagnostic file was produced by the previous storage verification. This
scenario writes no helper bytes, MAIN hooks, bank data or sequence settings.
"""
from pathlib import Path
import json
source=Path('work/test-PC-E10-storage-cold-reload.py').read_text(encoding='utf-8')
anchor="exec(compile(prefix,'E10-cold-reload-definitions','exec'))"
changes=[('outputs/Digitone-E09A-PC-path-layout.json','work/os144/PC_ONLY-E10-persistence-full-layout.json'),("folder/'E09A-PC-install-layout.json'","folder/'PC_ONLY-E10-persistence-layout.json'"),('outputs/Digitone-E09A-PC-startup-comparison.json','outputs/Digitone-E10-PC-persistence-startup.json'),("folder/'E09A-PC-layout-payload.bin'","folder/'PC_ONLY-E10-persistence-payload.bin'"),("folder/'E09A-PC-layout-main.bin'","folder/'PC_ONLY-E10-persistence-main.bin'")]
injection=''.join('prefix=prefix.replace('+repr(a)+','+repr(b)+')\n' for a,b in changes)
source=source.replace(anchor,injection+anchor).replace('outputs/Digitone-E10-PC-storage-cold-startup.json','outputs/Digitone-E10-PC-persistence-startup.json').replace('work/E10-storage-cold-reload','work/E10-persistence-save-load').replace('outputs/E10-storage-cold-reload-','outputs/E10-persistence-').replace('outputs/Digitone-E10-PC-storage-cold-reload.json','outputs/Digitone-E10-PC-persistence-native-save-load.json')
extra='''
original_persistence_install=install
def install(s):
 original_persistence_install(s)
 out['persistence_calls']=[]
 out['stock_cache_calls']=[]
 for address in [0x400a8200,0x400a8182,0x400a8160]:
  def cache_entered(u,pc,n,d):
   out['stock_cache_calls'].append(dict(pc=hex(pc),phase=phase,pending_bank=rd(u,0x402369e0),selected_bank=rd(u,0x402369e4)))
  s.at(address,cache_entered)
 for name,address in native['persistence']['entries'].items():
  def entered(u,pc,n,d,name=name):
   sp=u.reg_read(UC_M68K_REG_A7);meta=native['persistence']['meta']
   out['persistence_calls'].append(dict(kind=name,phase=phase,serialized=hex(rd(u,sp+4)),runtime_owner=hex(rd(u,sp+8)),bank_owner=hex(rd(u,meta+8)),valid=rd(u,meta+4)))
  s.at(address,entered)
'''
source=source.replace("s=Session(case['ui_snapshot']",extra+"\ns=Session(case['ui_snapshot']")
source=source.replace('from unicorn.m68k_const import UC_M68K_REG_A5,UC_M68K_REG_D3','from unicorn.m68k_const import UC_M68K_REG_A5,UC_M68K_REG_D3,UC_M68K_REG_A7')
anchor=" s.ev['esdhc'].card.flush();preserved(s);out['passed']=True"
extra='''
 bank=native['E10']['bank'];meta=native['persistence']['meta'];expected=b''.join(record_bytes(i) for i in range(128))
 assert bytes(s.m.uc.mem_read(bank,4096))==expected,'Native decode did not populate all bank records'
 assert rd(s.m.uc,meta+4)==1 and rd(s.m.uc,meta+16)==128
 out['metadata_after_load']=[rd(s.m.uc,meta+i) for i in range(0,32,4)]
 # Save As to the next empty slot, through the actual menus and stock writer.
 phase='save_named'
 for _ in range(3):tap('NO',150)
 s.press(s.code('FUNC'));s.run_ms(100);tap('GLOBAL');s.release(s.code('FUNC'));s.run_ms(300);mark('save_menu')
 tap('YES',800);tap('NO',200);tap('DOWN',200);tap('YES',800);mark('save_name');tap('YES',2000);s.run_ms(1000);mark('saved')
 out['metadata_after_save']=[rd(s.m.uc,meta+i) for i in range(0,32,4)]
 assert rd(s.m.uc,meta+24)==128,('Native emission did not find matching project ownership',out['persistence_calls'])
 assert bytes(s.m.uc.mem_read(bank,4096))==expected
 # Observe the native rebuilt retained mirror independently of its power-loss
 # flush. Do not manufacture an eMMC bank update when the PC run did not do it.
 mirror=0x40555ff4
 out['native_retained_mirror_records_match']=sum(bytes(s.m.uc.mem_read(mirror+0x240200+i*0xa00+0x940,32))==record_bytes(i) for i in range(128))
 assert out['native_retained_mirror_records_match']==128
 out['cache_bank_state_after_save']=dict(pending=rd(s.m.uc,0x402369e0),selected=rd(s.m.uc,0x402369e4))
 from emu.snapshot import save
 checkpoint='work/E10-persistence-save-load/post-save.snap'
 save(s.m,checkpoint,components={**s.ev['checkpoint_components'],'timers':s.pits},manifest=s.ev.get('checkpoint_manifest'))
 out['post_save_snapshot']=checkpoint
 out.update(persistence_helpers_host_loaded=False,persistence_hooks_host_patched=False,bank_host_written=False,native_load_capture_verified=True,native_named_save_emission_verified=True)
 s.ev['esdhc'].card.flush();preserved(s);out['passed']=True
'''
assert anchor in source;source=source.replace(anchor,extra)
exec(compile(source,'E10-native-persistence-load-save','exec'))
p=Path('outputs/Digitone-E10-PC-persistence-native-save-load.json');r=json.loads(p.read_text())
card=Path('work/E10-persistence-save-load/plusdrive.img');images=[]
with card.open('rb') as f:
 for base in [0xf400110,0xfc00000,0x10000000,0x10400000]:
  f.seek(base)
  if f.read(8)!=bytes.fromhex('beefbace0000000e'):continue
  matches=[]
  for slot in range(128):
   f.seek(base+0x240200+slot*0xa00+0x940);matches.append(f.read(32)==record_bytes(slot))
  images.append(dict(base=hex(base),matching_records=sum(matches)))
named_calls=[x for x in r['persistence_calls'] if x['kind']=='emit' and x['phase']=='save_named']
r['serialized_project_images']=images;r['native_named_save_encode_calls']=len(named_calls)
r['native_serialized_records_match']=max(x['matching_records'] for x in images)
r['cold_working_cache_restoration_pending']=True
r['passed']=r['passed'] and r['native_serialized_records_match']==128 and bool(named_calls)
if not r['passed']:r['failure']='Missing named-save emission or working-cache record mismatch.'
r['limits']=['Native copier-installed PC image; input named file contains prior diagnostic records, but this test injects no records, bank data, hooks or helper code.','Device editor publication and automatic pattern recall are not connected to the bank.','Physical storage/cache/timing, incremental kit writes, copy/clear and asynchronous project replacement are not certified.']
p.write_text(json.dumps(r,indent=2));assert r['passed'],('Persistence check failed',images,named_calls);print('Native load/save emits all 128 records; cold restoration is the next check.',flush=True)
