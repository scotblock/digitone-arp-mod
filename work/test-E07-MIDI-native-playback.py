from pathlib import Path
import sys,os,json,struct,hashlib,traceback,time,wave
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from emu import bootstrap as bs,longrun,midi
from emu.session import Session
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import *
original_build=longrun.build
def build(*a,**kw):kw['unblock']=False;return original_build(*a,**kw)
longrun.build=build
cfg=json.loads(Path('outputs/Digitone-E07-PC-candidate-layout.json').read_text());startup=json.loads(Path('outputs/Digitone-E07-PC-startup-comparison.json').read_text());assert startup['passed']
cases={r['image']:r for r in startup['cases']};cases['E07_mirror_off']=cases['E07_restored'];payload=Path('work/os144/E07-PC-payload.bin').read_bytes();qpc=json.loads(Path('work/packed-context-build.json').read_text())['layout']['quantize']['address']
rows={r['raw_scale']:r['pitch_classes'] for r in json.loads(Path('outputs/Digitone-OS1.44-scale-map.json').read_text())['scales']}
def rd(u,a):return int.from_bytes(u.mem_read(a,4),'big')
def oracle(note,word):
 raw=((word>>7)&63)-1;root=word&127
 if not word>>31 or raw not in rows or not 0<=note<128:return note
 return min((n for n in range(128) if (n-root)%12 in rows[raw]),key=lambda n:(abs(n-note),n))
out={'PC_only':True,'cases':[],'limits':['Continuous guest playback from native cold/intro snapshots; emulator peripheral and bootstrap shortcuts remain.','Root/scale and MIDI gate values are disclosed matched PC fixtures; note descriptors, arp eligibility, copies and output are guest-produced.','Audio sample equality is a separate result from pitch equality; modeled scheduling can differ.','Eight-step arp settings are applied as disclosed PC fixtures before the actual stock selector; guest capture, eligibility and hook execution remain native.','Native copying supplies MIDI code and private-state seed; tests install scoped ISA emulation and observations only. No host injects outgoing MIDI packets.','DIN output only; physical timing and USB mirroring remain outside this candidate.','No physical cache, timing, DMA or hardware-ready claim.']}
dest=Path('outputs/Digitone-E07-MIDI-native-playback.json')

