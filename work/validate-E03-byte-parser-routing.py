exec(open('work/E03-receiver-test-environment.py').read())
PARSER,RING,REALTIME,RUN=0x418f9f8c,0x429b0000,0x429f1000,0x47f40000
loop=bytes.fromhex('246f0004242f0008266f000c2f0b4280101a2f004eb9400e7eca508f538266ec4e75')
r={'PC_only':True,'cases':[],'limits':['Kernel enqueue/wakeup are collected; each complete frame is delivered synchronously to the stock manufacturer/device dispatcher.','UART/USB peripheral ingress and actual scheduling are not executed.']}
try:
 for name in ['complete_E03','wrong_manufacturer','wrong_device']:
  m=machine();
  for a in [RUN,PARSER,REALTIME,0x418e9f88,0x431f2dd0,0x431f4dd0]+list(range(RING,RING+0x29000,4096)):m.ensure(a)
  m.uc.mem_write(RUN,loop)
  m.uc.mem_write(PARSER,u32(RING)+u32(REALTIME)+bytes(44));m.uc.mem_write(0x418e9f88,u32(0))
  def wake(uc,pc,n,d):
   sp=uc.reg_read(UC_M68K_REG_A7);ret=int.from_bytes(uc.mem_read(sp,4),'big');uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_PC,ret)
  m.uc.hook_add(UC_HOOK_CODE,wake,begin=0x400019a0,end=0x400019a0)
  routed=0;total=0;t=time.time()
  stream=packets if name=='complete_E03' else packets[:3]
  for p in stream:
   p=bytearray(p)
   if name=='wrong_manufacturer':p[3]^=1
   if name=='wrong_device':p[4]=0x0e
   m.uc.mem_write(MSG,bytes(p));before=len(m.notes)
   call(m,RUN,[MSG,len(p),PARSER],stack_top=STACK,limit=100000);assert m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
   events=m.notes[before:];assert len(events)==1
   count,ptr=struct.unpack('>II',bytes.fromhex(events[0]['message'])[:8]);assert count==len(p) and bytes(m.uc.mem_read(ptr,count))==bytes(p)
   del m.notes[before:]
   call(m,0x400eaac8,[ptr,count,8],stack_top=STACK,limit=100000);assert m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
   routed+=1;total+=len(p)
  complete=call(m,0x400eab94,[],stack_top=STACK,limit=10000)
  if name=='complete_E03':assert complete==DATA and bytes(m.uc.mem_read(DATA,len(wire)))==wire and sum(x['type']==18 for x in m.notes)==1
  else:assert complete==0 and not m.notes
  r['cases'].append({'name':name,'bytes_parsed':total,'frames_routed':routed,'state':state(m),'completed_buffer':hex(complete),'seconds':time.time()-t});print('PASS',name,total,flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc()+' PC='+hex(m.uc.reg_read(UC_M68K_REG_PC));print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-byte-parser-routing-checks.json').write_text(json.dumps(r,indent=2))


