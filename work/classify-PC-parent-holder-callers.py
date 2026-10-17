from pathlib import Path
exec(Path('work/inspect-PC-pattern-field-writers.py').read_text().split('for a,n')[0])
import collections,json
rows=[];groups=collections.Counter();needle=b'\x48\x79\x41\x9f\x0d\xe4';pos=0
while True:
 pos=d.find(needle,pos)
 if pos<0:break
 following=list(c.disasm(d[pos+6:pos+24],b+pos+6,count=3));text=[i.mnemonic+' '+i.op_str for i in following];groups[text[0] if text else 'undecoded']+=1;rows.append({'argument_pc':hex(b+pos),'following':text});pos+=1
print(groups)
Path('outputs/Digitone-E04-PC-parent-global-holder-callers.json').write_text(json.dumps({'literal_argument_calls':rows,'target_groups':dict(groups),'limit':'Literal scan candidates; no global computed pointer proof.'},indent=2))
for a,n in [(0x4001c93c,46),(0x40152fb2,44),(0x400f800a,44)]:
 print('WINDOW',hex(a))
 for i in c.disasm(d[a-b:a-b+n],a):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
