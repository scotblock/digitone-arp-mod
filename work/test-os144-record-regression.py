from pathlib import Path
import sys,os,json,struct,hashlib,traceback
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,panelleds
from emu.session import Session
from unicorn.m68k_const import *
mode=sys.argv[1];stocksyx=Path('inputs/Digitone_and_Digitone_Keys_OS1.44.syx')
customsyx=Path('outputs/Digitone_OS1.44E01_SCALE_ARP_DIGIEMU_ONLY.syx').resolve()
custom=mode.startswith('custom') or mode=='fixed'
if mode=='fixed':customsyx=Path('outputs/Digitone_OS1.44E02_SCALE_ARP_DIGIEMU_ONLY.syx').resolve()
syx=customsyx if custom else stocksyx
root=Path('work/os144-emulator-E02-engine' if mode=='fixed' else 'work/os144-emulator-build-engine' if custom else 'work/os144-stock-engine').resolve()
class Paths(bs.FirmwarePaths):
 @property
 def syx(self):return str(syx)
paths=Paths(str(root),customsyx.name if custom else 'Digitone_and_Digitone_Keys_OS1.44.syx',str(Path('work/upstream/digiemu/devices').resolve()))
os.environ.update(paths.env());port=json.loads(Path('work/os144/helper-port.json').read_text())
r={'mode':mode,'input_events':[],'marks':[],'failure':None,'RAM_only_controls':[]}
def rd(uc,a):return struct.unpack('>I',uc.mem_read(a,4))[0]
def install(s):
 if mode=='custom-no-arp':
  for h in port['hooks']:
   s.m.uc.mem_write(int(h['site'],16),bytes.fromhex(h['stock_bytes']))
  r['RAM_only_controls'].append('Restore seven arp hooks after the custom startup')
 if mode=='stock-with-arp':
  uc=s.m.uc;s.m.ensure(0x47be0000);blob=Path('work/os144/packed-context-overlay.bin').read_bytes();uc.mem_write(0x47be0000,blob)
  uc.mem_write(0x47be1000,struct.pack('>I',0x47be1004-0x14100));uc.mem_write(0x47be1004,struct.pack('>IIII',0x534c4332,2,0xb70,1))
  for h in port['hooks']:
   op='4eb9' if h['name'] in ['before','copy'] else '4ef9'
   uc.mem_write(int(h['site'],16),bytes.fromhex(op)+struct.pack('>I',h['helper'])+bytes.fromhex('4e71')*((h['length']-6)//2))
  r['RAM_only_controls'].append('Install seven arp hooks in stock settled state')
 def key(uc,pc,n,d):
  p=uc.reg_read(UC_M68K_REG_A2);r['input_events'].append({'ms':s.now_ms(),'pc':hex(pc),'bytes':bytes(uc.mem_read(p,16)).hex()})
 if s.profile.ui_key_dispatch is not None:s.at(s.profile.ui_key_dispatch,key)
def mark(label):
 uc=s.m.uc;p=rd(uc,0x4138f214);selectors=bytes(uc.mem_read(0x419cf71c,18));slot=(selectors[38//4]>>(2*(38%4)))&3
 palette_index=bytes(uc.mem_read(0x4322ad43+(38+1)*4+slot,1))[0]
 color=rd(uc,0x40241e4c+palette_index*4) if palette_index<41 else None
 seeded=panelleds.seed(lambda a,n:bytes(uc.mem_read(a,n)),'1.44','Digitone')
 wire=bytes(s.ev.get('uart_out',b''));s.gui_led_state.feed(wire[s.uart_cursor:]);s.uart_cursor=len(wire)
 r['marks'].append({'label':label,'ms':s.now_ms(),'record_LED_slot':slot,'record_LED_palette':palette_index,'record_LED_RGB':hex(color) if color is not None else None,'pattern_hash':hashlib.sha256(bytes(uc.mem_read(p,4*0x3d0))).hexdigest(),'ui_frames':len(s.frames),'seeded_colors':seeded.colours()[38] if seeded else None})
 r['marks'][-1].update(gui_record_colour=s.gui_led_state.colours().get(38),wire_bytes=len(wire))
try:
 s=Session(paths.gui,syx=str(syx),ddr=0x08000000,on_machine=install)
 try:
  r['device_version']=s.device.firmware_for_sha256(hashlib.sha256(syx.read_bytes()).hexdigest()).version
  r['default_LED_seed_available']=panelleds.seed_table(r['device_version'],'Digitone') is not None
  s.gui_led_state=panelleds.seed(lambda a,n:bytes(s.m.uc.mem_read(a,n)),r['device_version'],'Digitone') or panelleds.new_state(r['device_version'],'Digitone');s.uart_cursor=0
  mark('initial');s.tap(s.code('T1'),hold_ms=100,after_ms=100);mark('track1')
  s.tap(s.code('RECORD'),hold_ms=100,after_ms=200);mark('RECORD on')
  s.tap(s.code('1'),hold_ms=100,after_ms=200);mark('step1 toggle')
  s.tap(s.code('RECORD'),hold_ms=100,after_ms=200);mark('RECORD off')
  r['halted']=s.halted;r['inputs']=s.inputs
 finally:s.close()
except BaseException:r['failure']=traceback.format_exc();print(r['failure'])
Path('outputs/Digitone-OS1.44-record-'+mode+'.json').write_text(json.dumps(r,indent=2));print(json.dumps(r['marks'],indent=2))
