from pathlib import Path
import sys,json,struct
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from emu.harness import Machine,call
c=json.loads(Path('work/os144/E08-PC-M1-controls-layout.json').read_text());blob=Path('work/os144/E08-PC-M1-controls.bin').read_bytes();m=Machine(ddr=0x8000000);u=m.uc;P=0x47bc8000;E=P+0x400;VT=P+0x500;CLOSE=P+0x600;ST=P+0x7f00
for a in [c['base'],P,ST,0x40052400]:m.ensure(a)
u.mem_write(c['base'],blob)
for r in c['regions']:
 code=blob[r['base']-c['base']:r['base']-c['base']+r['bytes']];m.install_isa_patches_scoped(code,r['base'])
put=lambda a,v:u.mem_write(a,struct.pack('>I',v&0xffffffff))
get=lambda a:int.from_bytes(u.mem_read(a,4),'big')
put(P,VT);put(P+0x2c8,0x4d314352);put(VT+0x28,CLOSE)
u.mem_write(CLOSE,bytes.fromhex('203947bc8700528023c047bc87004e75'));m.ensure(P+0x700);put(P+0x700,0)
def invoke(name,args):
 r=next(r for r in c['regions'] if r['name']==name);return call(m,r['base'],args,stack_top=ST,limit=2000)
checks=[]
for name in ['M1_view_tick','refuse_synth_shortcut_0','refuse_synth_shortcut_1','refuse_synth_shortcut_2']:
 invoke(name,[P]);assert get(P+0x2c8)==0x4d314352
checks.append('tag survives native tick; synth arp copy/clear/paste callbacks bypassed')
for code in [14,20,21,22,23,24,25,42,43,44,45]:
 put(E+12,code);put(E+16,0x10);before=get(P+0x700);invoke('M1_controls_key',[P,E]);assert get(P+0x700)==before
 put(E+16,1);invoke('M1_controls_key',[P,E]);assert get(P+0x700)==before+1
checks.append('release events do not close; NO/page/track press invokes native close callback')
# Selection changes while a retained MIDI view still exists must not edit it.
u.mem_write(c['base'],bytes.fromhex('70054e75'));put(E+12,1);put(E+16,30);before=bytes(u.mem_read(P,0x2cc));invoke('M1_controls_turn',[P,E]);assert bytes(u.mem_read(P,0x2cc))==before
checks.append('late encoder callback after selection changes to M2 refuses mutation')
out={'PC_only':True,'passed':True,'checks':checks,'limits':['Isolated native page/closure fixtures; actual UI selection and destruction need continuous coverage.']}
Path('outputs/Digitone-E08-M1-view-guard-tests.json').write_text(json.dumps(out,indent=2));print('Native retained-view guards passed')
