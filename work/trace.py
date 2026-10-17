import pathlib,struct,json,hashlib
exec(pathlib.Path('work/firmware_inspect.py').read_text().split('result=')[0])
sections=[struct.unpack('>IIII',c[32+i*16:48+i*16]) for i in range(u(c[28:32]))]
print('trailer',c[-32:].hex(),'sha256match',hashlib.sha256(c[:-32]).digest()==c[-32:])
raw=pathlib.Path('work/section-3.bin').read_bytes(); base=0x40000400
targets=[b'ArpSetupMenuView\0',b'T%d ARPEGGIATOR\0',b'ScaleMenuView\0',b'PENTATONIC MINOR\0']
for t in targets:
 at=raw.find(t); addr=base+at;needle=struct.pack('>I',addr)
 refs=[i for i in range(len(raw)-3) if raw[i:i+4]==needle]
 print(t.decode().strip('\0'),hex(at),hex(addr),'absolute refs',[(hex(i),hex(base+i),raw[max(0,i-8):i+12].hex()) for i in refs][:30])
for sid,off,n,dest in sections:
 s=c[off:off+n]
 print('section',sid,'tail',s[-16:].hex(),'anchor',s.find(bytes.fromhex('bef9a3f7c67178f2')))
