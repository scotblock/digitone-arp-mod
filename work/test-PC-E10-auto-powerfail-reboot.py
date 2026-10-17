"""Cold native restore of records edited without Save Project."""
from pathlib import Path
import json,sys,zlib
sys.path.insert(0,'work')
proof=json.loads(Path('outputs/Digitone-E10-PC-auto-powerfail.json').read_text());assert proof['passed']
expected_bank=bytes.fromhex(proof['expected_bank'])
source=Path('work/test-PC-E10-integrated-startup.py').read_text(encoding='utf-8')
for old,new in [('PC_ONLY-E10-startup','PC_ONLY-E10-life'),('Digitone-E10-PC-integrated-startup.json','Digitone-E10-PC-auto-powerfail-reboot.json')]:source=source.replace(old,new)
before="assert bytes(m.uc.mem_read(cfg['E10']['bank'],4096))==bytes(4096)";after="assert bytes(m.uc.mem_read(cfg['E10']['bank'],4096))==expected_bank"
assert before in source;source=source.replace(before,after)
anchor="exec(compile(source,'E10-direct-MAIN-native-startup','exec'))"
extra="source=source.replace('work/os144/PC_ONLY-saved-mirror-valid_first.img',"+repr(Path(proof['card']).as_posix())+").replace('work/E10-startup-','work/E10-auto-powerfail-reboot-').replace('generated-E10-startup.py','generated-E10-auto-powerfail-reboot.py')\n"
assert anchor in source;source=source.replace(anchor,extra+anchor)
exec(compile(source,'E10-unsaved-cache-cold-restore','exec'))
from emu.snapshot import _load_blob
from emu.harness import PAGE
p=Path('outputs/Digitone-E10-PC-auto-powerfail-reboot.json');r=json.loads(p.read_text());assert r['passed']
b=_load_blob(r['cases'][0]['ui_snapshot']);pages={a:zlib.decompress(v) for a,v in b['pages'].items()};c=json.loads(Path('work/os144/PC_ONLY-E10-life-layout.json').read_text())
def peek(a,n):return bytes(pages.get((a+i)&~(PAGE-1),bytes(PAGE))[(a+i)&(PAGE-1)] for i in range(n))
assert peek(c['E10']['bank'],4096)==expected_bank
assert int.from_bytes(peek(c['lifecycle']['meta'],4),'big')==0x4d434831
r.update(native_project_persistence=True,automatic_pattern_binding=True,unsaved_editor_cold_restore_verified=True,restored_records_match=128,no_manual_project_save=True,preceding_writer_explicitly_invoked=False,preceding_writer_interrupt_dispatched=True,physical_power_loss_verified=False)
r['limits'].append('Unsaved panel edits survive the modeled pin/interrupt-dispatched stock shutdown writer and fresh PC cold restore. Physical power decay, energy reserve, timing and persistence are not established.')
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
print('Interrupt-dispatched shutdown records restored after cold PC boot; physical power loss remains unverified.')
