from pathlib import Path
import sys,json,hashlib,struct,collections,wave
prefix=Path('work/test-os144-record-regression.py').read_text().split('try:\n s=Session')[0]
prefix=prefix.replace('Digitone_OS1.44E01_SCALE_ARP_DIGIEMU_ONLY.syx','Digitone_OS1.44E02_SCALE_ARP_DIGIEMU_ONLY.syx').replace('work/os144-emulator-build-engine','work/os144-emulator-E02-engine')
prefix=prefix.replace('work/emulator-deps','outputs/Digiemu-audio-fix/deps').replace('work/upstream/digiemu','outputs/Digiemu-audio-fix/emulator')
exec(compile(prefix,'packaged-control-environment','exec'))
import numpy as np
scenario=os.environ.get('AUDIO_SCENARIO','simple');mode=sys.argv[1];out={'mode':mode,'scenario':scenario,'limits':['Settled first-boot snapshots, instruction-paced functional timing.','Identical native panel action order; realized times and initial scheduling phase may differ.'],'failure':None,'marks':[],'DSP':[],'pitch':[]};s=None
user_session=scenario.startswith('user')
if user_session:
 root=Path('work/user-session-audio/modified' if mode.startswith('custom') else 'work/user-session-audio/stock').resolve();syx=root/'Digitone_OS1.44.syx';paths=bs.FirmwarePaths(str(root),syx.name,str(Path('outputs/Digiemu-audio-fix/emulator/devices').resolve()));os.environ.update(paths.env())
native_install=install
def instrument(s):
 native_install(s);uc=s.m.uc
 if mode=='custom-allocator-only':
  for h in port['hooks']:
   if h['name']!='allocate_clear':uc.mem_write(int(h['site'],16),bytes.fromhex(h['stock_bytes']))
 if mode=='custom-no-pitch':
  for h in port['hooks']:
   if h['name']=='pitch_hook':uc.mem_write(int(h['site'],16),bytes.fromhex(h['stock_bytes']))
 if mode=='custom-all-stock':
  for h in port['hooks']:uc.mem_write(int(h['site'],16),bytes.fromhex(h['stock_bytes']))
  uc.mem_write(0x40000538,bytes.fromhex('4eb940001df4'));uc.mem_write(0x400ffed0,bytes.fromhex('2f032f0241f9419ebe70'))
  out['all_nine_hook_sites_restored_in_RAM']=True
 counts=collections.Counter();out['helper_hits']=counts
 for name in ['producer_capture','allocate_clear','before','after','caller_commit','pitch_hook','copy','first_copy']:
  s.at(port['layout'][name]['address'],lambda uc,pc,n,d,name=name:counts.update([name]))
 s.at(0x4009e890,lambda uc,pc,n,d:out['pitch'].append({'ms':s.now_ms(),'fixed_pitch':uc.reg_read(UC_M68K_REG_D6)}))
 link=s.ev['dsplink'];original=link._service_dsp
 def service(d,elapsed,taken=False):
  before=link.renders;packet=bytes(link._buf.raw[:0x3a0]);answer=original(d,elapsed,taken=taken)
  if link.renders>before:out['DSP'].append({'ms':s.now_ms(),'packet_sha256':hashlib.sha256(packet).hexdigest(),'voices_sha256':hashlib.sha256(bytes(link._buf.raw[0x3a0:0x7a0])).hexdigest()})
  return answer
 link._service_dsp=service
 if '-threaded' in scenario:
  link.start_thread();out['limits'].append('DSP executes on background thread like the GUI; host scheduling makes results nondeterministic.')
  if scenario.endswith('-barrier'):
   assert bytes(uc.mem_read(0x4009d1ac,6))==bytes.fromhex('13c0fc04401e')
   def wait_for_voices(uc,pc,n,d):
    out['DSP_read_barrier_calls']=out.get('DSP_read_barrier_calls',0)+1
    if link._busy:out['DSP_busy_at_voice_read']=out.get('DSP_busy_at_voice_read',0)+1
    link.wait_idle()
   s.at(0x4009d1ac,wait_for_voices)
   out['emulator_only_voice_read_barrier']=True
def mark(label):
 p=rd(s.m.uc,0x4138f214);out['marks'].append({'label':label,'ms':s.now_ms(),'pattern_hash':hashlib.sha256(bytes(s.m.uc.mem_read(p,0x16111))).hexdigest()})
 print(label,round(s.now_ms(),3),flush=True)
try:
 snap=Path(paths.snapshots)/'Digitone_OS1.44'/'resume.snap' if user_session else paths.gui
 s=Session(str(snap),syx=str(syx),ddr=None if user_session else 0x08000000,on_machine=instrument)
 mark('initial')
 s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
 if user_session:
  mark('saved user pattern retained')
 elif scenario.startswith('arp'):
  if scenario=='arp-scale':
   for t in range(4):s.m.uc.mem_write(0x40813531+t*0x3d0+0x3cb,bytes([61]));s.m.uc.mem_write(0x40813531+t*0x3d0+0x3ce,bytes([0]))
   out['scale_fixture']='Source pattern2 root61/raw0 before native stopped selection; no event/context injection.'
  s.press(s.code('PTN'));s.run_ms(100);s.tap(s.code('2'),hold_ms=100,after_ms=100);s.release(s.code('PTN'));s.run_ms(300);s.tap(s.code('T3'),hold_ms=100,after_ms=100)
  mark('existing factory pattern2 arp')
 else:
  s.tap(s.code('T1'),hold_ms=100,after_ms=100)
  s.tap(s.code('RECORD'),hold_ms=100,after_ms=100);s.tap(s.code('1'),hold_ms=100,after_ms=100);s.tap(s.code('RECORD'),hold_ms=100,after_ms=100)
  mark('matching step1 edit')
 s.tap(s.code('PLAY'),hold_ms=100,after_ms=int(os.environ.get('AUDIO_PLAY_MS','2200')));mark('played')
 s.tap(s.code('STOP'),hold_ms=100,after_ms=200);mark('stopped');out['halted']=s.halted;out['inputs']=s.inputs;out['production_voice_dma_waits']=s.ev['dsplink'].voice_dma_waits;out['DSP_error']=str(s.ev['dsplink'].error) if s.ev['dsplink'].error else None
 x=np.frombuffer(s.pcm,dtype='<i2').reshape(-1,2);z=x.astype(float)/32768;d=np.max(np.abs(np.diff(z,axis=0)),axis=1);idx=np.arange(1,len(x));means=[float(d[idx%32==k].mean()) for k in range(32)];phase=int(np.argmax(means));boundary=idx%32==phase
 out['audio']={'frames':len(x),'sha256':hashlib.sha256(s.pcm).hexdigest(),'peak':float(np.max(np.abs(z))),'largest_jump':float(d.max()),'jumps_over_0_02':int((d>.02).sum()),'jumps_over_0_02_on_32_boundary':int(((d>.02)&boundary).sum()),'boundary_phase':phase,'boundary_jump_ratio':float(means[phase]/d[~boundary].mean()),'channels_equal':bool(np.array_equal(x[:,0],x[:,1]))}
 with wave.open('outputs/Digitone-E02-audio-control-'+scenario+'-'+mode+'.wav','wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(s.pcm)
except BaseException:
 import traceback;out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
 if s:s.close()
 Path('outputs/Digitone-E02-audio-control-'+scenario+'-'+mode+'.json').write_text(json.dumps(out,indent=2));print(out.get('audio'),flush=True)
