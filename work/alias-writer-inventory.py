exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for off in range(0,len(b)-4,2):
 value=struct.unpack_from('>I',b,off)[0]
 if 0x431dbfb8<=value<=0x431dc4c4:
  lines.append(f'QUEUE RANGE RAW {base+off:08x} {value:08x} '+b[max(0,off-8):off+8].hex())
for i in md.disasm(b[:0x170000],base):
 if '$3cb(' in i.op_str or '$3ce(' in i.op_str:
  lines.append(f'FIELD ACCESS {i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
for target in [0x40032580,0x40032846]:
 refs=[]
 for off in range(0,0x170000-6,2):
  op=struct.unpack_from('>H',b,off)[0]
  if op in (0x4eb9,0x4ef9) and struct.unpack_from('>I',b,off+2)[0]==target:refs.append(base+off)
  elif op in (0x4eba,0x4efa,0x6100,0x6000) and base+off+2+struct.unpack_from('>h',b,off+2)[0]==target:refs.append(base+off)
 lines.append(f'SETTER CALL REFS {target:08x}: '+','.join(f'{x:08x}' for x in refs))
 lines.append(f'SETTER RAW REFS {target:08x}: '+','.join(f'{base+m.start():08x}' for m in re.finditer(re.escape(struct.pack('>I',target)),b)))
pathlib.Path('work/alias-writer-inventory.txt').write_text('\n'.join(lines));print('\n'.join(lines))
