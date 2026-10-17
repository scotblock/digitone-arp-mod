import pathlib
p=pathlib.Path('work/shared_dma_arbiter.py');s=p.read_text()
s=s.replace('  finally:self.servicing=False','   if self.owner is None:self.dispatch(self.clock.cycles)\n  finally:self.servicing=False')
s=s.replace("         count=e.iteration_count(citer_raw)","         if csr&32:raise RuntimeError('Software major channel links not implemented')\n         if bool(citer_raw&0x8000)!=bool(biter&0x8000):raise RuntimeError('CITER/BITER link mismatch')\n         count=e.iteration_count(citer_raw)")
s=s.replace("  data=bytearray()", "  if supplied and len(supplied)!=nbytes:raise RuntimeError('SSI RX supplied size mismatch')\n  data=bytearray()")
p.write_text(s)
p=pathlib.Path('work/test-shared-DMA-arbiter.py');s=p.read_text();a=s.index("out={'passed':")
s=s[:a]+'''# Source is fetched only when its granted read beat executes.
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
''' +s[a:];p.write_text(s)
