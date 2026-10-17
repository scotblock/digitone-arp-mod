exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x4009df78,0x4009e14c),(0x4009e4a8,0x4009e600),(0x400f03a0,0x400f0440)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/voice-pitch-followup.txt').write_text('\n'.join(lines));print('\n'.join(lines))
