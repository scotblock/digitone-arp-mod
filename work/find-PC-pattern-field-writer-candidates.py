from pathlib import Path
exec(Path('work/inspect-PC-pattern-field-writers.py').read_text().split('for a,n')[0]);c.skipdata=False
rows=[]
for end in range(2,len(d)-2,2):
 if d[end:end+2]!=b'\x00\x20':continue
 for off in range(max(0,end-8),end,2):
  ins=list(c.disasm(d[off:end+2],b+off,count=1))
  if not ins:continue
  i=ins[0]
  if i.size!=end+2-off or not i.mnemonic.startswith(('move.','clr.','lea.')):continue
  if '$20(a' not in i.op_str.split(', ')[-1]:continue
  rows.append({'pc':hex(i.address),'bytes':i.bytes.hex(),'text':i.mnemonic+' '+i.op_str})
import json
Path('outputs/PC-pattern-field-writer-candidates.json').write_text(json.dumps(rows,indent=2));print('CANDIDATES',len(rows))
for row in rows:print(row)
