"""Controlled DIN ring input and actual saved completion-interrupt path."""
from pathlib import Path
exec(Path('work/probe-PC-startup-note-admission.py').read_text().split('\nout=')[0])
from emu import midi
out={'PC_only':True,'cases':[],'limits':['Three controlled non-clock bytes are written together through the emulator DIN feed API; physical UART/DMA timing and bus contention are not modeled here.','Vector 156 is offered only if the saved INTC configuration and saved SR permit it; no gate or SR is changed to authorize input.','Execution stops at first note producer entry before its note-pool writes. This tests reachability, not completed pre-initializer note behavior.','No continuous device startup or USB/panel transport claim.']}
for image in ['E04_default','E04_restored']:
 for pc in [0x4009d0d8,0x4008d31e,0x4008d3ec]:
  path=Path('work/startup-producer-order-'+image)/('producer-'+hex(pc)+'.snap');m=restored(path);m.install_exceptions();u=m.uc;initial_pc=u.reg_read(UC_M68K_REG_PC);initial_sr=u.reg_read(UC_M68K_REG_SR);channel=rd(u,0x41368d2c)&15;hits=[]
  def observed(u,at,n,d):
   hits.append(hex(at))
   if at==0x400eae5c:u.emu_stop()
  callback=rd(u,0x405285dc)
  for at in [rd(u,0x40000270),callback,0x400eb2d2,0x400eb166,0x400eae5c,0x400ff3ec,0x40100252]:u.hook_add(UC_HOOK_CODE,observed,begin=at,end=at)
  item={'image':image,'checkpoint':hex(pc),'initial_SR':hex(initial_sr),'phase':hex(rd(u,0x47be2840)),'READY':rd(u,0x47be1010),'receive_gate':rd(u,0x41368d64),'note_gate':rd(u,0x41368d88),'interrupt_level':interrupt_level(m,156),'DIN_callback':hex(callback),'failure':None}
  try:
   item['DIN_read_index_before']=rd(u,0x405285cc);item['DIN_DADDR_before']=rd(u,0xfc045490)
   midi.feed(m,bytes([0x90|channel,64,100]));item['DIN_DADDR_after_feed']=rd(u,0xfc045490);taken=midi._take(m,156);item['interrupt_taken']=taken
   if taken:u.emu_start(u.reg_read(UC_M68K_REG_PC),initial_pc,count=300000)
   item['end_pc']=hex(u.reg_read(UC_M68K_REG_PC));item['producer_reached']='0x400eae5c' in hits;item['returned_from_interrupt']=u.reg_read(UC_M68K_REG_PC)==initial_pc;item['DIN_read_index_after']=rd(u,0x405285cc)
   assert not taken or item['returned_from_interrupt'] or item['producer_reached'],item
  except Exception:
   item['failure']=traceback.format_exc();item['failure_PC']=hex(u.reg_read(UC_M68K_REG_PC));item['failure_bytes']=bytes(u.mem_read(u.reg_read(UC_M68K_REG_PC),12)).hex()
  item['native_sites']=hits;out['cases'].append(item);print('DIN',image,hex(pc),item.get('interrupt_taken'),item.get('producer_reached'),bool(item['failure']),flush=True)
out['passed']=all(c['failure'] is None for c in out['cases'])
Path('outputs/Digitone-E04-PC-startup-DIN-interrupt-probes.json').write_text(json.dumps(out,indent=2))
if not out['passed']:raise SystemExit(1)
