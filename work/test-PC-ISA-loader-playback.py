from pathlib import Path
import json,os,struct,hashlib,time,traceback
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from emu import bootstrap as bs
from emu.session import Session
from emu import longrun
# Preserve the checkpoint's no-forced-semaphore policy in the playback build.
original_build=longrun.build
def matching_build(*args,**kwargs):
 kwargs['unblock']=False
 return original_build(*args,**kwargs)
longrun.build=matching_build
from unicorn.m68k_const import UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_D4,UC_M68K_REG_D6
syx=Path('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx').resolve()
payload=Path('work/os144/PC_ONLY-E04-ISA-corrected-payload.bin').read_bytes()
port=json.loads(Path('work/os144/helper-port.json').read_text())
info=json.loads(Path('work/packed-context-build.json').read_text())
rows={x['raw_scale']:x['pitch_classes'] for x in json.loads(Path('outputs/Digitone-OS1.44-scale-map.json').read_text())['scales']}
def rd(uc,a):return int.from_bytes(uc.mem_read(a,4),'big')
def oracle(note,word):
 raw=((word>>7)&63)-1;root=word&127
 if not word>>31 or raw not in rows or not 0<=note<128:return note
 return min((n for n in range(128) if (n-root)%12 in rows[raw]),key=lambda n:(abs(n-note),n))
