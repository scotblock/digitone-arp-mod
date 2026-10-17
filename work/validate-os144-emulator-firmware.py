from pathlib import Path
import sys,os,json,time,traceback,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,release
syx=Path('outputs/Digitone_OS1.44E01_SCALE_ARP_DIGIEMU_ONLY.syx').resolve()
root=Path('work/os144-emulator-build-engine').resolve();root.mkdir(exist_ok=True)
devices=Path('work/upstream/digiemu/devices').resolve()
class Paths(bs.FirmwarePaths):
 @property
 def syx(self):return str(syx)
paths=Paths(str(root),syx.name,str(devices))
rel=release.identify_release(str(syx),str(devices));release.write_device_overlay(rel,paths.overlay,str(devices))
os.environ.update(paths.env())
out={'emulator_only':True,'startup_overlay_injected':False,'progress':[],'failure':None};start=time.monotonic()
def progress(ev):
 out['progress'].append({'step':ev.step,'kind':ev.kind,'text':ev.text});persist();print(ev.step,ev.kind,ev.text,flush=True)
def persist():
 out['seconds']=time.monotonic()-start;Path('outputs/Digitone-OS1.44E01-emulator-validation.json').write_text(json.dumps(out,indent=2))
try:
 out['snapshot']=bs.first_run(paths,progress=progress,options={'ddr':0x08000000})
 from emu.session import Session
 from unicorn.m68k_const import *
 import struct,collections
 hits=collections.Counter();port=json.loads(Path('work/os144/helper-port.json').read_text());quantized=[];pending=[]
 def probes(s):
  for name in ['producer_capture','allocate_clear','before','caller_commit','pitch_hook','copy','first_copy']:
   s.at(port['layout'][name]['address'],lambda uc,pc,n,d,name=name:hits.update([name]))
  rows={x['raw_scale']:x['pitch_classes'] for x in json.loads(Path('outputs/Digitone-OS1.44-scale-map.json').read_text())['scales']}
  def q(uc,pc,n,d):
   sp=uc.reg_read(UC_M68K_REG_A7);note,word=struct.unpack('>II',uc.mem_read(sp+4,8));root=word&127;raw=((word>>7)&63)-1
   expected=min((p for p in range(128) if (p-root)%12 in rows[raw]),key=lambda p:(abs(p-note),p))
   pending.append({'input':note,'word':hex(word),'expected':expected})
  def output(uc,pc,n,d):
   if pending:
    item=pending.pop(0);item['fixed_pitch']=uc.reg_read(UC_M68K_REG_D6);item['actual']=item['fixed_pitch']>>16;quantized.append(item)
  s.at(port['layout']['quantize']['address'],q);s.at(0x4009e890,output)
 s=Session(out['snapshot'],syx=str(syx),ddr=0x08000000,on_machine=probes)
 try:
  uc=s.m.uc;out['header']=list(struct.unpack('>IIII',uc.mem_read(0x47be1004,16)))
  assert out['header']==[0x534c4332,2,0xb70,1]
  assert bytes(uc.mem_read(0x47be0000,2212))==Path('work/os144/packed-context-overlay.bin').read_bytes()
  for h in port['hooks']:
   op='4eb9' if h['name'] in ['before','copy'] else '4ef9'
   assert bytes(uc.mem_read(int(h['site'],16),6))==bytes.fromhex(op)+struct.pack('>I',h['helper'])
  # Same source pattern and root/scale fixture used by the tested continuous scenario.
  for track in range(4):
   uc.mem_write(0x40813531+track*0x3d0+0x3cb,bytes([61]));uc.mem_write(0x40813531+track*0x3d0+0x3ce,bytes([0]))
  out['scale_test_fixture']='Source pattern root61/raw0 before stopped selection; no event/context injection.'
  s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
  s.press(s.code('PTN'));s.run_ms(100);s.tap(s.code('2'),hold_ms=100,after_ms=100);s.release(s.code('PTN'));s.run_ms(300)
  s.tap(s.code('PLAY'),hold_ms=100,after_ms=1000)
  s.tap(s.code('STOP'),hold_ms=100,after_ms=200)
  out.update(halted=s.halted,helper_hits=dict(hits),audio_bytes=len(s.pcm),audio_sha256=hashlib.sha256(s.pcm).hexdigest())
  out['scale_outputs']=quantized
  assert s.halted is None and hits['allocate_clear']>0 and hits['pitch_hook']>0
  assert quantized and all(q['actual']==q['expected'] for q in quantized) and any(q['input']!=q['actual'] for q in quantized)
  out['passed']=True
 finally:s.close()
except BaseException:
 out['passed']=False;out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:persist()
