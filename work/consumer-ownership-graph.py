exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
import json,hashlib
conditional={'beq','bne','bgt','bge','blt','ble','bcs','bcc','bhi','bls','bpl','bmi','bvc','bvs'}
def graph(name,start,lo,hi,exits=()):
 seen={};todo=[start];calls=[];outside=[]
 while todo:
  a=todo.pop()
  if a in seen:continue
  if a in exits:outside.append(hex(a));continue
  assert lo<=a<hi,(name,hex(a))
  i=next(md.disasm(b[a-base:a-base+16],a,count=1));op=i.mnemonic.split('.')[0]
  assert i.id or bytes(i.bytes) in [bytes.fromhex(f'4a8{x:x}') for x in range(8,16)],(name,hex(a),i.mnemonic)
  seen[a]={'bytes':i.bytes.hex(),'instruction':i.mnemonic+' '+i.op_str}
  if op in ('rts','rte'):continue
  if op in ('jsr','bsr'):calls.append({'site':hex(a),'instruction':i.mnemonic+' '+i.op_str})
  if op=='jmp':raise RuntimeError((name,hex(a),i.op_str))
  if op in conditional|{'bra'}:
   todo.append(int(re.findall(r'\$([0-9a-f]+)',i.op_str)[0],16))
   if op!='bra':todo.append(a+i.size)
  else:todo.append(a+i.size)
 return {'name':name,'instruction_count':len(seen),'instructions':{hex(a):v for a,v in sorted(seen.items())},'calls':calls,'exits':sorted(set(outside))}
graphs=[graph('type_zero_note_route',0x4009dc5e,0x4009dc5e,0x4009e352,(0x4009cef0,)),graph('parameter_apply',0x4009b600,0x4009b600,0x4009b6c0),graph('child_clone',0x4009bd8a,0x4009bd8a,0x4009bde8),graph('note_off_arp_lookup',0x4009743e,0x4009743e,0x4009755e),graph('state_sync_gate',0x4009e70c,0x4009e70c,0x4009e720),graph('voice_bitmap_getter',0x4009f23c,0x4009f23c,0x4009f266)]
g=graphs[0]
writes=[];reads=[]
for a,v in g['instructions'].items():
 ins=v['instruction'];ops=re.split(r', (?![^()]*\))',ins.split(' ',1)[1]);op=ins.split('.')[0].split()[0]
 if ops and re.search(r'\(a3(?:,|\))',ops[-1]) and op not in ('tst','cmp','cmpa','btst','pea','jsr','lea'):
  writes.append({'site':a,'instruction':ins})
 if '$38(a3)' in ins:reads.append({'site':a,'instruction':ins})
assert all('$38(a3)' not in w['instruction'] for w in writes)
assert not graphs[1]['calls']
assert not any('$400f05' in c['instruction'] or '$400f0690' in c['instruction'] for c in graphs[2]['calls'])
results={'graphs':graphs,'event_writes':writes,'payload_reads':reads,'hash_section3':hashlib.sha256(b).hexdigest()}
pathlib.Path('outputs/Digitone-consumer-ownership-graph-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps({'graphs':[(g['name'],g['instruction_count']) for g in graphs],'calls':g['calls'],'event_writes':writes,'payload_reads':reads},indent=2))
