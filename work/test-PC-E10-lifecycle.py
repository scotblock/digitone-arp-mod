"""Native clipboard/undo and retained-image contracts, with stock copy/checksum."""
from pathlib import Path
import json,struct
ns={};exec(compile(Path('work/test-PC-E10-pattern-binding.py').read_text(encoding='utf-8').split('checks=[];reset()')[0],'E10-lifecycle-fixture','exec'),ns)
globals().update({k:v for k,v in ns.items() if not k.startswith('__')})
from unicorn.m68k_const import UC_M68K_REG_PC
c=json.loads(Path('work/os144/PC_ONLY-E10-life-layout.json').read_text());L=c['lifecycle'];Z=L['meta'];CLIPS=L['clips'];PM=c['persistence']['meta'];BM=c['binding']['meta'];BANK=c['E10']['bank']
raw=Path('work/os144/PC_ONLY-E10-life-payload.bin').read_bytes()
PROJECT=0x407fd3f8;DATA=PROJECT+0xb0946a;KIT=DATA-0x5ce;MIRROR=0x40555ff4;FIELD=MIRROR+0x240200+0x940
for lo,hi in [(0x40500000,0x40800000),(0x41300000,0x41400000),(0x41c00000,0x41d00000),(c['base'],c['copy_destination_end']+4096)]:
 for p in range(lo,hi,4096):m.ensure(p)
u.mem_write(c['base'],raw)
for lo,hi in [(0x4008511a,0x400852cc),(0x400fbad8,0x400fbb90)]:
 code=stock[lo-0x40000400:hi-0x40000400];m.ensure(lo);u.mem_write(lo,code);m.install_isa_patches_scoped(code,lo)
for r in c['regions']:
 if r['base']<c['base']:continue
 code=raw[r['base']-c['base']:r['base']-c['base']+r['bytes']];off=0
 while off<len(code):
  ins=cfisa.decode(lambda v:int.from_bytes(code[off+v:off+v+2],'big'),r['base']+off)
  assert ins.length and off+ins.length<=len(code) and not ins.flags&(cfisa.ILLEGAL|cfisa.LINEF|cfisa.FPU) and not audit['move_restriction'](int.from_bytes(code[off:off+2],'big')),(r,off,ins)
  off+=ins.length
 m.install_isa_patches_scoped(code,r['base'])
proof=json.loads(Path('outputs/Digitone-E10-PC-bound-panel-patterns.json').read_text());records=[bytes.fromhex(x) for x in proof['expected_records']]
def setup():
 # Use the existing native M1 initializer and native COKI header finalizer.
 ns['DATA']=DATA;ns['KIT']=KIT;ns['PROJECT']=PROJECT;ns['reset']()
 u.mem_write(Z,bytes(L['meta_bytes']));u.mem_write(0x40555ee4,bytes(0x110));u.mem_write(MIRROR,bytes.fromhex('beefbace0000000e'))
 invoke(0x40085268,[]);assert invoke(0x4008525a,[])==1
 for i in range(128):u.mem_write(FIELD+i*0xa00,records[i] if i<2 else bytes(32))
 assert invoke(L['entries']['capture'],[MIRROR,PROJECT])==1
 assert get(Z)==0x4d434831 and get(Z+4)==get(PM+12)
 return ns['recall'](DATA)
def cp(caller,dest,src):
 u.mem_write(STACK,struct.pack('>IIII',caller,dest,src,0x988));u.reg_write(UC_M68K_REG_A7,STACK);u.reg_write(UC_M68K_REG_SR,0x2000)
 u.emu_start(L['entries']['copy'],caller,count=300000)
 assert u.reg_read(UC_M68K_REG_PC)==caller and u.reg_read(UC_M68K_REG_D0)==dest
