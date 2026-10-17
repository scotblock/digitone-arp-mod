"""Read-only discovery of additional image sections and relative dispatches.
Candidate scans are explicitly not a whole-program ownership proof.
"""
import pathlib,struct,re,json,hashlib
exec(pathlib.Path('work/firmware_inspect.py').read_text().split('result=')[0])
container=c
exec(pathlib.Path('work/disassemble.py').read_text().split('out=[]')[0])
md.skipdata=True
ring=(0x400f021c,0x400f0296)
marker=(0x4199d510,0x4199d518)
sections=[]
for n in range(struct.unpack_from('>I',container,28)[0]):
 sid,off,size,dest=struct.unpack_from('>IIII',container,32+16*n)
 if sid in (2,3):
  data=pathlib.Path(f'work/section-{sid}.bin').read_bytes();form='previously decoded'
 else:
  data=container[off:off+size];form='stored bytes; no executable address assumption'
 matches=[]
 for k in range(len(data)-3):
  v=struct.unpack_from('>I',data,k)[0]
  if marker[0]<=v<marker[1] or ring[0]<=v<ring[1] or v in (0x4199d50c,0x4199d520,0x431dc4b8,0x431dc4bc,0x431dc4c0):
   matches.append(dict(offset=hex(k),value=hex(v)))
 sections.append(dict(id=sid,bytes=len(data),container_destination=hex(dest),form=form,sha256=hashlib.sha256(data).hexdigest(),matches=matches))
 # Raw additional sections are scratch artifacts, never flashable containers.
 if sid not in (2,3):pathlib.Path(f'work/storage-section-{sid}-stored.bin').write_bytes(data)

# Recover compiler's standard signed-word PC jump-table expression. Scan even
# offsets, not linear decode, to avoid losing tables after inline data.
dispatches=[];other_indexed=[]
for k in range(0,len(b)-10,2):
 op=struct.unpack_from('>H',b,k)[0]
 if op not in (0x4efb,0x4ebb):continue
 a=base+k
 i=next(md.disasm(b[k:k+16],a,count=1),None)
 if i is None:continue
 entry=dict(site=hex(a),bytes=i.bytes.hex(),instruction=f'{i.mnemonic} {i.op_str}')
 ext=struct.unpack_from('>H',b,k+2)[0]
 if ext&0x100: # full-extension addressing has separate unresolved semantics
  entry['reason']='full extension';other_indexed.append(entry);continue
 tablebase=a+2+((ext&255)^128)-128
 # Standard expression: move.w table(pc,index.l),dN; ext.l dN; jmp table(pc,dN.l)
 prev=list(md.disasm(b[max(0,k-6):k],a-6)) if k>=6 else []
 if len(prev)!=2 or not prev[0].mnemonic.startswith('move.w') or '(pc,' not in prev[0].op_str or prev[1].mnemonic!='ext.l':
  entry['reason']='not standard word-table expression';other_indexed.append(entry);continue
 reg=(ext>>12)&7
 if prev[1].op_str!=f'd{reg}' or not prev[0].op_str.endswith(f', d{reg}'):
  entry['reason']='register mismatch';other_indexed.append(entry);continue
 loadbase=prev[0].address+2+((struct.unpack_from('>H',b,k-4)[0]&255)^128)-128
 if loadbase!=tablebase:
  entry['reason']='load and jump bases differ';other_indexed.append(entry);continue
 # At most signed16 reach: if whole ring is outside it, no table value can
 # produce a ring address, independently of table length or selector bounds.
 can_reach=tablebase-32768<ring[1] and tablebase+32767>=ring[0]
 witnesses=[]
 if can_reach:
  # Discovery envelope only; selector/table length must be validated manually.
  for slot in range(256):
   pos=tablebase-base+slot*2
   if 0<=pos<=len(b)-2:
    disp=struct.unpack_from('>h',b,pos)[0];target=tablebase+disp
    if ring[0]<=target<ring[1]:witnesses.append(dict(slot=slot,target=hex(target)))
 entry.update(table_base=hex(tablebase),signed_word_can_reach_ring=can_reach,first_256_word_candidates=witnesses,table_length_verified=False)
 dispatches.append(entry)

