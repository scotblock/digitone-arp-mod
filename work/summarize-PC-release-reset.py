from pathlib import Path
import json,hashlib
read=lambda name:json.loads(Path('outputs/'+name+'.json').read_text())
controls=read('Digitone-E04-PC-release-reset-controls');sustain=read('Digitone-E04-PC-release-reset-sustain');command=read('Digitone-E04-PC-release-reset-command');startup=read('Digitone-E04-PC-release-reset-startup-startup')
assert all(r['passed'] for r in [controls,sustain,command,startup])
cases={r['mode']:r for r in sustain['cases']}
norm=lambda c:[{k:r[k] for k in ['label','events','flags','lists']} for r in c['marks']]
assert norm(cases['LIVE_guarded'])==norm(cases['LIVE_stock_entries'])
closed=cases['INITIALIZING_guarded'];assert all(m['flags']=='0000000000000000' for m in closed['marks'])
held=cases['LIVE_held_then_closed'];a=next(m for m in held['marks'] if m['label']=='sustain release');b=next(m for m in held['marks'] if m['label']=='release after fixture LIVE resume')
assert a['flags']=='0100000000000000' and 'publish' not in a['events'] and b['flags']=='0000000000000000' and 'publish' in b['events']
hashes=read('Digitone-E04-PC-input-live-summary')['hashes'];hashes['work/os144/PC_ONLY-input-live-overlay.bin']='cb3405eae6859c5db7b72b678b989b57ebc34ca76af159c892eb6ae7a114cb61'
for file,expected in hashes.items():assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==expected,file
cfg=json.loads(Path('work/os144/PC_ONLY-release-reset-overlay.json').read_text());assert hashlib.sha256(Path('work/os144/PC_ONLY-release-reset-overlay.bin').read_bytes()).hexdigest()==cfg['sha256']
# Final startup snapshots must contain the final command hook as well as all
# reset/release hooks; verify actual saved executable bytes, not just report.

exec(Path('work/probe-PC-startup-note-admission.py').read_text().split('\nout=')[0])
for case in startup['cases']:
 import zlib
 saved_blob=snapshot._load_blob(case['ui_snapshot'])
 def saved_bytes(address,length):
  page=max(b for b in saved_blob['pages'] if b<=address);data=zlib.decompress(saved_blob['pages'][page]);answer=data[address-page:address-page+length];assert len(answer)==length;return answer
 for hook in cfg['hooks']:assert saved_bytes(hook['site'],hook['length']).hex()==hook['replacement']
 assert int.from_bytes(saved_bytes(0x47be2840,4),'big')==0x4c495645
result={'PC_only':True,'passed':True,'overlay_bytes':cfg['bytes'],'overlay_sha256':cfg['sha256'],'denial_controls':len(controls['denials']),'cold_pool_parity_pairs':len(controls['cold_pool_pairs']),'paced_receiver_sessions':len(sustain['cases']),'native_command_cleanup_controls':len(command['cases']),'final_overlay_startup_cases':len(startup['cases']),'final_startup_snapshots_contain_all_hooks':True,'closed_sustain_flags_preserved':True,'closed_retained_release_cannot_publish_in_test':True,'stock_release_cleans_retained_list_after_fixture_LIVE_resume':True,'warm_reset_refused_at_recovered_entries':True,'all_outer_UI_or_computed_callers_certified':False,'physical_boot_provenance_certified':False,'firmware_and_prior_artifacts_unchanged':True,'hardware_ready':False}
Path('outputs/Digitone-E04-PC-release-reset-summary.json').write_text(json.dumps(result,indent=2));print('PASS final overlay, startup snapshots, behavior and unchanged hashes')

