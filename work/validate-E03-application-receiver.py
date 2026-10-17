from pathlib import Path
import sys,json,struct,time,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import *
from dt2.container import decode_syx
stock=Path('work/os144/section-3.bin').read_bytes();raw=Path('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx').read_bytes();wire=decode_syx('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx')
packets=[];i=0
while i<len(raw):j=raw.index(247,i+1);packets.append(raw[i:j+1]);i=j+1
STATE,DATA,MSG,STACK=0x40325ee0,0x40325f00,0x47f20000,0x47fdff00
u32=lambda x:struct.pack('>I',x&0xffffffff)
def machine():
 m=Machine(ddr=0x08000000);m.load(stock,0x40000400);m.install_isa_patches_scoped(stock,0x40000400)
 for a in [STATE,0x40400000,MSG,STACK,0x419950a4]:m.ensure(a)
 m.uc.mem_write(STATE,bytes(32));m.uc.mem_write(DATA,b'\xa5'*(len(wire)+512));m.notes=[]
 def notify(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);ret,q,msg=struct.unpack('>III',uc.mem_read(sp,12));m.notes.append({'type':bytes(uc.mem_read(msg,1))[0],'message':bytes(uc.mem_read(msg,9)).hex()})
  uc.reg_write(UC_M68K_REG_D0,0);uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_PC,ret)
 m.uc.hook_add(UC_HOOK_CODE,notify,begin=0x40001cda,end=0x40001cda)
 call(m,0x400ed8dc,[],stack_top=STACK,limit=10000)
 return m
def feed(m,p):
 m.uc.mem_write(MSG,bytes(p));v=call(m,0x400e9fcc,[MSG,len(p)],stack_top=STACK,limit=100000);assert m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0;return v
def state(m):return {'phase':m.uc.mem_read(STATE,1)[0],'received':int.from_bytes(m.uc.mem_read(STATE+12,4),'big'),'total':int.from_bytes(m.uc.mem_read(STATE+8,4),'big'),'notices':[x['type'] for x in m.notes]}
r={'PC_only':True,'cases':[],'failure':None,'limits':['Full framed messages supplied to the actual application callback; UART/USB byte ingress, kernel queue delivery and natural OS-upgrade UI entry not executed.','Only notification queue enqueue is stubbed to collect stock-produced messages; packet decode/counters/completion and content checksum execute unchanged.','Hardware/model timing is outside this test.']};start=time.monotonic()
try:
 m=machine()
 for i,p in enumerate(packets):
  feed(m,p)
  if i%2000==0:print('received',i,'of',len(packets),flush=True)
 assert state(m)['phase']==3 and state(m)['received']==len(packets)-2
 assert bytes(m.uc.mem_read(DATA,len(wire)))==wire
 assert bytes(m.uc.mem_read(DATA+len(wire),512))==b'\xa5'*512
 assert m.notes[-1]['type']==0x12 and sum(x['type']==0x12 for x in m.notes)==1
 assert call(m,0x400eab94,[],stack_top=STACK,limit=10000)==DATA
 checked=call(m,0x400eb76c,[DATA],stack_top=STACK,limit=5000000);print('checksum return',hex(checked),'PC',hex(m.uc.reg_read(UC_M68K_REG_PC)),flush=True);assert checked==1
 r['cases'].append({'kind':'full valid application session','packets_executed':len(packets)-2,'received_stream_exact':True,'content_checksum_accepted':True,'state':state(m),'notices_count':len(m.notes)})
 # Persist received bytes for the subsequent stock updater check, without a generated completed-state fixture.
 Path('work/os144/E03-actual-received-stream.bin').write_bytes(bytes(m.uc.mem_read(DATA,len(wire))))
 for name in ['checksum','sequence','bad_terminator','early_end','gate_off','wrong_seed','bad_end_count']:
  q=machine();feed(q,packets[0]);p=bytearray(packets[1])
  if name=='checksum':p[-2]^=1
  if name=='sequence':p[9]^=1
  if name=='bad_terminator':p[-1]=246
  if name=='gate_off':call(q,0x400ed8ea,[],stack_top=STACK,limit=10000)
  if name=='wrong_seed':p=bytearray(packets[0]);p[8]^=1
  if name=='bad_end_count':p=bytearray(packets[-1]);p[-2]^=1
  feed(q,packets[-1] if name=='early_end' else p)
  if name not in ['early_end','bad_end_count']:feed(q,packets[-1])
  assert not any(x['type']==0x12 for x in q.notes),name
  assert call(q,0x400eab94,[],stack_top=STACK,limit=10000)==0,name
  r['cases'].append({'kind':'invalid/incomplete application reception','case':name,'no_complete_notice':True,'no_completed_buffer':True,'state':state(q)})
 # A mid-stream stop produces no completion; a new start resets actual counters.
 q=machine()
 for p in packets[:103]:feed(q,p)
 assert not any(x['type']==0x12 for x in q.notes) and call(q,0x400eab94,[],stack_top=STACK,limit=10000)==0
 before=state(q);feed(q,packets[0]);assert state(q)['received']==0 and state(q)['phase']==1
 r['cases'].append({'case':'interrupt and restart','before':before,'after':state(q),'passed':True})
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc();print(r['failure'],flush=True)
r['seconds']=time.monotonic()-start;Path('outputs/Digitone-OS1.44E03-application-receive-checks.json').write_text(json.dumps(r,indent=2));print('result',r.get('passed'),r['seconds'],flush=True)


