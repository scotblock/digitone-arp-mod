exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[];ins=list(md.disasm(b[:0x170000],base))
refs=[]
for m in re.finditer(b'\x41\x99',b):
 if m.start()+4<=len(b):
  value=struct.unpack_from('>I',b,m.start())[0]
  if 0x4199d4e0<=value<0x4199d538:refs.append((base+m.start(),value))
for a,v in refs:out.append(f'NEARBY LITERAL {a:08x}: {v:08x}')
for t in [0x400efc56,0x400f00ea]:
 out.append(f'TARGET {t:08x}')
 for k,i in enumerate(ins):
  if f'${t:x}' in i.op_str:out.extend(f'{j.address:08x} {j.mnemonic:10} {j.op_str}' for j in ins[max(0,k-3):k+3])
for s,e in [(0x400f000c,0x400f003a),(0x400efed6,0x400efef6),(0x400004b2,0x40000518),(0x400efc50,0x400efc56)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
pathlib.Path('work/busy-marker-alias-boundaries.txt').write_text('\n'.join(out));print('\n'.join(out))
