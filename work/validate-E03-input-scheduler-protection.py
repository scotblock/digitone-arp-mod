exec(open('work/E03-receiver-test-environment.py').read().split('def machine():')[0])
from unicorn.m68k_const import *
W,I,WS,IS=0x47db0000,0x47db1000,0x47dc0000,0x47dc8000
m=Machine(ddr=0x08000000);m.load(stock,0x40000400);m.install_isa_patches_scoped(stock,0x40000400)
for a in [W,I,WS,IS,STACK,0x429f2148,0x40528180,0x419eaf08,0xfc050014,0xfc080000]:m.ensure(a)
m.uc.mem_write(0x429f2148,bytes(64));m.uc.mem_write(0x40528180,u32(0x429f2148))
for tcb,entry,priority,st in [(W,0x400a89c6,2,WS),(I,0x400e9b7e,7,IS)]:
 m.uc.mem_write(tcb,bytes(84));call(m,0x4000170c,[tcb,entry,priority,st,0x4000],stack_top=STACK,limit=1000);call(m,0x40001758,[tcb],stack_top=STACK,limit=1000)
frame=int.from_bytes(m.uc.mem_read(W+72,4),'big');assert bytes(m.uc.mem_read(frame,4)).hex()=='407c2000'
assert int.from_bytes(m.uc.mem_read(0x40528180,4),'big')==0x429f2164
m.uc.mem_write(0x429f2188,u32(W));m.uc.mem_write(STACK,bytes(16));m.uc.reg_write(UC_M68K_REG_SR,0x2000);m.uc.reg_write(UC_M68K_REG_A7,STACK)
m.uc.emu_start(0x40000410,0x40000452,count=1000)
selected=int.from_bytes(m.uc.mem_read(0x429f2188,4),'big');assert selected==I
# An uncontended real flash mutex restores incoming SR instead of keeping IRQs masked.
m.uc.mem_write(0x429f2188,u32(W));call(m,0x400019c0,[0x419eaf08],stack_top=STACK,limit=1000)
m.uc.mem_write(STACK,u32(0xdeadbee0)+u32(0x419eaf08));m.uc.reg_write(UC_M68K_REG_SR,0x2000);m.uc.reg_write(UC_M68K_REG_A7,STACK);m.uc.emu_start(0x400019e4,0xdeadbee0,count=1000)
assert (m.uc.reg_read(UC_M68K_REG_SR)&0x2700)==0x2000 and int.from_bytes(m.uc.mem_read(0x419eaf08,4),'big')==W
r={'passed':True,'PC_only':True,'input_priority':7,'worker_priority':2,'worker_initial_exception_frame':bytes(m.uc.mem_read(frame,4)).hex(),'highest_ready_slot':'0x429f2164','stock_dispatcher_selected_input_task':selected==I,'flash_mutex_owned_by_worker':True,'uncontended_mutex_return_SR':hex(m.uc.reg_read(UC_M68K_REG_SR)), 'returned_interrupt_mask':0,'limits':['Task stacks/control blocks and ready-list state are fixtures, constructed by actual stock task/ready-list routines.','Dispatcher executes through selection, stopping before restoring the selected task and RTE.','Actual peripheral arrival, interrupt delivery and complete task execution are not established.']}
Path('outputs/Digitone-OS1.44E03-input-scheduler-protection-check.json').write_text(json.dumps(r,indent=2));print(r)

