exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for address in [0x41342150,0x40093b84,0x40093b72,0x407b00cc,0x4001fc74]:
 refs=[base+m.start() for m in re.finditer(re.escape(struct.pack('>I',address)),b)]
 lines.append(f'REFS {address:08x} {[hex(x) for x in refs]}')
 if address==0x41342150:
  for x in refs:
   start=x-12;end=x+42
   lines.append(f'WINDOW {start:08x}')
   for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/active-pattern-refs.txt').write_text('\n'.join(lines));print('\n'.join(lines))
