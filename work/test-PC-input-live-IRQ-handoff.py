from pathlib import Path
exec(Path('work/test-PC-input-live-controls.py').read_text().split('\nout=')[0])
from emu import midi
m=restored('work/startup-producer-order-E04_restored/producer-0x4008d3ec.snap');m.install_exceptions();install_inputs(m);u=m.uc;m.ensure(0x47fdff00)
out={'PC_only':True,'phase_before':hex(rd(u,STATE)),'offered_under_publication':None}
def publish(u,access,a,n,v,d):
 if a==STATE and v==P['live']:
  assert out['offered_under_publication'] is None
  channel=rd(u,0x41368d2c)&15;midi.feed(m,bytes([0x90|channel,65,100]))
  out['offered_under_publication']={'IPL':(u.reg_read(UC_M68K_REG_SR)>>8)&7,'phase_before_write':hex(rd(u,STATE)),'DIN_interrupt_taken':midi._take(m,156)}
h=u.hook_add(UC_HOOK_MEM_WRITE,publish)
invoke(u,input_cfg['layout']['normal_completion']['address']+6,[],ret=0x4008d3fa,count=2000);u.hook_del(h)
assert rd(u,STATE)==P['live'] and u.reg_read(UC_M68K_REG_PC)==0x4008d3fa
assert out['offered_under_publication']=={'IPL':7,'phase_before_write':hex(P['initializing']),'DIN_interrupt_taken':False}
index_before=rd(u,0x405285cc);taken=midi._take(m,156);assert taken
u.emu_start(u.reg_read(UC_M68K_REG_PC),0x4008d3fa,count=300000)
assert u.reg_read(UC_M68K_REG_PC)==0x4008d3fa and rd(u,STATE)==P['live'] and rd(u,0x405285cc)==(index_before+3)&0x7fff
out.update(passed=True,interrupt_taken_after_mask_restore=taken,three_ring_bytes_consumed_after_publication=True,phase_after=hex(rd(u,STATE)),limits=['Controlled bytes and interrupt offers on a post-stock-return checkpoint, not measured physical arrival timing.','Native completion executes from its post-original-call entry; full call-to-return startup tested separately.','Deferred IRQ is explicitly offered again by the test; actual peripheral request latching/retry is not established.','ISR consumption tested here; successful full note publication after LIVE is tested in settled sessions.'])
Path('outputs/Digitone-E04-PC-input-live-IRQ-handoff.json').write_text(json.dumps(out,indent=2));print('PASS publication masks DIN IRQ; restored mask admits and consumes its three bytes')
