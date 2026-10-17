"""Keep named-file persistence and working-cache loss as separate verdicts."""
from pathlib import Path
import json,hashlib,sys
sys.path.insert(0,'work')
from E10_storage_probe import record_bytes
def report(name):
 r=json.loads(Path('outputs/Digitone-E10-PC-storage-'+name+'.json').read_text());assert r['passed'],name;return r
s=report('native-save-load');c=report('cold-startup');r=report('cold-reload');d=report('stock-decoder-control')
assert s['all_records_recovered'] and s['encoded_buffer_poisoned_after_save']
assert r['all_128_slots_reached'] and r['all_records_recovered'] and not r['diagnostic_record_host_injection'] and not r['code_overlay']
assert c['all_128_slots_observed'] and not c['all_observed_records_match']
assert len(c['serialized_candidate_observations'])==128 and all(x['actual']==bytes(32).hex() for x in c['serialized_candidate_observations'])
assert d['stock_runtime_decode_byte_identical'] and d['stock_reencode_drops_candidate']
card=Path('work/E10-storage-save-load/plusdrive.img');zero_slots=[]
with card.open('rb') as f:
 f.seek(0xf400110);head=f.read(8);assert head==bytes.fromhex('beefbace0000000e')
 for slot in range(128):
  f.seek(0xf400110+0x240200+slot*0xa00+0x940);zero_slots.append(f.read(32)==bytes(32))
assert all(zero_slots)
firmware=Path('outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx');digest=hashlib.sha256(firmware.read_bytes()).hexdigest()
assert digest=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c'
out=dict(PC_only=True,passed=True,scope='Candidate serialized storage verification; E10 helpers remain unconnected',candidate_kit_offset=['0x940','0x960'],candidate_bytes=32,patterns=128,
 named_project_native_save_reload_verified=True,named_project_cold_boot_then_reload_verified=True,
 native_cold_working_cache_preserves_records=False,cold_cache_zero_records=128,
 stock_kit_decode_byte_identical=True,stock_decode_reencode_loses_extension=True,
 injection_only_at_first_save=True,executable_patch_used=False,E10_runtime_restoration_implemented=False,E09A_unchanged=True,E09A_sha256=digest,
 verdict='Candidate survives named-project persistence, including a fresh cold boot and later native reload. It is not self-preserving through stock working-cache rebuilds. Both capture on decode and re-emission on encode are required before connecting E10.',
 required_integration=['Validate/capture each record during native project decode, before stock conversion discards it.','Emit records during both named saves and working-cache reconstruction, from the correctly bound per-project pattern bank.','Establish defaults for old/blank/malformed records and guard project replacement before changing bank ownership.','Keep copy/clear/undo, asynchronous replacement and physical behavior as separate validation scopes.'],
 limits=['Initial diagnostic records are PC host fixtures inserted at actual native serialize completion; no machine-code persistence hook is claimed.','Cold boot and named reload use the saved private card with no record injection. The emulator storage/DMA/cache models remain in use.','Passing these storage checks does not certify every writer, automatic pattern ownership or hardware readiness.'])
Path('outputs/Digitone-E10-PC-storage-verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
