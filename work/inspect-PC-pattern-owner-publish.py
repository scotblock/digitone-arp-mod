from pathlib import Path
exec(Path('work/inspect-PC-copy-provenance.py').read_text().split('for a,n')[0]);c.skipdata=True
for i in c.disasm(d[0x401532c2-b:0x40153332-b],0x401532c2):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
