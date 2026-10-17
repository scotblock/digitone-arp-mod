exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x4009bd20,0x4009bd8a),(0x4009e320,0x4009e36c),(0x40001696,0x400017b0),(0x40000400,0x40000510)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
for t in [0x40016d56,0x4009c838]:
 out.append(f'RAW REFS {t:08x} '+','.join(hex(base+m.start()) for m in re.finditer(re.escape(struct.pack('>I',t)),b)))
for i in md.disasm(b[0x4009c838-base:0x4009e36c-base],0x4009c838):
 if i.mnemonic in ('rts','rte') or ('sr' in i.op_str and 'macsr' not in i.op_str):out.append(f'AUDIO END/MASK {i.address:08x} {i.mnemonic} {i.op_str}')
pathlib.Path('work/interrupt-resume-inventory.txt').write_text('\n'.join(out));print('\n'.join(out))
