from pathlib import Path
import os,json
source=Path('work/test-os144-stock-delayed-queue.py').read_text().split("exec(compile(s,'stock-delayed-queue','exec'))")[0]
exec(compile(source,'build-continuous-scenario','exec'))
MODE=os.environ.get('OS144_HOOK_MODE','stock');SCENARIO=os.environ.get('OS144_HOOK_SCENARIO','ordinary')
assert MODE in ['stock','helpers'] and SCENARIO in ['ordinary','scale','early-scale']
s=s.replace('Digitone-OS1.44-stock-delayed-queue.json','Digitone-OS1.44-continuous-'+SCENARIO+'-'+MODE+'.json')
prefix="""
port=json.loads(Path('work/os144/helper-port.json').read_text());info=json.loads(Path('work/packed-context-build.json').read_text())
blob=Path('work/os144/packed-context-overlay.bin').read_bytes()
RAM,PTR,BSS=0x47be0000,0x47be1000,0x47be1004
rows={x['raw_scale']:x['pitch_classes'] for x in json.loads(Path('outputs/Digitone-OS1.44-scale-map.json').read_text())['scales']}
def oracle(note,word):
 raw=((word>>7)&63)-1;root=word&127
 if not word>>31 or raw not in rows or not 0<=note<128:return note
 return min((n for n in range(128) if (n-root)%12 in rows[raw]),key=lambda n:(abs(n-note),n))
"""
s=s.replace("def install(s):",prefix+"\ndef install(s):"+"""
 uc=s.m.uc;s.m.ensure(RAM);uc.mem_write(RAM,bytes(0x20000));uc.mem_write(RAM,blob)
 uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1))
 s.m.install_isa_patches_scoped(blob[:info['code_bytes']],RAM)
 guard=bytes(uc.mem_read(RAM,0x20000));r['guard_sha256']=hashlib.sha256(guard).hexdigest()
 r['helper_mode']=MODE;r['scenario']=SCENARIO;r['custom_arp_hooks_installed']=MODE=='helpers'
 r['fixtures'].append({'kind':'PC ready header/code setup after settled stock boot','startup_hook_installed':False,'helper_image_sha256':hashlib.sha256(blob).hexdigest(),'owner_pointer':hex(BSS-0x14100)})
 if MODE=='helpers':
  for h in port['hooks']:
   address=int(h['site'],16);assert bytes(uc.mem_read(address,h['length']))==bytes.fromhex(h['stock_bytes'])
   op='4eb9' if h['name'] in ['before','copy'] else '4ef9'
   uc.mem_write(address,bytes.fromhex(op)+u32(h['helper'])+bytes.fromhex('4e71')*((h['length']-6)//2))
 def storage_write(uc,access,a,n,value,d):
  pc=uc.reg_read(UC_M68K_REG_PC)
  if not (PTR<=a and a+n<=BSS+0xb70 and RAM<=pc<RAM+info['code_bytes']):
   r.setdefault('unexpected_storage_writes',[]).append({'pc':hex(pc),'address':hex(a),'size':n})
 for alias in range(8):
  lo=RAM+alias*DDR
  def watch(uc,access,a,n,value,d,lo=lo):
   physical=RAM+(a-lo)
   if RAM<=physical<RAM+0x20000:storage_write(uc,access,physical,n,value,d)
  uc.hook_add(UC_HOOK_MEM_WRITE,watch,begin=lo,end=lo+0x1ffff)
 for name in ['producer_capture','allocate_clear','before','after','caller_commit','pitch_hook','copy','first_copy']:
  address=info['layout'][name]['address']
  s.at(address,lambda uc,pc,n,d,name=name:r.setdefault('helper_hits',collections.Counter()).update([name]))
 def captured(uc,pc,n,d):
  e=uc.reg_read(UC_M68K_REG_A2);track=uc.reg_read(UC_M68K_REG_D4);back=uc.reg_read(UC_M68K_REG_A3)
  if track>=4:return
  root=bytes(uc.mem_read(back+track*0x3d0+0x3cb,1))[0];raw=struct.unpack('b',uc.mem_read(back+track*0x3d0+0x3ce,1))[0]
  expected=(0x80000000|root|((raw+1)<<7)|(track<<13)) if root<128 and -1<=raw<35 else 0
  slot=None
  if 0<=e-0x419ebe2c<9216 and (e-0x419ebe2c)%72==0:slot=BSS+32+(e-0x419ebe2c)//72*4
  elif 0<=e-0x419f182c<288 and (e-0x419f182c)%72==0:slot=BSS+2592+(e-0x419f182c)//72*4
  r.setdefault('capture_checks',[]).append({'ms':s.now_ms(),'event':hex(e),'generation':generations[e],'track':track,'backing':hex(back),'expected':hex(expected),'actual':hex(rd(uc,slot)) if slot else None,'matches':rd(uc,slot)==expected if slot and MODE=='helpers' else None})
 s.at(0x400947f4,captured)
 def metadata_slot(e):
  if 0<=e-0x419ebe2c<9216 and (e-0x419ebe2c)%72==0:return BSS+32+(e-0x419ebe2c)//72*4
  if 0<=e-0x419f182c<288 and (e-0x419f182c)%72==0:return BSS+2592+(e-0x419f182c)//72*4
  return None
 def allocation_cleared(uc,pc,n,d):
  e=uc.reg_read(UC_M68K_REG_A0);slot=metadata_slot(e)
  if slot:
   r['allocation_clear_checks']=r.get('allocation_clear_checks',0)+1
   if rd(uc,slot)!=0:r.setdefault('allocation_clear_failures',[]).append({'ms':s.now_ms(),'event':hex(e),'actual':hex(rd(uc,slot))})
 s.at(0x47be055a,allocation_cleared)
 copy_pending={}
 def copy_enter(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);dst,src,length=struct.unpack('>3I',uc.mem_read(sp,12));slot=metadata_slot(src)
  copy_pending[pc]={'ms':s.now_ms(),'site':hex(pc),'destination':hex(dst),'source':hex(src),'bytes':length,'expected':rd(uc,slot) if slot else 0}
 def copy_exit(uc,pc,n,d):
  item=copy_pending.pop(pc-6,None)
  if item:
   slot=metadata_slot(int(item['destination'],16));item['actual']=rd(uc,slot) if slot else None;item['matches']=item['actual']==item['expected'] if slot and MODE=='helpers' else None
   r.setdefault('copy_checks',[]).append(item)
 for pc in [0x40093d46,0x4009418a]:s.at(pc,copy_enter);s.at(pc+6,copy_exit)
 def quantize(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);note=rd(uc,sp+4);word=rd(uc,sp+8)
  r.setdefault('quantizer_calls',[]).append({'ms':s.now_ms(),'event':hex(uc.reg_read(UC_M68K_REG_A3)),'note':note,'word':hex(word),'expected':oracle(note,word)})
 s.at(info['layout']['quantize']['address'],quantize)
 def pitch_output(uc,pc,n,d):
  e=uc.reg_read(UC_M68K_REG_A3)
  r.setdefault('pitch_outputs',[]).append({'ms':s.now_ms(),'event':hex(e),'generation':generations[e],'fixed_pitch':uc.reg_read(UC_M68K_REG_D6),'fields':list(struct.unpack('>18I',uc.mem_read(e,72)))})
 s.at(0x4009e890,pitch_output)
 r['_guard']=guard.hex()
""")
s=s.replace("mark('stopped selected 2')","""mark('stopped selected 2')
 if SCENARIO=='scale':
  receiving=int(r['marks'][0]['backing'],16);source=rd(session.m.uc,CURRENT)
  for back,root,raw in [(source,61,0),(receiving,59,5)]:
   for t in range(4):session.m.uc.mem_write(back+t*0x3d0+0x3cb,bytes([root]));session.m.uc.mem_write(back+t*0x3d0+0x3ce,bytes([raw]))
  r['fixtures'].append({'kind':'Root/scale PC pattern field fixture','source_backing':hex(source),'source_root':61,'source_raw':0,'receiving_backing':hex(receiving),'receiving_root':59,'receiving_raw':5,'event_fields_or_eligibility_injected':False})""")
