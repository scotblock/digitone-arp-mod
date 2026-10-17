"""Verify automatic modeled dispatch and retain the failed cut-safety result."""
from pathlib import Path
import hashlib,json,py_compile
reports={n:json.loads(Path('outputs/Digitone-E10-PC-'+n+'.json').read_text()) for n in ['powerfail-status','powergood-startup','auto-powerfail','auto-powerfail-reboot','powerfail-cut-first-command','powerfail-cut-first-command-0','powerfail-cut-first-command-2785280']}
assert all(reports[n]['passed'] for n in ['powerfail-status','powergood-startup','auto-powerfail','auto-powerfail-reboot'])
a=reports['auto-powerfail'];boot=reports['auto-powerfail-reboot'];cut=reports['powerfail-cut-first-command']
assert a['native_unsaved_edit'] and a['ready_byte']==1 and not a['explicit_host_entry'] and a['forced_fired']['30']==1 and a['records_match']==128
assert len(a['commands'])==86 and all(v['command']==25 and v['bytes']==32768 for v in a['commands'])
assert boot['unsaved_editor_cold_restore_verified'] and boot['restored_records_match']==128 and boot['preceding_writer_interrupt_dispatched'] and not boot['physical_power_loss_verified']
for n in ['powerfail-cut-first-command','powerfail-cut-first-command-0','powerfail-cut-first-command-2785280']:assert reports[n]['test_completed']
assert reports['powerfail-cut-first-command-0']['all_previous_records']
assert reports['powerfail-cut-first-command-2785280']['all_new_records']
assert cut['observed_partial_new_bank_selection'] and not cut['all_previous_records'] and not cut['all_new_records']
stock=Path('work/os144/section-3.bin').read_bytes();main=Path('work/os144/PC_ONLY-E10-life-main.bin').read_bytes();base=0x40000400
for lo,hi in [(0x40001e00,0x40002126),(0x4008cdf2,0x4008ce10),(0x400a7a6c,0x400a8452),(0x4008511a,0x40085268)]:assert main[lo-base:hi-base]==stock[lo-base:hi-base]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
layout=json.loads(Path('work/os144/PC_ONLY-E10-life-layout.json').read_text());assert sha('work/os144/PC_ONLY-E10-life-main.bin')==layout['main_sha256'] and sha('work/os144/PC_ONLY-E10-life-payload.bin')==layout['payload_sha256']
e09a=sha('outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx');assert e09a=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c'
sources=['E10_powerfail_fixture.py','E10_powerfail_startup_template.py','test-PC-E10-powerfail-status.py','test-PC-E10-powergood-startup.py','test-PC-E10-auto-powerfail.py','test-PC-E10-auto-powerfail-reboot.py','test-PC-E10-powerfail-cut.py','verify-PC-E10-powerfail.py']
for n in sources:py_compile.compile('work/'+n,doraise=True)
out=dict(PC_only=True,verification_completed=True,automatic_modeled_dispatch_and_cold_restore_passed=True,unsaved_records_recovered=128,physical_power_loss_verified=False,mid_write_recovery_safe=False,partial_write_counterexample_observed=True,stock_dispatch_writer_reader_checksum_bytes_unchanged=True,E10_main_payload_unchanged=True,E09A_unchanged=True,E09A_sha256=e09a,firmware_container_created=False,hardware_ready=False,checks={n:r.get('passed',r.get('test_completed')) for n,r in reports.items()},source_hash_normalization='UTF-8 with LF newlines',source_sha256={n:hashlib.sha256(Path('work/'+n).read_text(encoding='utf-8').encode('utf-8')).hexdigest() for n in sources},limits=['Board-sense high input, pin C2 low plus external vector 66 are PC fixtures; physical wiring/thresholds are not measured.','INTC2 source 30 delivery uses the generic forced-interrupt model, synthetic idle scheduler yield is disabled, and CC/TC acknowledgements use a narrow W1C adapter. eMMC payload copy and completion are immediate.','The completed-write path reaches cache-loop completion before a fresh native cold boot; final power-latch hardware is not tested.','The cut controls reconstruct zero/one/all completed commands before old-bank invalidation and invoke the actual stock cold reader in a stopped entry fixture. No torn sector or physical brownout is simulated.','Only pending bank 0 with old bank 1 is covered. It exposes a counterexample, not an exhaustive storage-fault proof.'])
Path('outputs/Digitone-E10-PC-powerfail-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Modeled automatic dispatch/cold recovery pass; first-command cut is unsafe; physical power loss remains unverified.')
