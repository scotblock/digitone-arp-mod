exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x4003d63e,0x4003d692),(0x400d6efc,0x400d6f52),(0x400d0a44,0x400d0a60),(0x4003ac84,0x4003acb6),(0x4003b5fe,0x4003b6cc),(0x40007200,0x40007224),(0x4009c838,0x4009c872)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
for code in [10,11,12]:
 off=0x4003c8d2-base+2*(code-1);rel=struct.unpack_from('>h',b,off)[0]
 out.append(f'UI JUMP code {code}: table offset {rel:x}, target {0x4003c8d2+rel:08x}')
for a in range(0x40177ba8,0x40177bf4,4):out.append(f'VTABLE {a:08x} slot {a-0x40177ba8:02x}: {struct.unpack_from(">I",b,a-base)[0]:08x}')
pathlib.Path('work/outer-protection-ui-route.txt').write_text('\n'.join(out));print('\n'.join(out))