def edit(encoder,delta=1):return invoke(L['entries']['edit'],[DATA,encoder,delta&0xffffffff])
checks=[];assert setup()==1
assert edit(6)==1 and bytes(u.mem_read(FIELD,32))==bytes(u.mem_read(BANK,32)) and bytes(u.mem_read(FIELD,32))!=records[0]
assert invoke(0x4008525a,[])==1
checks.append('An unsaved native editor change updates the bank and retained record; the actual stock COKI validator accepts the refreshed header.')
before=bytes(u.mem_read(FIELD,32));put(Z+4,get(PM+12)+1);assert invoke(L['entries']['sync'],[0])==0 and bytes(u.mem_read(FIELD,32))==before
put(Z+4,get(PM+12));put(0x40555ee4,0);assert invoke(L['entries']['sync'],[0])==0 and bytes(u.mem_read(FIELD,32))==before
invoke(0x40085268,[]);assert invoke(L['entries']['sync'],[128])==0
put(0x4136bcc4,0);put(0x40555ee8,get(0x40555ee8)^1)
assert invoke(L['entries']['sync'],[0])==0 and bytes(u.mem_read(FIELD,32))==before and get(0x4136bcc4)==0
invoke(0x40085268,[])

checks.append('Stale project generation, invalid COKI header and out-of-range slots refuse before retained-record writes.')
assert setup()==1;clip=0x41c681c1;undo=0x41c881c1;clear=0x41ca81c1;kit2=KIT+0x988
cp(0x400288dc,clip,KIT);cp(0x400280ea,undo,kit2);cp(0x4002815a,kit2,clip)
assert bytes(u.mem_read(BANK+32,32))==records[0] and bytes(u.mem_read(FIELD+0xa00,32))==records[0]
cp(0x400282ce,kit2,undo);assert bytes(u.mem_read(BANK+32,32))==records[1] and bytes(u.mem_read(FIELD+0xa00,32))==records[1]
cp(0x4002815a,kit2,clip);cp(0x40028764,clear,kit2);cp(0x400282ce,kit2,clear)
assert bytes(u.mem_read(BANK+32,32))==records[0] and bytes(u.mem_read(BANK,32))==records[0]
checks.append('Actual stock memcpy plus exact producer/consumer continuations carry step records through paste, undo-paste and the clear-undo snapshot, preserving the source pattern.')
cp(0x4002815a,kit2,0x41c781c1);assert bytes(u.mem_read(BANK+32,32))==bytes(32)
assert setup()==1;cp(0x400288dc,clip,KIT);put(PM+12,get(PM+12)+1);cp(0x4002815a,kit2,clip)
assert bytes(u.mem_read(BANK+32,32))==bytes(32)
checks.append('Unknown and previous-generation clipboard sources produce absent/disabled steps, not stale destination or foreign-project settings.')
assert setup()==1;assert invoke(L['entries']['capture'],[0,PROJECT])==0 and get(Z)==0
assert setup()==1;put(Z,0);assert invoke(L['entries']['emit'],[MIRROR,PROJECT])==1 and get(Z)==0x4d434831
checks.append('A new/failed project capture revokes mirror ownership; a successful matching retained-image encode reestablishes it.')
for sr in [0x201f,0x2310,0x2700]:
 assert setup()==1;u.mem_write(STACK,struct.pack('>IIII',0xdeadbee0,DATA,6,1));u.reg_write(UC_M68K_REG_A7,STACK);u.reg_write(UC_M68K_REG_SR,sr)
 u.emu_start(L['entries']['edit'],0xdeadbee0,count=300000);assert u.reg_read(UC_M68K_REG_D0)==1 and u.reg_read(UC_M68K_REG_SR)==sr
checks.append('The editor retains its original interrupt mask/flags around notification, bank commit and retained-image synchronization.')
out=dict(PC_only=True,passed=True,strict_ColdFire_checked=True,checks=checks,limits=L['limits']+['Isolated native-header, project and exact-callsite fixtures; actual panel copy/undo and write/reboot chains are separate tests.'])
Path('outputs/Digitone-E10-PC-lifecycle-contracts.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
