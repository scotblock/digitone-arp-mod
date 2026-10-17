from pathlib import Path
import sys,json,struct
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from emu.harness import Machine,call
c=json.loads(Path('work/os144/E08-PC-M1-controls-layout.json').read_text());n=json.loads(Path('work/os144/E08-PC-install-layout.json').read_text());m=Machine(ddr=0x8000000);u=m.uc;S=n['state'];ROOT=0x47bc8000;H=ROOT+0xff8;DATA=ROOT+0x2000;OTHER=DATA+0x400;SRC=ROOT+0x3000;ST=ROOT+0x7f00
main=Path('work/os144/E08-PC-layout-main.bin').read_bytes()
for p in range(0x40000000,0x40000400+len(main),0x100000):m.ensure(p)
u.mem_write(0x40000400,main);m.install_isa_patches_scoped(main,0x40000400)
for p in [ROOT,S,c['base'],0x419f0000,0x80004614]:m.ensure(p)
payload=Path('work/os144/E08-PC-layout-payload.bin').read_bytes();u.mem_write(n['base'],payload)
for r in n['regions']:m.install_isa_patches_scoped(payload[r['base']-n['base']:r['base']-n['base']+r['bytes']],r['base'])
for name in ['M1-controls','settings-codec-bridge']:
 cc=json.loads(Path('work/os144/E08-PC-'+name+'-layout.json').read_text());b=Path('work/os144/E08-PC-'+name+'.bin').read_bytes();u.mem_write(cc['base'],b)
 for r in cc['regions']:m.install_isa_patches_scoped(b[r['base']-cc['base']:r['base']-cc['base']+r['bytes']],r['base'])
hook=next(h for h in c['hooks'] if h['site']==0x4014a056);u.mem_write(hook['site'],bytes.fromhex(hook['replacement']))
for p in [0x400f40ba,0x400f4126]:u.mem_write(p,bytes.fromhex('4e75'))
put=lambda a,v:u.mem_write(a,struct.pack('>I',v&0xffffffff));get=lambda a:int.from_bytes(u.mem_read(a,4),'big')
def invoke(addr,args=[]):return call(m,addr,args,stack_top=ST,limit=30000)
invoke(n['entries']['init'],[SRC+0x100]);put(0x47be2840,0x4c495645);put(0x419f0de0,ROOT);put(H,0x40193b90);put(H+16,DATA)
def observe():assert invoke(0x40149fba)==ROOT
def consume():
 u.mem_write(SRC,bytes(52));put(SRC,3);u.reg_write(UC_M68K_REG_A2,SRC);u.reg_write(UC_M68K_REG_D6,2);invoke(next(r['base'] for r in c['regions'] if r['name']=='M1_settings_consumer'))
checks=[];observe();assert get(S+320)==2;consume();assert [get(S+x) for x in [4,304,308,320]]==[0,2,50,0]
observe();assert get(S+320)==0;checks.append('initialized native UI root getter publishes defaults once and retains its return value')
u.mem_write(DATA+158,bytes.fromhex('add0'));observe();consume();assert [get(S+x) for x in [4,304,308,320]]==[1,3,80,0]
checks.append('a restored settings word publishes and reaches the native consumer without a panel edit')
put(H+16,OTHER);observe();consume();assert [get(S+x) for x in [4,304,308,320]]==[0,2,50,0]
put(H+16,DATA);observe();consume();assert [get(S+x) for x in [4,304,308,320]]==[1,3,80,0]
checks.append('data rebinding to legacy and saved pattern records applies their separate settings')
put(H,0);put(S+320,0);observe();assert get(S+320)==0;put(H,0x40193b90);put(H+16,0);observe();assert get(S+320)==0
put(H+16,DATA);put(0x47be2840,0x434f4c44);u.mem_write(DATA+158,bytes.fromhex('a932'));observe();assert get(S+320)==0
checks.append('wrong class, null data and COLD admission refuse synchronization')
out={'PC_only':True,'passed':True,'checks':checks,'limits':['The native getter and consumer execute with isolated initialized-root/data fixtures. Continuous save/reload remains a separate test.']}
Path('outputs/Digitone-E08-current-settings-binding-tests.json').write_text(json.dumps(out,indent=2));print('Native current-M1 binding checks passed')
