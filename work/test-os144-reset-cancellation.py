import sys,json,struct,hashlib
from pathlib import Path
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import *
info=json.loads(Path('work/packed-context-build.json').read_text());port=json.loads(Path('work/os144/helper-port.json').read_text())
stock=Path('work/os144/section-3.bin').read_bytes();blob=Path('work/os144/packed-context-overlay.bin').read_bytes()
RAM,PTR,BSS,STACK,POOL=0x47be0000,0x47be1000,0x47be1004,0x47fdff00,0x419ebe2c
m=Machine(ddr=0x08000000)
for offset in range(0,len(stock)+0x400,0x100000):m.ensure(0x40000000+offset)
for address in [RAM,STACK,POOL,0x47bccf04,0x413915f4]:m.ensure(address)
uc=m.uc;uc.mem_write(0x40000400,stock);uc.mem_write(RAM,blob);m.install_isa_patches_scoped(blob[:info['code_bytes']],RAM)
u32=lambda v:struct.pack('>I',v&0xffffffff)
def ready():
 uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1))
 uc.mem_write(BSS+16,bytes([0xa5])*(0xb70-16));uc.reg_write(UC_M68K_REG_SR,0x2700)
resets=[]
for mode in ['ready','not_ready','magic','version','size','null_pointer','bad_argument']:
 ready()
 if mode=='not_ready':uc.mem_write(BSS+12,u32(0))
 if mode in ['magic','version','size']:uc.mem_write(BSS+['magic','version','size'].index(mode)*4,u32(0))
 if mode=='null_pointer':uc.mem_write(PTR,u32(0))
 before=bytes(uc.mem_read(PTR,0xb74));arg=157 if mode=='bad_argument' else 158
 if mode in ['ready','not_ready']:
  call(m,info['layout']['reset']['address'],[arg],stack_top=STACK,limit=300000)
  assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
  assert bytes(uc.mem_read(BSS,16))==struct.pack('>IIII',0x534c4332,2,0xb70,1)
  assert bytes(uc.mem_read(BSS+16,0xb70-16))==bytes(0xb70-16)
 else:
  uc.mem_write(STACK,u32(0xdeadbee0)+u32(arg));uc.reg_write(UC_M68K_REG_A7,STACK)
  end=info['instruction_map'][str(0x47be0752)]
  uc.emu_start(info['layout']['reset']['address'],end,count=300000)
  assert uc.reg_read(UC_M68K_REG_PC)==end and bytes(uc.mem_read(PTR,0xb74))==before
 resets.append({'mode':mode,'passed':True,'failure_loop':mode not in ['ready','not_ready']})
# Isolate the real stock rejection gate with valid-looking retained metadata.
# The custom helper intentionally relies on this upstream consumer gate.
hits=[]
uc.hook_add(UC_HOOK_CODE,lambda uc,a,n,d:hits.append(hex(a)),begin=RAM,end=RAM+info['code_bytes']-1)
for h in port['hooks']:
 if h['name'] in ['before','caller_commit','pitch_hook']:
  assert bytes(uc.mem_read(int(h['site'],16),h['length']))==bytes.fromhex(h['stock_bytes'])
  op='4eb9' if h['name']=='before' else '4ef9'
  uc.mem_write(int(h['site'],16),bytes.fromhex(op)+u32(h['helper'])+bytes.fromhex('4e71')*((h['length']-6)//2))
cancel=[]
for track in range(4):
 ready();event=POOL+track*72;identity=0x41a120a0+track*0x504
 data=bytearray(72)
 for offset,value in [(0,0),(4,1),(8,track),(12,0xffffffff),(40,1<<19),(56,identity),(64,identity)]:data[offset:offset+4]=u32(value)
 uc.mem_write(event,bytes(data));uc.mem_write(BSS+32+track*4,u32(0x800000bd|(track<<13)))
 uc.mem_write(BSS+0xb30+track*16,struct.pack('>IIII',identity,0x800000bd|(track<<13),0,0x80000000|track))
 before=bytes(uc.mem_read(BSS,0xb70));hits.clear();uc.reg_write(UC_M68K_REG_D0,0);uc.reg_write(UC_M68K_REG_A3,event);uc.reg_write(UC_M68K_REG_A7,STACK)
 uc.emu_start(0x4009d760,0x40100028,count=10000)
 assert uc.reg_read(UC_M68K_REG_PC)==0x40100028
 assert not hits and bytes(uc.mem_read(BSS,0xb70))==before and bytes(uc.mem_read(event,72))==data
 cancel.append({'track':track,'stock_rejection_reached_release':True,'custom_helper_entries':0,'retained_context_and_event_unchanged_before_release':True})
assert bytes(uc.mem_read(RAM,len(blob)))==blob
result={'passed':True,'firmware_modified':False,'reset_cases':resets,'cancelled_consumer_cases':cancel,'limits':['Direct reset invocation with explicit ready/not-ready storage; no startup installation or concurrent producer proof.','Invalid-mode paths stop at the helper failure loop; no outer failure recovery claim.','Cancellation tests execute stock gate to release entry with temporary downstream PC overlays, not full playback.','Pitch helper itself relies on upstream eligibility; it does not independently reject +0x0c=-1.']}
Path('outputs/Digitone-OS1.44-helper-reset-cancellation.json').write_text(json.dumps(result,indent=2));print('PASS',len(resets),'reset cases;',len(cancel),'stock cancellation gates')
