from pathlib import Path
s=Path('work/trace-E08-MIDI-controls.py').read_text()
s=s.replace('audio=False','audio=True')
# Use the last completed OLED flush; FRONT may be blank or half drawn between
# native rendering and the firmware's buffer swap.
s=s.replace('frame=panel.read(s.m,s.profile.fb_front)', 'frame=s.frames[-1][1] if s.frames else panel.read(s.m,s.profile.fb_back)')
s=s.replace("s=Session(case['ui_snapshot']", "warm=Path('work/os144/E08-controls-warm.snap')\nif warm.exists():case['ui_snapshot']=str(warm.resolve())\ns=Session(case['ui_snapshot']")
s=s.replace('UC_M68K_REG_D3','UC_M68K_REG_D3,UC_M68K_REG_D0',1)
s=s.replace("'writes':[]","'writes':[],'encoder_events':[],'sound_lookups':[],'MIDI_handles':[]")
extra='''
 from unicorn import UC_HOOK_CODE
 exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\\nregions=')[0],globals())
 controls=json.loads(Path('work/os144/E08-PC-M1-controls-layout.json').read_text())
 for f in ['settings-accessors','settings-codec-bridge','M1-controls']:
  c=json.loads(Path('work/os144/E08-PC-'+f+'-layout.json').read_text());data=Path('work/os144/E08-PC-'+f+'.bin').read_bytes()
  if f=='settings-codec-bridge':
   data=data.replace(bytes.fromhex('4eb9400081f6'),bytes.fromhex('4eb947be6e00')).replace(bytes.fromhex('4eb94000818a'),bytes.fromhex('4eb947be6e20'))
  s.m.uc.mem_write(c['base'],data)
  for r in c['regions']:
   code=data[r['base']-c['base']:r['base']-c['base']+r['bytes']];p=0
   while p<len(code):
    ins=cfisa.decode(lambda off:int.from_bytes(code[p+off:p+off+2],'big'),r['base']+p)
    assert ins.length>0 and p+ins.length<=len(code) and not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(code[p:p+2],'big')),(r['name'],p,ins)
    p+=ins.length
   s.m.install_isa_patches_scoped(code,r['base'])
 for h in controls['hooks']:
  assert bytes(s.m.uc.mem_read(h['site'],h['length'])).hex() in [h['original'],h['replacement']],h
  s.m.uc.mem_write(h['site'],bytes.fromhex(h['replacement']))
 for site,target,tramp in [(0x400081f6,0x47be5a00,0x47be6e00),(0x4000818a,0x47be5b80,0x47be6e20)]:
  original=Path('work/os144/E08-PC-layout-main.bin').read_bytes()[site-0x40000400:site-0x40000400+8];t=original+bytes.fromhex('4ef9')+struct.pack('>I',site+8);s.m.uc.mem_write(tramp,t);s.m.install_isa_patches_scoped(t,tramp)
  s.m.uc.mem_write(site,bytes.fromhex('4ef9')+struct.pack('>I',target)+bytes.fromhex('4e71'))
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
   if 0x47be5e00<=args[6]<0x47be6e00 and len(out['draw_calls'])<20:out['draw_calls'].append({'phase':phase,'args':[hex(v) for v in args],'format':bytes(u.mem_read(args[6],40)).split(b'\\0')[0].decode('ascii','replace')})
 s.at(0x400de120,draw_call)
 def codec_call(u,pc,n,d):
  if phase!='setup' and len(out['codec_calls'])<80:
   sp=u.reg_read(UC_M68K_REG_A7);out['codec_calls'].append({'phase':phase,'pc':hex(pc),'args':[hex(rd(u,sp+i*4)) for i in range(4)]})
 for pc in [0x47be5a00,0x47be5b80,0x4001f09e,0x4014eff8]:s.at(pc,codec_call)
'''
s=s.replace(" out['offers']=[]",extra+" out['offers']=[]")
s=s.replace("try:\n s.run_ms(6500)", "try:\n from emu.dtim import Dtims\n if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):\n  extra_timer=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False);extra_timer.now=s.pits.now;s.pits.sources=s.pits.sources+(extra_timer,)\n if not warm.exists():\n  s.run_ms(6500)\n  from emu.snapshot import save\n  components={**s.ev['checkpoint_components'],'timers':s.pits};save(s.m,str(warm),components=components,manifest=s.ev.get('checkpoint_manifest'))\n else:s.run_ms(200)")
s=s.replace("out['steps'].append({'label':label", "out['steps'].append({'MIDI_settings_word':int.from_bytes(s.m.uc.mem_read(out['MIDI_handles'][-1]['data']+158,2),'big') if out['MIDI_handles'] else None,'M1_config':[rd(s.m.uc,cfg['state']+x) for x in [4,304,308,320]],'label':label")
a0=" phase='M1_page';"
a=s.index(" for page in ['SYN1'");z=s.index(" out['halted']=s.halted",a)
s=s[:a]+''' phase='M1_page';s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('SYN2'),hold_ms=100,after_ms=200);s.release(s.code('FUNC'));s.run_ms(200);record(phase)
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
''' + s[z:]
s=s.replace('Digitone-E08-MIDI-controls-trace.json','Digitone-E08-native-M1-controls.json').replace("'E08-MIDI-controls-'","'E08-native-M1-controls-'")
exec(compile(s,'E08-native-M1-device-controls','exec'))
