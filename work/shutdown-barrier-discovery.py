exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for start,end in [(0x400ae9b0,0x400aeb32),(0x400d95cc,0x400d9620),(0x400d920c,0x400d9278),(0x4008dfd2,0x4008e034),(0x4015a5a4,0x4015a61e)]:
 out.append('WINDOW '+hex(start))
 for i in md.disasm(b[start-base:end-base],start):out.append(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}')
pathlib.Path('work/shutdown-barrier-discovery.txt').write_text('\n'.join(out))
print('\n'.join(out))
