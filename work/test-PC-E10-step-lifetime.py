"""Execute native cold/reset and pattern-record APIs; no filesystem hooks."""
from pathlib import Path
import json,struct,sys
exec(compile(Path('work/test-PC-E10-step-publication.py').read_text().split('\nchecks=[]\n')[0],'E10-lifetime-fixture','exec'))
life=json.loads(Path('work/os144/PC_ONLY-E10-step-lifetime.json').read_text())
life_blob=Path('work/os144/PC_ONLY-E10-step-lifetime.bin').read_bytes();BANK=life['bank']
for page in range(life['base'],BANK+life['bank_bytes']+4096,4096):m.ensure(page)
u.mem_write(life['base'],life_blob)
for r in life['regions']:
 raw=life_blob[r['base']-life['base']:r['base']-life['base']+r['bytes']];off=0
 while off<len(raw):
  ins=cfisa.decode(lambda x:int.from_bytes(raw[off+x:off+x+2],'big'),r['base']+off)
  assert ins.length and off+ins.length<=len(raw) and not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not audit['move_restriction'](int.from_bytes(raw[off:off+2],'big')),(r,off,ins)
  off+=ins.length
 m.install_isa_patches_scoped(raw,r['base'])
def run(name,args=[]):return invoke(life['entries'][name],args)
checks=[]
reset();put(0x47be2840,0x434f4c44);u.mem_write(X,b'\xa7'*64);u.mem_write(BANK-16,b'\x59'*16);u.mem_write(BANK,b'\xa7'*4096);u.mem_write(BANK+4096,b'\x59'*16)
assert run('init')==1
assert [get(X+x) for x in [0,4,8,12,16,20,24,28,48,52,56,60]]==[0x4d535131,0,16,0,0,0xffff,0x80000080,0,0,0,0,0]
assert bytes(u.mem_read(X+32,16))==bytes(16) and bytes(u.mem_read(BANK,4096))==bytes(4096)
assert bytes(u.mem_read(BANK-16,16))==bytes(u.mem_read(BANK+4096,16))==b'\x59'*16
checks.append('Cold initialization clears all 128 records and all 64 runtime bytes, then publishes disabled defaults; canaries intact.')
for label,gate,field in [('LIVE',0x4c495645,None),('bad admission',0,None),('active',0x434f4c44,8),('live source',0x434f4c44,12),('held',0x434f4c44,16),('arena',0x434f4c44,280)]:
 reset();put(0x47be2840,gate)
 if field is not None:put(S+field,1)
 before=bytes(u.mem_read(X,64))+bytes(u.mem_read(BANK,4096));assert run('init')==0
 assert bytes(u.mem_read(X,64))+bytes(u.mem_read(BANK,4096))==before,label
checks.append('LIVE, invalid admission, active, retained-source, held and outstanding-arena reset requests refuse before mutation.')
args=reset();assert publish(args)==1
before_stock=bytes(u.mem_read(DATA,164));expected={}
for slot in range(128):
 put(X+4,slot&1);put(X+8,slot%16+1);put(X+20,(slot*503)&0xffff);put(X+24,0x80000000|((slot%36)<<7)|(slot%12))
 u.mem_write(X+32,bytes(((slot+j)%49-24)&255 for j in range(16)))
 expected[slot]=[get(X+x) for x in [4,8,20,24]]+[bytes(u.mem_read(X+32,16)).hex()]
 assert run('save',[slot,DATA])==1,slot
 raw=bytes(u.mem_read(BANK+32*slot,32));assert raw[:4]==b'MS10' and int.from_bytes(raw[28:],'big')==sum(raw[:28])
 assert run('validate',[BANK+32*slot])==1
for slot in reversed(range(128)):
 new_owner=DATA+0x400+slot*4
 assert run('load',[slot,new_owner])==1
 actual=[get(X+x) for x in [4,8,20,24]]+[bytes(u.mem_read(X+32,16)).hex()]
 assert actual==expected[slot],(slot,actual,expected[slot])
 assert get(X+28)==new_owner and all(get(X+x)==0 for x in [12,16,48,52,56,60])
assert bytes(u.mem_read(DATA,164))==before_stock
checks.append('All 128 independent pattern records round-trip natively with varied flags, lengths, masks, roots/scales and signed offsets; owner/cursors are not persisted; stock MIDI record untouched.')
for name,args in [('save',[128,get(X+28)]),('load',[128,DATA]),('save',[0,DATA]),('load',[0,0])]:
 before=bytes(u.mem_read(X,64))+bytes(u.mem_read(BANK,4096));assert run(name,args)==0,(name,args)
 assert bytes(u.mem_read(X,64))+bytes(u.mem_read(BANK,4096))==before
checks.append('Out-of-range slots, stale save owner and invalid load owner refuse without mutation.')
raw=bytes(u.mem_read(BANK,32));corruptions=0
for off in range(32):
 bad=bytearray(raw);bad[off]^=1;u.mem_write(BANK,bytes(bad));before=bytes(u.mem_read(X,64))
 assert run('load',[0,DATA])==0 and bytes(u.mem_read(X,64))==before,off
 corruptions+=1
u.mem_write(BANK,raw)
checks.append('A single-byte corruption at each of the 32 record positions rejects without touching runtime state.')
for field in [8,12,16,280]:
 put(S+field,1);before=bytes(u.mem_read(X,64))+bytes(u.mem_read(BANK,4096))
 assert run('load',[0,DATA])==run('save',[0,get(X+28)])==0
 assert bytes(u.mem_read(X,64))+bytes(u.mem_read(BANK,4096))==before
 put(S+field,0)
checks.append('Saving and loading are explicitly quiescent-only, including outstanding descriptor ownership.')
for field,value in [(4,256),(8,0),(8,257),(20,0x10001),(24,0x80002080),(24,0x80)]:
 old=get(X+field);put(X+field,value);before=bytes(u.mem_read(BANK,4096));assert run('save',[0,get(X+28)])==0,(field,value)
 assert bytes(u.mem_read(BANK,4096))==before;put(X+field,old)
checks.append('Full-width fields are checked before narrowing to the stored representation.')
for sr in [0x201f,0x2310,0x2700]:
 args=[0,get(X+28)];u.mem_write(STACK,struct.pack('>I',0xdeadbee0)+b''.join(struct.pack('>I',v) for v in args))
 u.reg_write(UC_M68K_REG_SR,sr);u.reg_write(UC_M68K_REG_A7,STACK);u.emu_start(life['entries']['save'],0xdeadbee0,count=50000)
 assert u.reg_read(UC_M68K_REG_D0)==1 and u.reg_read(UC_M68K_REG_SR)==sr
checks.append('Publication retains the caller interrupt mask and flags.')
out=dict(PC_only=True,passed=True,strict_ColdFire_checked=True,checks=checks,patterns_round_tripped=128,corruption_cases=corruptions,native_project_persistence=False,automatic_pattern_binding=False,limits=life['limits'])
Path('outputs/Digitone-E10-PC-step-lifetime.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
