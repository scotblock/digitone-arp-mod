"""Stock 128-kit decode must be identical with/without candidate records."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'work')
from E10_storage_probe import record_bytes
ns={};source=Path('work/audit-PC-E10-native-kit-codec.py').read_text().split('\nout=dict')[0];exec(compile(source,'E10-storage-codec-control-fixture','exec'),ns)
u=ns['u'];FR=ns['FR'];BR=ns['BR'];STACK=ns['STACK']
from unicorn.m68k_const import UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D7,UC_M68K_REG_PC
baseline=bytes(u.mem_read(BR,0x4c400));before=bytes(u.mem_read(FR,0x50000))
for slot in range(128):u.mem_write(FR+slot*0xa00+0x940,record_bytes(slot))
after=bytes(u.mem_read(FR,0x50000))
for slot in range(128):
 a=slot*0xa00;assert before[a:a+0x940]==after[a:a+0x940] and before[a+0x960:a+0xa00]==after[a+0x960:a+0xa00]
u.mem_write(BR,b'\x59'*0x4c420)
for reg,value in [(UC_M68K_REG_A5,FR),(UC_M68K_REG_D4,BR),(UC_M68K_REG_A6,0x400093d0),(UC_M68K_REG_D5,0x40014e84),(UC_M68K_REG_D3,0),(UC_M68K_REG_A7,STACK)]:u.reg_write(reg,value)
u.emu_start(0x4000e960,0x4000e98a,count=20000000);assert u.reg_read(UC_M68K_REG_PC)==0x4000e98a
assert bytes(u.mem_read(BR,0x4c400))==baseline and bytes(u.mem_read(BR+0x4c400,32))==b'\x59'*32
# Rebuilding a project image from those runtime kits cannot reconstruct data
# the decoder never retained. Prove that loss through the actual encoder loop.
u.mem_write(FR,bytes(0x50020))
for reg,value in [(UC_M68K_REG_A4,FR),(UC_M68K_REG_A6,BR),(UC_M68K_REG_A5,0x400095f4),(UC_M68K_REG_D5,0),(UC_M68K_REG_D7,0),(UC_M68K_REG_A7,STACK)]:u.reg_write(reg,value)
u.emu_start(0x4000ecd6,0x4000ecf6,count=20000000);assert u.reg_read(UC_M68K_REG_PC)==0x4000ecf6
assert all(bytes(u.mem_read(FR+slot*0xa00+0x940,32))==bytes(32) for slot in range(128))
out=dict(PC_only=True,passed=True,kit_count=128,stock_runtime_decode_byte_identical=True,stock_decoder_ignores_candidate=True,stock_reencode_drops_candidate=True,only_candidate_serialized_bytes_changed=True,runtime_sha256=hashlib.sha256(baseline).hexdigest(),limits=['Restored native parameters cloned into 128 scratch source kits; isolated native conversion loops, not filesystem or hardware.','No automatic E10 record capture is implied. A separate decode bridge and encode bridge are both required, including working-cache rebuilds.'])
Path('outputs/Digitone-E10-PC-storage-stock-decoder-control.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
