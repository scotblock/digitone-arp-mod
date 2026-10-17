from pathlib import Path
import sys,json,struct,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from dt2.container import decode_syx
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import *
u32=lambda n:struct.pack('>I',n&0xffffffff)
raw=Path('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx').read_bytes();wire=decode_syx('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx');image=Path('work/os144/startup-bootstrap-image.bin').read_bytes()
packets=[];p=0
while p<len(raw):q=raw.index(247,p+1);packets.append(raw[p:q+1]);p=q+1
STACK=0x47fdff00;MSG=0x47f20000

def make():
 m=Machine(ddr=0x08000000);m.load(image,0x80000400);m.install_isa_patches_scoped(image,0x80000400);m.install_exceptions()
 for a in [STACK,MSG,0xec074000,0xfc04c000,0xfc048000,0xfc050000]:m.ensure(a)
 m.load(bytes(len(wire)+512),0x40000000);m.flash=bytearray(b'\xa6'*(4*1024*1024));m.actions=[]
 def fixture(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);ret,*args=struct.unpack('>IIII',uc.mem_read(sp,16));result={0x800030f4:0xef,0x80003108:0x4018,0x800030ce:256,0x800030e2:0x10000}.get(pc,0)
  if pc==0x80003076:
   a=args[0];m.actions.append(('erase',a));m.flash[a:a+0x40000]=b'\xff'*0x40000
  elif pc==0x8000300a:
   a,count,src=args;assert 0x40000008<=src and src+count<=0x40000000+len(wire)
   m.actions.append(('program',a,count,src));m.flash[a:a+count]=bytes(uc.mem_read(src,count))
  uc.reg_write(UC_M68K_REG_D0,result);uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_PC,ret)
 for pc in [0x8000181c,0x80001cd0,0x800017ec,0x80001b0a,0x80001bf0,0x800030f4,0x80003108,0x800030ce,0x800030e2,0x8000311c,0x80003076,0x8000300a]:m.uc.hook_add(UC_HOOK_CODE,fixture,begin=pc,end=pc)
 call(m,0x80003bf2,[],stack_top=STACK,limit=10000)
 return m

def irq_frame(m,p):
 for b in p:
  m.uc.mem_write(0xec074004,b'\x01');m.uc.mem_write(0xec07400c,bytes([b]));m.uc.reg_write(UC_M68K_REG_SR,0x2700);m.uc.reg_write(UC_M68K_REG_A7,STACK)
  m.uc.mem_write(STACK,struct.pack('>HHI',0x42d4,0x2700,0xdeadbee0));m.uc.emu_start(0x80003a24,0xdeadbee0,count=10000);assert m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0

r={'PC_only':True,'cases':[],'failure':None,'limits':['SRAM bootstrap instructions execute. First/end frames traverse stock UART9 IRQ byte parser; data frames start at its recovered receiver callback. Full UART pacing/overrun and panel selection are not joined in one continuous run.','Display/flash identity/geometry/erase/program are fixtures. No hardware writes or physical recovery trial.']}
try:
 for name in ['valid_E03','bad_whole_checksum','missing_end','bad_packet_checksum']:
  m=make();irq_frame(m,packets[0]);stream=list(packets[1:-1])
  if name=='bad_packet_checksum':b=bytearray(stream[0]);b[-2]^=1;stream[0]=bytes(b)
  for frame in stream:m.uc.mem_write(MSG,frame);call(m,0x80003820,[MSG+6],stack_top=STACK,limit=100000)
  if name!='missing_end':irq_frame(m,packets[-1])
  phase=m.uc.mem_read(0x800078e2,1)[0];complete=int.from_bytes(m.uc.mem_read(0x80008b7e,4),'big');error=int.from_bytes(m.uc.mem_read(0x80008a7a,4),'big')
  exact=bytes(m.uc.mem_read(0x40000000,len(wire)))==wire
  if name in ['valid_E03','bad_whole_checksum']:assert phase==3 and complete==2 and exact
  else:assert phase!=3 and error==(1 if name=='bad_packet_checksum' else 0)
  if name=='bad_whole_checksum':m.uc.mem_write(0x40000000+200,b'\xff')
  if phase==3:
   boundary=0x80004116 if name=='valid_E03' else 0x80003df4
   h=m.uc.hook_add(UC_HOOK_CODE,lambda uc,pc,n,d:uc.emu_stop(),begin=boundary,end=boundary)
   call(m,0x80003d26,[],stack_top=STACK,limit=5000000);m.uc.hook_del(h);assert m.uc.reg_read(UC_M68K_REG_PC)==boundary
  if name=='valid_E03':
   logical=int.from_bytes(wire[:4],'big');assert m.flash[0x80000:0x80000+logical]==wire[8:8+logical] and m.flash[0x380000:0x380200]==b'\xa6'*512
   assert len([a for a in m.actions if a[0]=='erase'])==5 and len([a for a in m.actions if a[0]=='program'])==2472
  else:assert not m.actions
  r['cases'].append({'name':name,'phase':phase,'completion_state':complete,'error_flag':error,'exact_received_stream':exact,'erase_calls':sum(a[0]=='erase' for a in m.actions),'program_calls':sum(a[0]=='program' for a in m.actions),'program_end':hex(m.actions[-1][1]+m.actions[-1][2]) if m.actions and m.actions[-1][0]=='program' else None})
  print('PASS startup DIN',name,flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc()+' PC='+hex(m.uc.reg_read(UC_M68K_REG_PC));print(r['failure'],flush=True)
Path('outputs/Digitone-E03-startup-DIN-checks.json').write_text(json.dumps(r,indent=2))
if r['failure']:raise SystemExit(1)
