from pathlib import Path
import sys,os,json,struct,time,traceback
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,longrun,midi
from emu.session import Session
from unicorn.m68k_const import *
from unicorn import UC_HOOK_MEM_WRITE
original=longrun.build
def build(*args,**kwargs):kwargs['unblock']=False;return original(*args,**kwargs)
longrun.build=build
syx=Path('work/os144/E06-PC-candidate.syx').resolve();case=next(r for r in json.loads(Path('outputs/Digitone-E06-PC-startup-comparison.json').read_text())['cases'] if r['image']=='E06_restored');root=Path(case['ui_snapshot']).parents[2]
paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
cfg=json.loads(Path('outputs/Digitone-E06-PC-candidate-layout.json').read_text());payload=Path('work/os144/E06-PC-payload.bin').read_bytes();out={'PC_only':True,'firmware_unchanged':True,'events':[],'wire':[],'marks':[],'failure':None}
def rd(u,a):return int.from_bytes(u.mem_read(a,4),'big')
def install(s):
 for r in cfg['regions']:
  if r['base']>=0x47be0000:s.m.install_isa_patches_scoped(payload[r['base']-0x47be0000:r['base']-0x47be0000+r['bytes']],r['base'])
 def driver(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7);args=[rd(u,sp+i*4) for i in range(7)]
  event={'ms':s.now_ms(),'pc':hex(pc),'stack':[hex(x) for x in args],'registers':[hex(u.reg_read(UC_M68K_REG_D0+i)) for i in range(8)]}
  if pc==0x40002a3a and 0<args[1]<512:event['buffer']=list(u.mem_read(args[2],args[1]))
  out['events'].append(event)
 for pc in [0x40002a3a,0x40002b6e,0x40002c08]:s.at(pc,driver)
 mo=midi.MidiOut(lambda data:out['wire'].append({'ms':s.now_ms(),'bytes':list(data)}));mo.install(s.m);mo.attach(s.m,s.ips);s.sources=s.sources+(mo,);s.midi_mirror_observer=mo
s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x08000000,on_machine=install)
def mark(label):
 out['marks'].append({'label':label,'ms':s.now_ms(),'pc':hex(s.pc),'wire_bytes':s.midi_mirror_observer.sent});print(label,'ms',s.now_ms(),'wire',s.midi_mirror_observer.sent,flush=True)
try:
 for _ in range(10):
  s.run_ms(1000)
  if s.ev['dsplink'].booted and s.ev['dsplink'].renders>100:break
 mark('warm')
 s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
 s.press(s.code('MIDI'));s.tap(s.code('T1'),hold_ms=100,after_ms=100);s.release(s.code('MIDI'));s.run_ms(200)
 s.tap(s.code('SYN1'),hold_ms=100,after_ms=100)
 # Native UI: enable MIDI source channel with FUNC + encoder A, then channel 1.
 s.press(s.code('FUNC'));s.tap(s.code('A'),hold_ms=100,after_ms=100);s.release(s.code('FUNC'));s.run_ms(200)
 mark('MIDI track source channel enabled')
 s.tap(s.code('RECORD'),hold_ms=100,after_ms=100);s.tap(s.code('1'),hold_ms=100,after_ms=100);s.tap(s.code('RECORD'),hold_ms=100,after_ms=100);s.tap(s.code('PLAY'),hold_ms=100,after_ms=1000);mark('MIDI-track playback')
 s.tap(s.code('STOP'),hold_ms=100,after_ms=500);mark('stopped')
 out['halted']=s.halted
except Exception:out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
 s.close();Path('outputs/Digitone-synth-arp-MIDI-output-discovery.json').write_text(json.dumps(out,indent=2))
