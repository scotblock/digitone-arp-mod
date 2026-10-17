"""Bounded reachable-instruction screen; indirect edges remain unresolved."""
import pathlib,json,re,collections
exec(pathlib.Path('work/disassemble.py').read_text().split('out=[]')[0]);md.skipdata=True
roots=[0x40000532,0x4012b344,0x4008c4f6,0x4008c634,0x4008c7d4,0x400f0504,0x4009df9a,0x40093ef4]
roots += [int.from_bytes(b[0x40241ab8-base+4*j:0x40241abc-base+4*j],'big') for j in range(119)]
queue=collections.deque(roots);seen={};unknown=[];indirect=[];hits=[]
while queue:
 pc=queue.popleft()
 if pc in seen or not(base<=pc<base+len(b)) or pc&1:continue
 raw=b[pc-base:pc-base+16];items=list(md.disasm(raw,pc,count=1))
 if not items:unknown.append(hex(pc));continue
 i=items[0];op=i.mnemonic.split('.')[0]
 if not i.id:
  if raw[:2] in [bytes.fromhex(f'4a8{x:x}') for x in range(8,16)]:seen[pc]='tst address';queue.append(pc+2);continue
  unknown.append(hex(pc));continue
 seen[pc]=i.mnemonic+' '+i.op_str
 for match in re.finditer(r'\$([0-9a-f]+)',i.op_str):
  v=int(match[1],16)
  if 0x40000000<=v<0x80000000 and 0x47be0000<=0x40000000+(v-0x40000000)%0x08000000<0x47c00000:hits.append({'pc':hex(pc),'instruction':seen[pc],'value':hex(v)})
 if op in ['rts','rte','rtr','illegal','stop']:continue
 target=re.fullmatch(r'\$([0-9a-f]+)(?:\(pc\)|\.l|\.w)?',i.op_str)
 control=op in ['jsr','jmp','bsr','bra'] or (op.startswith('b') and op not in ['btst','bset','bclr','bchg','bitrev','byterev'])
 if control:
  if target:queue.append(int(target[1],16))
  elif op in ['jsr','jmp']:indirect.append({'pc':hex(pc),'instruction':seen[pc]})
  if op in ['bra','jmp']:continue
 queue.append(pc+i.size)
r={'roots':[hex(a) for a in roots],'reached_instruction_count':len(seen),'region_operand_hits':hits,'unknown_boundaries':unknown,'indirect_edges':indirect,'scope':'Rooted recursive disassembly screen, not complete control flow, computed pointers, bulk-write reach or ownership proof.'}
pathlib.Path('outputs/Digitone-reserved-RAM-all-alias-reference-screen.json').write_text(json.dumps(r,indent=2));print('reachable',len(seen),'region operands',len(hits),'unknown',len(unknown),'indirect',len(indirect))
