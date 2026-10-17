exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for s,e in [(0x4009bcb8,0x4009bd68),(0x400f00ea,0x400f00ee)]:
 lines.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):lines.append(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
lines.append('QUEUE HANDLER STACK REFERENCES')
for i in md.disasm(b[0x400efcb8-base:0x400f003a-base],0x400efcb8):
 if 'a7' in i.op_str:lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/queue-reset-frame-audit.txt').write_text('\n'.join(lines));print('\n'.join(lines))
