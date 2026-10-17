from pathlib import Path
import sys,os,json,struct,hashlib,time,traceback
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs
from emu.session import Session
from unicorn.m68k_const import UC_M68K_REG_D6
mode=sys.argv[1];assert mode in ['stock','repeat','fallback','no-pitch','only-pitch','timing-only','timing-allocation','replay-stock']
data=json.loads(Path('outputs/Digitone-OS1.44-fallback-final-bad_pointer.json').read_text());assert data['passed']
syx=Path('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx').resolve()
paths=bs.FirmwarePaths(str(Path('work/os144-fallback-final-bad_pointer').resolve()),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
port=json.loads(Path('work/os144/helper-port.json').read_text())
r={'PC_only':True,'mode':mode,'snapshot':data['snapshot'],'pitch':[],'DSP':[],'transfers':[],'events':[],'failure':None};start=time.monotonic()
def instrument(s):
 uc=s.m.uc
 for h in port['hooks']:
  keep=mode in ['fallback','replay-stock'] or mode=='no-pitch' and h['name']!='pitch_hook' or mode=='only-pitch' and h['name']=='pitch_hook'
  if not keep:uc.mem_write(int(h['site'],16),bytes.fromhex(h['stock_bytes']))
 if mode in ['timing-only','timing-allocation']:
  h=next(h for h in port['hooks'] if h['name']==('pitch_hook' if mode=='timing-only' else 'allocate_clear'));site=int(h['site'],16);address=0x47be0a00
  shim=bytes.fromhex('4e71')*32+bytes.fromhex(h['stock_bytes'])+bytes.fromhex('4ef9')+struct.pack('>I',site+h['length'])
  s.m.load(shim,address);uc.mem_write(site,bytes.fromhex('4ef9')+struct.pack('>I',address)+bytes.fromhex('4e71')*((h['length']-6)//2))
 def pitch(uc,pc,n,d):r['pitch'].append({'ms':s.now_ms(),'value':uc.reg_read(UC_M68K_REG_D6)})
 s.at(0x4009e890,pitch)
 link=s.ev['dsplink'];service=link._service_dsp
 replay=json.loads(Path('outputs/Digitone-OS1.44-fallback-audio-stock.json').read_text())['DSP'] if mode=='replay-stock' else None
 def render(d,elapsed,taken=False):
  if replay is not None and (taken or link.irqs):
   import ctypes
   raw=bytes.fromhex(replay[len(r['DSP'])]['packet']);ctypes.memmove(ctypes.addressof(link._buf),raw,len(raw))
   r['replay_fixture']='Stock parameter packet by render ordinal, written to input shared RAM before pending DSP service; PC-only causality control.'
  before=link.renders;packet=bytes(link._buf.raw[:0x3a0]);answer=service(d,elapsed,taken=taken)
  if link.renders>before:
   assert link.renders==before+1
   r['DSP'].append({'ms':s.now_ms(),'index':len(r['DSP']),'packet':packet.hex(),'packet_sha256':hashlib.sha256(packet).hexdigest(),'voices_sha256':hashlib.sha256(bytes(link._buf.raw[0x3a0:0x7a0])).hexdigest()})
   r['events'].append({'kind':'render','index':len(r['DSP'])-1,'word8':packet[8:12].hex(),'word32c':packet[0x32c:0x330].hex()})
  return answer
 link._service_dsp=render
 def transfer(uc,pc,n,d):
  packet=bytes(uc.mem_read(0x80001c00,0x3a0));item={'ms':s.now_ms(),'index':len(r['transfers']),'packet':packet.hex(),'packet_sha256':hashlib.sha256(packet).hexdigest()};r['transfers'].append(item)
  r['events'].append({'kind':'transfer','index':item['index'],'word8':packet[8:12].hex(),'word32c':packet[0x32c:0x330].hex()})
 s.at(0x4009e050,transfer)
try:
 s=Session(data['snapshot'],syx=str(syx),ddr=0x08000000,on_machine=instrument)
 try:
  uc=s.m.uc;assert int.from_bytes(uc.mem_read(0x47be1000,4),'big')==0
  for track in range(4):uc.mem_write(0x40813531+track*0x3d0+0x3cb,bytes([61]));uc.mem_write(0x40813531+track*0x3d0+0x3ce,bytes([0]))
  s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
  s.press(s.code('PTN'));s.run_ms(100);s.tap(s.code('2'),hold_ms=100,after_ms=100);s.release(s.code('PTN'));s.run_ms(300)
  s.tap(s.code('PLAY'),hold_ms=100,after_ms=1500);s.tap(s.code('STOP'),hold_ms=100,after_ms=200)
  r.update(audio_sha256=hashlib.sha256(s.pcm).hexdigest(),audio_bytes=len(s.pcm),halted=s.halted,inputs=s.inputs,pointer_after=hex(int.from_bytes(uc.mem_read(0x47be1000,4),'big')))
  Path('work/os144/fallback-audio-'+mode+'.pcm').write_bytes(s.pcm)
  assert s.halted is None and r['pointer_after']=='0x0' and r['DSP'] and r['transfers'];r['passed']=True
 finally:s.close()
except BaseException:r['passed']=False;r['failure']=traceback.format_exc();print(r['failure'],flush=True)
r['seconds']=time.monotonic()-start;Path('outputs/Digitone-OS1.44-fallback-audio-'+mode+'.json').write_text(json.dumps(r,indent=2));print('audio',mode,r.get('passed'),r.get('audio_sha256'),len(r['DSP']),len(r['transfers']),flush=True)
if not r.get('passed'):raise SystemExit(1)
