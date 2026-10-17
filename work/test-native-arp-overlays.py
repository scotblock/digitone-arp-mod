"""Actual RAM hooks in native Digiemu sessions. Never writes firmware files."""
import pathlib,os,json,struct,hashlib,collections,traceback,subprocess,sys
subprocess.run([sys.executable,'-c',"import pathlib,json; ns={}; s=pathlib.Path('work/test-reserved-RAM-route.py').read_text(); exec(s[:s.index('m=fresh();')],ns); pathlib.Path('work/native-overlay-code.bin').write_bytes(ns['runblob']); pathlib.Path('work/native-overlay-layout.json').write_text(json.dumps(ns['layout']))"],check=True)
subprocess.run([sys.executable,'work/lower-native-overlay.py'],check=True)
# Reuse exact-hash local environment, without installing the stock sentinel watch.
prefix=pathlib.Path('work/watch-continuous-reserved-RAM.py').read_text().split('def canonical')[0]
os.environ.pop('DIGITONE_CONTINUE_WATCH',None)
exec(compile(prefix,'environment','exec'))
from emu.session import Session
from unicorn.m68k_const import *
RAM,BSS,PTR=0x47be0000,0x47be1004,0x47be1000
blob=pathlib.Path('work/native-overlay-code.bin').read_bytes();layout=json.loads(pathlib.Path('work/native-overlay-layout.json').read_text())
stock=pathlib.Path('work/section-3.bin').read_bytes();base=0x40000400
rows={r['raw_scale']:r['pitch_classes'] for r in json.loads(pathlib.Path('outputs/Digitone-OS1.42-scale-map.json').read_text())['scales']}
OUT=pathlib.Path('outputs/Digitone-native-arp-overlay-results.json')
report={'firmware_modified':False,'firmware_before':hashlib.sha256(SYX.read_bytes()).hexdigest(),'code_bytes':len(blob),'runs':[],'failure':None}
def u32(x):return struct.pack('>I',x)
def rd(uc,a):return struct.unpack('>I',uc.mem_read(a,4))[0]
def oracle(note,word):
 raw=((word>>7)&63)-1;root=word&127
 if not word>>31 or raw not in rows or not 0<=note<128:return note
 return min((n for n in range(128) if (n-root)%12 in rows[raw]),key=lambda n:(abs(n-note),n))
