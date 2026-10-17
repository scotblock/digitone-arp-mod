exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x4013a4c0,0x4013a584),(0x401361e8,0x40136216),(0x4013b25c,0x4013b2d4),(0x4013b0f0,0x4013b158)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
for vt in [0x401764c8,0x40173e14]:
 out.append(f'VT EXTRA {vt:08x}')
 for off in [0x28,0x44,0x48,0x4c]:out.append(f'{off:02x}: {struct.unpack_from(">I",b,vt-base+off)[0]:08x}')
print('\n'.join(out));pathlib.Path('work/cleanup-notification-second.txt').write_text('\n'.join(out))
for path in ['work/section-2.bin','work/section-3.bin']:
 data=pathlib.Path(path).read_bytes();refs=[]
 for m in re.finditer(b'\x41\x99',data):
  if m.start()+4<=len(data):
   v=struct.unpack_from('>I',data,m.start())[0]
   if 0x4199d000<=v<0x4199da94:refs.append((m.start(),v))
 print(path,'RAM-area literals',len(refs),'payload refs',[(hex(p),hex(v)) for p,v in refs if 0x4199d510<=v<0x4199d520])
