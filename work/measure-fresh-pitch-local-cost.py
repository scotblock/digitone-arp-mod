"""Isolated helper cost bounds; no claim about playback scheduler phase."""
import sys,pathlib,json,struct,types,collections
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from unicorn import UC_HOOK_BLOCK
from emu.harness import Machine
from emu.cftiming import CycleClock
from shared_memory_timing import MemoryTiming
from unicorn.m68k_const import *
class LocalMemory(MemoryTiming):
 def install_dma(self):pass
stock=pathlib.Path('work/section-3.bin').read_bytes();blob=pathlib.Path('work/cache-context-overlay.bin').read_bytes()
layout=json.loads(pathlib.Path('work/native-overlay-layout.json').read_text())
base=0x40000400;ram=0x47be0000;bss=ram+0x1004;ptr=ram+0x1000
report=json.loads(pathlib.Path('outputs/Digitone-cycle-complete-handoff-native-pattern-copy.json').read_text())
control={int(k,16):int(v,16) for k,v in report['timing']['memory']['initial_controls'].items()}
u32=lambda x:struct.pack('>I',x)
rows=[]
for mode in ['stock','helper']:
 m=Machine(ddr=0x08000000);m.load(stock,base);m.ensure(ram);uc=m.uc
 uc.mem_write(ram,blob);m.install_isa_patches_scoped(blob[:1892],ram)
 uc.mem_write(ptr,u32(bss-0x14100));uc.mem_write(bss,struct.pack('>IIII',0x534c4332,2,0xb70,1))
 event=0x4199dc44;track=2;identity=0x419c38c0+track*0x504;word=0x8000433b
 for address in [event,0x41345f08+track*72,0x41344530+track*40+24,0x41345620+track*4,0x47fdff00]:m.ensure(address)
 data=bytearray(72)
 for off,value in [(0,0),(4,1),(8,track),(40,1<<19),(64,identity)]:data[off:off+4]=u32(value)
 uc.mem_write(event,bytes(data));uc.mem_write(0x41345f08+track*72,bytes(data))
 uc.mem_write(0x41344530+track*40+24,u32(identity));uc.mem_write(0x41345620+track*4,u32(1))
 uc.mem_write(bss+0xb30+track*16,struct.pack('>IIII',identity,word,0,0x80000000|track))
 if mode=='helper':uc.mem_write(0x4009df9a,bytes.fromhex('4ef9')+u32(layout['pitch_hook']['address'])+bytes.fromhex('4e71'))
 m.ctlregs.update(control)
 c=CycleClock(m,fsys=264000000,accel='max',stalls=True,icache=True)
 s=types.SimpleNamespace(m=m,clock=c,main_img=stock)
 mem=LocalMemory(s,fill=40,writeback=32,beat=8,contention=True)
 parts=collections.defaultdict(collections.Counter)
 def owner(pc):
  return next((name for name,v in layout.items() if v['address']<=pc<v['address']+v['size']),'stock')
 original_block=c._on_block;uc.hook_del(c.hook)
 def block(uc,address,size,d):
  before=c.cycles;instructions=c.instructions
  original_block(uc,address,size,d)
  parts[owner(address)]['block_cycles']+=c.cycles-before
  parts[owner(address)]['instructions']+=c.instructions-instructions
 c.hook=uc.hook_add(UC_HOOK_BLOCK,block)
 original_data=mem.data
 def data_cost(address,size,write):
  before=c.cycles;result=original_data(address,size,write)
  parts[owner(uc.reg_read(UC_M68K_REG_PC))]['data_cycles']+=c.cycles-before
  return result
 mem.data=data_cost
 for repetition in range(3):
  uc.reg_write(UC_M68K_REG_SR,0x2700);uc.reg_write(UC_M68K_REG_A7,0x47fdff00);uc.reg_write(UC_M68K_REG_A3,event);uc.reg_write(UC_M68K_REG_D6,57)
  before=c.cycles;instructions=c.instructions;counts=dict(mem.counts)
  parts.clear()
  uc.emu_start(0x4009df9a,0x4009dfa8,count=100000)
  assert uc.reg_read(UC_M68K_REG_PC)==0x4009dfa8 and uc.reg_read(UC_M68K_REG_D6)==57<<16
  rows.append({'mode':mode,'repetition':repetition,'cache_state':'cold' if repetition==0 else 'self-warmed','cycles':c.cycles-before,'instructions':c.instructions-instructions,'memory_costs':{k:v-counts.get(k,0) for k,v in mem.counts.items() if k.endswith('_stall_cycles')},'helper_parts':{k:dict(v) for k,v in parts.items()}})
 assert c.decode_mismatches==0
out={'firmware_modified':False,'fixtures':'Isolated type/state/track/identity/ready-header/retained-record fixtures; snapshot cache-control registers, empty cache initially. No scheduler or DMA execution.','cases':rows}
pathlib.Path('outputs/Digitone-fresh-pitch-local-cost.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
