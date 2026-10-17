from pathlib import Path
import sys,os,json,struct,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs
from emu.session import Session
from unicorn.m68k_const import UC_M68K_REG_D6
syx=Path('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx').resolve()
port=json.loads(Path('work/os144/helper-port.json').read_text())
r={'PC_only':True,'scope':'Restore stock hook-site bytes in an independent replay of each fallback UI snapshot; compare identical panel input and source-pattern fixture','cases':[]}
for mode in ['bad_pointer','bad_magic']:
 data=json.loads(Path('outputs/Digitone-OS1.44-fallback-continuous-'+mode+'.json').read_text());assert data['passed']
 paths=bs.FirmwarePaths(str(Path('work/os144-fallback-prepared-'+mode).resolve()),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
 def install(s):
  for h in port['hooks']:s.m.uc.mem_write(int(h['site'],16),bytes.fromhex(h['stock_bytes']))
  stock=Path('work/os144/section-3.bin').read_bytes();s.m.uc.mem_write(0x400ffed0,stock[0xffad0:0xffad0+10])
 s=Session(data['snapshot'],syx=str(syx),ddr=0x08000000,on_machine=install)
 try:
  pitches=[];uc=s.m.uc
  for track in range(4):
   uc.mem_write(0x40813531+track*0x3d0+0x3cb,bytes([61]));uc.mem_write(0x40813531+track*0x3d0+0x3ce,bytes([0]))
  s.at(0x4009e890,lambda uc,pc,n,d:pitches.append(uc.reg_read(UC_M68K_REG_D6)))
  s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
  s.press(s.code('PTN'));s.run_ms(100);s.tap(s.code('2'),hold_ms=100,after_ms=100);s.release(s.code('PTN'));s.run_ms(300)
  s.tap(s.code('PLAY'),hold_ms=100,after_ms=1500);s.tap(s.code('STOP'),hold_ms=100,after_ms=200)
  item={'mode':mode,'pitches_match_stock_sites':pitches==data['pitches'],'stock_pitches':pitches,'fallback_pitches':data['pitches'],'stock_audio_sha256':hashlib.sha256(s.pcm).hexdigest(),'fallback_audio_sha256':data['audio_sha256'],'audio_matches':hashlib.sha256(s.pcm).hexdigest()==data['audio_sha256'],'halted':s.halted}
  r['cases'].append(item);assert s.halted is None and pitches and item['pitches_match_stock_sites']
 finally:s.close()
r['passed']=True;Path('outputs/Digitone-OS1.44-fallback-stock-playback-comparison.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
