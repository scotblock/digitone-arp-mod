from pathlib import Path
exec(Path('work/inspect-PC-pattern-field-writers.py').read_text().split('for a,n')[0])
for a,n in [(0x40149fba,166),(0x40146410,148)]:
 print('WINDOW',hex(a))
 for i in c.disasm(d[a-b:a-b+n],a):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
print('CONTROL_TABLE',[(hex(k),hex(int.from_bytes(d[0x40191b98-b+k:0x40191b98-b+k+4],'big'))) for k in range(0,0x20,4)])
