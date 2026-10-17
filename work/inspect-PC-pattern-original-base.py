from pathlib import Path
exec(Path('work/inspect-PC-copy-provenance.py').read_text().split('for a,n')[0]);c.skipdata=True
for a,n in [(0x40153372,140),(0x400a86de,65)]:
 print('WINDOW',hex(a))
 for i in c.disasm(d[a-b:a-b+n],a):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
