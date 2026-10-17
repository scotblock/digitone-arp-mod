from pathlib import Path
import sys,os,json,struct,traceback
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,longrun,midi
from emu.session import Session
from unicorn.m68k_const import *
baseline_build=longrun.build
def build_without_forced_unblock(*args,**kwargs):kwargs['unblock']=False;return baseline_build(*args,**kwargs)
longrun.build=build_without_forced_unblock
def rd(u,a):return int.from_bytes(u.mem_read(a,4),'big')
startup=json.loads(Path('outputs/Digitone-E04-PC-startup-producer-order-startup.json').read_text())
syx=Path('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx').resolve();out={'PC_only':True,'cases':[],'limits':['GUI checkpoint follows native cold startup via existing intro shortcuts, not a continuous physical run.','DIN bytes are paced through the existing emulator MidiIn source; hardware UART/DMA/cache/timing remain modeled.','Gate values and admission phase are not changed to permit input.','This tests settled input functionality, not the earliest possible concurrent input on every transport.']}
for c in startup['cases']:
 root=Path(c['ui_snapshot']).parents[2];paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env());s=None
 r={'image':c['image'],'events':[],'failure':None};out['cases'].append(r)
 try:
  def install(s):
   for base,length in [(0x47be0000,1784),(0x47be3000,474),(0x47be3400,304),(0x47be3600,182),(0x47fa0000,332),(0x47fa0300,280)]:s.m.install_isa_patches_scoped(bytes(s.m.uc.mem_read(base,length)),base)
   def observed(u,pc,n,d):r['events'].append({'pc':hex(pc),'phase':hex(rd(u,0x47be2840)),'READY':rd(u,0x47be1010),'current_task':hex(rd(u,0x429f2188)),'ms':s.now_ms()})
   for pc in [0x400025c8,0x400e842c,0x400eb2d2,0x400eb166,0x400eae5c,0x400eaf48,0x40100252]:s.at(pc,observed)
  s=Session(c['ui_snapshot'],syx=str(syx),ddr=0x08000000,on_machine=install)
  s.run_ms(100)
  channel=rd(s.m.uc,0x41368d2c)&15;r['receive_gate']=rd(s.m.uc,0x41368d64);r['note_gate']=rd(s.m.uc,0x41368d88);r['phase_before']=hex(rd(s.m.uc,0x47be2840))
  mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,)
  data=[0x90|channel,64,100]
  for i,b in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*0.00032,b)
  mi.received+=len(data);s.run_ms(300)
  r['delivered']=mi.delivered;r['raised']=mi.raised;r['producer_reached']=any(e['pc']=='0x400eae5c' for e in r['events']);r['published']=any(e['pc']=='0x40100252' for e in r['events']);r['halted']=s.halted
  assert mi.delivered==3 and s.halted is None
  assert r['published']==bool(r['receive_gate']&1),r
  r['passed']=True
 except Exception:r['failure']=traceback.format_exc();r['passed']=False
 finally:
  if s:s.close()
 print('SETTLED DIN',r['image'],r.get('published'),r['passed'],flush=True)
out['passed']=all(c['passed'] for c in out['cases']);Path('outputs/Digitone-E04-PC-startup-settled-MIDI-probes.json').write_text(json.dumps(out,indent=2))
if not out['passed']:raise SystemExit(1)
