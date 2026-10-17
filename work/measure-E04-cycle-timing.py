from pathlib import Path
import sys,os,json,struct,time,traceback,hashlib
sys.path[:0]=['work','work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,edma_sw,snapshot
from emu.session import Session
from emu.cftiming import deadline_report,measured_period
from unicorn.m68k_const import *
from phase_audio_dma import PhaseAudioMemory
mode=sys.argv[1];assert mode in ['prepare','stock','E04']
fill=int(sys.argv[2]) if len(sys.argv)>2 else 20
syx=Path('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx').resolve()
paths=bs.FirmwarePaths(str(Path('work/os144-E04-loader-startup-valid').resolve()),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
data=json.loads(Path('outputs/Digitone-OS1.44E04-startup-valid.json').read_text());port=json.loads(Path('work/os144/helper-port.json').read_text());prepared='work/os144/E04-cycle-prepared.snap'
if mode=='prepare':
 s=Session(data['snapshot'],syx=str(syx),ddr=0x08000000)
 try:
  for t in range(4):s.m.uc.mem_write(0x40813531+t*0x3d0+0x3cb,bytes([61]));s.m.uc.mem_write(0x40813531+t*0x3d0+0x3ce,bytes([0]))
  s.tap(s.code('STOP'),hold_ms=100,after_ms=100);s.press(s.code('PTN'));s.run_ms(100);s.tap(s.code('2'),hold_ms=100,after_ms=100);s.release(s.code('PTN'));s.run_ms(300)
  s.tap(s.code('PLAY'),hold_ms=100,after_ms=200)
  snapshot.save(s.m,prepared,s.st,components=s.ev['checkpoint_components'],manifest=s.ev['checkpoint_manifest'])
  print('prepared playing pattern2 from packaged E04 startup',flush=True)
 finally:s.close()
 raise SystemExit(0)
original_bank=edma_sw.install_bank
def python_bank(m,ev,**kw):kw['native']=False;return original_bank(m,ev,**kw)
edma_sw.install_bank=python_bank
out=Path('outputs/Digitone-OS1.44E04-cycle-'+mode+'-'+str(fill)+'.json');started=time.monotonic();r={'PC_only':True,'hardware_measured':False,'mode':mode,'fill_cycles_assumed':fill,'core_Hz_assumed':264000000,'bus_Hz_assumed':132000000,'duration_ms_requested':200,'snapshot':prepared,'pitches':[],'quantizer_calls':0,'failure':None}
def persist():r['wall_seconds']=time.monotonic()-started;out.write_text(json.dumps(r,indent=2))
def install(s):
 if mode=='stock':
  for h in port['hooks']:s.m.uc.mem_write(int(h['site'],16),bytes.fromhex(h['stock_bytes']))
  s.m.uc.mem_write(0x400ffed0,bytes.fromhex('2f032f0241f9419ebe70'))
 s.memtime=PhaseAudioMemory(s,fill=fill,writeback=max(16,fill*4//5),beat=max(4,fill//5),contention=True)
 s.at(0x4009e890,lambda uc,pc,n,d:r['pitches'].append({'cycles':s.clock.cycles,'value':uc.reg_read(UC_M68K_REG_D6)}))
 def quantize(uc,pc,n,d):r['quantizer_calls']+=1
 s.at(port['layout']['quantize']['address'],quantize)
try:
 s=Session(prepared,syx=str(syx),ddr=0x08000000,hle=False,timing={'fsys':264000000,'accel':'max','stalls':True,'icache':True,'miss_penalty':0},on_machine=install)
 try:
  for i in range(10):s.run_ms(20);r['completed_ms']=s.now_ms();persist();print(mode,fill,round(s.now_ms(),3),'ms',flush=True)
  r.update(clock=s.clock.report(),memory=s.memtime.report(),halted=s.halted,render=deadline_report(s.clock,191,176000),measured_render_period_cycles=measured_period(s.clock,191),audio_bytes=len(s.pcm),audio_sha256=hashlib.sha256(s.pcm).hexdigest())
  assert s.halted is None and r['clock']['decode_mismatches']==0 and r['render']['runs']>0
  r['execution_passed']=True
 finally:s.close()
except BaseException:r['execution_passed']=False;r['failure']=traceback.format_exc();print(r['failure'],flush=True)
finally:persist()
print('RESULT',mode,fill,r.get('execution_passed'),r.get('render'),flush=True)
