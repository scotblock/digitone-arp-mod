from pathlib import Path
p=Path('work/validate-E03-continuous-queue-action.py').read_text()
p=p.replace("   call(m,0x400a8690", "   if name=='content_corrupt':\n    import collections;m.recent=collections.deque(maxlen=70)\n    m.uc.hook_add(UC_HOOK_CODE,lambda uc,pc,n,d:m.recent.append((hex(pc),hex(uc.reg_read(UC_M68K_REG_A7)))))\n   call(m,0x400a8690")
p=p.replace("print(r['failure'],flush=True)","print(r['failure'],flush=True);print(list(getattr(m,'recent',[])),flush=True)")
Path('work/validate-E03-continuous-queue-action.py').write_text(p)
