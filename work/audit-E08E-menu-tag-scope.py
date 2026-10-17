"""Read-only package audit and isolated page-marker execution. No new firmware."""
from pathlib import Path
import json,sys,hashlib,struct
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine
from unicorn.m68k_const import UC_M68K_REG_D2,UC_M68K_REG_A4,UC_M68K_REG_A6,UC_M68K_REG_A7,UC_M68K_REG_SR
cfg=json.loads(Path('work/os144/E08E-PC-install-layout.json').read_text())
payload=Path('work/os144/E08E-PC-layout-payload.bin').read_bytes()
r=next(r for r in cfg['regions'] if r['name']=='mark_M1_view')
code=payload[r['base']-cfg['base']:r['base']-cfg['base']+r['bytes']]
syx=Path('outputs/Digitone_OS1.44E08E_M1_ARP_PC_ONLY.syx')
assert hashlib.sha256(syx.read_bytes()).hexdigest()=='74219ea223999ae190f5c935973b96bf67eea60148416a1009565af6f48dd3a3'
results=[]
for key in [0x15,0x16]:
    m=Machine(ddr=0x8000000);u=m.uc
    view,stack=0x47bd0000,0x47bcf000
    for p in [r['base'],view,stack,0x4003f000]:m.ensure(p)
    u.mem_write(r['base'],code);m.install_isa_patches_scoped(code,r['base'])
    u.mem_write(view+0x2c8,struct.pack('>I',1234))
    u.reg_write(UC_M68K_REG_SR,0x2000);u.reg_write(UC_M68K_REG_A7,stack+0x800)
    u.reg_write(UC_M68K_REG_D2,view);u.reg_write(UC_M68K_REG_A4,key);u.reg_write(UC_M68K_REG_A6,view+0x100)
    u.emu_start(r['base'],0x4003fc60,count=1000)
    tag=int.from_bytes(u.mem_read(view+0x2c8,4),'big')
    results.append({'saved_A4_key':hex(key),'page_field_after':hex(tag),'M1_tagged':tag==0x4d314352})
assert [x['M1_tagged'] for x in results]==[False,True]
sel=next(r for r in cfg['regions'] if r['name']=='selected_track')['base']
assert b'\x4e\xb9'+struct.pack('>I',sel) not in code
report={'PC_only':True,'firmware_unchanged':True,'actual_packaged_marker':r,'marker_bytes':code.hex(),
 'selected_track_accessor_called':False,'isolated_key_controls':results,
 'finding':'Marker writes M1CR for matching key without selected-track predicate. This is a scope defect candidate; no claim that it explains reported effects pages without exact reproduction.',
 'limits':['Isolated helper execution with crafted native register inputs, not a complete physical menu transition.','Reported effects controls on MIDI channels have not yet been reproduced or classified against stock.']}
Path('outputs/Digitone-E08E-menu-tag-scope-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
