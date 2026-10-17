exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x40004d40,0x40004e20),(0x400dcb8a,0x400dccb0),(0x400d9660,0x400d9710)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/midi-parser-candidates.txt').write_text('\n'.join(lines));print('\n'.join(lines))
