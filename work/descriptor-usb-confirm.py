exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for s,e in [(0x400030a4,0x40003338),(0x40006032,0x40006142),(0x40006acc,0x40006b52),(0x40007224,0x40007264)]:
 lines.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):lines.append(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
lines.append('ENDPOINT TABLE '+','.join(hex(x) for x in struct.unpack_from('>8I',b,0x4016cfbc-base)))
pathlib.Path('work/descriptor-usb-confirm.txt').write_text('\n'.join(lines));print('\n'.join(lines))
