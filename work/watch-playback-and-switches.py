"""Exercise stock playback, panel notes, track and pattern selection. PC only."""
import pathlib,os
os.environ.pop('DIGITONE_CONTINUE_WATCH',None)
source=pathlib.Path('work/watch-continuous-reserved-RAM.py').read_text().split('# Bound a first compatibility run;')[0]
source=source.replace('outputs/Digitone-continuous-RAM-watch-results.json','outputs/Digitone-playback-switch-RAM-watch-results.json')
exec(compile(source,'playback-watch-prefix','exec'))
os.environ['DIGITONE_CONTINUE_WATCH']='1'
from emu.session import Session
import numpy as np
milestones=[];hits=collections.Counter();note_tracks=collections.Counter()
def installed(session):
 install(session.m,session.ev,'playback switches')
 for name,pc in [('producer_finalization',0x40093ef4),('acceptance',0x4009dd80),('coarse_pitch',0x4009df9a),('event_allocator',0x400f0626),('transport_start',profile.transport_start)]:
  if pc:
   session.at(pc,lambda uc,a,n,d,label=name:hits.update([label]))
 # Existing pitch-site ABI identifies the event in a3 and track at +8.
 from unicorn.m68k_const import UC_M68K_REG_A3
 def pitch_track(uc,a,n,d):
  event=uc.reg_read(UC_M68K_REG_A3)
  try:note_tracks.update([str(struct.unpack('>I',uc.mem_read(event+8,4))[0])])
  except Exception:note_tracks.update(['unreadable'])
 session.at(0x4009df9a,pitch_track)
session=None
def mark(label):
 data={'label':label,'ms':session.ms,'hits':dict(hits)}
 for key,a in [('transport_state',profile.transport_state),('current_pattern_backing',0x41342150),('DSP_status',profile.dsp_status)]:
  try:data[key]=hex(struct.unpack('>I',session.m.uc.mem_read(a,4))[0])
  except Exception:data[key]=None
 ptr=int(data['current_pattern_backing'] or '0',16)
 try:data['pattern_backing_sha256']=hashlib.sha256(bytes(session.m.uc.mem_read(ptr,4*0x3d0))).hexdigest()
 except Exception:data['pattern_backing_sha256']=None
 milestones.append(data);refresh();persist();print(label,round(session.ms,1),dict(hits),flush=True)
try:
 session=Session(paths.gui,syx=str(SYX),ddr=DDR,on_machine=installed)
 mark('before playback');session.tap(session.code('PLAY'),hold_ms=50,after_ms=1200);mark('playing')
 for track in ['T1','T2','T3','T4']:
  session.tap(session.code(track),hold_ms=40,after_ms=60)
  session.tap(session.code('1'),hold_ms=80,after_ms=120)
  mark('panel note '+track)
 for pattern in ['2','1']:
  session.press(session.code('PTN'));session.run_ms(40);session.tap(session.code(pattern),hold_ms=50,after_ms=40);session.release(session.code('PTN'));session.run_ms(3500)
  mark('after selecting pattern '+pattern)
 session.tap(session.code('STOP'),hold_ms=50,after_ms=300);mark('stopped')
 pcm=np.frombuffer(session.pcm,dtype='<i2').astype(np.float64)
 playback={'emulated_ms':session.ms,'frames':len(session.frames),'audio_bytes':len(session.pcm),'audio_nonzero_samples':int(np.count_nonzero(pcm)),'audio_rms':float(np.sqrt(np.mean(pcm*pcm))) if len(pcm) else 0,'halted':session.halted,'inputs':session.inputs,'milestones':milestones,'stock_instruction_hits':dict(hits),'pitch_event_tracks':dict(note_tracks)}
except BaseException as exc:
 failure={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()};print('STOP',failure['type'],failure['message'],flush=True)
finally:
 refresh();persist()
 if session:session.close()
 print('Saved',OUT,flush=True)
