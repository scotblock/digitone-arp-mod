"""Native owned slot mapping, recall and editor persistence contracts."""
from pathlib import Path
import json,struct
exec(compile(Path('work/test-PC-E10-step-publication.py').read_text(encoding='utf-8').split('\nchecks=[]\n')[0],'E10-binding-fixture','exec'))
c=json.loads(Path('work/os144/PC_ONLY-E10-bound-layout.json').read_text());b=c['binding'];PM=c['persistence']['meta'];BM=b['meta'];BANK=c['E10']['bank']
raw=Path('work/os144/PC_ONLY-E10-bound-payload.bin').read_bytes()
stock=Path('work/os144/section-3.bin').read_bytes();start=0x4014ef80;notify=stock[start-0x40000400:0x4014f034-0x40000400]
m.ensure(start);u.mem_write(start,notify);m.install_isa_patches_scoped(notify,start)
for p in range(c['base'],c['copy_destination_end']+4096,4096):m.ensure(p)
u.mem_write(c['base'],raw)
for r in c['regions']:
 if r['base']<c['base']:continue
 code=raw[r['base']-c['base']:r['base']-c['base']+r['bytes']];off=0
 while off<len(code):
  ins=cfisa.decode(lambda v:int.from_bytes(code[off+v:off+v+2],'big'),r['base']+off)
  assert ins.length and off+ins.length<=len(code) and not ins.flags&(cfisa.ILLEGAL|cfisa.LINEF|cfisa.FPU) and not audit['move_restriction'](int.from_bytes(code[off:off+2],'big')),(r,off,ins)
  off+=ins.length
 m.install_isa_patches_scoped(code,r['base'])
PROJECT=DATA-0xb0946a
assert 0x40000000<=PROJECT<=0x47494000,hex(PROJECT)
original_reset=reset
def reset():
 args=original_reset();put(get(S+40),0);u.mem_write(BM,bytes(32));u.mem_write(PM,bytes(32));u.mem_write(BANK,bytes(4096))
 # This isolated handle has no live subscriber graph. The actual callbacks
 # are exercised by the native panel test, not replaced with host outcomes.
 u.mem_write(ROOT+0xff8+0xc,b'\1');u.mem_write(ROOT+0xff8+0x24,b'\1')
 for off,v in [(0,0x4d535031),(4,1),(8,PROJECT),(12,1)]:put(PM+off,v)
 return args
