"""Actual owner helpers + DIN driver + USB packetizer/allocator; endpoint fixture."""
from pathlib import Path
import json,sys,struct
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from emu import cfisa
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_A7,UC_M68K_REG_D0,UC_M68K_REG_PC
cfg=json.loads(Path('work/os144/E09-PC-dual-port-layout.json').read_text())
old=json.loads(Path('outputs/Digitone-E08F-PC-path-layout.json').read_text())
main=Path('work/os144/E08F-PC-layout-main.bin').read_bytes();payload=Path('work/os144/E09-PC-dual-port-payload.bin').read_bytes();PB=cfg['base'];MB=0x40000400
STACK=0x47bcf800;POOL=0x47bd1000;DIN=0x4bc09000;records=old['MIDI_records'];usb_records=cfg['USB_records']
u32=lambda v:struct.pack('>I',v)
rows=[]
def setup(mask):
 m=Machine(ddr=0x8000000);u=m.uc
 for p in [STACK,POOL,POOL+4096,DIN,0x4bc0c000,0x40528000,0x40529000,0x419c5000,0x41368000,0x429f2000,0xfc045000,0xfc0b0000]:m.ensure(p)
 for a,z in [(0x40001000,0x40003000),(0x40004000,0x40006000)]:
  for p in range(a,z,4096):m.ensure(p)
  code=main[a-MB:z-MB];u.mem_write(a,code);m.install_isa_patches_scoped(code,a)
 for p in range(PB,PB+len(payload),4096):m.ensure(p)
 u.mem_write(PB,payload)
 for r in old['regions']+cfg['regions']:
  if r['base']>=PB:
   code=payload[r['base']-PB:r['base']-PB+r['bytes']];m.install_isa_patches_scoped(code,r['base'])
 for state in [old['MIDI_state'],cfg['USB_state']]:u.mem_write(state,u32(0x53414d31)+u32(1)+bytes(152))
 for a,v in [(0x419c5df4,mask),(0x405285a4,DIN),(0x4052859c,1),(0x40529244,1),(0xfc0b01c4,1),(0x40529388,POOL)]:u.mem_write(a,u32(v))
 for a in [0x405285b0,0x405285b4,0x405285b8,0x405285bc,0x40529248,0x4052924c,0x40529234,0x429f23b8]:u.mem_write(a,u32(0))
 for i in range(64):u.mem_write(POOL+i*64,bytes(64));u.mem_write(POOL+i*64+0x34,u32(POOL+(i+1)*64 if i<63 else 0))
 for t in range(4):u.mem_write(old['MIDI_markers']+4*t,u32(0x419e0000+72*t));u.mem_write(0x41368d30+4*t,u32(t))
 m.usb=[];m.reject=False
 def submit(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7);desc=int.from_bytes(u.mem_read(sp+8,4),'big')
  size=int.from_bytes(u.mem_read(desc+0x20,4),'big');ptr=int.from_bytes(u.mem_read(desc+8,4),'big')
  if not m.reject:m.usb.extend(bytes(u.mem_read(ptr,size)))
  u.reg_write(UC_M68K_REG_D0,0xffffffff if m.reject else 0);u.reg_write(UC_M68K_REG_PC,int.from_bytes(u.mem_read(sp,4),'big'));u.reg_write(UC_M68K_REG_A7,sp+4)
 u.hook_add(UC_HOOK_CODE,submit,begin=0x40005f1e,end=0x40005f1e)
 return m
def get(m,a):return int.from_bytes(m.uc.mem_read(a,4),'big')
def put(m,a,v):m.uc.mem_write(a,u32(v))
def invoke(m,name,args=[]):return call(m,cfg['bridge_entries'][name],args,stack_top=STACK,limit=50000)
def start(m,v=0,t=0,n=60):invoke(m,'start_both',[v,t,0x419e0000+72*t,n,100])
def release(m,v=0):invoke(m,'release_both',[v])
def packets(m):
 raw=bytes(m.uc.mem_read(DIN,get(m,0x405285b4)))
 assert len(raw)%3==0 and len(m.usb)%4==0
 return [list(raw[i:i+3]) for i in range(0,len(raw),3)],[m.usb[i+1:i+4] for i in range(0,len(m.usb),4)]
