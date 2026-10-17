import pathlib,json,struct,os
p=pathlib.Path('work/test-FIFO-deadlines.py').read_text().split('checks=[]')[0].replace('from fifo_audio_dma import FifoAudioMemory as MemoryTiming','from phase_audio_dma import PhaseAudioMemory as MemoryTiming')
exec(p)
checks=[]
def check(n,v):assert v,n;checks.append(n)
def setup(period=Fraction(100),phase=Fraction(100),initial=14):
 c.cycles=0;t.bus.free=0;t.events.clear();t.active.clear();t.pending.clear();t.owner=None;t.next_word=phase;t.word_period=period;t.bit_period=period/32;t.audio_period=period*2;t.fifo_counts.clear();t.tx_level=initial;t.rx_level=0;t.min_tx=initial;t.max_rx=0;t.status_due=None;t.tx_flag=False;t.rx_flag=False;t.status_flags=0;t.error_flags=0;t.shift_started=None;t.shift_finished=0;ssi.int50_asserted=False
 m.uc.mem_write(0xfc044000,(0xe406).to_bytes(4,'big'))
 for ch,src,dst,soff,doff in [(54,0x80001a00,0xfc0c8000,4,0),(52,0xfc0c8008,0x80001800,0,4)]:m.uc.mem_write(ssi._tcd(ch),struct.pack(edma_sw.TCD_FMT,src,0x202,soff,8,0,dst,64,doff,0,64,6))
def at(n):c.cycles=n;t.service_payload()
setup();at(100);check('TX shift begins at word edge',t.shift_started==100 and t.tx_level==13 and t.shift_valid)
check('DMA assertion waits for first serial bit',54 not in t.active and t.status_due==Fraction(825,8))
at(103);check('fractional first-bit deadline rounds upward',54 not in t.active)
at(104);check('TX first-bit flag and request published',54 in t.active and t.status_flags&1)
check('frame-window diagnostic uses current request phase',t.active[54]['deadline']==304)
at(120);check('FIFO payload fills independently of shift register',t.tx_level==15 and t.shift_started==100)
check('TX flag deasserts when level no longer needs service',not t.status_flags&1)
at(200);check('previous shift completes at next word edge',t.shift_finished==1 and t.shift_started==200)
check('RX flag also waits for next first-bit completion',52 not in t.active)
at(204);check('RX two-word threshold asserts after first bit',52 in t.active and t.status_flags&4)
at(212);check('RX flag clears on payload drain',t.rx_level==0 and not t.status_flags&4)
# Guest ISR/SFCSR reads exercise actual memory hooks.
raw=bytes.fromhex('2039fc0c80142239fc0c802c4e71');m.uc.mem_write(0x40008000,raw);m.install_isa_patches_scoped(raw,0x40008000);before=t.status_reads
m.uc.emu_start(0x40008000,0x40008000+len(raw))
check('guest status and counter reads use phase model',t.status_reads==before+2 and m.uc.reg_read(UC_M68K_REG_D1)&0xff00==(t.rx_level<<12)|(t.tx_level<<8))
# Blocked traffic detects shift starvation and latched error status.
setup();t.tx_level=0;at(100);check('missing FIFO word invalidates active shift',not t.shift_valid and t.fifo_counts['TX_underflow']==1)
at(104);check('underrun flag appears at first-bit checkpoint',t.status_flags&0x100)
raw=bytes.fromhex('23fc00000100fc0c80144e71');m.uc.mem_write(0x40008000,raw);m.install_isa_patches_scoped(raw,0x40008000);m.uc.emu_start(0x40008000,0x40008000+len(raw));check('guest W1C clears only requested error',not t.error_flags&0x100 and not t.status_flags&0x100)
# DMA starvation exposes both FIFO overflow and delayed error publication.
setup();m.uc.mem_write(0xfc044000,(0xe446).to_bytes(4,'big'))
count=0x8000|(42<<9)|120
m.uc.mem_write(bank.channels[42].tcd,struct.pack(edma_sw.TCD_FMT,0x40001000,0x202,4,16,0,0x40003000,count,4,0,count,0))
bank.channels[42]._transfer(m.uc,False);at(2000)
check('starvation invalidates completed shift words',t.fifo_counts['invalid_shift_words_completed']>0)
check('starvation latches both underrun and overrun',t.error_flags&0x500==0x500)
at(2004);check('both error flags publish at serial status update',t.status_flags&0x500==0x500)
raw=bytes.fromhex('23fc00000100fc0c80144e71');m.uc.mem_write(0x40008000,raw);m.install_isa_patches_scoped(raw,0x40008000);m.uc.emu_start(0x40008000,0x40008000+len(raw))
check('selective guest W1C preserves receive overrun',t.error_flags&0x500==0x400)
for fsys in (250000000,264000000):
 for rate in (48000,44100):
  for mode in ('first-bit','word-edge'):
   t.phase_mode=mode
   for phase in (Fraction(1),Fraction(fsys,rate*64),Fraction(fsys,rate*2)):
    setup(Fraction(fsys,rate*2),phase);at(100000)
    check(f'{fsys}/{rate}/{mode}/{phase} no FIFO fault',not any(t.fifo_counts[k] for k in ('TX_underflow','TX_overflow','RX_empty_read','RX_overflow')))
    check(f'{fsys}/{rate}/{mode}/{phase} exact phase',t.next_word==phase+t.fifo_counts['word_ticks']*t.word_period)
pathlib.Path('outputs/Digitone-SSI1-serial-phase-checks.json').write_text(json.dumps(dict(passed=len(checks),checks=checks,scope='44.1 kHz is an alternative-source sensitivity, not a recovered board configuration',firmware_modified=False),indent=2));print('Passed',len(checks),'phase, flag and native MMIO checks')
