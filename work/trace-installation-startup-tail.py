exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for lo,hi in [(0x400004e8,0x4000053e),(0x400dac16,0x400dac70),(0x400dabce,0x400dac16),(0x4008cb1e,0x4008cb80)]:
 print('WINDOW',hex(lo));print('\n'.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[lo-base:hi-base],lo)))
for val in [0x40241c90,0x40241c98,0x40242000,0x401fe594,0x401fe5a4]:
 pat=val.to_bytes(4,'big');print(hex(val),[hex(base+m.start()) for m in re.finditer(re.escape(pat),b)])
