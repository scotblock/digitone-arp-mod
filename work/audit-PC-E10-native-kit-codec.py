"""Execute complete stock kit codecs with restored native parameters.

Find serialized extents without treating untouched allocation padding as owned.
No sequence record is written into any stock project or kit.
"""
from pathlib import Path
import sys,json,zlib,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call,PAGE
from emu.snapshot import _load_blob
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_PC
from unicorn.m68k_const import UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D7
c=json.loads(Path('outputs/Digitone-E10-PC-integrated-startup.json').read_text())['cases'][0]
b=_load_blob(c['ui_snapshot']);m=Machine(ddr=0x8000000);u=m.uc
stock=Path('work/os144/section-3.bin').read_bytes()
for p in range(0x40000000,0x40000400+len(stock),PAGE):m.ensure(p)
u.mem_write(0x40000400,stock);m.install_isa_patches_scoped(stock,0x40000400)
for p,compressed in b['pages'].items():
 if 0x40400000<=p<0x48000000:m.ensure(p);u.mem_write(p,zlib.decompress(compressed))
get=lambda a:int.from_bytes(u.mem_read(a,4),'big')
root=get(0x419f0de0);handle=root+0xff8;KIT=get(handle+16)-0x5ce
assert KIT==get(get(handle+4)+16)
F=0x47b80000;BACK=F+0x2000;STACK=0x47b8ff00
for p in [F,BACK,STACK]:m.ensure(p)
u.mem_write(F,b'\xa5'*0xa20);u.mem_write(BACK,b'\x59'*0x9a8)
phase='encode';writes=[];reads=[]
def write(uc,access,address,size,value,data):writes.append((phase,address-F,size,hex(uc.reg_read(UC_M68K_REG_PC))))
def read(uc,access,address,size,value,data):reads.append((phase,address-F,size,hex(uc.reg_read(UC_M68K_REG_PC))))
u.hook_add(UC_HOOK_MEM_WRITE,write,begin=F,end=F+0xa1f)
u.hook_add(UC_HOOK_MEM_READ,read,begin=F,end=F+0xa1f)
assert call(m,0x400095f4,[F,KIT,0],stack_top=STACK,limit=200000)&255==1
encoded=bytes(u.mem_read(F,0xa00));extent=max(o+n for _,o,n,_ in writes)
assert encoded[:4]==bytes.fromhex('0000000b')
phase='decode';assert call(m,0x400093d0,[BACK,F],stack_top=STACK,limit=200000)&255==1
read_extent=max(o+n for _,o,n,_ in reads)
assert bytes(u.mem_read(BACK+0x988,32))==b'\x59'*32
assert bytes(u.mem_read(F+0xa00,32))==b'\xa5'*32
# Execute the actual 128-kit project conversion loops, not a Python loop over
# the codec. Native code advances serialized records by 0xa00 and runtime kits
# by 0x988. Cloned source kits and direct loop entry are disclosed fixtures.
FR=0x47b00000;RR=0x47a00000;BR=0x47900000
for base,size in [(FR,0x50020),(RR,0x4c420),(BR,0x4c420)]:
 for p in range(base,base+size,PAGE):m.ensure(p)
u.mem_write(FR,b'\xa5'*0x50020);u.mem_write(RR,bytes(u.mem_read(KIT,0x988))*128+b'\x59'*32);u.mem_write(BR,b'\x59'*0x4c420)
for reg,value in [(UC_M68K_REG_A4,FR),(UC_M68K_REG_A6,RR),(UC_M68K_REG_A5,0x400095f4),(UC_M68K_REG_D5,0),(UC_M68K_REG_D7,0),(UC_M68K_REG_A7,STACK)]:u.reg_write(reg,value)
u.emu_start(0x4000ecd6,0x4000ecf6,count=20000000);assert u.reg_read(UC_M68K_REG_PC)==0x4000ecf6
assert u.reg_read(UC_M68K_REG_A4)==FR+0x50000 and u.reg_read(UC_M68K_REG_D7)==0x4c400
for slot in range(128):
 actual=bytes(u.mem_read(FR+slot*0xa00,0xa00))
 # Codec writes continue twelve bytes beyond its observed decode extent.
 # Those bytes vary with surrounding source contents; exclude them from the
 # logical round-trip comparison, not from the writer's occupied extent.
 assert actual[:read_extent]==encoded[:read_extent],slot
 assert actual[extent:]==b'\xa5'*(0xa00-extent),slot
for reg,value in [(UC_M68K_REG_A5,FR),(UC_M68K_REG_D4,BR),(UC_M68K_REG_A6,0x400093d0),(UC_M68K_REG_D5,0x40014e84),(UC_M68K_REG_D3,0),(UC_M68K_REG_A7,STACK)]:u.reg_write(reg,value)
u.emu_start(0x4000e960,0x4000e98a,count=20000000);assert u.reg_read(UC_M68K_REG_PC)==0x4000e98a
assert u.reg_read(UC_M68K_REG_D4)==BR+0x4c400 and u.reg_read(UC_M68K_REG_D3)==0x50000
assert bytes(u.mem_read(FR+0x50000,32))==b'\xa5'*32 and bytes(u.mem_read(BR+0x4c400,32))==b'\x59'*32
out=dict(PC_only=True,passed=True,stock_encode_entry=hex(0x400095f4),stock_decode_entry=hex(0x400093d0),runtime_kit_bytes=0x988,serialized_version=11,serialized_write_end=hex(extent),serialized_read_end=hex(read_extent),untouched_after_write_end=encoded[extent:]==b'\xa5'*(0xa00-extent),native_project_persistence=False,record_embedding_implemented=False,
 findings=['The entire stock kit encoder/decoder execute with native restored-project parameters. MIDI records begin at serialized +0x548 and runtime +0x5ce; these are body offsets, not unverified third-party image offsets.','Untouched trailing bytes alone do not prove project ownership: enclosing record lengths, initialization, save/load, copy/clear and compatibility still need tracing.'],
 limits=['One restored kit and normal success paths, with stock code and scoped ISA adapters; not the filesystem/project writer.','The output is an isolated scratch buffer. No stock project, firmware or existing candidate is modified.'])
Path('outputs/Digitone-E10-PC-native-kit-codec.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
out.update(native_project_array_loops_executed=True,kit_count=128,serialized_stride=0xa00,runtime_stride=0x988,source_kits_are_cloned_fixtures=True,possible_serialized_extension=[hex(0x940),hex(0x960)],extension_ownership_verified=False)
out['findings'].append('The native project conversion loops independently confirm 128 records at serialized stride 0xa00 and runtime stride 0x988. +0x940..+0x95f is untouched in these controls; no extension is installed there.')
Path('outputs/Digitone-E10-PC-native-kit-codec.json').write_text(json.dumps(out,indent=2));print('Native 128-kit project encode/decode loops passed; no extension embedded.')
