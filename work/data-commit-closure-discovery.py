exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x40128448,0x401284e0),(0x40007e3e,0x40007e98),(0x40034226,0x40034380),(0x40020c8c,0x40020d20)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
for s,e in [(0x4000879c,0x400088ca),(0x40008ca4,0x40008de0),(0x4001341c,0x40013478)]:
 out.append(f'CALLS {s:08x}..{e:08x}')
 for i in md.disasm(b[s-base:e-base],s):
  if i.mnemonic.split('.')[0] in ['jsr','bsr','jmp'] or ('lea' in i.mnemonic and '$400' in i.op_str):out.append(f'{i.address:08x} {i.mnemonic} {i.op_str}')
pathlib.Path('work/data-commit-closure-discovery.txt').write_text('\n'.join(out));print('\n'.join(out))
