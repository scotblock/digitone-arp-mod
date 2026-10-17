from pathlib import Path
exec(Path('work/test-E03-USB-queue-freeze.py').read_text().split('\ntry:\n for alternate')[0])
def encode_usb(p,cable=0):
 out=bytearray()
 for off in range(0,len(p),3):
  part=p[off:off+3];cin=(4 if off+3<len(p) else 4+len(part));out.extend(bytes([(cable<<4)|cin])+part+bytes(3-len(part)))
 return bytes(out)
def bulk(m,p,cable=0):
 data=encode_usb(p,cable);m.uc.mem_write(MSG,data);call(m,0x4000499c,[len(data),MSG],stack_top=STACK-0x3000,limit=100000)
def register_release_fixture(m):
 def release(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);ret=int.from_bytes(uc.mem_read(sp,4),'big');uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_PC,ret)
 m.uc.hook_add(UC_HOOK_CODE,release,begin=0x40004962,end=0x40004962)
r={'PC_only':True,'cases':[],'failure':None,'limits':['Actual USB-MIDI CIN/cable decoding, registered callbacks, software queues and input consumer execute.','Completed bulk payload and DMA-buffer release are fixtures; endpoint interrupts/pacing are not executed.','Cable 1 consumption remains unproven for OS update and does not provide a restoration certificate.']}
try:
 for name in ['full_cable0','queued_before_freeze','partial_before_freeze']:
  m=make();usb_setup(m);register_release_fixture(m);m.uc.mem_write(STATE,bytes(32));t=time.time()
  if name=='full_cable0':
   for p in packets:bulk(m,bytes(p));usb_drain(m);consume(m)
   assert m.uc.mem_read(STATE,1)[0]==3 and bytes(m.uc.mem_read(DATA,len(wire)))==wire
   r['cases'].append({'name':name,'frames':len(packets),'exact_received_stream':True,'seconds':time.time()-t})
  else:
   before=bytes(m.uc.mem_read(DATA,202))
   if name=='queued_before_freeze':
    for p in [bytes(packets[0]),changed_packet(1)]:bulk(m,p)
    assert int.from_bytes(m.uc.mem_read(UQ+4,4),'big')==2
   else:
    # Raw callback chunk represents a USB bulk transfer boundary within one frame.
    p=bytes(packets[0]);prefix=p[:-1];encoded=bytearray()
    for off in range(0,len(prefix),3):
     part=prefix[off:off+3];assert len(part)==3;encoded.extend(b'\x04'+part)
    m.uc.mem_write(MSG,bytes(encoded));call(m,0x4000499c,[len(encoded),MSG],stack_top=STACK-0x3000,limit=100000)
    assert m.uc.mem_read(0x418e9f74,1)[0]==0xf0
   call(m,0x400ed8ea,[],stack_top=STACK,limit=1000)
   if name=='partial_before_freeze':bulk(m,b'\xf7')
   usb_drain(m);assert bytes(m.uc.mem_read(DATA,202))==before and m.uc.mem_read(STATE,1)[0]==0
   r['cases'].append({'name':name,'receiver_unchanged':True,'partial_status_after':m.uc.mem_read(0x418e9f74,1)[0],'seconds':time.time()-t})
  print('PASS bulk',name,flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc()+' PC='+hex(m.uc.reg_read(UC_M68K_REG_PC));print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-USB-bulk-freeze-checks.json').write_text(json.dumps(r,indent=2))

