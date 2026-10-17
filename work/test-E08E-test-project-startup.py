"""Restore generated project through native startup, in an isolated PC card."""
from pathlib import Path
import json,sys
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import sparse
source=Path('work/os144/PC_ONLY-saved-mirror-valid_first.img')
card=Path('work/os144/PC_ONLY-E08E-test-project.img')
with source.open('rb') as src,card.open('wb') as dst:
    sparse.make_sparse(dst);sparse.extend(dst,source.stat().st_size)
    while chunk:=src.read(1024*1024):
        if chunk.strip(b'\0'):dst.seek(src.tell()-len(chunk));dst.write(chunk)
    dst.seek(0xf400110);dst.write(Path('work/os144/E08E-test-project-image.bin').read_bytes())
exec(compile(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0],'ISA-definitions','exec'))
cfg=json.loads(Path('outputs/Digitone-E08E-PC-path-layout.json').read_text())
s=Path('work/generated-E08E-startup.py').read_text()
s=s.replace('work/os144/PC_ONLY-saved-mirror-valid_first.img',str(card).replace('\\','/'))
s=s.replace("work/E08E-startup-","work/E08E-test-project-startup-")
s=s.replace('outputs/Digitone-E08E-PC-startup-comparison.json','outputs/Digitone-E08E-test-project-startup.json')
s=s.replace('machine_out=box)',"machine_out=box,handoff='work/os144/E08E-PC-loader-handoff.bin')")
s=s.replace("  sp=m.uc.reg_read(UC_M68K_REG_A7);m.uc.mem_write(sp+4,struct.pack('>I',0x00140000))", "  row['loader_handoff']='work/os144/E08E-PC-loader-handoff.bin'\n  assert bytes(m.uc.mem_read(0x40000400,len(image)))==image")
print('Starting native restoration of isolated generated test project',flush=True)
exec(compile(s,'generated-project-native-startup','exec'))
