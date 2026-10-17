exec(open('work/disassemble.py').read().split('out=[]')[0])
import json
def string(a):
 p=a-base
 return b[p:b.index(b'\0',p)].decode('ascii')
rows=[]
for raw in range(-1,35):
 ui=raw+1
 name=string(struct.unpack_from('>I',b,0x40200378-base+4*ui)[0])
 short=string(struct.unpack_from('>I',b,0x40200408-base+4*ui)[0])
 row=list(b[0x401b107c-base+13*raw:0x401b107c-base+13*(raw+1)]) if raw>=0 else None
 pcs=[i for i in range(12) if row[i]] if row else list(range(12))
 if row:assert bool(row[0])==bool(row[12])
 rows.append(dict(raw_scale=raw,name_index=ui,name=name,short_name=short,pitch_classes=pcs,degree_bytes=row))
checks=0
for row in rows:
 for root in range(12):
  for note in range(128):
   rel=note-root
   while rel<0:rel+=12
   while rel>12:rel-=12
   observed=True if row['raw_scale']==-1 else bool(row['degree_bytes'][rel])
   assert observed==((note-root)%12 in row['pitch_classes'])
   checks+=1
result=dict(source='Decoded OS 1.42 tables; static comparison, not CPU execution',membership_cases=checks,scales=rows)
pathlib.Path('outputs/Digitone-OS1.42-scale-map.json').write_text(json.dumps(result,indent=2)+'\n')
print('Membership cases:',checks)
for r in rows:print(r['raw_scale'],r['name'],r['pitch_classes'])
