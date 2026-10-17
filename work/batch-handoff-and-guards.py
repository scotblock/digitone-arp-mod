exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x40137012,0x401370e0),(0x40022548,0x40022574),(0x4001fc74,0x4001fcc0),(0x40025628,0x40025646),(0x400255d0,0x40025628),(0x400efca0,0x400efcd8),(0x400efe60,0x400eff24),(0x400effa0,0x400f0060),(0x400f0626,0x400f0688)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
pathlib.Path('work/batch-handoff-and-guards.txt').write_text('\n'.join(out));print('\n'.join(out))
