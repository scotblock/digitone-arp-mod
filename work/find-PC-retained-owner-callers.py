from pathlib import Path
exec(Path('work/inspect-PC-copy-provenance.py').read_text().split('for a,n')[0]);c.skipdata=True
target=0x4002f80c
for off in range(0,len(d)-6,2):
 direct=d[off:off+2]==b'\x4e\xb9' and int.from_bytes(d[off+2:off+6],'big')==target
 relative=d[off:off+2]==b'\x4e\xba' and b+off+2+int.from_bytes(d[off+2:off+4],'big',signed=True)==target
 if direct or relative:
  print('CALL',hex(b+off))
  for i in c.disasm(d[off-48:off+10],b+off-48):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
