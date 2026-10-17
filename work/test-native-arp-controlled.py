"""Controlled native-engine fixtures; field preconditions explicit, PC RAM only."""
import pathlib
exec(pathlib.Path('work/test-native-arp-overlays.py').read_text().split('def run(mode):')[0])
from emu.harness import call
result={'cases':[],'failure':None,'firmware_modified':False,'preconditions':'Explicit event/cache/selection fields, private ready header and root/scale in restored native engine. Not proof of producer ordering or startup.'}
def installed(session):
 m=session.m;m.ensure(RAM);uc=m.uc
 uc.mem_write(RAM,blob);uc.mem_write(PTR,bytes(0xb74));uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1));m.install_isa_patches_scoped(blob,RAM)
session=Session(paths.gui,syx=str(SYX),ddr=DDR,on_machine=installed)
uc=session.m.uc;stack=0x47fdff00;session.m.ensure(stack)
def invoke(name,args):
 v=call(session.m,layout[name]['address'],args,stack_top=stack,limit=100000)
 assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0,(name,hex(uc.reg_read(UC_M68K_REG_PC)))
 return v
try:
 comparisons=0
 for raw in [-1,0,1,5,17,34]:
  for root in [0,60,127]:
   word=0x80000000|root|((raw+1)<<7)
   for note in [0,1,59,60,61,62,64,126,127]:
    actual=invoke('quantize',[note,word]);expected=oracle(note,word);assert actual==expected,(raw,root,note,actual,expected);comparisons+=1
 result['quantizer_comparisons']=comparisons
 for track in range(4):
  backing=0x47bd0000;session.m.ensure(backing)
  uc.mem_write(backing+track*0x3d0+0x3cb,bytes([60+track]));uc.mem_write(backing+track*0x3d0+0x3ce,b'\0')
  word=invoke('capture',[backing,track]);expected=0x80000080|(60+track)|(track<<13);assert word==expected
  event=0x4199da94+track*72;identity=0x419c38c0+track*0x504
  # Compare producer hook at its actual stock continuation, including all registers.
  regs=[UC_M68K_REG_D0+i for i in range(8)]+[UC_M68K_REG_A0+i for i in range(8)]
  site=0x40093ef4;original=bytes(uc.mem_read(site,8));event_before=bytes(uc.mem_read(event,72))
  uc.reg_write(UC_M68K_REG_SR,0x2700);uc.reg_write(UC_M68K_REG_A7,stack);uc.reg_write(UC_M68K_REG_A2,event);uc.reg_write(UC_M68K_REG_A3,backing);uc.reg_write(UC_M68K_REG_D4,track)
  startregs={r:uc.reg_read(r) for r in regs}
  uc.mem_write(site,bytes.fromhex('4ef9')+u32(layout['producer_capture']['address'])+bytes.fromhex('4e71'))
  uc.emu_start(site,0x40093efc,count=100000);patched_producer={r:uc.reg_read(r) for r in regs};producer_sr=uc.reg_read(UC_M68K_REG_SR);event_after=bytes(uc.mem_read(event,72))
  assert uc.reg_read(UC_M68K_REG_PC)==0x40093efc
  uc.mem_write(site,original);uc.mem_write(event,event_before)
  for r,v in startregs.items():uc.reg_write(r,v)
  uc.reg_write(UC_M68K_REG_SR,0x2700);uc.emu_start(site,0x40093efc,count=100000)
  assert patched_producer=={r:uc.reg_read(r) for r in regs} and producer_sr==uc.reg_read(UC_M68K_REG_SR)
  assert event_after==bytes(uc.mem_read(event,72))
  assert rd(uc,BSS+32+track*4)==word
  record=BSS+0xb30+track*16;assert invoke('begin',[record])==1;assert invoke('commit',[record,identity,word,track])==1
  data=bytearray(72)
  for off,value in [(0,0),(4,1),(8,track),(40,1<<19),(64,identity)]:data[off:off+4]=u32(value)
  uc.mem_write(event,bytes(data));uc.mem_write(0x41345f08+track*72,bytes(data));uc.mem_write(0x41344530+track*40+24,u32(identity));uc.mem_write(0x41345620+track*4,u32(1))
  note=61+track;after=invoke('pitch',[event,note]);assert after==oracle(note,word)
  assert bytes(uc.mem_read(event,72))==bytes(data)
  # Execute actual hook and displaced stock instructions to fixed-point boundary.
  pc=0x4009df9a;original=bytes(uc.mem_read(pc,8));uc.mem_write(pc,bytes.fromhex('4ef9')+u32(layout['pitch_hook']['address'])+bytes.fromhex('4e71'))
  regs=[UC_M68K_REG_D0+i for i in range(8)]+[UC_M68K_REG_A0+i for i in range(8)]
  uc.reg_write(UC_M68K_REG_SR,0x2700);uc.reg_write(UC_M68K_REG_A7,stack);uc.reg_write(UC_M68K_REG_A3,event);uc.reg_write(UC_M68K_REG_D6,note)
  before={r:uc.reg_read(r) for r in regs};uc.emu_start(pc,0x4009dfa8,count=100000);patched={r:uc.reg_read(r) for r in regs};patched_sr=uc.reg_read(UC_M68K_REG_SR)
  assert uc.reg_read(UC_M68K_REG_PC)==0x4009dfa8
  uc.mem_write(pc,original)
  for r,v in before.items():uc.reg_write(r,v)
  uc.reg_write(UC_M68K_REG_SR,0x2700);uc.emu_start(pc,0x4009dfa8,count=100000);baseline={r:uc.reg_read(r) for r in regs}
  assert patched[UC_M68K_REG_D6]==after<<16
  assert all(patched[r]==baseline[r] for r in regs if r!=UC_M68K_REG_D6)
  assert patched_sr==uc.reg_read(UC_M68K_REG_SR)
  uc.mem_write(record+12,u32(0));assert invoke('pitch',[event,note])==note
  result['cases'].append({'track':track,'captured':hex(word),'before':note,'after':after,'fixed_point':hex(patched[UC_M68K_REG_D6]),'other_registers_and_SR_match_stock':True,'producer_registers_SR_and_event_match_stock':True,'invalid_context_falls_back':True})
 result['code_intact']=bytes(uc.mem_read(RAM,len(blob)))==blob
 result['firmware_sha256']=hashlib.sha256(SYX.read_bytes()).hexdigest()
 print('PASS',comparisons,'quantizer comparisons and',len(result['cases']),'native pitch hook tracks',flush=True)
except BaseException as exc:
 result['failure']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()};print(result['failure']['traceback'],flush=True)
finally:
 session.close();pathlib.Path('outputs/Digitone-native-arp-controlled-results.json').write_text(json.dumps(result,indent=2))
