from pathlib import Path
import sys,json
sys.path.insert(0,'work/emulator-deps')
from capstone import *
d=Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes();cs=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040)
for target in [0x400f0580,0x400eabb4]:
 needle=bytes.fromhex('4eb9')+target.to_bytes(4,'big');p=0
 while True:
  p=d.find(needle,p)
  if p<0:break
  addr=0x40000400+p;print('direct candidate',hex(target),hex(addr))
  for i in cs.disasm(d[p-10:p+24],addr-10):print(hex(i.address),i.mnemonic,i.op_str)
  p+=2
