exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for start,end in [(0x4009ce78,0x4009cf22),(0x4009dc5e,0x4009e39e),(0x4009e70c,0x4009e77c),(0x4009f23c,0x4009f28c)]:
 out.append(f'\nENTRY {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/full-consumer-discovery.txt').write_text('\n'.join(out))
print('\n'.join(out))
