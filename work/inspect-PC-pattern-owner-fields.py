from pathlib import Path
exec(Path('work/inspect-PC-copy-provenance.py').read_text().split('for a,n')[0]);c.skipdata=True
for a,n in [(0x4002c1fe,380),(0x40092000,80),(0x400113c0,60),(0x401464f4,210),(0x4000a1a6,14)]:
 print('WINDOW',hex(a))
 for i in c.disasm(d[a-b:a-b+n],a):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
for target in [0x4000a1a6,0x4002c1d2,0x4002f448]:
 refs=[]
 for off in range(0,len(d)-6,2):
  if d[off:off+2] in [b'\x4e\xb9',b'\x4e\xf9'] and int.from_bytes(d[off+2:off+6],'big')==target:refs.append(hex(b+off))
  elif d[off:off+2] in [b'\x61\x00',b'\x60\x00'] and b+off+2+int.from_bytes(d[off+2:off+4],'big',signed=True)==target:refs.append(hex(b+off)+' relative')
 print('CALLERS',hex(target),refs)
