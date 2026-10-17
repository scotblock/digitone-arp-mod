from pathlib import Path
import sys,os,time,json,hashlib,wave
root=Path('outputs/Digiemu-audio-fix').resolve()
sys.path[:0]=[str(root/'deps'),str(root/'emulator')]
from emu import bootstrap as bs
from emu.gui import Emulator
from emu.portable import disable_power_throttling
print("Power throttling off:",disable_power_throttling(),flush=True)
import numpy as np
mode=sys.argv[1];slug='dn1-1.44-'+('8e1d9c4e' if mode=='modified' else 'd4f200d0')
f=Path('work/live-audio-fix-check')/slug
p=bs.FirmwarePaths(str(f.resolve()),'Digitone_OS1.44.syx',str(root/'emulator/devices'))
os.environ.update(p.env())
r={'mode':mode,'packaged_source':str(root),'failure':None};e=None
try:
 e=Emulator(p.resume,syx=p.syx,realtime=True,save_on_exit=None);e.release_card=True;e.start()
 assert e.ready.wait(40),'load timeout'
 assert not e.error,e.error
 assert e.audio_live,'native live output unavailable'
 def tap(name):
  code=next(c for c,label in e.device.labels.items() if label.upper()==name)
  e.inbox.append(('press',code,0));time.sleep(.2);e.inbox.append(('release',code,0));time.sleep(.3)
 tap('STOP');e.audio_clear();tap('PLAY')
 start=time.monotonic()
 while time.monotonic()-start<20 and e.is_alive():time.sleep(.25)
 tap('STOP')
 pcm=e.audio_take();out=e._live_out
 r.update(audio_live=e.audio_live,windows_output_open=out is not None,submitted_blocks=out.played if out else 0,dropped_blocks=out.dropped if out else None,live_underruns=e.live_underruns,live_error=e._live_error,audio_error=e.audio_error,emulator_error=e.error,wall_seconds=time.monotonic()-start,recorded_seconds=len(pcm)/4/48000,stats=e.stats)
 e.stop_flag.set();e.join(30);r['clean_stop']=not e.is_alive() and e.flushed;r['error_after_stop']=e.error
 z=np.frombuffer(pcm,dtype='<i2').reshape(-1,2).astype(float)/32768;d=np.max(np.abs(np.diff(z,axis=0)),axis=1)
 r.update(pcm_sha256=hashlib.sha256(pcm).hexdigest(),peak=float(abs(z).max()),large_jumps=int((d>.02).sum()),largest_jump=float(d.max()))
 with wave.open(str(Path('outputs')/('Digiemu-audio-fix-live-'+mode+'.wav')),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(pcm)
 assert r['windows_output_open'] and r['submitted_blocks']>0,r
 assert r['clean_stop'] and not r['error_after_stop'],r
except BaseException:
 import traceback;r['failure']=traceback.format_exc();print(r['failure'],flush=True)
finally:
 if e and e.is_alive():e.stop_flag.set();e.join(10)
 Path('outputs/Digiemu-audio-fix-live-'+mode+'.json').write_text(json.dumps(r,indent=2,default=str));print(json.dumps(r,default=str),flush=True)
