"""Consolidate bounded native persistence evidence; never create firmware."""
from pathlib import Path
import hashlib,json,py_compile

names=['bridge-contracts','startup','native-save-load','explicit-cache-flush','cache-reboot','playback']
reports={n:json.loads(Path('outputs/Digitone-E10-PC-persistence-'+n+'.json').read_text(encoding='utf-8')) for n in names}
assert all(r['passed'] for r in reports.values())
assert reports['native-save-load']['native_retained_mirror_records_match']==128
assert reports['native-save-load']['native_serialized_records_match']==128
assert reports['cache-reboot']['record_count']==128
assert reports['cache-reboot']['preceding_cache_flush_explicitly_invoked']
assert not reports['cache-reboot']['automatic_power_fail_persistence_verified']
assert reports['playback']['matching_note_pairs']==23
assert reports['playback']['observed_DIN_notes']==reports['playback']['observed_USB_notes']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
e09a='outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx'
assert sha(e09a)=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c'
layout=json.loads(Path('work/os144/PC_ONLY-E10-persistence-layout.json').read_text())
assert sha('work/os144/PC_ONLY-E10-persistence-main.bin')==layout['main_sha256']
assert sha('work/os144/PC_ONLY-E10-persistence-payload.bin')==layout['payload_sha256']
sources=['build-PC-E10-persistence-bridge.py','integrate-PC-E10-persistence.py']+['test-PC-E10-persistence-'+('bridge' if n=='bridge-contracts' else n)+'.py' for n in names]
for name in sources:py_compile.compile(str(Path('work')/name),doraise=True)
out=dict(PC_only=True,passed=True,patterns=128,code_bytes_added=sum(r['bytes'] for r in layout['persistence']['regions']),copied_payload_bytes=layout['payload_bytes'],native_helpers_installed=True,bank_records_host_injected_in_integration_tests=False,initial_named_file_is_prior_diagnostic_fixture=True,explicit_cache_flush_entry_is_fixture=True,automatic_power_fail_persistence_verified=False,editor_to_pattern_bank_connected=False,automatic_pattern_recall=False,E09A_sha256=sha(e09a),E09A_unchanged=True,firmware_container_created=False,hardware_ready=False,checks={n:r['passed'] for n,r in reports.items()},source_sha256={n:sha(Path('work')/n) for n in sources},limits=['Input named file has 128 prior diagnostic records. The integrated tests insert no bank records, helper bytes or MAIN hooks; the native copier installs code.','The retained-cache writer is explicitly invoked on a separate PC card; physical power-loss dispatch, timing and persistence are not established.','Direct MAIN startup with unchanged E09A DSP/resources, not an E10 packaged loader path.','Editor publication, automatic pattern recall, copy/clear/undo and asynchronous replacement remain unconnected or uncertified.','Expanded RAM ownership and physical cache/timing are not certified.'])
Path('outputs/Digitone-E10-PC-persistence-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Native persistence evidence: six checks pass; 128 records; 23 matched note pairs per port; E09A unchanged.')
