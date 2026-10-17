"""Consolidate scoped E10 lifecycle evidence; never build a container."""
from pathlib import Path
import json,hashlib,py_compile
names=['lifecycle-contracts','life-startup','life-named-load','life-copy-cache','life-reset-refusal','life-playback','life-cache-write','life-cache-reboot']
reports={n:json.loads(Path('outputs/Digitone-E10-PC-'+n+'.json').read_text(encoding='utf-8')) for n in names}
assert all(r['passed'] for r in reports.values())
copy=reports['life-copy-cache'];reset=reports['life-reset-refusal'];play=reports['life-playback'];boot=reports['life-cache-reboot']
assert copy['pattern_paste_and_undo_preserve_steps'] and copy['clear_and_undo_retain_steps'] and copy['all_128_retained_records_match_bank']
assert len(reset['cases'])==10 and all(r['balanced_return'] and not r['writes'] for r in reset['cases'])
assert play['matching_note_pairs']==23 and play['observed_DIN_notes']==play['observed_USB_notes']
assert reports['life-cache-write']['records_match']==128 and boot['restored_records_match']==128 and boot['unsaved_editor_cold_restore_verified'] and not boot['physical_power_loss_verified']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
c=json.loads(Path('work/os144/PC_ONLY-E10-life-layout.json').read_text())
assert sha('work/os144/PC_ONLY-E10-life-main.bin')==c['main_sha256'] and sha('work/os144/PC_ONLY-E10-life-payload.bin')==c['payload_sha256']
e09a=sha('outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx');assert e09a=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c'
sources=['build-PC-E10-lifecycle.py','integrate-PC-E10-lifecycle.py','test-PC-E10-lifecycle.py','test-PC-E10-life-startup.py','test-PC-E10-life-named-load.py','test-PC-E10-life-copy-cache.py','probe-PC-E10-copy-cache.py','test-PC-E10-life-playback.py','test-PC-E10-bound-reset-refusal.py','test-PC-E10-life-reset-refusal.py','test-PC-E10-life-cache-write.py','test-PC-E10-life-cache-reboot.py','verify-PC-E10-lifecycle.py']
for n in sources:py_compile.compile('work/'+n,doraise=True)
out=dict(PC_only=True,passed=True,checks={n:r['passed'] for n,r in reports.items()},native_clipboard_and_undo_checked=True,clear_preserves_steps_like_native_MIDI_settings=True,guarded_reset_cases=10,unsaved_retained_RAM_records=128,explicit_native_write_and_cold_restore_records=128,physical_power_loss_verified=False,automatic_power_fail_dispatch_verified=False,DIN_USB_matched_note_pairs=23,copied_payload_bytes=c['payload_bytes'],E09A_unchanged=True,E09A_sha256=e09a,firmware_container_created=False,hardware_ready=False,source_hash_normalization='UTF-8 with LF newlines',source_sha256={n:hashlib.sha256(Path('work/'+n).read_text(encoding='utf-8').encode('utf-8')).hexdigest() for n in sources},limits=c['limitations']+['Stopped native panel copy/paste/undo and trig clear/undo, not all clipboard or factory-reset families.','Reset tests invoke ten guarded entries with explicit admission fixtures and no concurrent input.','Unsaved recovery uses an explicitly invoked stock retained-bank writer; real automatic power-fail dispatch, energy reserve, incomplete writes and physical reboot remain untested.','Named reload and native panel clipboard are separate continuous workloads. Emulator snapshots omit EMAC mode, so the new load checkpoint avoids fractional-audio interrupt state.'])
Path('outputs/Digitone-E10-PC-lifecycle-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Scoped E10 lifecycle checks pass. Physical power loss remains unverified; E09A unchanged.')
