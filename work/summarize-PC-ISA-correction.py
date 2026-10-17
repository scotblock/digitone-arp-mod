from pathlib import Path
import json,hashlib
layout=json.loads(Path('outputs/Digitone-E04-PC-ISA-correction-layout.json').read_text())
contracts=json.loads(Path('outputs/Digitone-E04-PC-ISA-fallback-contracts.json').read_text())
startup=json.loads(Path('outputs/Digitone-E04-PC-ISA-startup-checks.json').read_text())
assert contracts['passed'] and len(contracts['cases'])==33 and len(contracts['full_SR_checks'])==33
assert all(c['incoming']==c['returned'] for c in contracts['full_SR_checks'])
summary={'PC_only':True,'packaged_firmware_modified':False,'fallback_contract_cases':33,'copier_registers_and_status_match_original':layout['copier_comparison']['all_registers_SR_and_continuation_match_old'],'startup_cases':[]}
for r in startup['cases']:
 assert r['passed'] and not r['strict_failures'] and r['intro']['up']
 restored=r['image'] in ['E04_restored','E04_post_stock_bad_magic'];disabled=r['image'] in ['E04_bad_pointer','E04_post_stock_bad_magic']
 assert len(r['capture_inputs'])==(4 if restored else 8)
 assert r['candidate_after_cold'][:8]==('00000000' if disabled else '800000bc' if restored else '80000043')
 if restored:
  assert any(e['pc']=='0x400a838c' and e['d0']=='0x1' for e in r['restore_events'])
  assert any(e['pc']=='0x400a83f4' for e in r['restore_events'])
  assert not any(e['pc']=='0x400a8402' for e in r['restore_events'])
  assert all(c['root']=='3c' and c['scale']=='00' for c in r['capture_inputs'])
 assert sum(r['strict_instruction_checks'].values())>4000
 summary['startup_cases'].append({'case':r['image'],'passed':True,'UI_up':True,'mod_disabled':disabled,'capture_count':len(r['capture_inputs']),'strict_custom_instruction_checks':sum(r['strict_instruction_checks'].values()),'candidate_word':r['candidate_after_cold'][:8],'native_timer_interrupts':r['timer_fired'],'host_completion_kicks':r['completion_kicks'],'general_intro_satisfactions':r['intro']['general_satisfactions']})
assert len(summary['startup_cases'])==4
expected={'outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx':'76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c','work/os144/emulator-E04-main.bin':'686dc4675e5af33f2e3b313e9101f92b914c0a848d0a858424b2d335d85b186c','work/os144/fallback-final-payload.bin':'eb908e6ae5ac26490bf4fea0216ba8fcfbff258a8f8ea0f7159342a00e14d2e7'}
for path,golden in expected.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==golden
summary['unchanged_originals']=expected
cards=json.loads(Path('outputs/Digitone-E04-saved-project-state-checks.json').read_text())
for row in cards['cards']:
 h=hashlib.sha256()
 with open(row['path'],'rb') as f:
  while block:=f.read(1024*1024):h.update(block)
 assert h.hexdigest()==row['sha256']
summary['original_cards_unchanged']=True
fixture=json.loads(Path('outputs/Digitone-E04-PC-saved-mirror-fixtures.json').read_text())
with open('work/os144/PC_ONLY-saved-mirror-valid_first.img','rb') as f:f.seek(0xf400000);p=f.read(fixture['payload_bytes'])
assert hashlib.sha256(p).hexdigest()==fixture['payload_sha256']
summary['restored_mirror_source_unchanged']=True
summary['limits']=['Raw MAIN overlay with original E04 flash source; not a rebuilt container/loader-to-corrected-image test.','Functional startup and injected metadata failures; bus faults, actual exception recovery and a non-returning stock initializer remain outside this test.','Physical instruction-cache coherence, RAM ownership and timing remain unverified.']
Path('outputs/Digitone-E04-PC-ISA-correction-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
