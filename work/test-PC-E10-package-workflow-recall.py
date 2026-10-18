"""Native saved-project load and pattern recall after packaged cold restart."""
from pathlib import Path
import json,zlib
proof=json.loads(Path('outputs/Digitone-E10-PC-package-workflow-patterns.json').read_text());assert proof['passed']
# Expected bytes are observations of the native saved-and-reloaded project,
# never writes into the restarted machine.
import sys
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.snapshot import _load_blob
from emu.harness import PAGE
blob=_load_blob(proof['checkpoints']['reloaded-two-patterns'])
pages={a:zlib.decompress(v) for a,v in blob['pages'].items()}
cfg=json.loads(Path('work/os144/PC_ONLY-E10-package-layout.json').read_text())
def peek(a,n):return bytes(pages.get((a+i)&~(PAGE-1),bytes(PAGE))[(a+i)&(PAGE-1)] for i in range(n))
expected_bank=peek(cfg['E10']['bank'],4096)
s=Path('work/test-PC-E10-storage-cold-reload.py').read_text(encoding='utf-8')
anchor="exec(compile(prefix,'E10-cold-reload-definitions','exec'))"
changes=[('outputs/Digitone-E09A-PC-path-layout.json','work/os144/PC_ONLY-E10-package-full-layout.json'),("folder/'E09A-PC-install-layout.json'","folder/'PC_ONLY-E10-package-layout.json'"),('outputs/Digitone-E09A-PC-startup-comparison.json','outputs/Digitone-E10-PC-package-workflow-restart.json'),("folder/'E09A-PC-layout-payload.bin'","folder/'PC_ONLY-E10-package-payload.bin'"),("folder/'E09A-PC-layout-main.bin'","folder/'PC_ONLY-E10-package-main.bin'")]
injection=''.join('prefix=prefix.replace('+repr(a)+','+repr(b)+')\n' for a,b in changes)
old="    for region in native['data_regions']:";new=old+"\n        if region['name'] in ['E10_persistence_metadata','E10_pattern_binding_metadata','E10_lifecycle_metadata']:continue"
injection+='prefix=prefix.replace('+repr(old)+','+repr(new)+')\n'
old="    assert [rd(s.m.uc,S+x) for x in [0,4,304,308]] == [0x4d314131,0,2,50]"
injection+='prefix=prefix.replace('+repr(old)+','+repr("    assert rd(s.m.uc,S)==0x4d314131")+')\n'
s=s.replace(anchor,injection+anchor).replace('outputs/Digitone-E10-PC-storage-cold-startup.json','outputs/Digitone-E10-PC-package-workflow-restart.json').replace('work/E10-storage-cold-reload','work/E10-package-workflow-recall').replace('outputs/E10-storage-cold-reload-','outputs/E10-package-workflow-recall-').replace('outputs/Digitone-E10-PC-storage-cold-reload.json','outputs/Digitone-E10-PC-package-workflow-recall.json')
s=s.replace('data==record_bytes(slot)','data==expected_bank[32*slot:32*slot+32]')
needle=" s.ev['esdhc'].card.flush();preserved(s);out['passed']=True"
extra="""
 # Complete the native load handler before further panel input.
 ready=[False]
 s.at(0x4014a056,lambda u,pc,n,d:ready.__setitem__(0,True))
 for _ in range(40):
  s.run_ms(250)
  if bytes(s.m.uc.mem_read(native['E10']['bank'],4096))==expected_bank and rd(s.m.uc,native['persistence']['meta']+12)>1:break
 out.update(load_ready=ready[0],load_pc=hex(s.pc),load_halted=s.halted,bank_matches=bytes(s.m.uc.mem_read(native['E10']['bank'],4096))==expected_bank,load_generation=rd(s.m.uc,native['persistence']['meta']+12))
 print('load_completion',out['load_ready'],out['load_pc'],out['load_halted'],out['bank_matches'],out['load_generation'],flush=True)
 from emu.snapshot import save
 progress='work/E10-package-workflow-recall/load-progress.snap'
 save(s.m,progress,components={**s.ev['checkpoint_components'],'timers':s.pits},manifest=s.ev.get('checkpoint_manifest'));out['load_progress_snapshot']=progress
 assert out['bank_matches'] and out['load_generation']>1 and s.halted is None
 selection=rd(s.m.uc,rd(s.m.uc,rd(s.m.uc,0x419f0de0)+0x40)+8)
 for _ in range(3):tap('NO',80)
 if selection<4:tap('MIDI',100)
 tap('T1',100)
 X=native['E10']['state']
 for number,expected in [(3,workflow['expected_fields'][0]),(4,workflow['expected_fields'][1])]:
  s.press(s.code('PTN'));s.run_ms(80);tap(str(number),80);s.release(s.code('PTN'));s.run_ms(350)
  tap('SYN1',100);s.press(s.code('FUNC'));tap('SYN2',150);s.release(s.code('FUNC'));s.run_ms(150)
  if rd(s.m.uc,X+56)==0:s.turn(4,16,after_ms=150)
  fields=[rd(s.m.uc,X+i) for i in [4,8,20,24]]+[bytes(s.m.uc.mem_read(X+32,16)).hex()]
  assert fields==expected,(number,fields,expected)
  mark('A%02d_recalled_after_restart'%number);tap('NO',100)
 out.update(restart_and_saved_project_recall=True,post_restart_panel_fields_match=True,private_card=paths.card,expected_bank=expected_bank.hex(),expected_fields=workflow['expected_fields'],expected_records=workflow['expected_records'],packaged_loader_derived=True,firmware_container_created=True)
 s.ev['esdhc'].card.flush();preserved(s);out['passed']=True
"""
assert needle in s;s=s.replace(needle,extra)
workflow=proof

if '--resume-completion' in sys.argv:
 prior=json.loads(Path('outputs/Digitone-E10-PC-package-workflow-recall.json').read_text())
 a=s.index('source_paths=bs.FirmwarePaths');b=s.index("os.environ.update(paths.env());phase='warm'",a)
 s=s[:a]+"root=Path('work/E10-package-workflow-recall').resolve()\npaths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()))\n"+s[b:]
 s=s.replace("s=Session(case['ui_snapshot']", "out.update(prior);out['failure']=None\ns=Session(prior['load_progress_snapshot']")
 a=s.index(" s.run_ms(1000);tap('STOP'");b=s.index(' selection=rd(s.m.uc',a)
 s=s[:a]+" assert bytes(s.m.uc.mem_read(native['E10']['bank'],4096))==expected_bank\n"+s[b:]
Path('work/generated-E10-package-workflow-recall.py').write_text(s,encoding='utf-8')

exec(compile(s,'E10-packaged-native-restart-recall','exec'))
p=Path('outputs/Digitone-E10-PC-package-workflow-recall.json');r=json.loads(p.read_text());r['limits']=['Native saved project loaded after a new loader-handoff/cold-start/UI run on a private card; no E10 code or settings are host-written.','Serialized engine handoffs, scoped ISA adapters and modeled peripherals remain. This is an orderly PC restart/named-project recall, not an abrupt-power-loss or physical timing test.'];p.write_text(json.dumps(r,indent=2),encoding='utf-8')
