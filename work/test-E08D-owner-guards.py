from pathlib import Path
import json,struct
audit={};exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0],audit)
cfisa=audit['cfisa'];move_restriction=audit['move_restriction']
from emu.harness import Machine,call
from unicorn.m68k_const import UC_M68K_REG_A2,UC_M68K_REG_D6
n=json.loads(Path('work/os144/E08C-PC-install-layout.json').read_text())
c=json.loads(Path('work/os144/E08D-PC-M1-controls-layout.json').read_text())
payload=Path('work/os144/E08C-PC-layout-payload.bin').read_bytes()
blob=Path('work/os144/E08D-PC-M1-controls.bin').read_bytes()
m=Machine(ddr=0x8000000);u=m.uc;S=n['state'];TP=0x47bc8000;A=TP+0x1000;B=A+0x400;E=A+0x800;ROOT=TP+0x3000;ST=TP+0x7f00
main=Path('work/os144/E08C-PC-layout-main.bin').read_bytes()
for p in range(0x40000000,0x40000400+len(main),0x100000):m.ensure(p)
for p in [TP,n['base'],0x419f0de0,0x80004614]:m.ensure(p)
u.mem_write(0x40000400,main);m.install_isa_patches_scoped(main,0x40000400)
u.mem_write(n['base'],payload)
for r in n['regions']:
    m.install_isa_patches_scoped(payload[r['base']-n['base']:r['base']-n['base']+r['bytes']],r['base'])
for r in c['regions']:
    code=blob[r['base']-c['base']:r['base']-c['base']+r['bytes']];off=0
    while off<len(code):
        ins=cfisa.decode(lambda x:int.from_bytes(code[off+x:off+x+2],'big'),r['base']+off)
        assert ins.length>0 and off+ins.length<=len(code) and not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(code[off:off+2],'big')),(r,off,ins)
        off+=ins.length
    u.mem_write(r['base'],code);m.install_isa_patches_scoped(code,r['base'])
ordered=sorted(c['regions'],key=lambda r:r['base'])
assert all(a['base']+a['bytes']<=b['base'] for a,b in zip(ordered,ordered[1:]))
init=n['entries']['init'];r=next(r for r in n['regions'] if r['base']==init)
code=payload[init-n['base']:init-n['base']+r['bytes']]
assert code.count(bytes.fromhex('7254'))==1
u.mem_write(init,code.replace(bytes.fromhex('7254'),bytes.fromhex('7256')))
for p in [0x400f40ba,0x400f4126]:u.mem_write(p,bytes.fromhex('4e75'))
put=lambda a,v:u.mem_write(a,struct.pack('>I',v&0xffffffff))
get=lambda a:int.from_bytes(u.mem_read(a,4),'big')
invoke=lambda p,args=[]:call(m,p,[v&0xffffffff for v in args],stack_top=ST,limit=50000)
entry=next(r['base'] for r in c['regions'] if r['name']=='M1_settings_consumer')
PUB=c['entries']['publish'];SELECT=c['entries']['select_owner'];SRC=c['entries']['source_owner']
def config():return [get(S+x) for x in [4,304,308,320]]
def consume(kind,ptr=None):
    if ptr is None:u.mem_write(E,bytes(52));put(E,kind)
    u.reg_write(UC_M68K_REG_A2,E);u.reg_write(UC_M68K_REG_D6,2);invoke(entry)
def context(data):
    u.mem_write(E,bytes(52));put(E,2);put(E+4,data-0x5ce if data else 0);consume(2,E)
def note(data,track=0,count=1,onoff=1,mode=2,note_value=60,gate=0):
    u.mem_write(E,bytes(52))
    for off,value in [(0,0),(4,track),(8,onoff),(12,1),(16,count),(28,gate),(40,data),(44,mode)]:put(E+off,value)
    u.mem_write(E+20,bytes([note_value])*min(8,max(0,count)))
