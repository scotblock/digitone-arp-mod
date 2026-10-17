"""Explicit stock retained-bank write from an unsaved native editor state."""
from pathlib import Path
import json
source=Path('work/test-PC-E10-persistence-explicit-cache-flush.py').read_text(encoding='utf-8')
source=source.replace('outputs/Digitone-E10-PC-persistence-native-save-load.json','outputs/Digitone-E10-PC-life-copy-cache.json')
source=source.replace("assert proof['passed'] and proof['native_retained_mirror_records_match']==128","assert proof['passed'] and proof['unsaved_editor_mirror_synchronized']\nexpected_bank=bytes.fromhex(proof['expected_bank'])")
source=source.replace('work/E10-persistence-explicit-cache-flush','work/E10-life-cache-write').replace('work/E10-persistence-save-load','work/E10-life-copy-cache')
source=source.replace("proof['post_save_snapshot']","proof['unsaved_snapshot']").replace('f.read(32)==record_bytes(i)',"f.read(32)==expected_bank[32*i:32*i+32]")
source=source.replace('outputs/Digitone-E10-PC-persistence-explicit-cache-flush.json','outputs/Digitone-E10-PC-life-cache-write.json')
anchor="s=Session(proof['unsaved_snapshot'],syx=str(syx),ddr=0x8000000,audio=True)"
replacement="""
layout=json.loads(Path('work/os144/PC_ONLY-E10-life-layout.json').read_text())
payload=Path('work/os144/PC_ONLY-E10-life-payload.bin').read_bytes()
def verify_code(session):
 for r in layout['regions']:
  if r['base']<layout['base']:continue
  offset=r['base']-layout['base'];code=payload[offset:offset+r['bytes']]
  assert bytes(session.m.uc.mem_read(r['base'],r['bytes']))==code,r['name']
  session.m.install_isa_patches_scoped(code,r['base'])
 out['copied_code_verified']=True
s=Session(proof['unsaved_snapshot'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=verify_code)
"""
assert anchor in source;source=source.replace(anchor,replacement)
exec(compile(source,'E10-unsaved-native-cache-write','exec'))
p=Path('outputs/Digitone-E10-PC-life-cache-write.json');r=json.loads(p.read_text());assert r['passed']
r.update(unsaved_editor_records_written=True,expected_bank=expected_bank.hex(),no_manual_project_save=True)
r['limits']=['Explicit native stock writer call, not an emulated physical power-fail interrupt. Source is the native editor/copy session without Save Project.','No record, cache, bank-selection or controller result bytes are inserted by the harness. Physical persistence/timing remain unverified.']
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
