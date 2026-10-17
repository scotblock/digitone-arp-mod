from pathlib import Path
import sys,json,hashlib,struct
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import cfisa
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import *
# Load the documented MOVE-combination check without running the old audit.
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
oldmain=bytes(main);oldpayload=bytes(payload);base=0x40000400;stage=0x4029c4b0
copier=oldmain[stage-base:stage-base+94];assert copier[48:88].hex()=='23fc47bccf0447be100023fc534c433247be100423fc0000000247be100823fc00000b7047be100c'
# D1 is known zero after the copier's clear loop. Restore it and set flags
# from the final length word, preserving the original continuation state.
stores=bytearray()
for value,address in [(0x47bccf04,0x47be1000),(0x534c4332,0x47be1004),(2,0x47be1008),(0xb70,0x47be100c)]:
 stores.extend(bytes.fromhex('223c')+struct.pack('>I',value)+bytes.fromhex('23c1')+struct.pack('>I',address))
stores.extend(bytes.fromhex('72004ab947be100c')) # MOVEQ #0,D1; TST.L length
corrected_copier=copier[:48]+stores+copier[88:];assert len(corrected_copier)==110
newpayload=bytearray(oldpayload);off=0x47be0998-0x47be0000
assert newpayload[off:off+10].hex()=='23fc0000000147be1010'
# D0 is scratch inside the already-saved fallback frame. Its stock return
# value is restored from frame offset 0; no branch or payload length changes.
newpayload[off:off+10]=bytes.fromhex('700123c047be10104e71')
newmain=bytearray(oldmain);newmain[stage-base:stage-base+256]=corrected_copier+bytes(256-len(corrected_copier))
newmain[stage+256-base:]=newpayload
assert len(newmain)==len(oldmain) and len(newpayload)==len(oldpayload)==2492
assert newmain[:stage-base]==oldmain[:stage-base]
assert newpayload[:off]==oldpayload[:off] and newpayload[off+10:]==oldpayload[off+10:]
out={'PC_only':True,'packaged_firmware_modified':False,'copier_bytes':110,'copier_old_bytes':94,'copier_end':'0x4029c51e','source_payload':'0x4029c5b0','copy_longwords':623,'payload_bytes':2492,'fallback_ready_site':'0x47be0998','fallback_replacement_bytes':'700123c047be10104e71','fallback_branch_offsets_unchanged':True,'static_regions':[],'copier_comparison':{}}
regions=[('copier',stage,110,newmain,base),('fallback',0x47be08a4,280,newpayload,0x47be0000)]+[(n,v['address'],v['size'],newpayload,0x47be0000) for n,v in port['layout'].items()]
for name,pc,length,data,load in regions:
 end=pc+length;n=0
 while pc<end:
  ins=cfisa.decode(lambda off:int.from_bytes(data[pc-load+off:pc-load+off+2],'big'),pc)
  assert pc+ins.length<=end and not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF)
  assert not move_restriction(int.from_bytes(data[pc-load:pc-load+2],'big')),(name,hex(pc))
  n+=1;pc+=ins.length
 out['static_regions'].append({'name':name,'instructions':n,'passed':True})
def execute(image):
 u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_CFV4E);u.mem_map(0x4029c000,4096);u.mem_write(stage,bytes(image[stage-base:]));u.mem_map(0x47be0000,8192)
 for i in range(8):u.reg_write(UC_M68K_REG_D0+i,0x12340000+i);u.reg_write(UC_M68K_REG_A0+i,0x56780000+i)
 u.reg_write(UC_M68K_REG_SR,0x2710);u.emu_start(stage,0x40001df4,count=10000)
 regs={**{'d'+str(i):u.reg_read(UC_M68K_REG_D0+i) for i in range(8)},**{'a'+str(i):u.reg_read(UC_M68K_REG_A0+i) for i in range(8)},'sr':u.reg_read(UC_M68K_REG_SR),'pc':u.reg_read(UC_M68K_REG_PC)}
 return regs,bytes(u.mem_read(0x47be0000,8192))
ra,ma=execute(oldmain);rb,mb=execute(newmain);assert ra==rb
assert ma[0x1000:]==mb[0x1000:] and mb[:2492]==bytes(newpayload)
out['copier_comparison']={'all_registers_SR_and_continuation_match_old':True,'metadata_match_old':True,'corrected_payload_copied_exact':True,'registers_at_continuation':{k:hex(v) for k,v in rb.items()}}
for path,data in [('work/os144/PC_ONLY-E04-ISA-corrected-main.bin',newmain),('work/os144/PC_ONLY-E04-ISA-corrected-payload.bin',newpayload)]:
 Path(path).write_bytes(data);out.setdefault('overlays',[]).append({'path':path,'sha256':hashlib.sha256(data).hexdigest()})
out['E04_syx_sha256']=hashlib.sha256(Path('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx').read_bytes()).hexdigest()
assert out['E04_syx_sha256']=='76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c'
assert Path('work/os144/emulator-E04-main.bin').read_bytes()==oldmain and Path('work/os144/fallback-final-payload.bin').read_bytes()==oldpayload
Path('outputs/Digitone-E04-PC-ISA-correction-layout.json').write_text(json.dumps(out,indent=2)+'\n')
print('PC overlay prepared; strict static checks and exact copier register comparison pass')
