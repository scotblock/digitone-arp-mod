import pathlib,json,struct
p=pathlib.Path('work/test-timestamped-DMA-native.py').read_text().split('c.left=100000;')[0]
p=p.replace('from timestamped_dma import TimestampedMemory as MemoryTiming','from fifo_audio_dma import FifoAudioMemory as MemoryTiming')
p=p.replace('c=CycleClock(m,icache=True);s=SimpleNamespace',"from emu.ssi import Ssi0Dma,MK1\nssi=Ssi0Dma(m,48000,250000000,profile=MK1);ssi.enabled={52,54}\nfor i,v in {0x10:0x37,0x18:0x500000,0x1c:0xe8,0x20:0x488,0x24:0x16101,0x2c:0x22}.items():m.uc.mem_write(0xfc0c8000+i,v.to_bytes(4,'big'))\nc=CycleClock(m,icache=True);s=SimpleNamespace")
p=p.replace("'edma_sw_bank':bank}","'edma_sw_bank':bank,'ssi0_dma':ssi}")
exec(p)
from fractions import Fraction
checks=[]
def check(n,v):assert v,n;checks.append(n)
def setup():
 c.cycles=0;t.bus.free=0;t.events.clear();t.active.clear();t.pending.clear();t.owner=None;t.next_word=Fraction(100);t.word_period=Fraction(100);t.fifo_counts.clear();t.tx_level=14;t.rx_level=0;t.min_tx=14;t.max_rx=0;ssi.int50_asserted=False
 m.uc.mem_write(0xfc044000,(0xe406).to_bytes(4,'big'))
 for ch,src,dst,soff,doff in [(54,0x80001a00,0xfc0c8000,4,0),(52,0xfc0c8008,0x80001800,0,4)]:
  m.uc.mem_write(ssi._tcd(ch),struct.pack(edma_sw.TCD_FMT,src,0x202,soff,8,0,dst,64,doff,0,64,6))
def at(n):c.cycles=n;t.service_payload()
setup();at(99);check('no early serial word',t.tx_level==14 and not t.active)
at(100);check('TX request at two empty slots',t.tx_level==13 and 54 in t.active)
check('RX requires two words',t.rx_level==1 and 52 not in t.active)
at(112);check('first final FIFO write arrives before second',t.tx_level==14)
at(116);check('two-word minor fills FIFO exactly',t.tx_level==15 and 54 not in t.active)
at(200);check('second RX word triggers request',t.rx_level==2 and 52 in t.active)
at(208);check('actual RX payload reads drain FIFO',t.rx_level==0)
at(10000);check('elapsed serial words are retained',t.fifo_counts['word_ticks']==100)
check('steady servicing avoids overflow and underflow',not any(t.fifo_counts[x] for x in ('TX_underflow','TX_overflow','RX_overflow','RX_empty_read')))
check('FIFO request is level held rather than dropped',t.arbitration['audio_requests_dropped_while_pending']==0)
# Block arbiter for more than FIFO buffering capacity.
setup();m.uc.mem_write(0xfc044000,(0xe446).to_bytes(4,'big'))
count=0x8000|(42<<9)|120;m.uc.mem_write(bank.channels[42].tcd,struct.pack(edma_sw.TCD_FMT,0x40001000,0x202,4,16,0,0x40003000,count,4,0,count,0));bank.channels[42]._transfer(m.uc,False);at(2000)
check('blocked TX reports physical occupancy underrun',t.fifo_counts['TX_underflow']>0)
check('blocked RX reports FIFO overflow',t.fifo_counts['RX_overflow']>0)
check('pending level requests are not counted as drops',t.arbitration['audio_requests_dropped_while_pending']==0)
check('FIFO maximum stays bounded',t.tx_level<=15 and t.rx_level<=15)
# Exact boundary: consume has priority over a refill at the same timestamp.
setup();t.tx_level=0;at(100);check('empty FIFO at serial tick is an underrun',t.fifo_counts['TX_underflow']==1)
setup();t.word_period=Fraction(100,3);t.next_word=Fraction(100,3);at(110)
check('fractional word phase has no accumulation drift',t.next_word==Fraction(400,3) and t.fifo_counts['word_ticks']==3)
# Exercise plausible resumed FIFO occupancies and sub-word phases.
for initial in (1,2,7,13,14,15):
 for phase in (Fraction(1),Fraction(100,3),Fraction(100)):
  setup();t.tx_level=initial;t.next_word=phase
  t.request_levels(0);at(10000)
  check(f'occupancy {initial} phase {phase} stays within capacity',not any(t.fifo_counts[x] for x in ('TX_underflow','TX_overflow','RX_overflow','RX_empty_read')))
pathlib.Path('outputs/Digitone-FIFO-deadline-checks.json').write_text(json.dumps(dict(passed=len(checks),checks=checks,firmware_modified=False),indent=2));print(checks)
