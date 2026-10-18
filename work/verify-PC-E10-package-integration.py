"""Consolidate actual internal E10 package/loader/startup/playback evidence."""
from pathlib import Path
import json,hashlib,struct,sys,py_compile
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from dt2.container import decode_syx
names=['container','loader','startup','playback'];reports={n:json.loads(Path('outputs/Digitone-E10-PC-package-'+n+'.json').read_text(encoding='utf-8')) for n in names}
assert all(r['passed'] for r in reports.values())
c=json.loads(Path('work/os144/PC_ONLY-E10-package-layout.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
syx=Path(c['candidate']);assert sha(syx.read_bytes())==c['candidate_sha256']==reports['loader']['candidate_sha256']==reports['startup']['candidate_sha256']
stream=decode_syx(syx);declared,checksum=struct.unpack_from('>II',stream)
body=stream[8:8+declared];assert len(body)==declared and not stream[8+declared:].strip(b'\0')
assert sum((i+1)^x[0] for i,x in enumerate(struct.iter_unpack('>I',body)))&0xffffffff==checksum
raw=syx.read_bytes();frames=[];i=0
while i<len(raw):
 assert raw[i]==0xf0;j=raw.index(0xf7,i);frames.append(raw[i+1:j]);i=j+1
base=frames[0][7];assert len(frames[0])==len(frames[-1])==14
for frame in frames[1:-1]:
 assert len(frame)==126 and all(v<128 for v in frame)
 assert frame[-1]==(base+sum(v^(base+j) for j,v in enumerate(frame[6:-1])))&127
assert reports['loader']['reached']=='0x400004e8' and reports['loader']['main_matches'] and not reports['loader']['flash_writes']
start=reports['startup'];case=start['cases'][0]
assert start['loader_derived_E10_state'] and case['loader_derived_MAIN_exact'] and case['copied_components_verified'] and not case['strict_failures'] and case['depack_clamps']==0 and case['completion_kicks']==0 and start['restored_records_match']==128
play=reports['playback'];assert play['loader_derived_E10_state'] and play['keyboard_and_sequence_covered'] and play['observed_DIN_notes']==play['observed_USB_notes'] and play['matching_note_pairs']>=12
assert play['restored_A01_A02_preserved'] and play['A03_native_editor_record_valid']
for kind in ['main','payload']:
 data=Path('work/os144/PC_ONLY-E10-package-'+kind+'.bin').read_bytes();assert sha(data)==c[kind+'_sha256'] and data==Path('work/os144/PC_ONLY-E10-life-'+kind+'.bin').read_bytes()
e09a=sha(Path('outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx').read_bytes());assert e09a=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c'
sources=['build-PC-E10-package.py','test-PC-E10-package-loader.py','test-PC-E10-package-startup.py','test-PC-E10-package-playback.py','verify-PC-E10-package-integration.py']
for n in sources:py_compile.compile('work/'+n,doraise=True)
r=dict(PC_only=True,passed=True,package_loader_startup_playback_connected=True,main_payload_identical_to_lifecycle_candidate=True,loader_derived_state=True,SYX_packet_checksums_verified=True,logical_container_checksum_verified=True,loader_MAIN_exact=True,flash_writes_observed=0,strict_ColdFire_startup_passed=True,restored_pattern_records=128,native_A03_editor_program_verified=True,restored_A01_A02_preserved=True,keyboard_and_sequence_covered=True,DIN_USB_matching_note_pairs=play['matching_note_pairs'],candidate_sha256=c['candidate_sha256'],main_sha256=c['main_sha256'],payload_sha256=c['payload_sha256'],copied_payload_bytes=c['payload_bytes'],E09A_unchanged=True,E09A_sha256=e09a,internal_test_container_created=True,firmware_release_created=False,hardware_ready=False,stock_power_handling='Accepted inherited assumption; no abrupt-loss guarantee or physical hold-up measurement gate.',checks={n:x['passed'] for n,x in reports.items()},source_hash_normalization='UTF-8 with LF newlines',source_sha256={n:sha(Path('work/'+n).read_text(encoding='utf-8').encode('utf-8')) for n in sources},limits=['Stock bootstrap, serialized loader handoff, native cold start, logo/UI snapshot, then native playback session; not one uninterrupted machine. No helper/hook/state initialization or sequence settings are host-inserted into the tested application.','Loader flash/PLL/DDR, scoped ISA, DSP/peripheral and board input models remain; stock flash-read shortcut and synthetic idle scheduling remain. No physical cache coherence or timing claim.','MIDI input, routing and USB endpoint handoff use inherited disclosed fixtures; no physical port certification.','The input private card contains previously native-created records. All 128 restore; A03 is programmed for this run without modifying the first two. No named save/reload, copy/reset or new failure-injection workload is added here.','The internal SYX is not a hardware-ready release or proof of the MIDI update receiver. No device update, new project format, stock power redesign or install recommendation is made.'])
Path('outputs/Digitone-E10-PC-package-integration.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print('Internal E10 loader/startup/playback integration passes;',play['matching_note_pairs'],'matched pairs per port. No hardware release.')
