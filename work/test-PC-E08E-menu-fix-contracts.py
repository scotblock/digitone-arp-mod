"""All track/button/modifier routes; actual helpers with selector return fixture."""
from pathlib import Path
import json,sys,struct
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine
from emu import cfisa
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import *
cfg=json.loads(Path('work/os144/PC_ONLY-E08E-menu-fix-layout.json').read_text())
stock=Path('work/os144/section-3.bin').read_bytes()
rows=[];marker=[];isa=[]
for r in cfg['regions']:
    code=bytes.fromhex(r['after'])[:r['bytes']];off=0
    while off<len(code):
        ins=cfisa.decode(lambda x:int.from_bytes(code[off+x:off+x+2],'big'),r['base']+off)
        assert ins.length>0 and not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF)
        off+=ins.length
    isa.append({'name':r['name'],'checked_bytes':off})
for track in range(8):
 for key in range(20,26):
  for modifier in [0,1]:
   for what in ['M1_SYN2_open','mark_M1_view']:
    m=Machine(ddr=0x8000000);u=m.uc;stack=0x47bcf000;view=0x47bd0000
    r=next(r for r in cfg['regions'] if r['name']==what);code=bytes.fromhex(r['after'])[:r['bytes']]
    for p in [0x4003f000,stack,view,r['base'],cfg['selected_track']]:m.ensure(p)
    u.mem_write(0x4003f000,stock[0x4003f000-0x40000400:0x40040000-0x40000400])
    u.mem_write(r['base'],code);m.install_isa_patches_scoped(code,r['base'])
    u.mem_write(cfg['selected_track'],bytes([0x70,track,0x4e,0x75]))
    u.mem_write(view+0x2c8,struct.pack('>I',1234))
    u.reg_write(UC_M68K_REG_SR,0x2300|(4 if not modifier else 0))
    u.reg_write(UC_M68K_REG_A7,stack+0x800);u.reg_write(UC_M68K_REG_A4,key)
    u.reg_write(UC_M68K_REG_A2,view);u.reg_write(UC_M68K_REG_A6,view+0x100)
    # Nonzero high bytes ensure the modifier test is genuinely byte-sized.
    u.reg_write(UC_M68K_REG_D3,0xaabbcc00|modifier);u.reg_write(UC_M68K_REG_D2,view)
    stops=[]
    def stop(u,pc,n,d):
        if pc in [0x4003fb94,0x4003fb9c,0x4003fc42,0x4003fc60]:stops.append(pc);u.emu_stop()
    u.hook_add(UC_HOOK_CODE,stop);u.emu_start(r['base'],0,count=1000)
    special=track==4 and key==22 and modifier==1
    assert len(stops)==1
    sp=u.reg_read(UC_M68K_REG_A7)
    if what=='M1_SYN2_open':
        expected=0x4003fc42 if special else 0x4003fb9c if modifier else 0x4003fb94
        assert stops[0]==expected,(track,key,modifier,stops)
        page=int.from_bytes(u.mem_read(sp+4,4),'big') if not modifier else None
        if not modifier:assert page==key-20
        assert sp==stack+0x800-(12 if not modifier else 0)
        rows.append({'track':track,'key':key,'modifier':modifier,'custom':special,'page':page})
    else:
        assert stops[0]==0x4003fc60 and sp==stack+0x7fc
        assert u.reg_read(UC_M68K_REG_D2)==view+0xf0
        tagged=int.from_bytes(u.mem_read(view+0x2c8,4),'big')==0x4d314352
        assert tagged==special,(track,key,modifier,tagged)
        marker.append({'track':track,'key':key,'modifier':modifier,'custom':tagged})
    assert u.reg_read(UC_M68K_REG_A4)==key
    assert u.reg_read(UC_M68K_REG_D3)==0xaabbcc00|modifier
    assert u.reg_read(UC_M68K_REG_SR)&0x2700==0x2300
out={'PC_only':True,'passed':True,'firmware_container_created':False,'routing_cases':len(rows),'marker_cases':len(marker),
 'selector_return_is_fixture':True,'ISA':isa,'routes':rows,'markers':marker,
 'limits':['Isolated helpers with selected-track return fixture; native full-panel execution is separate.']}
Path('outputs/Digitone-E08E-PC-menu-fix-contracts.json').write_text(json.dumps(out,indent=2))
print('Passed',len(rows),'routing and',len(marker),'marker cases; stock pages 0–5 preserved; one M1 modifier route custom.')
