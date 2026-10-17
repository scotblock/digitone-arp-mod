from pathlib import Path
exec(Path('work/os144-stock-env.py').read_text())
import json,traceback,collections
from emu.harness import Machine,call
from emu import snapshot
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import *
port=json.loads(Path('work/os144/helper-port.json').read_text());info=json.loads(Path('work/packed-context-build.json').read_text())
captures=json.loads(Path('outputs/Digitone-OS1.44-caller-state-capture.json').read_text())
assert captures['failure'] is None
blob=Path('work/os144/packed-context-overlay.bin').read_bytes();stock=Path('work/os144/section-3.bin').read_bytes()
RAM,PTR,BSS,PRIVATE_STACK=0x47be0000,0x47be1000,0x47be1004,0x47fdff00
regs=[('D'+str(i),UC_M68K_REG_D0+i) for i in range(8)]+[('A'+str(i),UC_M68K_REG_A0+i) for i in range(8)]
result={'firmware_modified':False,'startup_hook_installed':False,'cases':[],'failure':None,'limits':['Stock-produced guest snapshots replayed as bounded instruction slices, without the original timer, DMA and scheduler host components.','Private header and metadata candidate are supplied by a PC fixture; event/selection fields are not manufactured.','Only caller/selector/commit/pitch hooks are temporarily installed; no complete startup/playback integration.']}
OUT=Path('outputs/Digitone-OS1.44-real-selector-caller.json')
def invoke(m,name,args):
 value=call(m,info['layout'][name]['address'],args,stack_top=PRIVATE_STACK,limit=100000)
 assert m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
 return value
def replay(capture,mode,word_override=None,fault=None):
 m=Machine(ddr=DDR);snapshot.restore_into(m,capture['path']);uc=m.uc
 m.install_isa_patches_scoped(stock,0x40000400)
 m.ensure(RAM);m.ensure(PRIVATE_STACK);uc.mem_write(RAM,blob);m.install_isa_patches_scoped(blob[:info['code_bytes']],RAM)
 uc.mem_write(PTR,bytes(0xb74));uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1))
 saved={reg:uc.reg_read(reg) for _,reg in regs};sr=uc.reg_read(UC_M68K_REG_SR)
 event=int(capture['event'],16);track=rd(uc,event+8);pattern=rd(uc,0x4138f214)
 word=invoke(m,'capture',[pattern,track])
 if word_override is not None:word=word_override
 invoke(m,'candidate_store',[event,word])
 if fault in ['magic','version','size','ready']:uc.mem_write(BSS+['magic','version','size','ready'].index(fault)*4,u32(0))
 if fault=='null_pointer':uc.mem_write(PTR,u32(0))
 for reg,value in saved.items():uc.reg_write(reg,value)
 uc.reg_write(UC_M68K_REG_SR,sr)
 if mode=='helpers':
  for h in port['hooks']:
   if h['name'] not in ['before','caller_commit','pitch_hook']:continue
   addr=int(h['site'],16);assert bytes(uc.mem_read(addr,h['length']))==bytes.fromhex(h['stock_bytes'])
   opcode='4eb9' if h['name']=='before' else '4ef9'
   uc.mem_write(addr,bytes.fromhex(opcode)+u32(h['helper'])+bytes.fromhex('4e71')*((h['length']-6)//2))
 boundaries=[];hits=collections.Counter();transfers=[]
 def boundary(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7)
  boundaries.append({'pc':hex(pc),'regs':{name:uc.reg_read(reg) for name,reg in regs},'SR':uc.reg_read(UC_M68K_REG_SR),'stack64':bytes(uc.mem_read(sp,64)).hex(),'event72':bytes(uc.mem_read(event,72)).hex()})
 for pc in [0x4009e694,0x4009e738,0x4009e890]:uc.hook_add(UC_HOOK_CODE,boundary,begin=pc,end=pc)
 for name in ['before','after','caller_commit','pitch_hook','commit','read','quantize']:
  address=info['layout'][name]['address'];uc.hook_add(UC_HOOK_CODE,lambda uc,pc,n,d,name=name:hits.update([name]),begin=address,end=address)
 uc.hook_add(UC_HOOK_CODE,lambda uc,pc,n,d:transfers.append({'pc':hex(pc),'track':uc.reg_read(UC_M68K_REG_D0)}),begin=0x40097a94,end=0x40097a94)
 uc.emu_start(0x4009e668,0x4009d7d8,count=1000000)
 assert uc.reg_read(UC_M68K_REG_PC)==0x4009d7d8,hex(uc.reg_read(UC_M68K_REG_PC))
 boundary(uc,0x4009d7d8,0,None)
 assert bytes(uc.mem_read(RAM,len(blob)))==blob
 stock_regions={name:hashlib.sha256(bytes(uc.mem_read(address,length))).hexdigest() for name,address,length in [('event_pool',0x419ebe2c,9216),('physical_cache',0x419f182c,288),('selected_records',0x413915f4,160),('acceptance_cache',0x41392fcc,288),('selection_gates',0x413926e4,16),('caller_globals',0x41392fac,32)]}
 observed={'mode':mode,'captured_word':hex(word),'boundaries':boundaries,'selector_entries':transfers,'helper_hits':dict(hits),'metadata_hex':bytes(uc.mem_read(BSS,0xb70)).hex(),'event_final':bytes(uc.mem_read(event,72)).hex(),'stock_region_hashes':stock_regions,'new_faults':m.faults}
 m.close();return observed
try:
 for capture in captures['caller_states']:
  assert hashlib.sha256(Path(capture['path']).read_bytes()).hexdigest()==capture['sha256']
  case={'capture':capture,'runs':[]};result['cases'].append(case)
  for mode in ['stock','helpers']:case['runs'].append(replay(capture,mode))
  a,b=case['runs'];case['boundaries_identical']=a['boundaries']==b['boundaries'];case['selector_entries_identical']=a['selector_entries']==b['selector_entries'];case['event_final_identical']=a['event_final']==b['event_final']
  case['stock_regions_identical']=a['stock_region_hashes']==b['stock_region_hashes']
  assert case['boundaries_identical'] and case['selector_entries_identical'] and case['event_final_identical'] and case['stock_regions_identical'],(capture['event'],[(x['pc'],y['pc'],{k:(x['regs'][k],y['regs'][k]) for k in x['regs'] if x['regs'][k]!=y['regs'][k]},x['SR'],y['SR'],x['stack64']==y['stack64']) for x,y in zip(a['boundaries'],b['boundaries'])])
  print('PASS',capture['fields'][:4],a['captured_word'],b['helper_hits'],flush=True);OUT.write_text(json.dumps(result,indent=2))
 result['passed']=True
except BaseException:
 result['failure']=traceback.format_exc();print(result['failure'],flush=True)
finally:
 result['firmware_sha256_after']=hashlib.sha256(SYX.read_bytes()).hexdigest();OUT.write_text(json.dumps(result,indent=2))
