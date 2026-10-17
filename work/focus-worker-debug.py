from pathlib import Path
p=Path('work/validate-E03-continuous-queue-action.py').read_text().replace("for name in ['valid','content_corrupt','missing_end','busy_view']:","for name in (sys.argv[1:] or ['valid','content_corrupt','missing_end','busy_view']):")
p=p.replace("m.uc.hook_add(UC_HOOK_CODE,lambda uc,pc,n,d:m.recent.append((hex(pc),hex(uc.reg_read(UC_M68K_REG_A7)))))","m.uc.hook_add(UC_HOOK_CODE,lambda uc,pc,n,d:m.recent.append((hex(pc),hex(uc.reg_read(UC_M68K_REG_A7)),hex(uc.reg_read(UC_M68K_REG_A0)),hex(uc.reg_read(UC_M68K_REG_A1)))),begin=0x40146410,end=0x4014642a)")
Path('work/validate-E03-continuous-queue-action.py').write_text(p)
