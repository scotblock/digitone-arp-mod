import sys,pathlib,json,struct
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
from types import SimpleNamespace
from emu.harness import Machine
from emu.cftiming import CycleClock
from emu import edma_sw
from shared_memory_timing import MemoryTiming
from unicorn.m68k_const import *
m=Machine(ddr=128<<20)
for a in [0x40000000,0x80000000,0xfc000000]:m.ensure(a)
m.ctlregs.update({2:0xa50ce100,4:0x4007e020})
bank=edma_sw.SoftwareBank(m,native=False)
source=bytes(range(64));m.uc.mem_write(0x40001000,source)
tcd=struct.pack(edma_sw.TCD_FMT,0x40001000,0x0202,4,16,0,0x40003000,4,4,0,4,0x80)
m.uc.mem_write(0xfc045540,tcd)
raw=bytes.fromhex('13fc002afc04401e3039fc04555e02800000008067f24e71')
m.uc.mem_write(0x40002000,raw);m.install_isa_patches_scoped(raw,0x40002000);m.uc.reg_write(UC_M68K_REG_SR,0x2700);m.uc.reg_write(UC_M68K_REG_A7,0x8000fff0)
c=CycleClock(m,icache=True);s=SimpleNamespace(m=m,clock=c,ev={'edma_sw_bank':bank});t=MemoryTiming(s);t.prescan(raw,0x40002000)
c.left=100000;m.uc.emu_start(0x40002000,0x40002000+len(raw));c.left=None
r=t.report();r.update(cycles=c.cycles,ready_cycles=t.dma_ready[42],final_CSR=hex(bank.channels[42]._u16(edma_sw.CSR)))
assert r['counts']['DMA_completion_polls_deferred']>0,r
assert c.cycles>=t.dma_ready[42] and bank.channels[42]._pending is None,r
assert bytes(m.uc.mem_read(0x40003000,64))==source
assert bank.channels[42]._u16(edma_sw.CSR)&0xc0==0x80
r['result']='Native SSRT start with previous DONE bit: firmware polling waits until modeled bus completion'
pathlib.Path('outputs/Digitone-DMA-completion-native-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))