def record(name,m):
 d,u=packets(m);rows.append({'name':name,'DIN':d,'USB':u,'DIN_active':get(m,records),'USB_active':get(m,usb_records)})
for mask in range(4):
 m=setup(mask)
 for t in range(4):start(m,t,t,60+t);release(m,t)
 d,u=packets(m);expect=[x for t in range(4) for x in [[0x90+t,60+t,100],[0x80+t,60+t,0]]]
 assert d==(expect if mask&1 else []) and u==(expect if mask&2 else []),(mask,d,u)
 record('mask_'+str(mask),m)
m=setup(3)
for v in range(3):start(m,v)
release(m,0);release(m,1);assert packets(m)==([[144,60,100]],[[144,60,100]])
release(m,2);assert packets(m)==([[144,60,100],[128,60,0]],[[144,60,100],[128,60,0]])
record('shared_voices_one_pair_per_port',m)
m=setup(3);start(m);put(m,0x419c5df4,0);put(m,0x41368d30,9);release(m)
assert packets(m)==([[144,60,100],[128,60,0]],[[144,60,100],[128,60,0]])
record('route_and_channel_change_keep_original_release',m)
m=setup(3);put(m,0x405285b8,4094);start(m);release(m)
assert packets(m)==([],[[144,60,100],[128,60,0]]);record('DIN_full_USB_still_operates',m)
m=setup(3);put(m,0xfc0b01c4,0);start(m);release(m)
assert packets(m)==([[144,60,100],[128,60,0]],[]);record('USB_disconnected_DIN_still_operates',m)
m=setup(3);start(m);put(m,0x405285b8,4094);release(m)
assert get(m,records)==1 and get(m,usb_records)==0
put(m,0x405285b8,0);invoke(m,'pump_both')
assert packets(m)==([[144,60,100],[128,60,0]],[[144,60,100],[128,60,0]])
record('DIN_release_retries_without_duplicate_USB_off',m)
m=setup(3);start(m);pool=get(m,0x40529388);put(m,0x40529388,0);release(m)
assert get(m,records)==0 and get(m,usb_records)==1
put(m,0x40529388,pool);invoke(m,'pump_both')
assert packets(m)==([[144,60,100],[128,60,0]],[[144,60,100],[128,60,0]])
record('USB_release_retries_without_duplicate_DIN_off',m)
m=setup(3);m.reject=True;start(m);release(m)
assert packets(m)==([[144,60,100],[128,60,0]],[]) and get(m,usb_records)==0
record('USB_submit_failure_does_not_claim_owner',m)
for name,addr,value in [('USB_endpoint_stopped',0x429f23b8,32),('USB_pending_full',0x40529248,4092),('USB_pool_descriptor_busy',POOL+4,128),('USB_bad_write_alignment',0x4052924c,3)]:
 m=setup(3);put(m,addr,value);start(m);release(m)
 assert packets(m)==([[144,60,100],[128,60,0]],[]) and get(m,usb_records)==0
 record(name+'_DIN_continues',m)
m=setup(3);put(m,0x4052924c,4092);start(m);release(m)
assert packets(m)==([[144,60,100],[128,60,0]],[[144,60,100],[128,60,0]])
record('USB_buffer_wrap_preserves_pair',m)
m=setup(3);start(m);m.reject=True;release(m)
assert get(m,usb_records)==1 and get(m,records)==0
m.reject=False;invoke(m,'pump_both')
assert packets(m)==([[144,60,100],[128,60,0]],[[144,60,100],[128,60,0]])
record('USB_rejected_note_off_retries_without_DUP_DIN',m)
out={'PC_only':True,'passed':True,'cases':rows,'native_owner_helpers':True,'native_DIN_writer':True,'native_USB_packetizer_and_pool_allocator':True,
 'USB_endpoint_submit_is_fixture':True,'firmware_container_created':False,
 'limits':['Endpoint success/failure and peripheral readiness are fixtures, not real USB/DMA/host timing.','Host initializes the proposed extra code/state; native startup/reset integration and RAM lifetime remain outstanding.','These tests exercise synth voice mirroring; M1’s actual scheduler on both outputs is a separate continuous check.']}
Path('outputs/Digitone-E09-PC-dual-port-mirror.json').write_text(json.dumps(out,indent=2));print('PASS',len(rows),'native dual-port ownership/driver cases.')
