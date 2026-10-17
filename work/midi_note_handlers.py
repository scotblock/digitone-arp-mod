exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for n in range(16):lines.append(f'STATUS {n:x} -> {struct.unpack_from(">I",b,0x401aade0-base+4*n)[0]:08x}')
for n in [8,9,11]:
 start=struct.unpack_from('>I',b,0x401aade0-base+4*n)[0];end=start+0x180
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/midi-note-handlers.txt').write_text('\n'.join(lines));print('\n'.join(lines))
