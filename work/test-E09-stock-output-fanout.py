"""Native stock port fanout and both encoders; USB endpoint handoff is a sink."""
from pathlib import Path
import sys,json,struct
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_A7,UC_M68K_REG_PC
main=Path('work/os144/section-3.bin').read_bytes();MB=0x40000400
u32=lambda v:struct.pack('>I',v)
messages=[[0x92,60,100],[0x92,64,90],[0x92,67,80],[0x82,60,0],[0x82,64,0],[0x82,67,0]]
rows=[]
for mask in range(4):
 m=Machine(ddr=0x8000000);u=m.uc;stack=0x47bcf000;buf=0x47bd0000;din=0x4bc09000
 for p in [stack,buf,din,0x4bc0c000,0x40528000,0x40529000,0x419c5000,0xfc045000,0xfc0b0000]:m.ensure(p)
 for a,z in [(0x40002000,0x40003000),(0x40004000,0x40005000),(0x400f3000,0x400f4000)]:
  m.ensure(a);code=main[a-MB:z-MB];u.mem_write(a,code);m.install_isa_patches_scoped(code,a)
 def put(a,v):u.mem_write(a,u32(v))
 def get(a):return int.from_bytes(u.mem_read(a,4),'big')
 put(0x419c5df4,mask);put(0x405285a4,din);put(0x4052859c,1)
 for a in [0x405285b0,0x405285b4,0x405285b8,0x405285bc,0x40529248,0x4052924c,0x40529234]:put(a,0)
 put(0x40529244,1);put(0xfc0b01c4,1)
 bulk=[]
 def submit(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7);length=get(sp+4);ptr=get(sp+8)
  bulk.append(bytes(u.mem_read(ptr,length)).hex())
  u.reg_write(UC_M68K_REG_PC,get(sp));u.reg_write(UC_M68K_REG_A7,sp+4)
 u.hook_add(UC_HOOK_CODE,submit,begin=0x40004a6e,end=0x40004a6e)
 for msg in messages:
  u.mem_write(buf,bytes(msg));call(m,0x400f37ce,[3,buf],stack_top=stack+0x800,limit=20000)
 din_bytes=bytes(u.mem_read(din,get(0x405285b4)))
 expected=b''.join(bytes(x) for x in messages)
 assert din_bytes==(expected if mask&1 else b''),(mask,din_bytes.hex())
 usb_raw=b''.join(bytes.fromhex(x) for x in bulk)
 assert len(usb_raw)==(4*len(messages) if mask&2 else 0),(mask,bulk)
 usb_messages=[]
 for i in range(0,len(usb_raw),4):
  packet=usb_raw[i:i+4];assert packet[0]&15==packet[1]>>4
  usb_messages.append(list(packet[1:4]))
 assert usb_messages==(messages if mask&2 else []),(mask,usb_messages)
 rows.append({'route_mask':mask,'DIN_bytes':din_bytes.hex(),'USB_packets':bulk,'USB_decoded_messages':usb_messages,'note_pairs':3})
out={'PC_only':True,'passed':True,'native_stock_entry':'0x400f37ce','route_field':'0x419c5df4',
 'bit_1':'DIN','bit_2':'USB','actual_DIN_ring_writer':True,'actual_USB_MIDI_packetizer':True,
 'USB_endpoint_handoff_is_fixture':True,'cases':rows,
 'limits':['USB bulk submission is intercepted after native MIDI packetization; no physical endpoint or host receipt is proved.','This tests stock fanout, not integration of a new synth mirror or four independent arps.','Backpressure, routing changes and pending release ownership need separate tests.']}
Path('outputs/Digitone-E09-stock-output-fanout.json').write_text(json.dumps(out,indent=2));print('PASS stock off/DIN/USB/both: native encoders, 3 matched note pairs per enabled port.')