checks=[]
u.mem_write(S,b'\xa7'*(344+8));invoke(init,[TP]);assert bytes(u.mem_read(S+336,8))==bytes(8)
assert bytes(u.mem_read(S+344,8))==b'\xa7'*8 and bytes(u.mem_read(n['arena'],64))==bytes(64)
put(0x47be2840,0x4c495645);put(TP,0);u.mem_write(A+158,bytes.fromhex('add0'));u.mem_write(B+158,bytes.fromhex('ac94'))
put(0x419f0de0,ROOT);put(ROOT+0xff8,0x40193b90);put(ROOT+0xff8+16,B)
checks.append('Native initializer clears both added owner fields and preserves the remaining arena alignment gap.')
context(A);assert get(S+336)==A and config()==[1,3,80,0]
put(TP,1);put(S+8,1);put(S+12,1);put(S+16,3);put(S+24,0x100000)
before=bytes(u.mem_read(S,344));assert invoke(PUB,[B,0xac94,0])==0 and bytes(u.mem_read(S,344))==before
assert invoke(PUB,[B,0xac94,1])==0 and bytes(u.mem_read(S,344))==before
checks.append('While A owns playback, automatic B binding and B panel publication are refused without touching M1 state.')
put(ROOT+0xff8+16,A);u.mem_write(A+158,bytes.fromhex('ada0'))
assert invoke(PUB,[A,0xada0,1])==1;consume(3);assert config()==[1,3,32,0] and get(S+336)==A
checks.append('A panel edit to the consumed owner applies during playback through a complete owner-tagged request.')
u.mem_write(A+158,bytes.fromhex('adbf'));assert invoke(PUB,[A,0xadbf,1])==1;context(B);assert get(S+336)==B and config()==[1,1,20,0]
put(S+324,0xadd0);put(S+340,A);put(S+320,2);consume(3);assert config()==[1,1,20,0]
checks.append('A context replacement supersedes an old pending edit; a stale owner request is rejected at consumption.')
for kwargs in [dict(track=1),dict(count=0),dict(onoff=2),dict(mode=7),dict(note_value=128)]:
    note(A,**kwargs);assert invoke(SRC,[E])==0
    owner=get(S+336);consume(0,E);assert get(S+336)==owner
checks.append('Other tracks, empty/invalid notes, releases and invalid source modes do not take ownership.')
u.mem_write(A+158,bytes.fromhex('add0'));note(A);assert invoke(SRC,[E])==A;consume(0,E);assert get(S+336)==A and config()==[1,3,80,0]
put(0x419c5b14,A);put(0x419c5b10,B-0x5ce);note(0,mode=1,gate=1000)
assert invoke(SRC,[E])==A
put(0x419c5b14,0);assert invoke(SRC,[E])==B
note(A);assert invoke(SRC,[E])==A
checks.append('Eligible sources follow stock precedence: explicit parameters, cached track parameters, then the consumed KitActive record.')
put(S+280,1);context(0);assert get(S+336)==get(S+340)==0 and get(S+4)==get(S+8)==get(S+16)==0 and get(S+280)==1
checks.append('A null context revokes owner/requests and held generation without prematurely freeing an outstanding arena descriptor.')
put(S+280,0);put(TP,0);put(ROOT+0xff8+16,B);assert invoke(PUB,[B,0xac94,0])==1;consume(3);assert get(S+336)==B and config()==[1,1,20,0]
checks.append('A quiescent stopped binding adopts the selected bank and still applies its saved settings.')
put(S+312,7);put(S+316,99);put(S+320,1);consume(3);assert config()==[1,1,20,0]
checks.append('The old unowned PC-only request flag cannot bypass the owner guard.')
put(0x47be2840,0x434f4c44);before=bytes(u.mem_read(S,344))
assert invoke(PUB,[A,0xadd0,1])==0 and invoke(SELECT,[A])==0
context(A);assert bytes(u.mem_read(S,344))==before
checks.append('COLD admission refuses publishing, owner capture and consumer mutation.')
put(0x47be2840,0x4c495645)
for args in [[0,0xadd0,1],[A,0xffff,1],[A,0xadd0,2],[0xdeadbeef,0xadd0,0]]:
    before=bytes(u.mem_read(S,344));assert invoke(PUB,args)==0 and bytes(u.mem_read(S,344))==before
checks.append('Malformed data identity, tag and origin fail before metadata mutation.')
before=bytes(u.mem_read(S,344));assert invoke(PUB,[B,0xadd0,1])==0 and bytes(u.mem_read(S,344))==before
put(ROOT+0xff8+16,A);assert invoke(PUB,[B,0xac94,1])==0 and bytes(u.mem_read(S,344))==before
checks.append('An out-of-date value or a changed UI binding is rejected inside publication, closing a stale-read/admission gap.')
out={'PC_only':True,'passed':True,'strict_ColdFire_checked':True,'checks':checks,'state_bytes':344,'new_state_bytes':8,
     'limits':['Isolated native frames and explicit state/descriptor fixtures, not continuous UI or hardware evidence.']}
Path('outputs/Digitone-E08D-owner-guard-contracts.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
