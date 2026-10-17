exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for off in range(0,0x170000-4,2):
 value=struct.unpack_from('>I',b,off)[0]
 if 0x401a4800<=value<=0x401a4a00:out.append(f'TABLE REF {base+off:08x} {value:08x}')
for s,e in [(0x400eeb00,0x400eec58),(0x400eea80,0x400eeb00)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/writer-install-dispatch.txt').write_text('\n'.join(out));print('\n'.join(out))
