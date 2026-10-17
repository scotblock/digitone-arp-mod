exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for s,e in [(0x4012fa0e,0x4012fa30),(0x40029a92,0x40029b92),(0x4002377a,0x400237b0),(0x400206b2,0x40020752),(0x400132e0,0x40013310)]:
 lines.append(hex(s))
 for i in md.disasm(b[s-base:e-base],s):
  lines.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
  if i.mnemonic=='rts':break
pathlib.Path('work/writer-prelude-detail.txt').write_text('\n'.join(lines))
print('\n'.join(lines))