s=s.replace("mark('initial')","""mark('initial')
 if SCENARIO=='early-scale':
  source=0x40813531;receiving=rd(session.m.uc,CURRENT)
  for back,root,raw in [(source,61,0),(receiving,59,5)]:
   for t in range(4):session.m.uc.mem_write(back+t*0x3d0+0x3cb,bytes([root]));session.m.uc.mem_write(back+t*0x3d0+0x3ce,bytes([raw]))
  r['fixtures'].append({'kind':'Root/scale fields before stopped pattern-2 selection','source_backing':hex(source),'source_root':61,'source_raw':0,'receiving_backing':hex(receiving),'receiving_root':59,'receiving_raw':5,'event_fields_or_eligibility_injected':False})""",1)
s=s.replace("if event in pending:record('queued_event_released'", """f=r.get('delayed_queue_fixture')
  if f and hex(event)==f['event'] and generations[event]==f['generation']:
   r['delayed_release_observed']={'ms':s.now_ms(),'event':hex(event),'generation':generations[event],'fields':list(struct.unpack('>18I',uc.mem_read(event,72))),'return_to':hex(rd(uc,uc.reg_read(UC_M68K_REG_A7))),**state(uc)}
  if event in pending:record('queued_event_released'""")
# Export audio evidence and guards before closing the continuously executed engine.
s=s.replace("if session:session.close()", """if session:
  uc=session.m.uc;now=bytes(uc.mem_read(RAM,0x20000));guard=bytes.fromhex(r.pop('_guard'))
  r['storage_checks']={'code_intact':now[:len(blob)]==blob,'unused_region_intact':now[:PTR-RAM]==guard[:PTR-RAM] and now[BSS+0xb70-RAM:]==guard[BSS+0xb70-RAM:],'no_unexpected_writes':not r.get('unexpected_storage_writes',[])}
  r['audio_bytes']=len(session.pcm);r['audio_sha256']=hashlib.sha256(session.pcm).hexdigest();r['snapshot_sha256']=hashlib.sha256(Path(paths.gui).read_bytes()).hexdigest()
  session.close()""")
exec(compile(s,'continuous-1.44-hooks','exec'))
