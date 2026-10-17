from pathlib import Path
p=Path('work/validate-E03-continuous-queue-action.py').read_text()
p=p.replace("   call(m,0x400a8690", "   from unicorn import UC_HOOK_MEM_READ\n   m.uc.hook_add(UC_HOOK_MEM_READ,lambda uc,k,a,s,v,d:print('READ',hex(a),s,bytes(uc.mem_read(a,s)).hex(),flush=True) if uc.reg_read(UC_M68K_REG_PC)==0x40146414 else None,begin=STACK-0x1800,end=STACK)\n   call(m,0x400a8690")
Path('work/debug-worker-read.py').write_text(p.replace("continuous-queue-action-checks.json","continuous-worker-debug.json"))
