"""Verify the scoped editor/bank/recall evidence without building firmware."""
from pathlib import Path
import json,hashlib,py_compile
reports={name:json.loads(Path('outputs/'+name+'.json').read_text(encoding='utf-8')) for name in ['Digitone-E10-PC-pattern-binding-contracts','Digitone-E10-PC-bound-startup','Digitone-E10-PC-bound-panel-patterns','Digitone-E10-PC-bound-playback','Digitone-E10-PC-bound-running-handoff']}
assert all(r['passed'] for r in reports.values())
p=reports['Digitone-E10-PC-bound-panel-patterns'];play=reports['Digitone-E10-PC-bound-playback'];run=reports['Digitone-E10-PC-bound-running-handoff']
assert p['two_pattern_panel_recall'] and p['saved_project_reloaded'] and p['post_reload_pattern_recall'] and not p['bank_host_written']
assert play['matching_note_pairs']==23 and play['observed_DIN_notes']==play['observed_USB_notes']
assert run['confirmed_held_handoff'] and run['bank_preserved']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
e09a=sha('outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx')
assert e09a=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c'
c=json.loads(Path('work/os144/PC_ONLY-E10-bound-layout.json').read_text())
assert sha('work/os144/PC_ONLY-E10-bound-main.bin')==c['main_sha256']
assert sha('work/os144/PC_ONLY-E10-bound-payload.bin')==c['payload_sha256']
sources=['build-PC-E10-pattern-binding.py','integrate-PC-E10-pattern-binding.py','test-PC-E10-pattern-binding.py','test-PC-E10-bound-startup.py','test-PC-E10-bound-panel-patterns.py','test-PC-E10-bound-playback.py','test-PC-E10-bound-running-handoff.py']
for name in sources:py_compile.compile(str(Path('work')/name),doraise=True)
out=dict(PC_only=True,passed=True,editor_changes_saved_to_bank=True,exact_pattern_slot_count=128,two_panel_created_patterns_saved_and_recalled=True,project_replacement_generation_checked=True,confirmed_running_held_handoff=True,DIN_USB_matched_note_pairs=23,copied_payload_bytes=c['payload_bytes'],E09A_unchanged=True,E09A_sha256=e09a,firmware_container_created=False,hardware_ready=False,checks={n:r['passed'] for n,r in reports.items()},source_hash_normalization='UTF-8 with LF newlines',source_sha256={n:hashlib.sha256((Path('work')/n).read_text(encoding='utf-8').encode('utf-8')).hexdigest() for n in sources},limits=['Native save/load test resumed its own checkpoint at the load confirmation after a test-button error; no bank, settings, hook or executable bytes were inserted.','One held-chord handoff, not exhaustive transition/reset coverage. Outstanding arena refusal retries only on a subsequent eligible owner-selection call; no periodic retry hook is claimed.','Step settings are in the RAM bank and emitted by full project serialization. Incremental mirror updates and unsaved power-loss recovery remain unverified.','Copy/clear/undo, asynchronous project replacement, physical RAM ownership/cache/timing and E10 packaged loader continuity remain uncertified.'])
Path('outputs/Digitone-E10-PC-pattern-binding-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Editor/bank/recall: five native PC scenarios pass; E09A unchanged; no E10 container.')