startup=json.loads(Path('outputs/Digitone-E04-PC-ISA-loader-startup.json').read_text())
assert len(startup['cases'])==2 and all(c['passed'] for c in startup['cases'])
dest=Path('outputs/Digitone-E04-PC-ISA-loader-playback.json')
out={'PC_only':True,'cases':[],'limitations':['Snapshots join cold startup, intro and playback; peripheral models and scheduling shortcuts remain.','Root/scale fields are PC fixtures; event eligibility and note publication are guest-produced.','This is an overlay after the original E04 loader handoff, not a corrected packaged loader test.','Physical cache coherence, hardware timing and exclusive RAM ownership remain unverified.']}
for case in startup['cases']:
 root=Path(case['ui_snapshot']).parents[2]
 paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
 for scenario,mode in [('ordinary','corrected'),('ordinary','stock_sites'),('scale','corrected')]:
  r={'startup':case['image'],'scenario':scenario,'mode':mode,'quantize':[],'pitches':[],'captures':[],'strict_hits':0,'failure':None};out['cases'].append(r)
  started=time.monotonic();s=None
  try:
   pending={};installed=set()
   def install(session):
    uc=session.m.uc
    assert bytes(uc.mem_read(0x47be0000,len(payload)))==payload
    assert rd(uc,0x47be1010)==1
    if mode=='stock_sites':
     for h in port['hooks']:uc.mem_write(int(h['site'],16),bytes.fromhex(h['stock_bytes']))
    session.m.install_isa_patches_scoped(payload[:1784],0x47be0000)
    session.m.install_isa_patches_scoped(payload[2212:],0x47be08a4)
    def strict(uc,pc,size,data):
     ins=cfisa.decode(lambda off:int.from_bytes(uc.mem_read(pc+off,2),'big'),pc)
     bad=move_restriction(int.from_bytes(uc.mem_read(pc,2),'big'))
     assert not bad and not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF),(hex(pc),ins.op,bad)
     r['strict_hits']+=1
    for lo,hi in [(0x47be0000,0x47be06f7),(0x47be08a4,0x47be09bb)]:uc.hook_add(UC_HOOK_CODE,strict,begin=lo,end=hi)
    def returned(uc,pc,n,d):
     if pc in pending:
      item=pending.pop(pc);item['actual']=uc.reg_read(UC_M68K_REG_D0);item['matches']=item['actual']==item['expected'];r['quantize'].append(item)
    def quantize(uc,pc,n,d):
     sp=uc.reg_read(UC_M68K_REG_A7);ret=rd(uc,sp);note=rd(uc,sp+4);word=rd(uc,sp+8)
     assert ret not in pending
     pending[ret]={'ms':session.now_ms(),'note':note,'word':hex(word),'expected':oracle(note,word)}
     if ret not in installed:session.at(ret,returned);installed.add(ret)
    session.at(info['layout']['quantize']['address'],quantize)
    session.at(0x4009e890,lambda uc,pc,n,d:r['pitches'].append(uc.reg_read(UC_M68K_REG_D6)))
    def captured(uc,pc,n,d):
     e=uc.reg_read(UC_M68K_REG_A2);track=uc.reg_read(UC_M68K_REG_D4);back=uc.reg_read(UC_M68K_REG_A3)
     if track>=4:return
     root=bytes(uc.mem_read(back+track*0x3d0+0x3cb,1))[0];raw=struct.unpack('b',uc.mem_read(back+track*0x3d0+0x3ce,1))[0]
     expected=(0x80000000|root|((raw+1)<<7)|(track<<13)) if root<128 and -1<=raw<35 else 0
     slot=None
     if 0<=e-0x419ebe2c<9216 and (e-0x419ebe2c)%72==0:slot=0x47be1024+(e-0x419ebe2c)//72*4
     elif 0<=e-0x419f182c<288 and (e-0x419f182c)%72==0:slot=0x47be1a24+(e-0x419f182c)//72*4
     if slot:r['captures'].append({'event':hex(e),'expected':hex(expected),'actual':hex(rd(uc,slot)),'matches':rd(uc,slot)==expected})
    if mode=='corrected':session.at(0x400947f4,captured)
   s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x08000000,on_machine=install)
   # Change only ordinary root/scale pattern fields; the firmware produces events.
   for back in set([0x40813531,rd(s.m.uc,0x4138f214)]):
    for track in range(4):
     s.m.uc.mem_write(back+track*0x3d0+0x3cb,bytes([61]));s.m.uc.mem_write(back+track*0x3d0+0x3ce,bytes([0 if scenario=='scale' else 255]))
   s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
   s.press(s.code('PTN'));s.run_ms(100);s.tap(s.code('2'),hold_ms=100,after_ms=100);s.release(s.code('PTN'));s.run_ms(300)
   s.tap(s.code('PLAY'),hold_ms=100,after_ms=10000)
   s.tap(s.code('STOP'),hold_ms=100,after_ms=200)
   r.update(ms=s.now_ms(),halted=s.halted,audio_bytes=len(s.pcm),audio_sha256=hashlib.sha256(s.pcm).hexdigest(),payload_intact=bytes(s.m.uc.mem_read(0x47be0000,len(payload)))==payload,ready=rd(s.m.uc,0x47be1010),pending_returns=len(pending))
   assert s.halted is None and r['payload_intact'] and r['ready']==1 and r['pitches'] and r['audio_bytes']>0
   if mode=='corrected':assert r['strict_hits']>0 and r['captures'] and all(x['matches'] for x in r['captures']) and r['quantize'] and all(x['matches'] for x in r['quantize']) and not pending
   if scenario=='scale':assert any(x['note']!=x['actual'] for x in r['quantize'])
   r['passed']=True
  except Exception:r['failure']=traceback.format_exc();r['passed']=False;print(r['failure'],flush=True)
  finally:
   if s:s.close()
  r['seconds']=time.monotonic()-started;dest.write_text(json.dumps(out,indent=2));print('playback',r['startup'],scenario,mode,r.get('passed'),len(r['pitches']),len(r['quantize']),flush=True)
out['ordinary_comparisons']=[]
for name in [c['image'] for c in startup['cases']]:
 a,b=[r for r in out['cases'] if r['startup']==name and r['scenario']=='ordinary']
 out['ordinary_comparisons'].append({'startup':name,'pitches_identical':a['pitches']==b['pitches'],'audio_identical':a.get('audio_sha256')==b.get('audio_sha256'),'corrected_pitch_count':len(a['pitches']),'stock_sites_pitch_count':len(b['pitches'])})
out['passed']=all(r['passed'] for r in out['cases']);dest.write_text(json.dumps(out,indent=2))
assert out['passed']
