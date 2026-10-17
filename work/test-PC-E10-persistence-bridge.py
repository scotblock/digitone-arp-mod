"""Native bridge contracts and real project kit-loop hook continuations."""
from pathlib import Path
import json,sys,struct,hashlib
sys.path.insert(0,'work')
from E10_storage_probe import record_bytes
ns={};exec(compile(Path('work/audit-PC-E10-native-kit-codec.py').read_text().split('\nout=dict')[0],'E10-project-fixture','exec'),ns)
m=ns['m'];u=ns['u'];FR=ns['FR'];RR=ns['RR'];BR=ns['BR'];STACK=ns['STACK']
from emu.harness import call
from emu import cfisa
from unicorn.m68k_const import *
c=json.loads(Path('work/os144/PC_ONLY-E10-startup-layout.json').read_text());bridge=json.loads(Path('work/os144/PC_ONLY-E10-persistence-bridge.json').read_text());life=c['E10'];S=c['state'];X=life['state'];BANK=life['bank'];META=bridge['meta']
payload=Path('work/os144/PC_ONLY-E10-startup-payload.bin').read_bytes();raw=Path('work/os144/PC_ONLY-E10-persistence-bridge.bin').read_bytes()
for p in range(c['base'],bridge['base']+len(raw)+4096,4096):m.ensure(p)
u.mem_write(c['base'],payload);u.mem_write(bridge['base'],raw)
audit={};exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0],audit)
for r in c['regions']+bridge['regions']:
 data=payload if r['base']<bridge['base'] else raw;base=c['base'] if data is payload else bridge['base'];code=data[r['base']-base:r['base']-base+r['bytes']];off=0
 while off<len(code):
  ins=cfisa.decode(lambda v:int.from_bytes(code[off+v:off+v+2],'big'),r['base']+off)
  assert ins.length and off+ins.length<=len(code) and not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not audit['move_restriction'](int.from_bytes(code[off:off+2],'big')),(r,off,ins)
  off+=ins.length
 m.install_isa_patches_scoped(code,r['base'])
put=lambda p,v:u.mem_write(p,struct.pack('>I',v&0xffffffff))
get=lambda p:int.from_bytes(u.mem_read(p,4),'big')
invoke=lambda entry,args:call(m,entry,args,stack_top=STACK,limit=1000000)
SER=FR-0x240200;OWNER=RR-0xb08e9c;PROG=0x47b90000;m.ensure(PROG);u.mem_write(PROG,bytes(64))
def reset():
 invoke(c['entries']['init'],[0x4138f208]);put(0x47be2840,0x434f4c44);assert invoke(life['entries']['init'],[])==1
 u.mem_write(META,bytes(32));put(0x47be2840,0x4c495645)
def seed():
 for slot in range(128):u.mem_write(FR+slot*0xa00+0x940,record_bytes(slot))
def cap():return invoke(bridge['entries']['capture'],[SER,OWNER])
def emit(owner=OWNER):return invoke(bridge['entries']['emit'],[SER,owner])
checks=[];reset();seed();assert cap()==1 and get(META+4)==1 and get(META+8)==OWNER and get(META+16)==128
assert bytes(u.mem_read(BANK,4096))==b''.join(record_bytes(i) for i in range(128))
before=bytes(u.mem_read(FR,0x50000));u.mem_write(FR,bytes(0x50000));assert emit()==1 and get(META+24)==128
for i in range(128):assert bytes(u.mem_read(FR+i*0xa00+0x940,32))==record_bytes(i)
checks.append('All 128 valid records capture and emit through actual machine code.')
reset();seed()
for slot in [0,63,127]:u.mem_write(FR+slot*0xa00+0x940,b'\xcc'*32)
assert cap()==1 and get(META+16)==125
for slot in range(128):assert bytes(u.mem_read(BANK+slot*32,32))==(bytes(32) if slot in [0,63,127] else record_bytes(slot))
checks.append('Malformed/blank records become absent defaults without carrying the previous project.')
reset();seed();assert cap()==1;u.mem_write(FR,b'\xa5'*0x50000);assert emit(OWNER+4)==0
for i in range(128):assert bytes(u.mem_read(FR+i*0xa00+0x940,32))==bytes(32)
assert get(META+4)==1 and get(META+8)==OWNER
checks.append('A different project receives zero records, including reused serialized buffers; original ownership remains bound.')
for field in [8,12,16,280]:
 reset();seed();assert cap()==1;put(S+field,1);bank=bytes(u.mem_read(BANK,4096));assert cap()==0 and get(META+4)==0
 assert bytes(u.mem_read(BANK,4096))==bank
