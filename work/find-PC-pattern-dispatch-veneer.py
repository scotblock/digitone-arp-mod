from pathlib import Path
exec(Path('work/inspect-PC-copy-provenance.py').read_text().split('for a,n')[0]);c.skipdata=True
for off in range(0,len(d)-6,2):
 target=0x40030044
 found=d[off:off+2] in [b'\x4e\xb9',b'\x4e\xf9'] and int.from_bytes(d[off+2:off+6],'big')==target
 found=found or (d[off:off+2]==b'\x4e\xba' and b+off+2+int.from_bytes(d[off+2:off+4],'big',signed=True)==target)
 if found:
  print('CALL',hex(b+off))
  for i in c.disasm(d[off-32:off+10],b+off-32):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
