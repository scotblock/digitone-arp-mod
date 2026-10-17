exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x400b70f2,0x400b71c0),(0x4009ce00,0x4009ce90)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
for i in md.disasm(b[0x4009c838-base:0x4009d000-base],0x4009c838):
 if 'sr' in i.op_str or i.mnemonic in ('rte','rts'):out.append(f'AUDIO RETURN/MASK {i.address:08x} {i.mnemonic} {i.op_str}')
pathlib.Path('work/writer-dispatch-tail.txt').write_text('\n'.join(out));print('\n'.join(out))
