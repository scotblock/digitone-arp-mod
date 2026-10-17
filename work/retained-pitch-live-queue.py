exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for s,e in [(0x4009dd48,0x4009dfaa),(0x4009755e,0x40097596),(0x400efcb0,0x400f0030)]:
 lines.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):lines.append(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/retained-pitch-live-queue.txt').write_text('\n'.join(lines))
print('\n'.join(lines))
