exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
def window(start,end):
 lines.append(f'\nWINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
window(0x4002ecea,0x4002efb0)
window(0x400914b2,0x40091780)
window(0x4002eab2,0x4002ec5c)
# Decode jump-table targets independently; never treat table bytes as instructions.
table=0x4004eb94
for n in range(9):
 delta=struct.unpack_from('>h',b,table-base+2*n)[0];target=table+delta
 lines.append(f'\nEDIT CASE {n+1} TARGET {target:08x}')
 window(target,min(target+180,0x4004ef30))
pathlib.Path('work/arp-settings.txt').write_text('\n'.join(lines))
print('\n'.join(lines))