def recall(owner,role=1):return invoke(b['entries']['recall'],[owner,role])
def edit(owner,encoder,delta=1):return invoke(b['entries']['edit'],[owner,encoder,delta&0xffffffff])
def xfields():return [get(X+v) for v in [4,8,20,24]]+[bytes(u.mem_read(X+32,16)).hex()]
checks=[];reset()
for i in range(128):assert invoke(b['entries']['resolve'],[DATA+i*0x988])==i,i
for owner in [DATA-1,DATA+1,DATA+0xa4,DATA+128*0x988]:assert invoke(b['entries']['resolve'],[owner])==0xffffffff,hex(owner)
checks.append('All 128 exact kit-array owners map to their own slots; misaligned, adjacent-track and out-of-array pointers refuse.')
args=reset();assert recall(DATA)==1 and get(X+4)==0 and get(BM+8)==0
assert edit(DATA,3,-1)==1 and get(X+8)==15
assert edit(DATA,6,1)==1 and edit(DATA,8,1)==1
assert invoke(c['E10']['entries']['validate'],[BANK])==1
first=xfields();rec=bytes(u.mem_read(BANK,32))
second=DATA+0x988;put(ROOT+0x1008,second);assert recall(second)==1
assert get(X+4)==0 and get(X+8)==16 and bytes(u.mem_read(X+32,16))==bytes(16)
assert edit(second,1,1)==1 and edit(second,6,-1)==1 and edit(second,8,1)==1
second_fields=xfields();assert first!=second_fields and bytes(u.mem_read(BANK,32))==rec
put(ROOT+0x1008,DATA);assert recall(DATA)==1 and xfields()==first
put(ROOT+0x1008,second);assert recall(second)==1 and xfields()==second_fields
checks.append('Native editor changes immediately commit checksummed records; two patterns recall distinct lengths/roots/offsets/enables; blank patterns receive disabled defaults.')
# Source context changes while notes remain held. It changes only step settings,
# and never clears the held set or an outstanding native note descriptor.
put(S+8,1);put(S+16,3);put(S+336,DATA);assert recall(DATA,0)==1 and xfields()==first
before=bytes(u.mem_read(BANK,4096));assert edit(second,6,1)==0 and bytes(u.mem_read(BANK,4096))==before
put(ROOT+0x1008,DATA);assert edit(DATA,6,1)==1
assert get(S+8)==1 and get(S+16)==3
checks.append('Held-note consumed recall preserves held state; pending-panel edits refuse, while same-owner edits remain persistable.')
put(S+280,1);put(S+336,second);assert recall(second,0)==0 and get(X+28)==0
assert get(S+280)==1 and get(S+16)==3
put(S+280,0);assert recall(second,0)==1 and xfields()==second_fields
checks.append('Outstanding arena ownership defers recall and invalidates step ownership; retry succeeds after retirement without touching held notes.')
# Reuse exactly the same runtime project and kit addresses, but replace records.
put(S+8,0);put(S+16,0);put(ROOT+0x1008,second);u.mem_write(BANK+32,bytes(32));put(PM+12,2)
assert recall(second)==1 and get(X+4)==0 and bytes(u.mem_read(X+32,16))==bytes(16) and get(BM+4)==2
checks.append('Project-generation changes force fresh recall even when all runtime addresses are reused.')
put(PM+4,0);put(S+336,second);assert recall(second,0)==0 and get(X+28)==0
assert edit(second,6,1)==0
checks.append('Missing captured-project ownership prevents editor writes and invalidates consumed step ownership.')
args=reset();assert edit(DATA,6,1)==1
valid=bytes(u.mem_read(BANK,32));bad=bytearray(valid);bad[31]^=1
u.mem_write(BANK,bytes(bad));put(PM+12,2)
assert recall(DATA)==1 and get(X+4)==0 and get(X+8)==16 and bytes(u.mem_read(X+32,16))==bytes(16)
assert bytes(u.mem_read(BANK,32))==bytes(bad)
assert edit(DATA,6,1)==1 and invoke(c['E10']['entries']['validate'],[BANK])==1
checks.append('A malformed saved record recalls disabled defaults without rewriting it; the next accepted edit creates a valid replacement.')
for index,value in [(1,0),(1,17),(2,0x10000),(3,0x8000008c),(5,2)]:
 args=reset();assert recall(DATA)==1;args[index]=value;before=bytes(u.mem_read(BANK,4096))
 assert invoke(b['entries']['publish'],args)==0 and bytes(u.mem_read(BANK,4096))==before
checks.append('Rejected complete settings never partially commit a bank record.')
for sr in [0x201f,0x2310,0x2700]:
 reset();u.mem_write(STACK,struct.pack('>IIII',0xdeadbee0,DATA,6,1));u.reg_write(UC_M68K_REG_SR,sr);u.reg_write(UC_M68K_REG_A7,STACK)
 u.emu_start(b['entries']['edit'],0xdeadbee0,count=200000)
 assert get(BANK)==0x4d533130 and u.reg_read(UC_M68K_REG_D0)==1 and u.reg_read(UC_M68K_REG_SR)==sr
checks.append('Nested recall/editor/commit restores the original interrupt mask and flags.')
out=dict(PC_only=True,passed=True,checks=checks,strict_ColdFire_checked=True,editor_to_bank_connected=True,slot_count=128,limits=b['limits']+['Isolated owner/project/UI fixtures. Continuous native panel, transition and save/load tests are separate.'])
Path('outputs/Digitone-E10-PC-pattern-binding-contracts.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
