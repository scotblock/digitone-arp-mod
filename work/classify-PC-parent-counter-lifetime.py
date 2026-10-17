from pathlib import Path
import json,collections
exec(Path('work/inspect-PC-pattern-field-writers.py').read_text().split('for a,n')[0])
needle=bytes.fromhex('2039419f0d70');p=0;rows=[]
while True:
 p=d.find(needle,p)
 if p<0:break
 ins=list(c.disasm(d[p:p+70],b+p));ops=[i.mnemonic+' '+i.op_str for i in ins]
 kind='decrement' if any(i.mnemonic=='subq.l' and i.op_str=='#$1, d1' for i in ins[:8]) else 'other'
 rows.append({'pc':hex(b+p),'kind':kind,'instructions':ops});p+=1
increments=[];p=0;needle=bytes.fromhex('d3b9419f0d74')
while True:
 p=d.find(needle,p)
 if p<0:break
 assert d[p+6:p+20]==bytes.fromhex('2439419f0d70d58023c2419f0d70')
 increments.append(b+p);p+=1
table=0x4028e63c;count=int.from_bytes(d[table-b:table-b+4],'big');entries=[int.from_bytes(d[table-b+4+j*4:table-b+8+j*4],'big') for j in range(count)]
assert entries==sorted(entries)
pairs=[]
for pc in increments:
 ctor=max((a for a in entries if a<=pc),default=0)
 end=d.find(bytes.fromhex('4e75'),pc-b+20)
 thunk=b+end+2
 raw=d[thunk-b:thunk-b+6]
 refs=[];p=0
 while True:
  p=d.find(thunk.to_bytes(4,'big'),p)
  if p<0:break
  refs.append(hex(b+p));p+=1
 is_thunk=raw[:2]==bytes.fromhex('4ef9')
 pairs.append({'increment_pc':hex(pc),'preceding_constructor_table_entry':hex(ctor),'following_rts':hex(b+end),'following_jmp_thunk':hex(thunk) if is_thunk else None,'thunk_target':hex(int.from_bytes(raw[2:6],'big')) if is_thunk else None,'literal_thunk_references':refs if is_thunk else [],'following_code_is_jmp_thunk':is_thunk})
out={'counter':'419f0d70:419f0d74','literal_read_windows':rows,'counts':dict(collections.Counter(x['kind'] for x in rows)),'increment_sites':pairs,'increment_count':len(increments),'startup_table':{'address':hex(table),'count':count,'entries':[hex(a) for a in entries]},'limits':'Literal instruction scan and nearest preceding startup entries; computed stores/callers and full shutdown dispatcher are not certified. First RTS scan is a structural candidate, not control-flow proof.'}
Path('outputs/Digitone-E04-PC-parent-counter-lifetime-static.json').write_text(json.dumps(out,indent=2))
print(out['counts'])
for kind in ['increment','other']:
 for x in [x for x in rows if x['kind']==kind][:3]:print(x)
