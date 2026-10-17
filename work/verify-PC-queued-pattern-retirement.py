from pathlib import Path
import json,hashlib
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
files=['Digitone-E04-PC-queued-pattern-retirement-controls.json','Digitone-E04-PC-queued-pattern-reset-refusal-controls.json','Digitone-E04-PC-queued-pattern-native-parent-rebind.json'];reports=[json.loads(Path('outputs/'+f).read_text()) for f in files];assert all(r['passed'] for r in reports)
rows=[]
for file,report in zip(files,reports):
 for c in report['cases']:
  assert c['passed'] and c['halted'] is None and c['queue_unchanged'];events=c['events'];kinds=[e['kind'] for e in events];published=next(e for e in events if e['kind']=='queue_published');selected=next(e for e in events if e['kind']=='callback_selected');converted=next(e for e in events if e['kind']=='native_conversion');assert converted['destination']=='0x407ef9f4' and selected['destination']=='0x407ef9f4'
  destroy=next(i for i,e in enumerate(events) if e['kind']=='manager_destroy' and e['descriptor']==selected['descriptor']);free=next(i for i,e in enumerate(events) if e['kind']=='descriptor_free' and e['descriptor']==selected['descriptor']);assert kinds.index('native_conversion')<destroy<free
  assert published['descriptor']!=selected['descriptor'];assert any(e['kind']=='descriptor_clone' and e['descriptor']==selected['descriptor'] for e in events)
  row={'mode':c['mode'],'published_descriptor':published['descriptor'],'selected_clone':selected['descriptor'],'owner_field_at_consume':selected['owner_field'],'actual_conversion_destination':converted['destination'],'selected_clone_destroyed_after_conversion':True,'queue_copy_freed':any(e['kind']=='descriptor_free' and e['descriptor']==published['descriptor'] for e in events),'passed':True}
  if c['mode'].endswith('_refused'):
   assert 'stock_reset_body_entered' not in kinds and 'guard_refused_and_returned' in kinds;row['refused_before_monitored_mutation']=True;row['callback_then_retired']=True
  if c['mode']=='native_parent_rebind':assert selected['owner_field']=='0x40a96df8';row['full_native_parent_rebind_returned']=True
  if 'PC_only_guest_stub' in c:
   code=bytes.fromhex(c['PC_only_guest_stub']['bytes']);base=int(c['PC_only_guest_stub']['address'],16);p=0;instructions=[]
   while p<len(code):
    ins=cfisa.decode(lambda off:int.from_bytes(code[p+off:p+off+2],'big'),base+p);assert ins.length>0 and not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(code[p:p+2],'big'));instructions.append(ins.op);p+=ins.length
   assert p==len(code);row['temporary_guest_stub_ISA_checked']=True
  rows.append(row)
old=json.loads(Path('outputs/Digitone-E04-PC-input-live-summary.json').read_text())
for file,h in old['hashes'].items():assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==h
spec=json.loads(Path('work/os144/PC_ONLY-resident-deferred-release-overlay.json').read_text());assert hashlib.sha256(Path('work/os144/PC_ONLY-resident-deferred-release-overlay.bin').read_bytes()).hexdigest()==spec['sha256']
r={'PC_only':True,'passed':True,'cases':rows,'queue_baseline_field_controls':3,'native_reset_refusal_controls':4,'native_parent_rebinding_controls':1,'stock_field_clear_or_parent_rebind_cancels_old_callback':False,'selected_clone_retirement_observed':True,'queue_copy_retirement_observed':True,'naturally_scheduled_rebind_or_reset_overlap_proven':False,'parent_destruction_and_every_reset_caller_certified':False,'exclusive_storage_ownership_certified':False,'firmware_and_existing_overlay_binaries_unchanged':True,'evidence':files,'limits':['Field clear/rebind controls use host changes at queue publication; full parent/reset controls use transient PC guest call stubs at that boundary.','Existing modified PC guards refuse LIVE reset entries; this is not a claim that stock reset entries provide that protection.','Monitored reset fingerprint covers owner, custom context/queue and selected stock pool/flag spans, not every RAM address.','Clones contain raw owner/destination pointers; this evidence does not prove owner retention through arbitrary destruction or full DDR reset.','Emulator scheduling, clocks and cache behavior remain modeled; no physical hardware-ready claim.']}
Path('outputs/Digitone-E04-PC-queued-pattern-retirement-summary.json').write_text(json.dumps(r,indent=2));print('PASS 8 queue lifecycle controls; 4 reset guards; full native parent rebind; firmware hashes unchanged')
