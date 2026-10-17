exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x400dc758,0x400dc8c4),(0x400dc2f6,0x400dc3e2),(0x400dee6e,0x400deed0)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/midi-channel-to-held.txt').write_text('\n'.join(lines));print('\n'.join(lines))
