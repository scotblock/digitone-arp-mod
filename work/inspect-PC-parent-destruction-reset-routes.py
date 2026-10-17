from pathlib import Path
exec(Path('work/inspect-PC-pattern-field-writers.py').read_text().split('for a,n')[0])
for a,n in [(0x40152a1c,410),(0x40152b98,80),(0x4009c6d0,55),(0x4009c5ae,110)]:
 print('WINDOW',hex(a))
 for i in c.disasm(d[a-b:a-b+n],a):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
for target in [0x40152a1c,0x40152bae,0x4015141c,0x4009c6d0,0x4009c5ae]:
 needle=target.to_bytes(4,'big');refs=[hex(b+off) for off in range(0,len(d)-4,2) if d[off:off+4]==needle];print('WORDS',hex(target),refs)
