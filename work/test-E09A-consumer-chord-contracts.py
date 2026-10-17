"""Actual settings consumer/dispatcher/retirement, with stock exits bounded."""
from pathlib import Path
import json,struct,sys
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from unicorn.m68k_const import UC_M68K_REG_A2,UC_M68K_REG_A7,UC_M68K_REG_D2,UC_M68K_REG_D6
c=json.loads(Path('work/os144/E09A-PC-install-layout.json').read_text())
blob=Path('work/os144/E09A-PC-layout-payload.bin').read_bytes()
m=Machine(ddr=0x8000000);u=m.uc;S=c['state'];A=c['arena']
E=0x47bc8000;TP=E+0x100;KIT=E+0x1000;STACK=E+0x7f00
for p in [E,TP,KIT,STACK,0x80004614,0x419c5000,0x400f4000]:m.ensure(p)
for p in range(c['base'],c['base']+len(blob),4096):m.ensure(p)
u.mem_write(c['base'],blob)
for r in c['regions']:
 if r['base']>=c['base']:
  offset=r['base']-c['base'];m.install_isa_patches_scoped(blob[offset:offset+r['bytes']],r['base'])
for p in [0x400f40ba,0x400f4126]:u.mem_write(p,bytes.fromhex('4e75'))
put=lambda a,v:u.mem_write(a,struct.pack('>I',v&0xffffffff))
get=lambda a:int.from_bytes(u.mem_read(a,4),'big')
invoke=lambda p,args=[]:call(m,p,args,stack_top=STACK,limit=50000)
consumer=next(r['base'] for r in c['regions'] if r['name']=='M1_settings_consumer')

def init(word=0xaeb2):
 invoke(c['entries']['init'],[TP]);put(TP,1);put(0x47be2840,0x4c495645)
 put(0x419c5b10,KIT);put(0x419c5b14,0xcafebabe)
 u.mem_write(KIT+0x5ce+158,struct.pack('>H',word))

def event(notes,kind=0,mode=1,on=1,now=100000000,track=0):
 u.mem_write(E,bytes(52))
 for off,value in [(0,kind),(4,track),(8,on),(12,1),(16,len(notes)),(28,21600000 if mode==1 else 0),(32,100),(36,now),(40,0xdeadbeef),(44,mode)]:put(E+off,value)
 u.mem_write(E+20,bytes(notes));put(0x80004614,now)

def consume():
 u.reg_write(UC_M68K_REG_A2,E);u.reg_write(UC_M68K_REG_D6,2);invoke(consumer)
 return u.reg_read(UC_M68K_REG_A2)

def retire():
 u.reg_write(UC_M68K_REG_A2,A);u.reg_write(UC_M68K_REG_A7,STACK)
 u.emu_start(c['entries']['retire'],0x400f49cc,count=200)
 assert get(S+280)==0 and u.reg_read(UC_M68K_REG_D2)==get(A+48)

checks=[];init();event([67,60,64,60]);assert consume()==A
assert get(S+4)==1 and get(S+336)==KIT+0x5ce and get(S+16)==3
assert get(E+16)==0 and get(A+40)==0 and get(A+48)==E
notes=[u.mem_read(A+20,1)[0]];retire()
for i in range(1,6):
 event([],kind=3,now=100000000+i*900000)
 assert consume()==A;notes.append(u.mem_read(A+20,1)[0]);retire()
assert notes==[60,64,67,60,64,67],notes
checks.append('Sequenced fixture chord sorts/deduplicates to C E G twice, selecting consumed Kit settings and never dereferencing lock-list pointers.')
put(TP,2);event([],kind=3,now=106000000);assert consume()==E and get(S+8)==get(S+16)==0
checks.append('Transport stop clears generation after owned descriptor retirement.')
init();event([60],mode=2);assert consume()==E and get(S+4)==get(S+8)==1
event([],kind=3,now=100000001);assert consume()==A;assert u.mem_read(A+20,1)[0]==60;retire()
event([60],mode=2,on=2,now=101000000);assert consume()==E and get(S+8)==get(S+16)==0
checks.append('Live note-on, timed output and release remain functional with corrected owner selection.')
init();event([60],track=1);raw=bytes(u.mem_read(E,52));assert consume()==E and bytes(u.mem_read(E,52))==raw
checks.append('M2 bypass preserves the source descriptor.')
init(word=0xa932);event([60,64,67]);raw=bytes(u.mem_read(E,52));assert consume()==E and get(S+4)==0 and bytes(u.mem_read(E,52))==raw
checks.append('Pattern arp OFF preserves the original chord.')
out={'passed':True,'PC_only':True,'checks':checks,'notes':notes,
     'limits':['Descriptor and clock fixtures; stock consumer continuations stop at RTS boundaries. Native panel sequence playback is tested separately.']}
Path('outputs/Digitone-E09A-consumer-chord-contracts.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
