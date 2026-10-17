from pathlib import Path
import sys,os,json,struct,traceback
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,longrun,panel
from emu.session import Session
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_A0,UC_M68K_REG_A7,UC_M68K_REG_D3,UC_M68K_REG_D0
original=longrun.build
def build(*a,**k):k['unblock']=False;return original(*a,**k)
longrun.build=build
syx=Path('work/os144/E08D-PC-path-candidate.syx').resolve();case=json.loads(Path('outputs/Digitone-E08D-PC-startup-comparison.json').read_text())['cases'][0]
paths=bs.FirmwarePaths(str(Path(case['ui_snapshot']).parents[2]),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
cfg=json.loads(Path('outputs/Digitone-E08D-PC-path-layout.json').read_text());payload=Path('work/os144/E08D-PC-layout-payload.bin').read_bytes()
out={'PC_only':True,'steps':[],'writes':[],'encoder_events':[],'sound_lookups':[],'MIDI_handles':[]};phase='setup'
def rd(u,a):return int.from_bytes(u.mem_read(a,4),'big')
def install(s):
 for r in cfg['regions']:
  if r['base']>=0x47be0000:s.m.install_isa_patches_scoped(payload[r['base']-0x47be0000:r['base']-0x47be0000+r['bytes']],r['base'])

 from unicorn import UC_HOOK_CODE
 controls=json.loads(Path('work/os144/E08-PC-M1-controls-layout.json').read_text())

 out['helpers_host_loaded']=False;out['hooks_host_patched']=False;out['M1_initializer_host_called']=False
 for region in cfg['regions']:
  if region['base']<0x47be0000:continue
  expected=payload[region['base']-0x47be0000:region['base']-0x47be0000+region['bytes']]
  assert bytes(s.m.uc.mem_read(region['base'],region['bytes']))==expected,region['name']
 for hook in cfg['hooks']:
  assert bytes(s.m.uc.mem_read(hook['site'],hook['length'])).hex()==hook['replacement'],hook
 def encoder(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7);e=rd(u,sp+8)
  out['encoder_events'].append({'phase':phase,'id':rd(u,e+12),'delta':rd(u,e+16),'event':bytes(u.mem_read(e,24)).hex()})
 s.at(0x47be6300,encoder)
 out['open_events']=[]
 def opened(u,pc,n,d):out['open_events'].append({'phase':phase,'a4':hex(u.reg_read(UC_M68K_REG_A0+4))})
 s.at(0x47be5f00,opened)
 out['selection_results']=[]
 def selected(u,pc,n,d):
  if phase!='setup' and len(out['selection_results'])<80:out['selection_results'].append({'phase':phase,'value':u.reg_read(UC_M68K_REG_D0)})
 sel=next(r for r in controls['regions'] if r['name']=='selected_track');s.at(sel['base']+sel['bytes']-2,selected)
 def sound(u,pc,n,d):
  if phase!='setup':out['sound_lookups'].append({'phase':phase})
 s.at(0x4001dcf2,sound)
 def midi_handle(u,pc,n,d):
  h=u.reg_read(UC_M68K_REG_D0);out['MIDI_handles'].append({'phase':phase,'handle':h,'data':rd(u,h+16)})
 s.at(0x4001dd42,midi_handle)
 out['draw_calls']=[];out['codec_calls']=[]
 def draw_call(u,pc,n,d):
  if phase.startswith('M1') or phase.startswith('encoder_'):
   sp=u.reg_read(UC_M68K_REG_A7);args=[rd(u,sp+i*4) for i in range(8)]
   if 0x47be5e00<=args[6]<0x47be6e00 and len(out['draw_calls'])<20:out['draw_calls'].append({'phase':phase,'args':[hex(v) for v in args],'format':bytes(u.mem_read(args[6],40)).split(b'\0')[0].decode('ascii','replace')})
 s.at(0x400de120,draw_call)
 def codec_call(u,pc,n,d):
  if phase!='setup' and len(out['codec_calls'])<80:
   sp=u.reg_read(UC_M68K_REG_A7);out['codec_calls'].append({'phase':phase,'pc':hex(pc),'args':[hex(rd(u,sp+i*4)) for i in range(4)]})
 for pc in [0x47be5a00,0x47be5b80,0x4001f09e,0x4014eff8]:s.at(pc,codec_call)

 out['ownership_writes']=[]
 def ownership_write(u,access,a,n,value,d):
  out['ownership_writes'].append({'phase':phase,'address':hex(a),'value':hex(value),'writer':hex(u.reg_read(UC_M68K_REG_PC))})
 s.m.uc.hook_add(UC_HOOK_MEM_WRITE,ownership_write,begin=cfg['state']+336,end=cfg['state']+343)
 out['offers']=[]

 def offer(u,pc,n,d):
  if phase in ['SYN2','arp_menu'] and len(out['offers'])<250:
   sp=u.reg_read(UC_M68K_REG_A7);view=u.reg_read(UC_M68K_REG_D3);obj=view;vt=rd(u,obj);out['offers'].append({'phase':phase,'method':hex(rd(u,vt+8)),'view':hex(view),'object':hex(obj),'vtable':hex(vt),'stack':bytes(u.mem_read(sp,24)).hex()})
 if s.profile.view_offer:s.at(s.profile.view_offer,offer)
warm=Path('work/os144/E08D-controls-warm.snap')
# fresh packaged startup is required
s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=install)
try:
 from emu.dtim import Dtims
 if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):
  extra_timer=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False);extra_timer.now=s.pits.now;s.pits.sources=s.pits.sources+(extra_timer,)
 if True:
  s.run_ms(6500)
  from emu.snapshot import save
  components={**s.ev['checkpoint_components'],'timers':s.pits};save(s.m,str(warm),components=components,manifest=s.ev.get('checkpoint_manifest'))
 else:s.run_ms(200)
 s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
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
  frame=s.frames[-1][1] if s.frames else panel.read(s.m,s.profile.fb_back);p=Path('outputs')/('E08D-packaged-project-controls-'+label+'.png');panel.write_png(frame,str(p),4)
  out['steps'].append({'owner':hex(rd(s.m.uc,cfg['state']+336)),'request_owner':hex(rd(s.m.uc,cfg['state']+340)),'UI_data':hex(rd(s.m.uc,rd(s.m.uc,0x419f0de0)+0xff8+16)),'stock_kit':hex(rd(s.m.uc,0x419c5b10)),'MIDI_settings_word':int.from_bytes(s.m.uc.mem_read(out['MIDI_handles'][-1]['data']+158,2),'big') if out['MIDI_handles'] else None,'M1_config':[rd(s.m.uc,cfg['state']+x) for x in [4,304,308,320]],'label':label,'screen':str(p),'pattern':bytes(s.m.uc.mem_read(base,0x1200)).hex()});print(label,flush=True)
 phase='M1_page';s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('SYN2'),hold_ms=100,after_ms=200);s.release(s.code('FUNC'));s.run_ms(200);record(phase)
 h=out['MIDI_handles'][-1]['handle'];data=rd(s.m.uc,h+16);bank=rd(s.m.uc,h+4);t4_handle=bank+0x60+3*0x328;t4_data=rd(s.m.uc,t4_handle+16)
 out['T4_data_pointer']=hex(t4_data);before_t4=bytes(s.m.uc.mem_read(t4_data,0x146));before_midi=bytes(s.m.uc.mem_read(data,164))
 for channel in range(1,9):
  phase='encoder_'+str(channel);s.turn(channel,16,after_ms=300);record(phase)
 out['T4_data_unchanged']=bytes(s.m.uc.mem_read(t4_data,0x146))==before_t4
 after_midi=bytes(s.m.uc.mem_read(data,164));out['existing_MIDI_fields_unchanged']=after_midi[:158]==before_midi[:158] and after_midi[160:]==before_midi[160:]
 serialized=rd(s.m.uc,h+32);out['serialized_pointer']=hex(serialized);out['serialized_settings_word']=int.from_bytes(s.m.uc.mem_read(serialized+166,2),'big')
 phase='close';s.tap(s.code('NO'),hold_ms=100,after_ms=300);record(phase)
 from emu import midi
 mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,)
 gate=rd(s.m.uc,0x41368d64);s.m.uc.mem_write(0x41368d64,struct.pack('>I',gate|3));ch=rd(s.m.uc,0x41368d2c)&15
 def send(raw):
  for i,byte in enumerate(raw):mi._push(s.pits.now+(i+1)*s.ips*.00032,byte)
  mi.received+=len(raw);s.run_ms(100)
 phase='apply';send([0x90|ch,60,100]);s.run_ms(300);record(phase);send([0x80|ch,60,0]);s.run_ms(300)
 out['MIDI_delivered']=mi.delivered
 out['serialized_settings_after_input']=int.from_bytes(s.m.uc.mem_read(serialized+166,2),'big')
 phase='save_menu';s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('GLOBAL'),hold_ms=100,after_ms=300);s.release(s.code('FUNC'));s.run_ms(300);record(phase)
 phase='save_yes';s.tap(s.code('YES'),hold_ms=100,after_ms=1500);record(phase)
 phase='save_empty';s.tap(s.code('NO'),hold_ms=100,after_ms=200);s.tap(s.code('DOWN'),hold_ms=100,after_ms=200);s.tap(s.code('YES'),hold_ms=100,after_ms=1500);record(phase)
 phase='save_confirm';s.tap(s.code('YES'),hold_ms=100,after_ms=2000);record(phase)
 out['serialized_settings_after_save']=int.from_bytes(s.m.uc.mem_read(serialized+166,2),'big')
 s.run_ms(1000);s.tap(s.code('NO'),hold_ms=100,after_ms=200)
 phase='change_before_reload';s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('SYN2'),hold_ms=100,after_ms=200);s.release(s.code('FUNC'));s.run_ms(100);s.turn(1,-16,after_ms=300);record(phase);s.tap(s.code('NO'),hold_ms=100,after_ms=200)
 phase='load_settings';s.tap(s.code('GLOBAL'),hold_ms=100,after_ms=300);record(phase)
 phase='load_project_menu';s.tap(s.code('YES'),hold_ms=100,after_ms=300);record(phase)
 phase='load_selector';s.tap(s.code('YES'),hold_ms=100,after_ms=300);record(phase)
 phase='load_selected';s.tap(s.code('YES'),hold_ms=100,after_ms=2000);record(phase)
 phase='load_confirm';s.tap(s.code('YES'),hold_ms=100,after_ms=2000);record(phase)
 phase='reload_page';s.run_ms(1500)
 for _ in range(3):s.tap(s.code('NO'),hold_ms=100,after_ms=200)
 s.press(s.code('MIDI'));s.run_ms(150);s.tap(s.code('T1'),hold_ms=100,after_ms=200);s.release(s.code('MIDI'));s.run_ms(300);s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('SYN2'),hold_ms=100,after_ms=200);s.release(s.code('FUNC'));s.run_ms(300);record(phase)
 phase='reload_apply';send([0x90|ch,60,100]);s.run_ms(200);send([0x80|ch,60,0]);s.run_ms(200);record(phase)
 out['halted']=s.halted;out['passed']=not s.halted
except Exception:out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:s.close();Path('outputs/Digitone-E08D-packaged-project-controls.json').write_text(json.dumps(out,indent=2))
