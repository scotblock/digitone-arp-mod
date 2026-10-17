from pathlib import Path
import json,sys
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import snapshot
import zlib,struct
r=json.loads(Path('outputs/Digitone-E04-PC-resident-deferred-startup-startup.json').read_text());case=next(x for x in r['cases'] if x['image']=='E04_restored');blob=snapshot._load_blob(case['ui_snapshot']);hits=[]
for base,packed in blob['pages'].items():
 data=zlib.decompress(packed)
 for target in [0x407ef9f4,0x40555ff4]:
  needle=target.to_bytes(4,'big');pos=0
  while True:
   pos=data.find(needle,pos)
   if pos<0:break
   if pos%2==0:hits.append({'address':hex(base+pos),'value':hex(target)})
   pos+=1
print(hits)
Path('outputs/Digitone-E04-PC-pattern-owner-pointer-aliases.json').write_text(json.dumps({'PC_only':True,'snapshot_word_matches':hits,'limit':'Value matches are candidates, not proven pointer ownership or all computed aliases.'},indent=2))
