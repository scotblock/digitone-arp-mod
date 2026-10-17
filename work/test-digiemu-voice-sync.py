import sys,struct,threading,time,unittest
sys.path[:0]=['outputs/Digiemu-audio-fix/deps','outputs/Digiemu-audio-fix/emulator']
from emu.harness import Machine
from emu.edma_sw import SoftwareBank,TCD_BASE,TCD_FMT,EDMA_SSRT,CSR,CSR_DONE
from emu.dsplink import DspCpu,WINDOW
class SynchronizationTests(unittest.TestCase):
 def test_ssrt_waits_before_copy_and_done(self):
  m=Machine()
  for a in [TCD_BASE,WINDOW,0x80000000]:m.ensure(a)
  bank=SoftwareBank(m,native=False);ch=bank.channels[47]
  src=WINDOW+0x3a0;dst=0x80004110
  m.uc.mem_write(ch.tcd,struct.pack(TCD_FMT,src,0x202,4,0x400,0,dst,1,4,0,1,0))
  calls=[]
  def wait(channel,source,total):
   calls.append((channel,source,total));m.uc.mem_write(src,b'\x55'*0x400)
  m.dsp_voice_dma_wait=wait
  bank._on_ssrt(m.uc,None,EDMA_SSRT,1,47,None)
  self.assertEqual(calls,[(47,src,0x400)])
  self.assertEqual(bytes(m.uc.mem_read(dst,0x400)),b'\x55'*0x400)
  self.assertTrue(int.from_bytes(m.uc.mem_read(ch.tcd+CSR,2),'big')&CSR_DONE)
 def link(self):
  d=DspCpu.__new__(DspCpu);d.threaded=True;d.voice_dma_waits=0;d.error=None;d._job=threading.Condition();d._busy=False
  return d
 def test_only_voice_read_waits(self):
  d=self.link();d.wait_idle=lambda: self.fail('unrelated DMA waited')
  for args in [(47,WINDOW,0x3a0),(46,WINDOW+0x3a0,0x400),(47,WINDOW+0x3a0,4)]:d.wait_for_voice_dma(*args)
  d.threaded=False;d.wait_for_voice_dma(47,WINDOW+0x3a0,0x400)
 def test_wait_finishes_and_worker_error_surfaces(self):
  d=self.link();d._busy=True;started=threading.Event();finished=threading.Event()
  def reader():started.set();d.wait_for_voice_dma(47,WINDOW+0x3a0,0x400);finished.set()
  t=threading.Thread(target=reader);t.start();self.assertTrue(started.wait(1));self.assertFalse(finished.wait(.05))
  with d._job:d._busy=False;d._job.notify_all()
  self.assertTrue(finished.wait(1));t.join(1)
  d.error=ValueError('test render failure')
  with self.assertRaisesRegex(RuntimeError,'DSP voice render failed'):d.wait_for_voice_dma(47,WINDOW+0x3a0,0x400)
if __name__=='__main__':unittest.main()
