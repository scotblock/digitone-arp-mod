"""Relocate existing PC-only helpers without removing any reachable checks."""
import pathlib,sys,json,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import cfisa as cf
BASE=0x47be0000
old=pathlib.Path('work/cache-context-overlay.bin').read_bytes()
layout=json.loads(pathlib.Path('work/native-overlay-layout.json').read_text())
build=json.loads(pathlib.Path('work/cache-context-build.json').read_text())
roots={k:v['address'] for k,v in layout.items()}
roots.update(slot=build['slot_address'],copy=build['copy_address'],first_copy=build['first_copy_address'],reset=BASE+0x666,allocator_original=BASE+0x754)
alias={BASE+0x1aa:roots['slot']}
def target(a):return alias.get(a,a)
def instruction(a):return cf.decode(lambda p:int.from_bytes(old[a-BASE+p:a-BASE+p+2],'big'),a)
todo=list(roots.values());seen={}
while todo:
 a=target(todo.pop())
 if a in seen:continue
 assert BASE<=a<BASE+len(old) and not BASE+1904<=a<BASE+2324,hex(a)
 i=instruction(a);raw=old[a-BASE:a-BASE+i.length]
 assert not i.flags & (cf.ILLEGAL|cf.PCREL|cf.FPU|cf.LINEF),(hex(a),i)
 seen[a]=(i,raw)
 if i.flow not in (cf.F_BRA,cf.F_JMP,cf.F_RTS,cf.F_RTE):todo.append(a+i.length)
 if i.target is not None and BASE<=i.target<BASE+len(old):todo.append(target(i.target))
 # These three literal code pointers are return continuations, not CFG branches.
 if len(raw)==6 and raw[:2] in (bytes.fromhex('4879'),bytes.fromhex('2ebc')):
  v=int.from_bytes(raw[2:],'big')
  if BASE<=v<BASE+len(old):todo.append(v)
entries=[]
for a,(i,raw) in sorted(seen.items()):
 transfer=i.flow in (cf.F_BCC,cf.F_BRA,cf.F_BSR) or (i.flow in (cf.F_JSR,cf.F_JMP) and i.target in seen|alias.keys())
 if transfer:
  op=raw[0] if raw[0]&0xf0==0x60 else (0x61 if i.flow==cf.F_JSR else 0x60)
  entries.append({'old':a,'raw':raw,'branch':op,'target':target(i.target),'length':4})
 else:entries.append({'old':a,'raw':raw,'length':len(raw)})
def positions():
 p=BASE;mapping={}
 for e in entries:mapping[e['old']]=p;p+=e['length']
 return mapping,p
for _ in range(30):
 mapping,end=positions();changed=False
 for e in entries:
  if 'branch' in e:
   d=mapping[e['target']]-mapping[e['old']]-2
   if e['length']==4 and -128<=d<=127 and d!=0:e['length']=2;changed=True
 if not changed:break
mapping,end=positions();table_address=(end+15)//16*16
refs={**mapping,**{a:mapping[b] for a,b in alias.items()},BASE+1904:table_address}
code=bytearray();relocations=[]
for e in entries:
 a=e['old'];raw=e['raw']
 if 'branch' in e:
  d=mapping[e['target']]-mapping[a]-2
  raw=bytes([e['branch'],d&255]) if e['length']==2 else bytes([e['branch'],0])+d.to_bytes(2,'big',signed=True)
  relocations.append({'old':hex(a),'new':hex(mapping[a]),'old_bytes':e['raw'].hex(),'new_bytes':raw.hex(),'kind':'relative transfer'})
 elif len(raw)==6 and int.from_bytes(raw[2:],'big') in refs:
  assert raw[:2] in [bytes.fromhex(x) for x in ['4879','2ebc','207c','4eb9','4ef9']],(hex(a),raw.hex())
  raw=raw[:2]+refs[int.from_bytes(raw[2:],'big')].to_bytes(4,'big')
  relocations.append({'old':hex(a),'new':hex(mapping[a]),'old_bytes':e['raw'].hex(),'new_bytes':raw.hex(),'kind':'literal pointer'})
 code.extend(raw)
assert len(code)==end-BASE
code_bytes=len(code);code.extend(bytes(table_address-BASE-len(code)));code.extend(old[1904:2324])
new_layout={}
ordered_roots=sorted((mapping[a],k) for k,a in roots.items())
for j,(a,k) in enumerate(ordered_roots):
 metadata={key:value for key,value in layout.get(k,{}).items() if key!='size'}
 if k in layout:metadata['previous_size']=layout[k]['size']
 new_layout[k]={**metadata,'address':a,'size':(ordered_roots[j+1][0] if j+1<len(ordered_roots) else end)-a}
hooks=[]
for site,name,op,n in [(0x40093ef4,'producer_capture','4ef9',8),(0x400f0626,'allocate_clear','4ef9',6),(0x4009dda6,'before','4eb9',6),(0x4009de46,'caller_commit','4ef9',10),(0x4009df9a,'pitch_hook','4ef9',8),(0x4009344e,'first_copy','4ef9',6),(0x40093892,'copy','4eb9',6)]:
 hooks.append({'site':site,'name':name,'bytes':op+mapping[roots[name]].to_bytes(4,'big').hex()+'4e71'*((n-6)//2)})
info={'firmware_modified':False,'PC_only_runtime_extension':True,'size':len(code),'previous_size':len(old),'code_bytes':code_bytes,'previous_reachable_code_bytes':sum(len(r) for i,r in seen.values()),'table_address':table_address,'table_bytes':420,'table_unchanged':bytes(code[table_address-BASE:])==old[1904:2324],'new_state':False,'sha256':hashlib.sha256(code).hexdigest(),'layout':new_layout,'hooks':hooks,'instruction_map':{str(a):mapping[a] for a in seen},'relocations':relocations,'removed_checks':0,'method':'Retain all reachable instructions, shorten transfers, remove unreachable padding and internal slot forwarding jump. Preserve storage, register saves, interrupt masking, and check operands.'}
pathlib.Path('work/packed-context-overlay.bin').write_bytes(code)
pathlib.Path('work/packed-context-build.json').write_text(json.dumps(info,indent=2))
print(json.dumps({k:v for k,v in info.items() if k not in ['layout','hooks','instruction_map','relocations']},indent=2))
