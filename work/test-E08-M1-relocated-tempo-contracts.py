from pathlib import Path
import sys,json,struct,hashlib
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from emu.harness import Machine,call
c=json.loads(Path('work/os144/E08-PC-install-layout.json').read_text());blob=Path('work/os144/E08-PC-layout-payload.bin').read_bytes();m=Machine(ddr=0x08000000);u=m.uc;S=c['state'];A=c['arena'];SRC=0x47bc8000;STACK=0x47bcff00;TP=0x47bc8100;checks=[]
for a in [c['base'],S,A,SRC,STACK,TP,0x80004614,0x400f4000,0x47be2840]:m.ensure(a)

for address in range(c['base'],c['base']+len(blob),0x1000):m.ensure(address)
u.mem_write(c['base'],blob)
for r in c['regions']:
 code=blob[r['base']-c['base']:r['base']-c['base']+r['bytes']];p=0
 while p<len(code):
  i=cfisa.decode(lambda off:int.from_bytes(code[p+off:p+off+2],'big'),r['base']+p);assert i.length>0 and p+i.length<=len(code) and not i.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(code[p:p+2],'big')),(r['name'],hex(r['base']+p),i,code[p:p+12].hex());p+=i.length
 m.install_isa_patches_scoped(code,r['base'])
put=lambda a,v:u.mem_write(a,struct.pack('>I',v&0xffffffff))
get=lambda a:int.from_bytes(u.mem_read(a,4),'big')
def invoke(entry,args=[]):return call(m,entry,args,stack_top=STACK,limit=30000)
def init():
 invoke(c['entries']['init'],[TP]);assert get(S)==0x4d314131 and get(S+8)==0 and get(S+280)==0;put(S+4,1);put(TP,1);put(0x47be2840,0x4c495645);u.mem_write(S-8,b'BEFORE!!');u.mem_write(S+c['state_bytes'],b'AFTER!!!');u.mem_write(A+64,b'ARENAEND')
def src(notes=[60,64,67],kind=1,mode=1,on=True,gate=21600000,now=100000000):
 raw=bytearray(52);struct.pack_into('>5I',raw,0,kind,0,1 if on else 2,0x30401 if mode==1 else 0x30601,len(notes));raw[20:20+len(notes)]=bytes(notes);struct.pack_into('>I',raw,28,gate);raw[35]=100;struct.pack_into('>I',raw,36,now);struct.pack_into('>I',raw,40,0x47bb0000);struct.pack_into('>I',raw,44,mode);struct.pack_into('>I',raw,48,0);u.mem_write(SRC,bytes(raw));put(0x80004614,now);return raw
def dispatch():return invoke(c['entries']['dispatch'],[SRC])
def timer(now):u.mem_write(SRC,bytes(52));put(SRC,3);put(0x80004614,now);return dispatch()
def retire():
 u.reg_write(UC_M68K_REG_A2,A);u.reg_write(UC_M68K_REG_A7,STACK);u.emu_start(c['entries']['retire'],0x400f49cc,count=200);assert get(S+280)==0 and u.reg_read(UC_M68K_REG_D2)==get(A+48)
init();checks.append('native initialization + valid configs')
init();raw=src();put(S+4,0);assert dispatch()==SRC and bytes(u.mem_read(SRC,52))==raw;checks.append('OFF preserves source descriptor')
init();src([67,60,64,60]);assert dispatch()==A;assert get(S+16)==3 and [get(S+64+i*4) for i in range(3)]==[60,64,67];assert get(SRC+16)==0 and get(A+40)==0 and get(S+264)==0 and get(A+48)==SRC;assert u.mem_read(A+20,1)==b'\x3c';retire();notes=[60]
for n in range(1,8):
 assert timer(100000000+n*5400000)==A;notes.append(u.mem_read(A+20,1)[0]);retire()
assert notes==[60,64,67,60,64,67,60,64];assert timer(143200000)==SRC and get(S+8)==0;checks.append('native sorting/dedup, snapshot and finite-source ascending playback')
init();src();dispatch();original=bytes(u.mem_read(A,64));put(SRC,3);put(0x80004614,105400000);assert dispatch()==SRC and bytes(u.mem_read(A,64))==original;retire();checks.append('owned descriptor busy preflight prevents overwrite')
init();src();dispatch();retire();put(TP,2);assert timer(101000000)==SRC and get(S+8)==0 and get(S+56)==1;checks.append('native transport stop cancellation')
init();put(TP,2)
for note in [67,60,64]:src([note],kind=0,mode=2,gate=0);assert dispatch()==SRC
assert get(S+12)==1 and get(S+8)==1 and get(S+16)==3
assert timer(100000001)==A and u.mem_read(A+20,1)==b'\x3c' and get(A+28)==1350000;retire()
for note in [60,64,67]:src([note],kind=0,mode=2,on=False,gate=0,now=101000000);assert dispatch()==SRC
assert get(S+8)==0 and get(S+16)==0 and get(S+60)==1 and timer(120000000)==SRC;checks.append('live zero-gate input, actual release descriptors and no restart')
for off,val in [(32,0),(36,0),(32,0x40000000),(36,5400000)]:
 init();raw=src();put(S+off,val);assert dispatch()==SRC and bytes(u.mem_read(SRC,52))==raw and get(S+300)==1
