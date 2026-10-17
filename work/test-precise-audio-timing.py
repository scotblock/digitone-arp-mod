import pathlib,json,struct
p=pathlib.Path('work/test-timestamped-DMA-native.py').read_text().split('c.left=100000;')[0]
p=p.replace('from timestamped_dma import TimestampedMemory as MemoryTiming','from precise_audio_dma import PreciseAudioMemory as MemoryTiming')
p=p.replace('c=CycleClock(m,icache=True);s=SimpleNamespace',"from emu.ssi import Ssi0Dma,MK1\nssi=Ssi0Dma(m,2500000,250000000,profile=MK1);ssi.enabled={52,54}\nc=CycleClock(m,icache=True);s=SimpleNamespace")
p=p.replace("'edma_sw_bank':bank}","'edma_sw_bank':bank,'ssi0_dma':ssi}")
exec(p)
from fractions import Fraction
from unicorn.m68k_const import UC_M68K_REG_PC
checks=[];captured=[];ssi.sink=lambda raw:captured.append(raw)
def check(name,ok):assert ok,name;checks.append(name)
def setup():
 c.cycles=0;t.bus.free=0;t.events.clear();t.active.clear();t.pending.clear();t.owner=None;t.next_audio=Fraction(100);t.irq_asserted_at=None;t.audio_records.clear();t.audio_timing.clear();captured.clear();ssi.int50_asserted=False;ssi.int50_delivered=False
 m.uc.mem_write(0xfc044000,(0xe406).to_bytes(4,'big'))
 for ch,src,dst,soff,doff,slast,dlast in [(54,0x40004000,0xfc0c8000,4,0,0xfffffff0,0),(52,0xfc0c8008,0x80001800,0,4,0,0xfffffff0)]:
  m.uc.mem_write(ssi._tcd(ch),struct.pack(edma_sw.TCD_FMT,src,0x202,soff,8,slast,dst,2,doff,dlast,2,6))
 m.uc.mem_write(0x40004000,b'abcdefghABCDEFGH')
def at(n):c.cycles=n;t.service_payload()
setup();at(99);check('no early audio request',t.audio_timing['frames_requested']==0 and not captured)
at(100);check('requests share the scheduled timestamp',t.active[54]['request_cycle']==100 and t.active[52]['request_cycle']==100)
at(115);check('completion IRQ absent before final payload beat',not ssi.int50_asserted)
at(116);check('IRQ asserted at final payload completion',ssi.int50_asserted and t.irq_asserted_at==116)
check('payload completion precedes next frame',t.audio_records[0]['completion']==116 and t.audio_timing['next_frame_deadline_misses']==0)
# Real interrupt controller mask and live IPL are respected.
m.uc.mem_write(0xfc04c06e,b'\x06');m.uc.mem_write(0xfc04c008,bytes(8));m.uc.mem_write(0x40000000+174*4,(0x40009000).to_bytes(4,'big'));m.uc.mem_write(0x40009000,bytes.fromhex('4e73'));m.uc.reg_write(UC_M68K_REG_PC,0x40002000);m.uc.reg_write(UC_M68K_REG_SR,0x2700)
t.deliver_irqs();check('IPL mask retains pending interrupt',not ssi.int50_delivered and t.irq_asserted_at==116)
m.uc.reg_write(UC_M68K_REG_SR,0x2000);m.uc.mem_write(0xfc04c008,(1<<14).to_bytes(4,'big'));t.deliver_irqs();check('interrupt controller mask retains completion request',not ssi.int50_delivered)
m.uc.mem_write(0xfc04c008,bytes(4));t.deliver_irqs();check('unmask delivers actual native vector',ssi.int50_delivered and m.uc.reg_read(UC_M68K_REG_PC)==0x40009000)
check('delivery recorded against completion timestamp',t.irq_records[-1]['assertion_cycle']==116)
setup();t.next_audio=Fraction(100,3);t.audio_period=Fraction(100,3);at(110)
check('late service catches all elapsed frame requests',t.audio_timing['frames_requested']==3)
check('fractional request phase does not drift',t.next_audio==Fraction(400,3))
check('deadline uses the actual next fractional arrival',t.audio_records[0]['deadline']==67)
check('late service preserves original arrival timestamps',t.audio_records[0]['request']==34 and t.audio_records[1]['request']==34)
setup();t.audio_period=Fraction(100);m.uc.mem_write(0xfc044000,(0xe446).to_bytes(4,'big'))
count=0x8000|(42<<9)|40;m.uc.mem_write(bank.channels[42].tcd,struct.pack(edma_sw.TCD_FMT,0x40001000,0x202,4,16,0,0x40003000,count,4,0,count,0));bank.channels[42]._transfer(m.uc,False);at(1400)
check('blocked audio creates explicit deadline misses',t.audio_timing['next_frame_deadline_misses']>0)
check('overlapping requests are reported as drops',t.arbitration['audio_requests_dropped_while_pending']>0)
pathlib.Path('outputs/Digitone-precise-audio-timing-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'timing':t.report()['audio_event_timing'],'firmware_modified':False},indent=2));print(json.dumps({'passed':len(checks),'checks':checks}))