def persist():OUT.write_text(json.dumps(report,indent=2))
def run(mode):
 result={'mode':mode,'hits':{},'captures':[],'pitches':[],'quantize_calls':[],'writes':collections.Counter(),'unexpected_writes':[],'checks':{}}
 report['runs'].append(result);counts=collections.Counter();pending={};captures={}
 def installed(session):
  m=session.m;uc=m.uc;m.ensure(RAM)
  if mode!='stock':
   uc.mem_write(RAM,blob);uc.mem_write(PTR,bytes(0xb74))
   uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1))
   m.install_isa_patches_scoped(blob,RAM)
   result['_guard_image']=bytes(uc.mem_read(RAM,0x20000))
   for pc,name,op,length in [(0x40093ef4,'producer_capture','4ef9',8),(0x400f0626,'allocate_clear','4ef9',6),(0x4009dda6,'before','4eb9',6),(0x4009de46,'caller_commit','4ef9',10),(0x4009df9a,'pitch_hook','4ef9',8)]:
    original=bytes(uc.mem_read(pc,length));assert original==stock[pc-base:pc-base+length],hex(pc)
    uc.mem_write(pc,bytes.fromhex(op)+u32(layout[name]['address'])+bytes.fromhex('4e71')*((length-6)//2))
   def writes(uc,access,a,n,v,d):
    physical=0x40000000+(a-0x40000000)%DDR
    if not (physical<RAM+0x20000 and RAM<physical+n):return
    pc=uc.reg_read(UC_M68K_REG_PC);result['writes'][hex(pc)]+=1
    if not (PTR<=physical and physical+n<=BSS+0xb70 and RAM<=pc<RAM+len(blob)):
     result['unexpected_writes'].append({'pc':hex(pc),'address':hex(a),'size':n})
   for k in range(8):uc.hook_add(UC_HOOK_MEM_WRITE,writes,begin=RAM+k*DDR-64,end=RAM+k*DDR+0x20000+63)
  def count(label):return lambda uc,a,n,d:counts.update([label])
  for label,pc in [('allocator',0x400f0626),('producer',0x40093ef4),('acceptance',0x4009dd80),('commit_site',0x4009de46),('pitch_site',0x4009df9a)]:session.at(pc,count(label))
  def producer(uc,a,n,d):
   event=uc.reg_read(UC_M68K_REG_A2);back=uc.reg_read(UC_M68K_REG_A3);track=uc.reg_read(UC_M68K_REG_D4)
   if mode=='scale-fixture' and track==2:
    uc.mem_write(back+track*0x3d0+0x3cb,b'\x3d');uc.mem_write(back+track*0x3d0+0x3ce,b'\0')
   root=bytes(uc.mem_read(back+track*0x3d0+0x3cb,1))[0];raw=struct.unpack('b',uc.mem_read(back+track*0x3d0+0x3ce,1))[0]
   captures[event]={'event':hex(event),'backing':hex(back),'track':track,'root':root,'raw':raw,'expected':hex(0x80000000|root|((raw+1)<<7)|(track<<13)) if root<128 and -1<=raw<35 else '0x0'}
  def captured(uc,a,n,d):
   event=uc.reg_read(UC_M68K_REG_A2);item=captures.pop(event,None)
   if item and mode!='stock':
    valid=0<=event-0x4199da94<128*72 and (event-0x4199da94)%72==0
    item['pool_eligible']=valid
    item['actual']=hex(rd(uc,BSS+32+(event-0x4199da94)//72*4)) if valid else None
    item['matches']=item['actual']==item['expected'] if valid else None;result['captures'].append(item)
    if mode=='scale-fixture' and item['track']==2:
     back=int(item['backing'],16);uc.mem_write(back+2*0x3d0+0x3cb,b'\x3e');uc.mem_write(back+2*0x3d0+0x3ce,b'\x05')
  session.at(0x40093ef4,producer);session.at(0x40093efc,captured)
  def pitch(uc,a,n,d):
   event=uc.reg_read(UC_M68K_REG_A3);track=rd(uc,event+8);coarse=uc.reg_read(UC_M68K_REG_D6)
   item={'event':hex(event),'track':track,'before':coarse,'type':rd(uc,event),'state':rd(uc,event+4),'flags':hex(rd(uc,event+40)),'identity':hex(rd(uc,event+64))}
   if mode!='stock' and track<4:item['record']=[rd(uc,BSS+0xb30+track*16+j*4) for j in range(4)]
   pending[event]=item
  def pitched(uc,a,n,d):
   event=uc.reg_read(UC_M68K_REG_A3);item=pending.pop(event,None)
   if item:
    item['after']=uc.reg_read(UC_M68K_REG_D6);result['pitches'].append(item)
  session.at(0x4009df9a,pitch);session.at(0x4009dfa2,pitched)
  def fixed(uc,a,n,d):
   if result['pitches']:
    item=result['pitches'][-1];item['fixed_point']=uc.reg_read(UC_M68K_REG_D6);item['fixed_point_matches']=item['fixed_point']==item['after']<<16
  session.at(0x4009dfa8,fixed)
  if mode!='stock':
   def quantizing(uc,a,n,d):
    sp=uc.reg_read(UC_M68K_REG_A7);note=rd(uc,sp+4);word=rd(uc,sp+8)
    result['quantize_calls'].append({'note':note,'word':hex(word),'expected':oracle(note,word)})
   session.at(layout['quantize']['address'],quantizing)
 session=Session(paths.gui,syx=str(SYX),ddr=DDR,on_machine=installed)
 try:
  session.tap(session.code('PLAY'),hold_ms=50,after_ms=1200)
  for track in ['T1','T2','T3','T4']:
   session.tap(session.code(track),hold_ms=40,after_ms=60);session.tap(session.code('1'),hold_ms=80,after_ms=120)
  for pattern in ['2','1']:
   session.press(session.code('PTN'));session.run_ms(40);session.tap(session.code(pattern),hold_ms=50,after_ms=40);session.release(session.code('PTN'));session.run_ms(3500)
  session.tap(session.code('STOP'),hold_ms=50,after_ms=300)
  result.update(hits=dict(counts),ms=session.ms,halted=session.halted,audio_sha256=hashlib.sha256(session.pcm).hexdigest(),audio_bytes=len(session.pcm),owner=hex(rd(session.m.uc,0x4199d590)))
  if mode!='stock':
   guard=result.pop('_guard_image');now=bytes(session.m.uc.mem_read(RAM,0x20000));mutable_start=PTR-RAM;mutable_end=BSS+0xb70-RAM
   changed=[p for p in result['pitches'] if p['before']!=p['after']]
   result['checks']={'code_intact':bytes(session.m.uc.mem_read(RAM,len(blob)))==blob,'unused_region_and_guards_intact':now[:mutable_start]==guard[:mutable_start] and now[mutable_end:]==guard[mutable_end:],'no_unexpected_writes':not result['unexpected_writes'],'eligible_capture_matches':all(i['matches'] for i in result['captures'] if i['pool_eligible']),'live_quantizer_matches':[(p['before'],p['after']) for p in changed]==[(c['note'],c['expected']) for c in result['quantize_calls'] if c['note']!=c['expected']],'fixed_point_matches':all(p.get('fixed_point_matches',False) for p in result['pitches'])}
 finally:session.close();result['writes']=dict(result['writes']);persist()
 print(mode,dict(counts),'pitch changes',sum(i['before']!=i['after'] for i in result['pitches']),flush=True)
try:
 if os.environ.get('ARP_SKIP_BASELINE')!='1':run('stock')
 run(os.environ.get('ARP_MODE','overlay'))
 report['firmware_after']=hashlib.sha256(SYX.read_bytes()).hexdigest();report['checks']={'firmware_unchanged':report['firmware_before']==report['firmware_after']}
except BaseException as exc:
 report['failure']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()};print(report['failure']['traceback'],flush=True)
finally:persist()
