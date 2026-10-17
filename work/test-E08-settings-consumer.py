from pathlib import Path
import sys,json,struct
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from emu.harness import Machine,call
native=json.loads(Path('work/os144/E08-PC-install-layout.json').read_text());c=json.loads(Path('work/os144/E08-PC-M1-controls-layout.json').read_text());m=Machine(ddr=0x8000000);u=m.uc;S=native['state'];SRC=0x47bc8000;KIT=SRC+0x100;STACK=SRC+0x7f00;TP=SRC+0x1000
for p in [native['base'],c['base'],SRC,STACK,TP,0x400f4000,0x80004614]:m.ensure(p)
payload=Path('work/os144/E08-PC-layout-payload.bin').read_bytes();u.mem_write(native['base'],payload)
for r in native['regions']:m.install_isa_patches_scoped(payload[r['base']-native['base']:r['base']-native['base']+r['bytes']],r['base'])
for name in ['M1-controls','settings-codec-bridge']:
 cc=json.loads(Path('work/os144/E08-PC-'+name+'-layout.json').read_text());b=Path('work/os144/E08-PC-'+name+'.bin').read_bytes();u.mem_write(cc['base'],b)
 for r in cc['regions']:m.install_isa_patches_scoped(b[r['base']-cc['base']:r['base']-cc['base']+r['bytes']],r['base'])
for addr in [0x400f40ba,0x400f4126]:u.mem_write(addr,bytes.fromhex('4e75'))
put=lambda a,v:u.mem_write(a,struct.pack('>I',v&0xffffffff));get=lambda a:int.from_bytes(u.mem_read(a,4),'big')
entry=next(r['base'] for r in c['regions'] if r['name']=='M1_settings_consumer')
def init():call(m,native['entries']['init'],[TP],stack_top=STACK,limit=30000);put(0x47be2840,0x4c495645)
def consume(kind,word=None):
 u.mem_write(SRC,bytes(52));put(SRC,kind)
 if word is not None:put(SRC+4,KIT);u.mem_write(KIT+0x66c,struct.pack('>H',word))
 u.reg_write(UC_M68K_REG_A2,SRC);u.reg_write(UC_M68K_REG_D6,2);call(m,entry,[],stack_top=STACK,limit=30000)
checks=[];init();consume(2,0xadd0);assert [get(S+x) for x in [4,304,308,320]]==[1,3,80,0]
assert get(S+32)==2700000 and get(S+36)==1080000;checks.append('native context descriptor reads M1 settings at KitActive +0x5ce +0x9e and applies mode/rate/gate')
consume(2,0);assert [get(S+x) for x in [4,304,308,320]]==[0,2,50,0];checks.append('legacy pattern context returns OFF / 1/16 / 50%')
put(S+324,0xacff);put(S+320,2);consume(3);assert [get(S+x) for x in [4,304,308,320]]==[0,2,50,0]
checks.append('invalid tagged UI request leaves configuration unchanged and clears pending flag')
put(S+324,0xace3);put(S+320,2);consume(3);assert [get(S+x) for x in [4,304,308,320]]==[1,1,99,0];checks.append('tagged panel request applies complete settings inside native masked consumer')
put(S+312,7);put(S+316,25);put(S+320,1);consume(3);assert [get(S+x) for x in [4,304,308,320]]==[1,7,25,0];checks.append('earlier index/percent PC request contract retained')
out={'PC_only':True,'passed':True,'checks':checks,'limits':['Native context records are isolated fixtures here; continuous project reload and handoff need separate observation.']};Path('outputs/Digitone-E08-settings-consumer-tests.json').write_text(json.dumps(out,indent=2));print('Native settings consumer checks passed')