for name,scenario in [('E07_restored','scale'),('E07_mirror_off','scale')]:
 if any(r['image']==name and r['scenario']==scenario for r in out['cases']):continue
 row={'image':name,'scenario':scenario,'quantize':[],'degrees':[],'arp_setting_fixtures':[],'pitches':[],'captures':[],'pattern_publications':[],'failure':None,'voice_starts':[],'voice_state_writes':[],'MIDI_poll':[],'MIDI_mirror_starts':[],'output_channels':[],'wire':[]};out['cases'].append(row);s=None;started=time.monotonic();candidate=name.startswith('E07');syx=Path('work/os144/E07-PC-candidate.syx' if candidate else 'outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx').resolve();case=cases[name]
 try:
  root=Path(case['ui_snapshot']).parents[2];paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env());pending={};installed=set()
  def install(session):
   u=session.m.uc
   if candidate:
    for r in cfg['regions']:
     if r['base']<0x47be0000:continue
     off=r['base']-0x47be0000;code=payload[off:off+r['bytes']];assert bytes(u.mem_read(r['base'],r['bytes']))==code,r['name'];session.m.install_isa_patches_scoped(code,r['base'])
    assert rd(u,0x47be2840)==0x4c495645 and rd(u,0x47be1010)==(0 if name=='E07_disabled' else 1)
    def returned(u,pc,n,d):
     if pc in pending:
      x=pending.pop(pc);x['actual']=u.reg_read(UC_M68K_REG_D0);x['matches']=x['actual']==x['expected'];row[x.pop('kind','quantize')].append(x)
    def quantize(u,pc,n,d):
     sp=u.reg_read(UC_M68K_REG_A7);ret=rd(u,sp);note=rd(u,sp+4);word=rd(u,sp+8);assert ret not in pending;pending[ret]={'ms':session.now_ms(),'note':note,'word':hex(word),'expected':oracle(note,word)}
     if ret not in installed:session.at(ret,returned);installed.add(ret)
    session.at(qpc,quantize)
    def degree(u,pc,n,d):
     sp=u.reg_read(UC_M68K_REG_A7);ret=rd(u,sp);fallback,word,base,offset,octave=[rd(u,sp+i) for i in [4,8,12,16,20]]
     offset=offset-0x100000000 if offset&0x80000000 else offset
     raw=((word>>7)&63)-1;root=word&127;expected=fallback
     if word>>31 and not word&0x7fff8000 and raw in rows and base<128 and -128<=offset<=127:
      pcs=rows[raw];held=min((v for v in range(128) if (v-root)%12 in pcs),key=lambda v:(abs(v-base),v));pc0=(held-root)%12;cycles,index=divmod(pcs.index(pc0)+offset,len(pcs));expected=held-pc0+cycles*12+pcs[index]+octave
      if not 0<=expected<256:expected=-1
     assert ret not in pending
     pending[ret]={'kind':'degrees','ms':session.now_ms(),'base':base,'offset':offset,'octave':octave,'word':hex(word),'expected':expected&0xffffffff}
     if ret not in installed:session.at(ret,returned);installed.add(ret)
    session.at(cfg['degree_address'],degree)

    def capture(u,pc,n,d):
     pattern=u.reg_read(UC_M68K_REG_A2);track=u.reg_read(UC_M68K_REG_D2);note=u.reg_read(UC_M68K_REG_D3)
     if track<4 and note<128:
      raw=struct.unpack('b',u.mem_read(pattern+track*0x3d0+0x3ce,1))[0];root=bytes(u.mem_read(pattern+track*0x3d0+0x3cb,1))[0];expected=0x80000000|root|((raw+1)<<7)|(track<<13) if root<128 and -1<=raw<35 else 0;actual=rd(u,0x47be2800+track*8+4);row['captures'].append({'root':root,'raw_scale':raw,'word':hex(actual),'matches':actual==expected,'ms':session.now_ms()})
    if name!='E07_disabled':session.at(0x400eaf50,capture)
   row['MIDI_private_state_from_copier']=hex(rd(session.m.uc,cfg['MIDI_state']));assert rd(session.m.uc,cfg['MIDI_state'])==0x53414d31
   if name=='E07_mirror_off':session.m.uc.mem_write(cfg['MIDI_state']+4,bytes(4));row['MIDI_disable_fixture']=True
   def mirror_start(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7);voice,track,ev,note,velocity=[rd(u,sp+i) for i in [4,8,12,16,20]]
    row['MIDI_mirror_starts'].append({'ms':session.now_ms(),'voice':voice,'track':track,'event':hex(ev),'note':note,'velocity':velocity,'eligible':track<4 and rd(u,cfg['MIDI_markers']+track*4)==ev})
   session.at(cfg['MIDI_entries']['ON'],mirror_start)
   from unicorn import UC_HOOK_MEM_WRITE
   def voice_started(u,pc,n,d):
    frame=u.reg_read(UC_M68K_REG_A6);ev=u.reg_read(UC_M68K_REG_A3)
    row['voice_starts'].append({'ms':session.now_ms(),'event':hex(ev),'track':u.reg_read(UC_M68K_REG_D2),'voice':rd(u,frame-0x80),'pitch':u.reg_read(UC_M68K_REG_D0)>>16,'raw_event':bytes(u.mem_read(ev,72)).hex(),'SR':hex(u.reg_read(UC_M68K_REG_SR))})
   session.at(0x4009e934,voice_started)
   def voice_write(u,access,address,size,value,d):
    if len(row['voice_state_writes'])<10000:row['voice_state_writes'].append({'ms':session.now_ms(),'pc':hex(u.reg_read(UC_M68K_REG_PC)),'address':hex(address),'size':size,'value':hex(value)})
   session.m.uc.hook_add(UC_HOOK_MEM_WRITE,voice_write,begin=0x80005434,end=0x80005434+160-1)
   session.at(0x400f4c7e,lambda u,pc,n,d:row['MIDI_poll'].append(session.now_ms()))
   row['output_channels']=[rd(session.m.uc,0x41368d30+i*4) for i in range(4)]
   mo=midi.MidiOut(lambda data:row['wire'].append({'ms':session.now_ms(),'bytes':list(data)}));mo.install(session.m);mo.attach(session.m,session.ips);session.sources=session.sources+(mo,)
   def arp_fixture(u,pc,n,d):
    if scenario!='scale':return
    track=rd(u,u.reg_read(UC_M68K_REG_A7)+4)
    if track>=4:return
    state=0x413915f4+track*40;settings=rd(u,state+0x20)
    if not 0x40000000<=settings<0x48000000:return
    u.mem_write(settings+0x111,bytes([0]));u.mem_write(settings+0x113,bytes([7]));u.mem_write(settings+0x114,bytes.fromhex('00ff'));u.mem_write(settings+0x116,bytes(range(8)))
    if not any(x['settings']==hex(settings) for x in row['arp_setting_fixtures']):row['arp_setting_fixtures'].append({'track':track,'settings':hex(settings),'length':8,'offsets':list(range(8)),'range':0,'before_stock_selector':True})
   session.at(0x40097e46,arp_fixture)
   session.at(0x4009e890,lambda u,pc,n,d:row['pitches'].append({'ms':session.now_ms(),'pitch':u.reg_read(UC_M68K_REG_D6)}))
  s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x08000000,on_machine=install);link=s.ev['dsplink'];assert type(link).__name__=='DspCpu'
  for warm in range(10):
   s.run_ms(1000)
   if link.booted and link.renders>100:break
  assert link.booted and link.renders>100;row['warmup_ms']=s.now_ms()
  s.tap(s.code('STOP'),hold_ms=100,after_ms=100);s.tap(s.code('T1'),hold_ms=100,after_ms=100)
  s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('SYN1'),hold_ms=100,after_ms=100);s.release(s.code('FUNC'));s.run_ms(200)
  s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('KEYBOARD'),hold_ms=100,after_ms=100);s.release(s.code('FUNC'));s.run_ms(200);s.turn(3,16,after_ms=200);s.tap(s.code('NO'),hold_ms=100,after_ms=100)
  # Set both active and receiving pattern fields equally across stock/candidate.
  backings={rd(s.m.uc,0x4138f214),0x407fd414,0x40813531}
  for back in backings:
   for track in range(4):s.m.uc.mem_write(back+track*0x3d0+0x3cb,bytes([60]));s.m.uc.mem_write(back+track*0x3d0+0x3ce,bytes([0 if scenario=='scale' else 255]))
  row['pattern_field_fixture']={'backings':[hex(x) for x in sorted(backings)],'root':60,'raw_scale':0 if scenario=='scale' else -1}
  s.tap(s.code('RECORD'),hold_ms=100,after_ms=100);s.tap(s.code('1'),hold_ms=100,after_ms=100);s.tap(s.code('RECORD'),hold_ms=100,after_ms=100);s.tap(s.code('PLAY'),hold_ms=100,after_ms=500)
  mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,);gate=rd(s.m.uc,0x41368d64);s.m.uc.mem_write(0x41368d64,struct.pack('>I',gate|3));channel=rd(s.m.uc,0x41368d2c)&15;row['MIDI_gate_fixture']={'before':gate,'after':gate|3}
  def send(data):
   for i,byte in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*0.00032,byte)
   mi.received+=len(data);s.run_ms(20)
  send([0x90|channel,60,100] if scenario=='scale' else [0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100]);s.run_ms(2000)
  send([0xb0|channel,64,127]);send([0x80|channel,60,0,0x80|channel,64,0,0x80|channel,67,0]);s.run_ms(500)
  oldpattern=rd(s.m.uc,0x4138f214);s.press(s.code('PTN'));s.run_ms(100);s.tap(s.code('2'),hold_ms=100,after_ms=100);s.release(s.code('PTN'));s.run_ms(3000);newpattern=rd(s.m.uc,0x4138f214);row['pattern_handoff']={'before':hex(oldpattern),'after':hex(newpattern),'completed':oldpattern!=newpattern}
  send([0xb0|channel,64,0]);s.run_ms(300);send([0x90|channel,65,100]);s.run_ms(1000);send([0x80|channel,65,0]);s.run_ms(1000);s.tap(s.code('STOP'),hold_ms=100,after_ms=300)
  row.update(halted=s.halted,model_ms=s.now_ms(),audio_bytes=len(s.pcm),audio_nonzero_bytes=sum(x!=0 for x in s.pcm),audio_sha256=hashlib.sha256(s.pcm).hexdigest(),DSP_renders=link.renders,DSP_error=str(link.error) if link.error else None,MIDI_received=mi.received,MIDI_delivered=mi.delivered,pending_quantize_returns=len(pending))
  assert s.halted is None and row['audio_nonzero_bytes']>0 and not row['DSP_error'] and mi.received==mi.delivered and row['pitches']
  if candidate and name!='E07_disabled':
   assert row['captures'] and all(x['matches'] for x in row['captures']);assert row['quantize'] and all(x['matches'] for x in row['quantize']) and not pending
   if scenario=='scale':
    assert row['degrees'] and all(x['matches'] for x in row['degrees']);assert set(range(8))<=set(x['offset'] for x in row['degrees']),row['degrees']
    examples=[x for x in row['degrees'] if x['base']==60 and x['octave']==0 and x['word']=='0x800000bc'];assert examples
    assert set([60,62,64,65,67,69,71,72])<=set(x['actual'] for x in examples),examples
  if candidate:
   assert rd(s.m.uc,0x47be2840)==0x4c495645
   assert all(bytes(s.m.uc.mem_read(r['base'],r['bytes']))==payload[r['base']-0x47be0000:r['base']-0x47be0000+r['bytes']] for r in cfg['components'] if r['name']!='MIDI_private_state_seed')
  row['private_state_hex']=bytes(s.m.uc.mem_read(cfg['MIDI_state'],160)).hex()
  messages=[];stream=b''.join(bytes(x['bytes']) for x in row['wire']);assert len(stream)%3==0,stream.hex()
  active={};ons=[]
  for i in range(0,len(stream),3):
   status,note,velocity=stream[i:i+3];assert status&0xf0 in [0x80,0x90] and note<128 and velocity<128
   key=(status&15,note);on=status&0xf0==0x90 and velocity>0
   if on:assert key not in active,(key,messages);active[key]=True;ons.append(note)
   else:assert key in active,(key,messages);del active[key]
   messages.append({'channel':(status&15)+1,'note':note,'velocity':velocity,'on':on})
  if name=='E07_mirror_off':assert not messages
  else:assert messages and not active and set([60,62,64,65,67,69,71,72])<=set(ons),(messages,active)
  assert all(rd(s.m.uc,cfg['MIDI_records']+v*16)==0 for v in range(8))
  row['MIDI_messages']=messages;row['balanced_note_pairs']=len(ons);row['no_active_mirrored_notes_at_stop']=True;row['dropped_note_ons']=rd(s.m.uc,cfg['MIDI_state']+8);row['mirror_code_host_loaded']=False
  wav=Path('outputs',f'Digitone-E07-MIDI-native-{name}-{scenario}.wav')
  with wave.open(str(wav),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(s.pcm)
  row['audio_file']=str(wav.resolve());row['passed']=True
 except Exception:row.update(passed=False,failure=traceback.format_exc());print(row['failure'],flush=True)
 finally:
  if s:s.close()
 row['seconds']=time.monotonic()-started;dest.write_text(json.dumps(out,indent=2));print('PLAYBACK',name,scenario,row.get('passed'),'pitches',len(row['pitches']),'quantized',len(row['quantize']),flush=True)

out['passed']=all(r.get('passed') for r in out['cases']);dest.write_text(json.dumps(out,indent=2));
if not out['passed']:raise SystemExit(1)

on,off=out['cases'];baseline=json.loads(Path('outputs/Digitone-E06-PC-playback-comparison.json').read_text());reference=next(r for r in baseline['cases'] if r['image']=='E06_restored' and r['scenario']=='scale');out['internal_pitches_equal_E06_and_mirror_off']=[x['pitch'] for x in on['pitches']]==[x['pitch'] for x in off['pitches']]==[x['pitch'] for x in reference['pitches']];assert out['internal_pitches_equal_E06_and_mirror_off'];dest.write_text(json.dumps(out,indent=2))
