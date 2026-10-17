import sys,pathlib,json,struct
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
from types import SimpleNamespace
from emu.harness import Machine
from emu.cftiming import CycleClock,CycleStepper
from timestamped_dma import TimestampedMemory as MemoryTiming
from unicorn.m68k_const import *
m=Machine(ddr=128<<20);m.ensure(0x40000000);m.ensure(0x80000000)
# CACR, ACR0, dirty CPU store, physical CPUSHL DC, then global invalidations.
raw=bytes.fromhex('203ca40ce0004e7b0002203c4007e0204e7b000441f94000100020bc12345678f468203ca51ce1004e7b00024e71')
m.uc.mem_write(0x40002000,raw);m.install_isa_patches_scoped(raw,0x40002000);m.uc.reg_write(UC_M68K_REG_SR,0x2700);m.uc.reg_write(UC_M68K_REG_A7,0x8000fff0)
c=CycleClock(m,icache=True);s=SimpleNamespace(m=m,clock=c,ev={'edma_sw_bank':SimpleNamespace(_native=None,channels={})},sources=())
t=MemoryTiming(s);t.prescan(raw,0x40002000);c.left=100000;m.uc.emu_start(0x40002000,0x40002000+len(raw));c.left=None
print('decoded',[(hex(a),b.size,b.n) for a,b in c.blocks.items()]);print('raw',m.uc.mem_read(0x40002000,len(raw)).hex());print('counts',c.report());r=t.report();assert r['maintenance'].get('movec_2')==2,r;assert r['maintenance'].get('cpush_1')==1,r;assert r['counts'].get('cache_push_stall_cycles')==16,r
r['result']='Native machine-code control/CPUSHL hook integration passed';pathlib.Path('outputs/Digitone-timestamped-cache-maintenance-native-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))


