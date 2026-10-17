import pathlib,json,struct
prefix=pathlib.Path('work/test-timestamped-DMA-native.py').read_text().split('c.left=100000;')[0]
prefix=prefix.replace('from timestamped_dma import TimestampedMemory as MemoryTiming','from shared_dma_arbiter import SharedDmaMemory as MemoryTiming')
exec(prefix)
from emu.ssi import Ssi0Dma,MK1
ssi=Ssi0Dma(m,48000,250000000,profile=MK1);ssi.enabled={52,54};ssi.sink=lambda raw:captured.append(raw);captured=[]
t.ssi=ssi
checks=[]
def check(name,condition):assert condition,name;checks.append(name)
def desc(ch,count=3):
 n=0x8000|(ch<<9)|count;m.uc.mem_write(bank.channels[ch].tcd,struct.pack(edma_sw.TCD_FMT,0x40001000,0x0202,4,4,0,0x40003000+(ch-42)*64,n,4,0,n,0))
def audio():
 m.uc.mem_write(ssi._tcd(54),struct.pack(edma_sw.TCD_FMT,0x40004000,0x0202,4,8,0xfffffff0,0xfc0c8000,2,0,0,2,6));m.uc.mem_write(0x40004000,b'abcdefghABCDEFGH')
def reset(clm=False):
 c.cycles=0;t.bus.free=0;t.events.clear();t.active.clear();t.pending.clear();t.owner=None;t.grants.clear();t.payload_samples.clear();t.last_channel={g:0 for g in range(4)}
 m.uc.mem_write(0xfc044000,(0xe406|(64 if clm else 0)).to_bytes(4,'big'));desc(42);desc(47);audio();captured.clear()
def drain():
 for cycle in range(c.cycles+1,c.cycles+401):c.cycles=cycle;t.service_payload()
reset();bank.channels[42]._transfer(m.uc,False);bank.channels[47]._transfer(m.uc,False)
check('only one software channel ACTIVE',bank.channels[42]._u16(edma_sw.CSR)&64 and not bank.channels[47]._u16(edma_sw.CSR)&64)
drain();order=[x['channel'] for x in t.grants];check('same-group self-links rotate',order==[42,47,42,47,42,47]);check('final minor does not self-link again',len(order)==6);check('all software payload correct',bytes(m.uc.mem_read(0x40003000,12))==source[:12] and bytes(m.uc.mem_read(0x40003140,12))==source[:12])
reset();bank.channels[42]._transfer(m.uc,False);t.request_ssi(54,True);check('audio waits for active software minor',t.owner==42 and 54 in t.pending);drain();order=[x['channel'] for x in t.grants];check('higher group audio wins at boundary',order==[42,54,42,42]);check('audio captures actual timed source',captured==[b'abcdefgh']);check('audio half interrupt only after minor complete',ssi.int50_asserted)
reset(True);bank.channels[42]._transfer(m.uc,False);t.request_ssi(54,True);drain();check('CLM self-link bypasses pending audio until final minor', [x['channel'] for x in t.grants]==[42,42,42,54])
reset();t.request_ssi(54,True);drain();t.request_ssi(54,True);drain();check('audio major completion reloads CITER',ssi._u16(54,edma_sw.CITER)==2);check('audio major wraps source',ssi._u32(54,edma_sw.SADDR)==0x40004000)
check('controller and queues drain',not t.events and not t.pending and t.owner is None)
# Source is fetched only when its granted read beat executes.
reset();bank.channels[42]._transfer(m.uc,False);t.request_ssi(54,True)
check('queued audio is not ACTIVE',not ssi._u16(54,edma_sw.CSR)&64)
m.uc.mem_write(0x40004000,b'12345678');drain();check('queued audio reads late source value',captured==[b'12345678'])
# Scatter/gather retires into the same controller before the next descriptor.
reset();first=struct.pack(edma_sw.TCD_FMT,0x40001000,0x0202,4,4,0,0x40003000,1,4,0x40006000,1,16)
second=struct.pack(edma_sw.TCD_FMT,0x40001004,0x0202,4,4,0,0x40003004,1,4,0,1,0)
m.uc.mem_write(bank.channels[42].tcd,first);m.uc.mem_write(0x40006000,second);bank.channels[42]._transfer(m.uc,False);t.request_ssi(54,True);drain()
check('scatter transition re-arbitrates against audio',[x['channel'] for x in t.grants]==[42,54,42])
check('scatter payload and final DONE correct',bytes(m.uc.mem_read(0x40003000,8))==source[:8] and bank.channels[42]._u16(edma_sw.CSR)&128)
# Halt leaves requests queued and clearing it allows forward progress.
reset();m.uc.mem_write(0xfc044000,(0xe426).to_bytes(4,'big'));bank.channels[42]._transfer(m.uc,False)
check('HALT queues without an owner',t.owner is None and 42 in t.pending)
m.uc.mem_write(0xfc044000,(0xe406).to_bytes(4,'big'));drain();check('HALT clear resumes queued work',not t.pending and not t.active)
# Invalid fixed group settings must not silently run.
reset();m.uc.mem_write(0xfc044000,(6).to_bytes(4,'big'))
try:bank.channels[42]._transfer(m.uc,False)
except RuntimeError as err:check('invalid fixed group configuration rejected','Duplicate fixed group priorities' in str(err))
else:raise AssertionError('Invalid configuration accepted')
reset();check('no audio requests dropped in controlled workloads',t.arbitration['audio_requests_dropped_while_pending']==0)
out={'passed':len(checks),'checks':checks,'firmware_modified':False,'report':t.report()};pathlib.Path('outputs/Digitone-shared-DMA-arbiter-checks.json').write_text(json.dumps(out,indent=2));print(json.dumps({'passed':len(checks),'checks':checks}))




