from pathlib import Path
exec(Path('work/test-PC-stock-audio-restoration.py').read_text().split('\nfor recursive in [False,True]:')[0])
m=prepared();u=m.uc;A=call(m,0x400e96c0,[0x248],stack_top=RESETSTACK,limit=100000);call(m,0x400b2b5e,[A],stack_top=RESETSTACK,limit=2000000);O=call(m,0x400e96c0,[0x2cc],stack_top=RESETSTACK,limit=100000)
execute_until(m,0x40072a7e,[O],0x40072ac4,sr=0x201f);PP=O+0x38;print('PARENT',hex(O),'CB',[(hex(at),hex(rd(u,at+12))) for at in range(rd(u,PP+0x34),rd(u,PP+0x38),16)],flush=True)
M=0x47fb0000;m.ensure(M);u.mem_write(M,bytes(0x100));u.mem_write(M+20,u32(M+20)+u32(M+20));TASK=M+0x8000;m.ensure(TASK);u.mem_write(0x429f2188,u32(TASK));H=M+0x6000;m.ensure(H);u.reg_write(UC_M68K_REG_A0,H);call(m,0x400e43fc,[O,A+0x38],stack_top=RESETSTACK,limit=100000);call(m,0x401774c0,[O+0x8c,H],stack_top=RESETSTACK,limit=100000)
trail=[];h=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:trail.append(pc))
try:execute_until(m,0x400e4e1e,[O,M],0x400e4e42,sr=0x201f);print('ENTRY_PREFIX_OK',flush=True)
except Exception as e:print('FAIL',str(e),hex(u.reg_read(UC_M68K_REG_PC)),[hex(x) for x in trail[-15:]],flush=True)
