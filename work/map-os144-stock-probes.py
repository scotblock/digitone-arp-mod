import sys,json,struct,collections
from pathlib import Path
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.cfisa import decode
base=0x40000400;old=Path('work/section-3.bin').read_bytes();new=Path('work/os144/section-3.bin').read_bytes()
targets={'allocated_return':0x400f065a,'release':0x400f065c,'queue_publish':0x400f07ac,'pattern_publish':0x40094652,'transition_done':0x40095bd6,'cc_handler':0x400dea02,'input_dispatch_1':0x400db246,'input_dispatch_2':0x400db2ac,'selector':0x4009719e,'pitch':0x4009df9a,'producer':0x40093ef4,'acceptance':0x4009dd80}
targets.update({'sustain_init':0x400e0f9e,'sustain_on':0x400e10d6,'sustain_release':0x400e11bc})
report={'sites':{},'address_correspondences':[],'method':'Unique adjacent eight-byte anchor voting followed by sequential ColdFire instruction checks. Candidates require runtime evidence.'}
for name,addr in targets.items():
 off=addr-base;votes=collections.Counter()
 for rel in range(-64,128,2):
  p=off+rel;token=old[p:p+8];found=new.find(token)
  if found>=0 and found%2==0 and new.find(token,found+1)<0:votes[found-p]+=1
 delta,count=votes.most_common(1)[0];at=addr+delta
 row={'old':hex(addr),'new':hex(at),'anchors':count,'instruction_pairs':[]};p=0
 while p<180:
  ia=decode(lambda rel:struct.unpack_from('>H',old,off+p+rel)[0],addr+p);ib=decode(lambda rel:struct.unpack_from('>H',new,at-base+p+rel)[0],at+p)
  if (ia.op,ia.length,ia.flow)!=(ib.op,ib.length,ib.flow):break
  a=old[off+p:off+p+ia.length];b=new[at-base+p:at-base+p+ib.length]
  row['instruction_pairs'].append({'offset':p,'op':ia.op,'old':a.hex(),'new':b.hex()})
  for k in range(2,ia.length-3,2):
   av=int.from_bytes(a[k:k+4],'big');bv=int.from_bytes(b[k:k+4],'big')
   if 0x40000000<=av<0x50000000 and 0x40000000<=bv<0x50000000:report['address_correspondences'].append({'site':name,'old':hex(av),'new':hex(bv)})
  p+=ia.length
 row['shape_matching_bytes']=p;report['sites'][name]=row
report['global_candidates']={}
for address in [0x4131ba1c,0x4131b9e4,0x41962008,0x41962010,0x41962050]:
 token=address.to_bytes(4,'big');p=old.find(token);votes=collections.Counter();evidence=[]
 while p>=0:
  for rel in [-20,-12,4,12]:
   anchor=old[p+rel:p+rel+8];q=new.find(anchor)
   if q>=0 and new.find(anchor,q+1)<0:
    ref=q-rel
    if new[ref-2:ref]==old[p-2:p]:
     value=int.from_bytes(new[ref:ref+4],'big')
     if 0x40000000<=value<0x50000000:votes[value]+=1;evidence.append({'old_ref':hex(base+p),'new_ref':hex(base+ref),'value':hex(value)})
  p=old.find(token,p+1)
 report['global_candidates'][hex(address)]={'votes':[(hex(v),n) for v,n in votes.most_common()],'evidence':evidence}
Path('work/os144/stock-probe-map.json').write_text(json.dumps(report,indent=2))
for key,value in report['sites'].items():print(key,value['new'],value['anchors'],value['shape_matching_bytes'])
print(report['address_correspondences'])
