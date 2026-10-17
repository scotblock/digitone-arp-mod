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
cfg=json.loads(Path('outputs/Digitone-E05-PC-candidate-layout.json').read_text());startup=json.loads(Path('outputs/Digitone-E05-PC-startup-comparison.json').read_text());assert startup['passed']
cases={r['image']:r for r in startup['cases']};payload=Path('work/os144/E05-PC-payload.bin').read_bytes();qpc=json.loads(Path('work/packed-context-build.json').read_text())['layout']['quantize']['address']
rows={r['raw_scale']:r['pitch_classes'] for r in json.loads(Path('outputs/Digitone-OS1.44-scale-map.json').read_text())['scales']}
def rd(u,a):return int.from_bytes(u.mem_read(a,4),'big')
def oracle(note,word):
 raw=((word>>7)&63)-1;root=word&127
 if not word>>31 or raw not in rows or not 0<=note<128:return note
 return min((n for n in range(128) if (n-root)%12 in rows[raw]),key=lambda n:(abs(n-note),n))
out={'PC_only':True,'cases':[],'limits':['Continuous guest playback from native cold/intro snapshots; emulator peripheral and bootstrap shortcuts remain.','Root/scale and MIDI gate values are disclosed matched PC fixtures; note descriptors, arp eligibility, copies and output are guest-produced.','Audio sample equality is a separate result from pitch equality; modeled scheduling can differ.','No physical cache, timing, DMA or hardware-ready claim.']}
dest=Path('outputs/Digitone-E05-PC-playback-comparison.json')
for name,scenario in [('stock_restored','ordinary'),('E05_restored','ordinary'),('stock_restored','scale'),('E05_restored','scale'),('E05_disabled','ordinary')]:
 row={'image':name,'scenario':scenario,'quantize':[],'pitches':[],'captures':[],'pattern_publications':[],'failure':None};out['cases'].append(row);s=None;started=time.monotonic();candidate=name.startswith('E05');syx=Path('work/os144/E05-PC-candidate.syx' if candidate else 'outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx').resolve();case=cases[name]
 try:
  root=Path(case['ui_snapshot']).parents[2];paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env());pending={};installed=set()
  def install(session):
   u=session.m.uc
   if candidate:
    for r in cfg['regions']:
     if r['base']<0x47be0000:continue
     off=r['base']-0x47be0000;code=payload[off:off+r['bytes']];assert bytes(u.mem_read(r['base'],r['bytes']))==code,r['name'];session.m.install_isa_patches_scoped(code,r['base'])
    assert rd(u,0x47be2840)==0x4c495645 and rd(u,0x47be1010)==(0 if name=='E05_disabled' else 1)
    def returned(u,pc,n,d):
     if pc in pending:
      x=pending.pop(pc);x['actual']=u.reg_read(UC_M68K_REG_D0);x['matches']=x['actual']==x['expected'];row['quantize'].append(x)
    def quantize(u,pc,n,d):
     sp=u.reg_read(UC_M68K_REG_A7);ret=rd(u,sp);note=rd(u,sp+4);word=rd(u,sp+8);assert ret not in pending;pending[ret]={'ms':session.now_ms(),'note':note,'word':hex(word),'expected':oracle(note,word)}
     if ret not in installed:session.at(ret,returned);installed.add(ret)
    session.at(qpc,quantize)
    def capture(u,pc,n,d):
     pattern=u.reg_read(UC_M68K_REG_A2);track=u.reg_read(UC_M68K_REG_D2);note=u.reg_read(UC_M68K_REG_D3)
     if track<4 and note<128:
      raw=struct.unpack('b',u.mem_read(pattern+track*0x3d0+0x3ce,1))[0];root=bytes(u.mem_read(pattern+track*0x3d0+0x3cb,1))[0];expected=0x80000000|root|((raw+1)<<7)|(track<<13) if root<128 and -1<=raw<35 else 0;actual=rd(u,0x47be2800+track*8+4);row['captures'].append({'root':root,'raw_scale':raw,'word':hex(actual),'matches':actual==expected,'ms':session.now_ms()})
    if name!='E05_disabled':session.at(0x400eaf50,capture)
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
   for track in range(4):s.m.uc.mem_write(back+track*0x3d0+0x3cb,bytes([62]));s.m.uc.mem_write(back+track*0x3d0+0x3ce,bytes([0 if scenario=='scale' else 255]))
  row['pattern_field_fixture']={'backings':[hex(x) for x in sorted(backings)],'root':62,'raw_scale':0 if scenario=='scale' else -1}
  s.tap(s.code('RECORD'),hold_ms=100,after_ms=100);s.tap(s.code('1'),hold_ms=100,after_ms=100);s.tap(s.code('RECORD'),hold_ms=100,after_ms=100);s.tap(s.code('PLAY'),hold_ms=100,after_ms=500)
  mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,);gate=rd(s.m.uc,0x41368d64);s.m.uc.mem_write(0x41368d64,struct.pack('>I',gate|3));channel=rd(s.m.uc,0x41368d2c)&15;row['MIDI_gate_fixture']={'before':gate,'after':gate|3}
  def send(data):
   for i,byte in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*0.00032,byte)
   mi.received+=len(data);s.run_ms(20)
  send([0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100]);s.run_ms(2000)
  send([0xb0|channel,64,127]);send([0x80|channel,60,0,0x80|channel,64,0,0x80|channel,67,0]);s.run_ms(500)
  oldpattern=rd(s.m.uc,0x4138f214);s.press(s.code('PTN'));s.run_ms(100);s.tap(s.code('2'),hold_ms=100,after_ms=100);s.release(s.code('PTN'));s.run_ms(3000);newpattern=rd(s.m.uc,0x4138f214);row['pattern_handoff']={'before':hex(oldpattern),'after':hex(newpattern),'completed':oldpattern!=newpattern}
  send([0xb0|channel,64,0]);s.run_ms(300);send([0x90|channel,65,100]);s.run_ms(1000);send([0x80|channel,65,0]);s.run_ms(1000);s.tap(s.code('STOP'),hold_ms=100,after_ms=300)
  row.update(halted=s.halted,model_ms=s.now_ms(),audio_bytes=len(s.pcm),audio_nonzero_bytes=sum(x!=0 for x in s.pcm),audio_sha256=hashlib.sha256(s.pcm).hexdigest(),DSP_renders=link.renders,DSP_error=str(link.error) if link.error else None,MIDI_received=mi.received,MIDI_delivered=mi.delivered,pending_quantize_returns=len(pending))
  assert s.halted is None and row['audio_nonzero_bytes']>0 and not row['DSP_error'] and mi.received==mi.delivered and row['pitches']
  if candidate and name!='E05_disabled':
   assert row['captures'] and all(x['matches'] for x in row['captures']);assert row['quantize'] and all(x['matches'] for x in row['quantize']) and not pending
   if scenario=='scale':assert any(x['actual']!=x['note'] for x in row['quantize'])
  if candidate:
   assert rd(s.m.uc,0x47be2840)==0x4c495645
   assert all(bytes(s.m.uc.mem_read(r['base'],r['bytes']))==payload[r['base']-0x47be0000:r['base']-0x47be0000+r['bytes']] for r in cfg['components'])
  wav=Path('outputs',f'Digitone-E05-PC-{name}-{scenario}.wav')
  with wave.open(str(wav),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(s.pcm)
  row['audio_file']=str(wav.resolve());row['passed']=True
 except Exception:row.update(passed=False,failure=traceback.format_exc());print(row['failure'],flush=True)
 finally:
  if s:s.close()
 row['seconds']=time.monotonic()-started;dest.write_text(json.dumps(out,indent=2));print('PLAYBACK',name,scenario,row.get('passed'),'pitches',len(row['pitches']),'quantized',len(row['quantize']),flush=True)
ordinary={r['image']:r for r in out['cases'] if r['scenario']=='ordinary'};stock=ordinary['stock_restored'];out['ordinary_comparisons']=[]
for name in ['E05_restored','E05_disabled']:
 r=ordinary[name];out['ordinary_comparisons'].append({'image':name,'pitch_values_identical':[x['pitch'] for x in r['pitches']]==[x['pitch'] for x in stock['pitches']],'stock_pitch_count':len(stock['pitches']),'candidate_pitch_count':len(r['pitches']),'audio_byte_exact':r.get('audio_sha256')==stock.get('audio_sha256')})
out['passed']=all(r.get('passed') for r in out['cases']);dest.write_text(json.dumps(out,indent=2))
if not out['passed']:raise SystemExit(1)
