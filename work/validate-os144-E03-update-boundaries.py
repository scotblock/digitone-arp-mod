from pathlib import Path
import sys,json,struct,math,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import *
from dt2.container import decode_syx
stock=Path('work/os144/section-3.bin').read_bytes();c=Path('work/os144/E03-container.bin').read_bytes();r={'PC_only':True,'length':len(c),'update_loop':{},'receiving_size_cases':[],'limits':['Stock 1.44 loop instructions execute, but display and flash read/erase/program functions are simulated at their call boundaries.','Receiving-size comparison is a supplied positive-length service-buffer fixture, not a completed MIDI/USB receive session.','Actual flash errors, interruptions and post-update readback are not established.']}
def machine():
 m=Machine(ddr=0x08000000);m.load(stock,0x40000400);m.install_isa_patches_scoped(stock,0x40000400)
 for a in [0x4bc47080,0x47fdff00,0x41972340]:m.ensure(a)
 m.uc.reg_write(UC_M68K_REG_SR,0x2700);m.uc.reg_write(UC_M68K_REG_A7,0x47fdfe00);m.uc.reg_write(UC_M68K_REG_A6,0x47fdff00);return m
m=machine();uc=m.uc;m.load(c,0x4bc47088);uc.mem_write(0x4bc47084,struct.pack('>I',len(c)));uc.mem_write(0x4bc47088+len(c),b'\x7d'*512)
flash=bytearray(b'\xa6'*(4*1024*1024));erase=[];program=[]
def skip(uc,pc,n,d):
 sp=uc.reg_read(UC_M68K_REG_A7);args=struct.unpack('>IIII',uc.mem_read(sp,16));ret=args[0]
 if pc==0x400fd47e:
  a=args[1];erase.append(a);flash[a:a+0x40000]=b'\xff'*0x40000
 if pc==0x400fd402:
  a,count,src=args[1:];assert count==512 and 0x4bc47088<=src and src+count<=0x4bc47088+len(c),(a,count,src)
  payload=bytes(uc.mem_read(src,count));flash[a:a+count]=payload;program.append((a,count,src))
 uc.reg_write(UC_M68K_REG_D0,0);uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_PC,ret)
for pc in [0x400fd47e,0x400fd402,0x4000594c]:uc.hook_add(UC_HOOK_CODE,skip,begin=pc,end=pc)
uc.reg_write(UC_M68K_REG_D6,0);uc.emu_start(0x4008b60e,0x4008b75e,count=500000)
assert uc.reg_read(UC_M68K_REG_PC)==0x4008b75e
assert erase==list(range(0x80000,0x80000+math.ceil(len(c)/0x40000)*0x40000,0x40000))
assert program==[(0x80000+j*512,512,0x4bc47088+j*512) for j in range(len(c)//512)]
assert flash[0x80000:0x80000+len(c)]==c and flash[0x380000:0x380200]==b'\xa6'*512 and flash[0x3c0000:0x3c0200]==b'\xa6'*512
r['update_loop']={'passed':True,'erase_units':len(erase),'erase_end':hex(erase[-1]+0x40000),'program_blocks':len(program),'program_end':hex(program[-1][0]+512),'last_program_source':hex(program[-1][2]),'last_program_all_bytes_inside_advertised_container':True,'stock_data_guards_380000_3c0000_intact':True,'simulated_flash_content_matches':True}
for length in [len(c),3361440,0x1dfff8,0x1dfff9]:
 q=machine();u=q.uc;u.mem_write(0x41972340,struct.pack('>I',0x1e0000));u.reg_write(UC_M68K_REG_D0,length)
 def stop(u,pc,n,d):u.emu_stop()
 for pc in [0x400e885e,0x400e88ba]:u.hook_add(UC_HOOK_CODE,stop,begin=pc,end=pc)
 u.emu_start(0x400e8852,0xdeadbee0,count=20);pc=u.reg_read(UC_M68K_REG_PC);accepted=pc==0x400e885e
 assert accepted==(length+7<0x1e0000);r['receiving_size_cases'].append({'length':length,'accepted':accepted,'boundary':hex(pc)})
Path('outputs/Digitone-OS1.44E03-update-boundary-checks.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))

