from pathlib import Path
exec(Path('work/inspect-PC-pattern-field-writers.py').read_text().split('for a,n')[0])
for target in [0x40028354,0x4002c1a0]:
 for off in range(0,len(d)-6,2):
  direct=d[off:off+2] in [b'\x4e\xb9',b'\x4e\xf9'] and int.from_bytes(d[off+2:off+6],'big')==target
  rel=d[off:off+2] in [b'\x4e\xba',b'\x61\x00',b'\x60\x00'] and b+off+2+int.from_bytes(d[off+2:off+4],'big',signed=True)==target
  if direct or rel:
   print('CALL',hex(target),hex(b+off))
   for i in c.disasm(d[off-26:off+12],b+off-26):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
 needle=target.to_bytes(4,'big');refs=[hex(b+off) for off in range(0,len(d)-4,2) if d[off:off+4]==needle];print('WORDS',hex(target),refs)
