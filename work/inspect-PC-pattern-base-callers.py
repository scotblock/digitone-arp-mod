from pathlib import Path
exec(Path('work/inspect-PC-copy-provenance.py').read_text().split('for a,n')[0])
c.skipdata=True
for a,n in [(0x400113ec,160),(0x4002f41c,180),(0x400921a0,125),(0x4002c1d2,80),(0x400fb504,60)]:
 print('WINDOW',hex(a))
 for i in c.disasm(d[a-b:a-b+n],a):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