checks.append('zero/oversize/overlapping timing configurations fail before source mutation')
init();raw=src([255]);assert dispatch()==SRC and bytes(u.mem_read(SRC,52))==raw;checks.append('invalid note rejected before ownership')
init();raw=src();put(SRC+4,1);assert dispatch()==SRC and get(S+8)==0;checks.append('M2 bypass')
init();src([0,16,32,48,64,80,96,127]);assert dispatch()==A and get(S+16)==8;retire();checks.append('eight-note bounds and extremes')
init();src([60,64,67],now=0xfffff000);assert dispatch()==A;retire();assert timer((0xfffff000+5400000)&0xffffffff)==A and u.mem_read(A+20,1)==b'\x40';retire();assert timer((0xfffff000+43200000)&0xffffffff)==SRC and get(S+8)==0;checks.append('clock wraparound')
# Native consumer wrapper replays the displaced comparison with full frame.
init();src();u.mem_write(0x400f40ba,b'\x4e\x75');u.mem_write(0x400f4126,b'\x4e\x75');before={}
for reg in list(range(UC_M68K_REG_D0,UC_M68K_REG_D0+8))+list(range(UC_M68K_REG_A0,UC_M68K_REG_A0+7)):u.reg_write(reg,0x11100000+reg)
u.reg_write(UC_M68K_REG_A2,SRC);u.reg_write(UC_M68K_REG_D6,2);before={reg:u.reg_read(reg) for reg in list(range(UC_M68K_REG_D0,UC_M68K_REG_D0+8))+list(range(UC_M68K_REG_A0,UC_M68K_REG_A0+7))}
invoke(c['entries']['consumer']);assert u.reg_read(UC_M68K_REG_A2)==A and u.reg_read(UC_M68K_REG_D0)==1
for reg,val in before.items():
 if reg not in [UC_M68K_REG_D0,UC_M68K_REG_A2]:assert u.reg_read(reg)==val,(reg,hex(u.reg_read(reg)),hex(val))
retire();checks.append('native consumer wrapper register preservation')
# Ordinary descriptor path executes the exact stock push before free.
init();put(SRC+48,0x47bc8200);u.reg_write(UC_M68K_REG_A2,SRC);u.reg_write(UC_M68K_REG_A7,STACK);u.emu_start(c['entries']['retire'],0x400f49c6,count=200);assert u.reg_read(UC_M68K_REG_A7)==STACK-4 and get(STACK-4)==SRC and u.reg_read(UC_M68K_REG_D2)==0x47bc8200;checks.append('ordinary retirement retains stock free path')
for index,units in enumerate(c['rate_units']):
 for pct in [1,25,50,75,99]:
  init();assert invoke(c['entries']['configure'],[index,pct])==1;assert get(S+32)==units and get(S+36)==units*pct//200 and get(S+304)==index and get(S+308)==pct
checks.append('all native rate/gate choices in musical clock units')
for index,pct in [(8,50),(0xffffffff,50),(2,0),(2,100)]:
 init();before=bytes(u.mem_read(S+32,8));assert invoke(c['entries']['configure'],[index,pct])==0 and bytes(u.mem_read(S+32,8))==before
checks.append('invalid musical settings preserve prior configuration')
init();raw=src();put(0x47be2840,0x434f4c44);assert dispatch()==SRC and bytes(u.mem_read(SRC,52))==raw and get(S+8)==0
checks.append('COLD admission bypasses capture and generation')
init();raw=src();put(S+4,0);put(S+312,0);put(S+316,75);put(S+320,1);u.reg_write(UC_M68K_REG_A2,SRC);u.reg_write(UC_M68K_REG_D6,2);invoke(c['entries']['consumer']);assert get(S+320)==0 and get(S+32)==21600000 and get(S+36)==8100000 and bytes(u.mem_read(SRC,52))==raw
put(S+312,8);put(S+316,50);put(S+320,1);u.reg_write(UC_M68K_REG_A2,SRC);u.reg_write(UC_M68K_REG_D6,2);invoke(c['entries']['consumer']);assert get(S+320)==0 and get(S+32)==21600000 and get(S+36)==8100000
checks.append('native MIDI consumer applies pending settings atomically and rejects invalid requests')
assert bytes(u.mem_read(S-8,8))==b'BEFORE!!' and bytes(u.mem_read(S+c['state_bytes'],8))==b'AFTER!!!' and bytes(u.mem_read(A+64,8))==b'ARENAEND'
assert hashlib.sha256(Path('outputs/Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx').read_bytes()).hexdigest()=='a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'
out={'PC_only':True,'passed':True,'checks':checks,'groups':len(checks),'native_code_bytes':c['code_bytes'],'strict_ColdFire_regions_passed':True,'E07_unchanged':True,'limits':['Isolated native helper contracts; stock continuation stops at replayed boundaries. Continuous native MIDI playback still required.','Host code loading, native initialization in temporary frame and timing fixtures; no hardware placement or startup installation.']};Path('outputs/Digitone-E08-M1-relocated-tempo-contracts.json').write_text(json.dumps(out,indent=2));print('PASS',len(checks),'native contract groups')
