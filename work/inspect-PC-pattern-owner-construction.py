from pathlib import Path
exec(Path('work/inspect-PC-copy-provenance.py').read_text().split('for a,n')[0]);c.skipdata=True
for a,n in [(0x401461f4,64),(0x40025750,180),(0x40091fba,72)]:
 print('WINDOW',hex(a))
 for i in c.disasm(d[a-b:a-b+n],a):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
needle=(0x4002c1d2).to_bytes(4,'big');print('FUNCTION_REFERENCES',[hex(b+i) for i in range(0,len(d)-4,2) if d[i:i+4]==needle])
