from pathlib import Path
import sys,os,json,struct,traceback
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,longrun,panel
from emu.session import Session
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_A0,UC_M68K_REG_A7,UC_M68K_REG_D3
original=longrun.build
def build(*a,**k):k['unblock']=False;return original(*a,**k)
longrun.build=build
syx=Path('work/os144/E08-PC-path-candidate.syx').resolve();case=json.loads(Path('outputs/Digitone-E08-PC-startup-comparison.json').read_text())['cases'][0]
paths=bs.FirmwarePaths(str(Path(case['ui_snapshot']).parents[2]),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
cfg=json.loads(Path('outputs/Digitone-E08-PC-path-layout.json').read_text());payload=Path('work/os144/E08-PC-layout-payload.bin').read_bytes()
out={'PC_only':True,'steps':[],'writes':[]};phase='setup'
def rd(u,a):return int.from_bytes(u.mem_read(a,4),'big')
def install(s):
 for r in cfg['regions']:
  if r['base']>=0x47be0000:s.m.install_isa_patches_scoped(payload[r['base']-0x47be0000:r['base']-0x47be0000+r['bytes']],r['base'])
 out['offers']=[]
 def offer(u,pc,n,d):
  if phase in ['SYN2','arp_menu'] and len(out['offers'])<250:
   sp=u.reg_read(UC_M68K_REG_A7);view=u.reg_read(UC_M68K_REG_D3);obj=view;vt=rd(u,obj);out['offers'].append({'phase':phase,'method':hex(rd(u,vt+8)),'view':hex(view),'object':hex(obj),'vtable':hex(vt),'stack':bytes(u.mem_read(sp,24)).hex()})
 if s.profile.view_offer:s.at(s.profile.view_offer,offer)
s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x8000000,audio=False,on_machine=install)
try:
 s.run_ms(6500);s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
 s.press(s.code('MIDI'));s.tap(s.code('T1'),hold_ms=100,after_ms=100);s.release(s.code('MIDI'));s.run_ms(200)
 base=rd(s.m.uc,0x4138f214);out['pattern_pointer']=hex(base);out['source_pointer']=hex(rd(s.m.uc,0x4138f214))
 def write(u,access,a,n,v,d):
  if len(out['writes'])<4000:out['writes'].append({'phase':phase,'offset':hex(a-base),'size':n,'value':v,'pc':hex(u.reg_read(UC_M68K_REG_PC))})
 s.m.uc.hook_add(UC_HOOK_MEM_WRITE,write,begin=base,end=base+0x1611c)
 out['ui_writes']=[]
 def uiwrite(u,access,a,n,v,d):
  pc=u.reg_read(UC_M68K_REG_PC)
  if phase.endswith('_A') and 0x40020000<=pc<0x40080000 and not 0x4052bedc<=a<0x40553edc and len(out['ui_writes'])<2000:out['ui_writes'].append({'phase':phase,'address':hex(a),'size':n,'value':v,'pc':hex(pc)})
 s.m.uc.hook_add(UC_HOOK_MEM_WRITE,uiwrite,begin=0x40000000,end=0x47ffffff)
 def record(label):
  frame=panel.read(s.m,s.profile.fb_front);p=Path('outputs')/('E08-MIDI-controls-'+label+'.png');panel.write_png(frame,str(p),4)
  out['steps'].append({'label':label,'screen':str(p),'pattern':bytes(s.m.uc.mem_read(base,0x1200)).hex()});print(label,flush=True)
 for page in ['SYN1','SYN2','FLTR','AMP','LFO']:
  phase=page;s.tap(s.code(page),hold_ms=100,after_ms=200);record(page)
  if page in ['SYN1','FLTR']:
   s.press(s.code('FUNC'));s.tap(s.code('A'),hold_ms=100,after_ms=100);s.release(s.code('FUNC'));s.run_ms(100)
  phase=page+'_A';s.turn(s.encoder('A'),80,after_ms=400);record(phase)
 phase='arp_menu';s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('SYN1'),hold_ms=100,after_ms=100);s.release(s.code('FUNC'));s.run_ms(200);record(phase)
 out['halted']=s.halted;out['passed']=not s.halted
except Exception:out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:s.close();Path('outputs/Digitone-E08-MIDI-controls-trace.json').write_text(json.dumps(out,indent=2))