checks.append('Active/live/held/arena capture refuses before bank mutation and invalidates stale ownership.')
for gate in [0x434f4c44,0x4c495645,0]:
 reset();seed();put(0x47be2840,gate);assert cap()==(1 if gate else 0)
checks.append('Cold and LIVE quiescent loads are admitted; invalid admission refuses.')
for args in [[0,OWNER],[0x47d58bfe,OWNER],[SER,0]]:
 reset();seed();assert invoke(bridge['entries']['capture'],args)==0
checks.append('Serialized spans and runtime-owner bounds are checked.')
reset();seed();assert cap()==1
for sr in [0x201f,0x2310,0x2700]:
 u.mem_write(STACK,struct.pack('>III',0xdeadbee0,SER,OWNER));u.reg_write(UC_M68K_REG_SR,sr);u.reg_write(UC_M68K_REG_A7,STACK)
 u.emu_start(bridge['entries']['emit'],0xdeadbee0,count=1000000);assert get(META+24)==128 and u.reg_read(UC_M68K_REG_SR)==sr
checks.append('Caller interrupt mask and flags survive the atomic record loop.')
# Install the two real MAIN hooks, then execute the stock loops around them.
for h in bridge['hooks']:
 assert bytes(u.mem_read(h['site'],h['length'])).hex()==h['before'];u.mem_write(h['site'],bytes.fromhex(h['after']))
reset();seed();baseline=bytes(u.mem_read(BR,0x4c400))
for reg,value in [(UC_M68K_REG_A2,PROG),(UC_M68K_REG_A3,SER),(UC_M68K_REG_A4,OWNER),(UC_M68K_REG_A5,FR),(UC_M68K_REG_D4,RR),(UC_M68K_REG_A6,0x400093d0),(UC_M68K_REG_D5,0x40014e84),(UC_M68K_REG_D3,0),(UC_M68K_REG_A7,STACK)]:u.reg_write(reg,value)
u.emu_start(0x4000e960,0x4000e9a8,count=20000000);assert u.reg_read(UC_M68K_REG_PC)==0x4000e9a8 and get(META+8)==OWNER and get(META+16)==128
u.mem_write(FR,bytes(0x50000))
for reg,value in [(UC_M68K_REG_A3,SER),(UC_M68K_REG_D3,OWNER),(UC_M68K_REG_D4,2),(UC_M68K_REG_D5,0),(UC_M68K_REG_A7,STACK)]:u.reg_write(reg,value)
u.emu_start(0x4000ecc0,0x4000ecf6,count=20000000);assert u.reg_read(UC_M68K_REG_PC)==0x4000ecf6
for slot in range(128):assert bytes(u.mem_read(FR+slot*0xa00+0x940,32))==record_bytes(slot)
checks.append('The actual hooked native project decode and encode loops preserve all records through a fresh buffer rebuild.')
out=dict(PC_only=True,passed=True,strict_ColdFire_checked=True,checks=checks,patterns=128,native_MAIN_hooks_executed=True,limits=bridge['limits']+['Isolated project-array fixtures; complete UI/storage/startup continuity is tested separately.'])
Path('outputs/Digitone-E10-PC-persistence-bridge-contracts.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
