import pathlib,sys,collections,json
sys.path.insert(0,str(pathlib.Path('work/emulator-deps').resolve()))
from shared_memory_timing import Cache,SerialBus,MemoryTiming
from types import SimpleNamespace
checks=[]
def check(name,value):
 assert value,name
 checks.append(name)
c=Cache();address=0x40000000
check('first fill',c.access(address)==(True,False));check('dirty hit',c.access(address,True)==(False,False))
check('physical push retains line',c.maintain(address,True,False,True)==1 and address//16 in c.rows[0] and not c.dirty)
c.access(address,True);check('physical invalidation drops without writeback',c.maintain(address,True,True,False)==0 and not c.dirty and all(x is None for x in c.rows[0]))
for way in range(4):c.access(address+way*2048,True)
check('set full dirty eviction',c.access(address+4*2048)==(True,True))
check('index/way selects one',c.selected(2,False)==[(0,2)])
b=SerialBus();check('DMA reservation future',b.reserve(100,64,'dma')==164);check('CPU contends',b.reserve(120,20,'cpu')==184)
m=MemoryTiming.__new__(MemoryTiming);m.clock=SimpleNamespace(cycles=120,left=100);m.counts=collections.Counter();m.bus=b;m.contention=True
m.cpu_bus(16,'data');check('stall reaches both timer budget fields',m.clock.cycles==200 and m.clock.left==20)
m.d=Cache();m.i=Cache();m.regs={2:0xa40ce000};m.writeback=16;m.maintenance=collections.Counter();m.samples=[]
m.d.access(address,True);m.push(1,address,0);check('physical cpush writes and invalidates',m.clock.cycles==216 and not m.d.dirty and all(x is None for x in m.d.rows[0]))
m.d.access(address,True);m.regs[2]|=0x100000;m.push(1,address,0);check('IVO invalidates without writeback',m.clock.cycles==216 and not m.d.dirty)
m.control_write(2,0xa50ce100,0);check('global invalidate requests self-clear',not m.regs[2]&0x01000100)
m.d=Cache();m.hazards=collections.Counter();m.beat=4;m.d.access(address,True)
check('DMA alias observes dirty cached region',m.dma_span(0x48000000,16)==16 and m.hazards['DMA_read_dirty_lines']==1)
result={'passed':len(checks),'checks':checks,'scope':'Independent cache transitions, serialization, budget accounting and alias observations; no silicon timing claim'}
pathlib.Path('outputs/Digitone-shared-memory-model-checks.json').write_text(json.dumps(result,indent=2));print(result)
