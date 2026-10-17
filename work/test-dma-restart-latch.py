"""Boundary and payload checks for the shared arbiter's one-bit START latch."""
import pathlib,json,struct
exec(pathlib.Path('work/test-shared-dma-arbiter.py').read_text().split('reset();bank.channels[42]._transfer')[0])
checks=[]
def start(ch=42):bank.channels[ch]._transfer(m.uc,False)
def step(n):
 for _ in range(n):c.cycles+=1;t.service_payload()
def single():
 m.uc.mem_write(bank.channels[42].tcd,struct.pack(edma_sw.TCD_FMT,0x40001000,0x0202,4,4,0,0x40003000,1,4,0,1,0))
reset();start();start();start();drain()
check('two active requests coalesce with next self-link, no duplicated major',len(t.grants)==3 and bytes(m.uc.mem_read(0x40003000,12))==source[:12])
reset();start(47);start(42);start(42);start(42);drain()
check('pending requests coalesce before first grant',sum(g['channel']==42 for g in t.grants)==3)
reset();single();start();start();start();drain()
check('active final-minor requests retain one later activation',len(t.grants)==2 and bytes(m.uc.mem_read(0x40003000,8))==source[:8])
check('completion clears ACTIVE and START and sets DONE',bank.channels[42]._u16(edma_sw.CSR)&0xc1==0x80)
reset();start();step(8)
check('first minor publishes updated addresses and CITER',bank.channels[42]._u32(edma_sw.SADDR)==0x40001004 and edma_sw.iteration_count(bank.channels[42]._u16(edma_sw.CITER))==2)
# Guest rewrites active address/count fields; internal current-minor values
# take priority at writeback. Non-writeback BITER survives for final reload.
reset();start();step(1)
ch=bank.channels[42];ch._w32(edma_sw.SADDR,0x40001020);ch._w32(edma_sw.DADDR,0x40003100)
ch._w16(edma_sw.CITER,0xd406);ch._w16(edma_sw.BITER,0xd406);start();drain()
check('busy rewrites do not rewind active payload',bytes(m.uc.mem_read(0x40003000,12))==source[:12])
check('active address/count rewrites lose to minor writeback',ch._u32(edma_sw.SADDR)==0x4000100c and ch._u32(edma_sw.DADDR)==0x4000300c)
check('guest BITER survives and reloads on major completion',ch._u16(edma_sw.CITER)==0xd406)
# A request while HALTed does not capture a descriptor prematurely.
reset();m.uc.mem_write(0xfc044000,(0xe426).to_bytes(4,'big'));start()
bank.channels[42]._w32(edma_sw.SADDR,0x40001020)
m.uc.mem_write(0xfc044000,(0xe406).to_bytes(4,'big'));drain()
check('descriptor read follows actual arbitration grant',bytes(m.uc.mem_read(0x40003000,12))==source[32:44])
check('no owner or scheduled payload remains',not t.active and not t.pending and not t.events and t.owner is None)
# Actual guest SSRT stores exercise the bank hook, not just helper calls.
reset();single();ch=bank.channels[42]
ch._w32(edma_sw.NBYTES,64);m.uc.mem_write(0x40001000,bytes(range(128)))
raw=bytes.fromhex('13fc002afc04401e')*3
m.uc.mem_write(0x40002000,raw);m.install_isa_patches_scoped(raw,0x40002000)
m.uc.reg_write(UC_M68K_REG_SR,0x2700);m.uc.reg_write(UC_M68K_REG_A7,0x8000fff0)
c.left=1000;m.uc.emu_start(0x40002000,0x40002000+len(raw));c.left=None
drain()
check('three actual SSRT writes produce active plus one pending activation',len(t.grants)==2 and ch.transfers>=2)
check('native SSRT latch preserves both payloads',bytes(m.uc.mem_read(0x40003000,128))==bytes(range(128)))
out={'checks':checks,'passed':len(checks),'firmware_modified':False,'source':'https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf','sections':['19.4.11','19.5.1','19.6.4','19.6.6'],'scope':'SharedDmaMemory software channels, documented one-bit request and minor writeback rules; not physical bus calibration'}
pathlib.Path('outputs/Digitone-dma-restart-latch-checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
