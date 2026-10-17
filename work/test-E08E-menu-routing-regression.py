"""Execute stock/packaged/fixed page forwarding in isolated PC controls."""
from pathlib import Path
import sys,json,struct
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine
from unicorn.m68k_const import UC_M68K_REG_A2,UC_M68K_REG_A4,UC_M68K_REG_A7,UC_M68K_REG_D3,UC_M68K_REG_SR
cfg=json.loads(Path('work/os144/E08E-PC-install-layout.json').read_text())
payload=Path('work/os144/E08E-PC-layout-payload.bin').read_bytes()
stock=Path('work/os144/section-3.bin').read_bytes()
r=next(r for r in cfg['regions'] if r['name']=='M1_SYN2_open')
raw=payload[r['base']-cfg['base']:r['base']-cfg['base']+r['bytes']]
assert raw.count(bytes.fromhex('42a7486cfff2'))==1
fixed=raw.replace(bytes.fromhex('42a7486cfff2'),bytes.fromhex('42a7486cffec'))
rows=[]
for label,entry,code in [('stock',0x4003fb8a,None),('E08E',r['base'],raw),('PC_only_corrected_displacement',r['base'],fixed)]:
    for key in [20,21,23,24,25]:
        m=Machine(ddr=0x8000000);u=m.uc;stack=0x47bcf000
        for addr in [0x4003f000,stack,r['base']]:m.ensure(addr)
        u.mem_write(0x4003f000,stock[0x4003f000-0x40000400:0x40040000-0x40000400])
        if code:
            u.mem_write(entry,code);m.install_isa_patches_scoped(code,entry)
        u.reg_write(UC_M68K_REG_SR,0x2004)
        u.reg_write(UC_M68K_REG_A7,stack+0x800);u.reg_write(UC_M68K_REG_A4,key)
        u.reg_write(UC_M68K_REG_A2,0x47bd0000);u.reg_write(UC_M68K_REG_D3,0)
        try:u.emu_start(entry,0x4003fb94,count=1000)
        except Exception:
            from unicorn.m68k_const import UC_M68K_REG_PC
            print(label,key,'failure at',hex(u.reg_read(UC_M68K_REG_PC)),flush=True)
            raise
        sp=u.reg_read(UC_M68K_REG_A7)
        value=int.from_bytes(u.mem_read(sp+4,4),'big')
        expected=key-20
        assert value==expected+(6 if label=='E08E' else 0),(label,key,value)
        rows.append({'control':label,'key':key,'stock_page_index':expected,'forwarded_page_index':value})
Path('work/os144/PC_ONLY-E08E-menu-open-displacement-fix.bin').write_bytes(fixed)
out={'PC_only':True,'firmware_unchanged':True,'passed':True,'rows':rows,
 'cause':'Displaced stock PEA d16(A4) was replayed with FFF2 (-14), rather than FFEC (-20); unmodified forwarding selects page index +6.',
 'correction_tested':'Change the replay displacement to stock FFEC in an isolated helper only.',
 'remaining':['SYN2 special-case modifier handling','M1-only page marker guard','Full native stock-versus-corrected UI routing and physical tests']}
Path('outputs/Digitone-E08E-menu-routing-regression.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
