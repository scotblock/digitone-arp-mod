from pathlib import Path
import collections,math
exec(Path('work/E03-receiver-test-environment.py').read_text())
r={'PC_only':True,'cases':[],'failure':None,'limits':['Acquired framed messages enter the actual application callback, with kernel enqueue collected at a stub.','Hardware flash identity/geometry and factory-record read are explicit fixtures.','Stock updater instructions run to the programming-complete boundary; flash and display/string operations are simulated.','Actual USB/UART ingress, application queue consumption/user confirmation and reset completion are not executed.']}
try:
 for name in ['valid','bad_final_packet_checksum','bad_end_seed','bad_end_count','missing_last_packet','missing_end','container_corruption_with_valid_packet_checksums']:
  m=machine();stream=[bytes(p) for p in packets]
  if name=='bad_final_packet_checksum':b=bytearray(stream[-2]);b[-2]^=1;stream[-2]=bytes(b)
  if name=='bad_end_seed':b=bytearray(stream[-1]);b[8]^=1;stream[-1]=bytes(b)
  if name=='bad_end_count':b=bytearray(stream[-1]);b[14]^=1;stream[-1]=bytes(b)
  if name=='missing_last_packet':del stream[-2]
  if name=='missing_end':del stream[-1]
  if name=='container_corruption_with_valid_packet_checksums':
   b=bytearray(stream[100]);b[30]^=1;body=b[1:-1];seed=packets[0][8];b[-2]=(seed+sum(v^(seed+j) for j,v in enumerate(body[6:125])))&127;stream[100]=bytes(b)
  for p in stream:feed(m,p)
  complete=call(m,0x400eab94,[],stack_top=STACK,limit=10000)
  case={'name':name,'state':state(m),'completion_notices':sum(x['type']==0x12 for x in m.notes),'completed_buffer':hex(complete)}
  if name not in ['valid','container_corruption_with_valid_packet_checksums']:
   assert complete==0 and case['completion_notices']==0;case['no_updater_candidate']=True;r['cases'].append(case);print('PASS',name,flush=True);continue
  assert complete==DATA and case['completion_notices']==1
  csum=call(m,0x400eb76c,[DATA],stack_top=STACK,limit=5000000);case['stock_content_checksum_return']=csum
  # Connect this same stock-produced receive buffer directly to the stock updater entry.
  for a in [0x47f18000,0,0x41900000,0x41300000]:m.ensure(a)
  m.uc.mem_write(0x402296f0,u32(0));m.uc.mem_write(0,u32(0));m.uc.mem_write(0x47f18000,bytes(16))
  flash=bytearray(b'\xa6'*(4*1024*1024));actions=[];hw=[]
  def stub(uc,pc,n,d):
   sp=uc.reg_read(UC_M68K_REG_A7);ret,*args=struct.unpack('>IIII',uc.mem_read(sp,16));result=0
   if pc==0x400fccf0:assert args[1]==5;uc.mem_write(args[0],bytes.fromhex('ef40180000'));hw.append('supplied JEDEC ef/4018')
   elif pc==0x400fd552:result=256
   elif pc==0x400fd566:result=0x10000
   elif pc==0x400f578a:uc.mem_write(args[0],bytes(16))
   elif pc==0x400f5626:uc.mem_write(args[0],u32(0x47f18000))
   elif pc==0x400fcb2a:
    a=args[0];actions.append(('erase',a));flash[a:a+0x10000]=b'\xff'*0x10000
   elif pc==0x400fd402:
    a,count,src=args;assert DATA+8<=src and src+count<=DATA+8+int.from_bytes(m.uc.mem_read(DATA,4),'big')
    actions.append(('program',a,count,src));flash[a:a+count]=bytes(uc.mem_read(src,count))
   uc.reg_write(UC_M68K_REG_D0,result);uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_PC,ret)
  for pc in [0x400fccf0,0x400fd552,0x400fd566,0x400f578a,0x400f5626,0x400fcb2a,0x400fd402,0x4018afc8,0x4017d1ee,0x40189518]:m.uc.hook_add(UC_HOOK_CODE,stub,begin=pc,end=pc)
  if name=='valid':
   m.uc.mem_write(STACK,u32(0xdeadbee0)+u32(DATA));m.uc.reg_write(UC_M68K_REG_SR,0x2700);m.uc.reg_write(UC_M68K_REG_A7,STACK)
   m.uc.emu_start(0x40100440,0x40100504,count=10000000);assert m.uc.reg_read(UC_M68K_REG_PC)==0x40100504
   expected=wire[8:8+int.from_bytes(wire[:4],'big')];erases=[x for x in actions if x[0]=='erase'];program=[x for x in actions if x[0]=='program']
   assert len(erases)==math.ceil(len(expected)/0x10000) and len(program)==len(expected)//256
   assert flash[0x80000:0x80000+len(expected)]==expected and flash[0x380000:0x380200]==b'\xa6'*512
   case.update(updater_programming_boundary_reached=True,erase_calls=len(erases),program_calls=len(program),program_end=hex(program[-1][1]+program[-1][2]),stock_data_guard_intact=True,same_received_bytes_programmed=True,hardware_fixtures=hw)
  else:
   result=call(m,0x40100440,[DATA],stack_top=STACK,limit=5000000);assert m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
   assert result==3 and not actions and not hw
   case.update(updater_return=result,no_flash_calls=True,rejected_before_hardware_queries=True)
  r['cases'].append(case);print('PASS',name,flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc();print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-ordinary-receive-updater-checks.json').write_text(json.dumps(r,indent=2))
