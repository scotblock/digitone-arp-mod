exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x400d8170,0x400d82e0),(0x4003f110,0x4003f160)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/writer-event-pump.txt').write_text('\n'.join(out));print('\n'.join(out))
