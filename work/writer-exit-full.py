exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x40034a8c,0x40034c78),(0x40034c78,0x40034d7c),(0x40035268,0x400353d0),(0x4001330c,0x40013370),(0x400134e4,0x40013564),(0x400208a0,0x400208da),(0x40008de0,0x40008eb0),(0x40025628,0x40025796)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
pathlib.Path('work/writer-exit-full.txt').write_text('\n'.join(out));print('\n'.join(out[:235]))
strings=[]
for m in re.finditer(rb'[\x20-\x7e]{8,}',b):
 if re.search(rb'exception|unwind|terminate|bad_alloc|eh_frame|longjmp',m.group(),re.I):strings.append((hex(base+m.start()),m.group().decode()))
print('EXCEPTION STRINGS',strings[:45])
