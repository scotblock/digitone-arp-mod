from pathlib import Path
p=Path('work/validate-E03-continuous-queue-action.py').read_text()
p=p.replace('  elif pc==0x40016fb4:result=LIST','  elif pc==0x400e61cc:\n   out=uc.reg_read(UC_M68K_REG_A0);uc.mem_write(out,u32(VIEW)+u32(CTRL));count=int.from_bytes(uc.mem_read(CTRL+4,4),\'big\');uc.mem_write(CTRL+4,u32(count+1))\n  elif pc==0x40016fb4:result=LIST')
a=p.index("   if name=='content_corrupt':\n    import collections")
b=p.index('   call(m,0x400a8690',a)
p=p[:a]+p[b:]
p=p.replace(";print(list(getattr(m,'recent',[])),flush=True);print('D2',hex(m.uc.reg_read(UC_M68K_REG_D2)),'A0',hex(m.uc.reg_read(UC_M68K_REG_A0)));print(bytes(m.uc.mem_read(m.uc.reg_read(UC_M68K_REG_D2),20)).hex())",'')
Path('work/validate-E03-continuous-queue-action.py').write_text(p)
