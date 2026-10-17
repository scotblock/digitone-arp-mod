from pathlib import Path
exec(Path('work/test-PC-audio-selection-controls.py').read_text().split('\nfor recursive in [False,True]:')[0])
m=prepared();u=m.uc;a=call(m,0x400e96c0,[0x248],stack_top=RESETSTACK,limit=100000);print('ALLOCATION',hex(a),flush=True)
trail=[];h=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:trail.append(pc))
try:r=call(m,0x400b2b5e,[a],stack_top=RESETSTACK,limit=2000000);print('RETURN',hex(r),'vtable',hex(rd(u,a)),'name',hex(rd(u,a+0x38+0x28)),flush=True)
except Exception as e:print('FAILED',str(e),'PC',hex(u.reg_read(UC_M68K_REG_PC)),'trail',[hex(x) for x in trail[-15:]],flush=True)
