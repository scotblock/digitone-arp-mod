exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
ins=list(md.disasm(b[:0x170000],base))
for i in ins:
 if '$40016d56' in i.op_str or '$4000170c' in i.op_str:out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
for off in range(0,len(b)-6,2):
 if struct.unpack_from('>H',b,off)[0] in (0x61ff,0x60ff) and base+off+2+struct.unpack_from('>i',b,off+2)[0]==0x40016d56:out.append(f'BRANCH32 {base+off:08x}')
for s,e in [(0x4009dc26,0x4009dc60),(0x400012c8,0x40001320),(0x4009bcf0,0x4009bd22)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/audio-task-scheduler-discovery.txt').write_text('\n'.join(out));print('\n'.join(out))