# Two close tables have unsigned range rejection before dispatch. Exhaust the
# actual 65 and 222 slots, rather than treating the discovery envelope as proof.
anchors={0x400ee48e:'7440',0x400ee490:'b481',0x400ee492:'650001ee',0x400ee496:'343b1a08',0x400ee49a:'48c2',0x400ee49c:'4efb2802',0x400f0c16:'5380',0x400f0c18:'7180',0x400f0c1a:'0c80000000dd',0x400f0c20:'620025bc',0x400f0c24:'303b0a08',0x400f0c28:'48c0',0x400f0c2a:'4efb0802',0x4000170c:'202f000c',0x40001712:'c2af0014',0x4000171c:'226f0010',0x40001720:'d3c1',0x40001722:'43e9fff4',0x4000174a:'21490048'}
for a,h in anchors.items():assert b[a-base:a-base+len(bytes.fromhex(h))].hex()==h
checked_tables=[]
for table,count in [(0x400ee4a0,65),(0x400f0c2e,222)]:
 targets=[table+struct.unpack_from('>h',b,table-base+slot*2)[0] for slot in range(count)]
 assert all(not ring[0]<=t<ring[1] for t in targets)
 checked_tables.append(dict(table_base=hex(table),validated_selector_count=count,targets=[hex(t) for t in targets],target_min=hex(min(targets)),target_max=hex(max(targets)),ring_entry_excluded=True))

# At each recovered direct task initializer call, the five arguments are a
# contiguous sequence of constant pushes. Parse that sequence independently
# of the possibly misaligned preceding window.
task_stacks=[]
for match in re.finditer(bytes.fromhex('4eb94000170c'),b):
 end=match.start();solutions=[]
 for start in range(max(0,end-34),end,2):
  q=start;pushes=[]
  while q<end:
   op=struct.unpack_from('>H',b,q)[0]
   if op in (0x4879,0x2f3c):v=struct.unpack_from('>I',b,q+2)[0];n=6
   elif op==0x4878:v=struct.unpack_from('>h',b,q+2)[0]&0xffffffff;n=4
   elif op==0x487a:v=base+q+2+struct.unpack_from('>h',b,q+2)[0];n=4
   elif op==0x42a7:v=0;n=2
   else:break
   pushes.append(v);q+=n
  if q==end and len(pushes)==5:solutions.append((start,pushes))
 assert len(solutions)==1,(hex(base+end),solutions)
 start,args=solutions[0];size,low,priority,entry,task=args
 high=low+(size&~3)
 assert size>12 and high<=0xffffffff and not(low<marker[1] and high>marker[0])
 # Initial exception frame occupies the last 12 bytes in this reservation.
 assert low<=high-12<high
 task_stacks.append(dict(call=hex(base+end),argument_bytes=b[start:end].hex(),task=hex(task),entry=hex(entry),priority=priority,stack_start=hex(low),stack_end_exclusive=hex(high),stack_bytes=size,initial_saved_sp=hex(high-12),marker_disjoint=True))
assert len(task_stacks)==16
candidate=json.loads(pathlib.Path('work/marker-pointer-candidate-traces.json').read_text())
unresolved=[x for x in candidate['bulk_calls'] if x['status']=='unresolved_destination']
assert len(unresolved)==836
source=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes=dict(syx=hashlib.sha256(source.read_bytes()).hexdigest(),decoded_section_3=hashlib.sha256(b).hexdigest())
assert hashes['syx']=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
assert hashes['decoded_section_3']=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'
r=dict(read_only=True,global_storage_certified=False,sections=sections,standard_relative_table_dispatches=dispatches,other_indexed_dispatch_candidates=other_indexed,validated_nearby_tables=checked_tables,direct_task_stack_reservations=task_stacks,verified_instruction_anchors={hex(a):h for a,h in anchors.items()},unresolved_bulk_destination_candidates=len(unresolved),unchanged_hashes=hashes,limitations=['Raw matches are byte occurrences, not validated references','Other stored sections were not interpreted as executable mappings','Standard expression count is candidate discovery; no claim of every computed transfer','Relative-table scanning does not solve generic computed pointers or bulk destinations','Direct task stack reservations do not certify every saved-SP writer, computed constructor caller, interrupt stack or runtime stack bound'])
pathlib.Path('work/storage-ownership-expanded.json').write_text(json.dumps(r,indent=2)+'\n')
pathlib.Path('outputs/Digitone-storage-ownership-expanded-results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(section_count=len(sections),standard_table_candidates=len(dispatches),bounded_nearby_tables=[{k:v for k,v in x.items() if k!='targets'} for x in checked_tables],verified_instruction_anchors=len(anchors),task_stacks=task_stacks,unresolved_bulk_destination_candidates=len(unresolved),hashes_unchanged=True,global_storage_certified=False),indent=2))
