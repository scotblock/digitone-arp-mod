exec(open('work/disassemble.py').read().split('out=[]')[0])
out=[]
for start,end in [(0x40093c26,0x40093d66),(0x4009719e,0x4009743e),(0x4009755e,0x40097848),(0x400f0626,0x400f0690),(0x4009dd5c,0x4009df78),(0x4009d4f0,0x4009d5d0)]:
 out.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):
  out.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/context-storage-audit.txt').write_text('\n'.join(out))
print('\n'.join(out))
