from pathlib import Path
exec(Path('work/inspect-PC-pattern-field-writers.py').read_text().split('for a,n')[0])
for a,n in [(0x400283b0,172),(0x4002c12c,128),(0x400a8e2c,30)]:
 print('WINDOW',hex(a))
 for i in c.disasm(d[a-b:a-b+n],a):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
print('PARENT_TABLE',[(hex(k),hex(int.from_bytes(d[0x401956ec-b+k:0x401956ec-b+k+4],'big'))) for k in range(0,0x40,4)])
