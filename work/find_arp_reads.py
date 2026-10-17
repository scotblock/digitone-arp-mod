exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for disp in [0x10f,0x110,0x111,0x114,0x116]:
 needle=struct.pack('>H',disp)
 lines.append(f'\nDISPLACEMENT {disp:x}')
 for m in re.finditer(re.escape(needle),b[:0x170000]):
  at=m.start()
  if at%2 or at<2:continue
  ins=list(md.disasm(b[at-2:at+8],base+at-2,count=1))
  if not ins or ins[0].size<4:continue
  i=ins[0]
  if f'${disp:x}(' not in i.op_str:continue
  lines.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic} {i.op_str}')
pathlib.Path('work/arp-reads.txt').write_text('\n'.join(lines));print('\n'.join(lines))
