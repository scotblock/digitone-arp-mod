from pathlib import Path
exec(Path('work/test-PC-stock-audio-restoration.py').read_text().split('\nfor recursive in [False,True]:')[0])
m=prepared();u=m.uc;O=call(m,0x400e96c0,[0x2cc],stack_top=RESETSTACK,limit=100000);print('ROOT',hex(O),flush=True)
try:
 call(m,0x40072a7e,[O],stack_top=RESETSTACK,limit=5000000)
 print('CONSTRUCTED',hex(rd(u,O)),hex(rd(u,O+0x2b4)),flush=True)
 page=O+0x38
 for field in [0x34,0x40]:
  start=rd(u,page+field);end=rd(u,page+field+4);print('CALLBACKS',hex(field),[hex(rd(u,a+12)) for a in range(start,end,16)],flush=True)
except Exception as e:print('FAIL',str(e),'PC',hex(u.reg_read(UC_M68K_REG_PC)),flush=True)
