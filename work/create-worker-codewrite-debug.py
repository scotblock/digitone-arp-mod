from pathlib import Path
p=Path('work/debug-worker-read.py').read_text()
p=p.replace(' m.uc.mem_write(STATE,bytes(32));',' from unicorn import UC_HOOK_MEM_WRITE\n def codewrite(uc,k,a,s,v,d):\n  print("CODE_WRITE",hex(uc.reg_read(UC_M68K_REG_PC)),hex(a),s,hex(v),"A0",hex(uc.reg_read(UC_M68K_REG_A0)),"A2",hex(uc.reg_read(UC_M68K_REG_A2)),flush=True)\n m.uc.hook_add(UC_HOOK_MEM_WRITE,codewrite,begin=0x40146410,end=0x4014641a)\n m.uc.mem_write(STATE,bytes(32));')
Path('work/debug-worker-codewrite.py').write_text(p)
