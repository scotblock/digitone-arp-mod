from pathlib import Path
exec(Path('work/inspect-PC-copy-provenance.py').read_text().split('for a,n')[0]);c.skipdata=True
for table in [0x40190b44,0x40195858,0x40190474]:
 print('TABLE',hex(table),[(hex(table+k),hex(int.from_bytes(d[table-b+k:table-b+k+4],'big'))) for k in range(0,64,4)])
for a,n in [(0x40025712,80),(0x400f867c,80),(0x400113d0,32)]:
 print('WINDOW',hex(a))
 for i in c.disasm(d[a-b:a-b+n],a):print(hex(i.address),i.mnemonic,i.op_str)
