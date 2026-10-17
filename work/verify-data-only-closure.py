"""Read-only, bounded firmware call-closure audit; does not patch the image."""
exec(open('work/disassemble.py').read().split('out=[]')[0])
import hashlib, json
md.skipdata = True
specs = {
 'copy': (0x400ec23c,0x400ec282), 'clear': (0x400ec284,0x400ec2ce),
 'string_copy': (0x40128448,0x40128508), 'parameter_lookup': (0x40007e3e,0x40007e78),
 'track_defaults': (0x4001330c,0x40013370), 'track_import': (0x400089fa,0x40008b70),
 'header_import': (0x4000879c,0x400088ca), 'header_defaults': (0x4001341c,0x40013478),
 'parameter_import': (0x40008ca4,0x40008de0), 'step_defaults': (0x40013370,0x4001341c),
 'parameter_clear': (0x40013478,0x400134e4), 'pattern_defaults': (0x400134e4,0x40013564),
 'pattern_import': (0x40008de0,0x40008eb0),
}
# Register calls were resolved from constant loads in the same recovered routine.
# The report retains the concrete-target / preserved-register assumptions.
indirect = {
 0x40008cce:0x400ec284,0x40008d44:0x400ec284,0x40008d7a:0x40007e3e,
 0x400134cc:0x400ec284,0x40013524:0x4001330c,0x4001352a:0x40013370,
 0x40008e48:0x400089fa,0x40008e54:0x40013370,0x40008e5c:0x4001330c,
}
starts = {s:name for name,(s,e) in specs.items()}
anchors = {
 0x40008cc8:'47f9400ec284',0x40008d54:'49faf0e8',
 0x40013490:'47f9400ec284',0x40013514:'47fafdf6',0x40013518:'45fafe56',
 0x40008e2e:'4bfafbca',0x40008e32:'4df940013370',0x40008e38:'283c4001330c',
 0x40008e5a:'2044',0x400256bc:'49f9400ec23c',
 0x4013a33a:'206f0004202800104e75',0x4013b2a6:'206f0030',0x4013b2aa:'4e90',
}
for a,h in anchors.items():
 assert b[a-base:a-base+len(bytes.fromhex(h))].hex()==h,(hex(a),b[a-base:a-base+len(bytes.fromhex(h))].hex(),h)
assert int.from_bytes(b[0x401764c8+0x28-base:0x401764c8+0x2c-base],'big')==0x4013a33a
conditions = {'beq','bne','bgt','bge','blt','ble','bcs','bcc','bhi','bls','bpl','bmi','bvc','bvs'}
def decode(a):
 i=next(md.disasm(b[a-base:a-base+16],a,count=1),None)
 assert i is not None,hex(a)
 if i.mnemonic=='dc.w': assert bytes(i.bytes) in [bytes.fromhex(f'4a8{x:x}') for x in range(8,16)],hex(a)
 return i
def target(i):
 t=re.findall(r'\$([0-9a-f]+)',i.op_str)
 return int(t[0],16) if t else None
graphs=[]
for name,(s,e) in specs.items():
 todo=[s];seen=set();calls=[];tails=[];returns=[]
 while todo:
  a=todo.pop()
  if a in seen:continue
  assert s<=a<e,(name,hex(a))
  seen.add(a);i=decode(a);m=i.mnemonic.split('.')[0];n=a+i.size;t=target(i)
  assert m not in {'trap','trapv','illegal','stop','reset','rte','rtr'},(name,hex(a),m)
  if m=='rts':returns.append(f'{a:08x}');continue
  if m in {'jsr','bsr'}:
   t=t if t is not None else indirect[a]
   assert t in starts,(name,hex(a),hex(t))
   calls.append(dict(site=f'{a:08x}',target=f'{t:08x}',callee=starts[t],instruction=f'{i.mnemonic} {i.op_str}'))
   todo.append(n);continue
  if m in {'bra','jmp'}:
   assert t is not None,(name,hex(a))
   if s<=t<e:todo.append(t)
   else:
    assert t in starts,(name,hex(a),hex(t))
    tails.append(dict(site=f'{a:08x}',target=f'{t:08x}',callee=starts[t]))
   continue
  if m in conditions:
   assert t is not None
   todo.extend([n,t]);continue
  assert not m.startswith('db'),(name,hex(a),m)
  todo.append(n)
 graphs.append(dict(name=name,start=f'{s:08x}',end_exclusive=f'{e:08x}',reachable_instructions=len(seen),calls=calls,tails=tails,returns=sorted(returns),sha256=hashlib.sha256(b[s-base:e-base]).hexdigest()))

windows=[]
for name,s,e,allowed in [
 ('metadata_restore',0x40034bb4,0x40034c10,0x4013a33a),
 ('metadata_record_restore',0x40034d00,0x40034d5c,0x4013a33a),
 ('metadata_reset',0x40035356,0x400353a6,0x4013a33a),
 ('record_pattern_copy',0x400256dc,0x400256ee,0x400ec23c),
 ('pattern_copy',0x400225c2,0x400225d2,0x400ec23c),
]:
 a=s;calls=[]
 while a<e:
  i=decode(a);m=i.mnemonic.split('.')[0]
  assert m not in conditions|{'bra','jmp','rts','trap','trapv','illegal','stop','reset'}
  if m=='jsr':
   t=target(i)
   assert t is None or t==allowed
   calls.append(dict(site=f'{a:08x}',target=f'{allowed:08x}',resolution='fixed concrete track getter' if allowed==0x4013a33a else 'copy primitive'))
  a+=i.size
 assert a==e
 windows.append(dict(name=name,start=f'{s:08x}',end_exclusive=f'{e:08x}',calls=calls,sha256=hashlib.sha256(b[s-base:e-base]).hexdigest()))

inventory=[]
for section in [2,3]:
 data=pathlib.Path(f'work/section-{section}.bin').read_bytes()
 hits=[];exact=[]
 for off in range(len(data)-3):
  v=int.from_bytes(data[off:off+4],'big')
  if 0x4199d000<=v<0x4199da94:hits.append(dict(offset=f'{off:x}',value=f'{v:08x}'))
  if 0x4199d510<=v<0x4199d518:exact.append(dict(offset=f'{off:x}',value=f'{v:08x}'))
 inventory.append(dict(section=section,nearby_literals=hits,marker_interior_literals=exact))
 assert not exact
result=dict(scope='Bounded static application-call closure, not global certification',functions=graphs,commit_windows=windows,verified_provenance_anchors={f'{a:08x}':h for a,h in anchors.items()},literal_inventory=inventory,global_storage_certified=False,actual_exception_cleanup_certified=False,data_only_application_call_closure=True,firmware_guard_implemented=False,assumptions=['Valid arguments and mapped writable backing memory','Recovered concrete vtables and preserved-register calling convention','Asynchronous handlers do not throw through these routines'],limitations=['No proof against computed aliases or generic RAM bulk accesses','No CPU-fault or interrupt unwind certification','No validated unwind map for outer observer callbacks','No inserted guard or register-liveness proof'])
pathlib.Path('outputs/Digitone-data-only-closure-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(dict(functions=len(graphs),instructions=sum(g['reachable_instructions'] for g in graphs),calls=sum(len(g['calls']) for g in graphs),tails=sum(len(g['tails']) for g in graphs),windows=len(windows),window_calls=sum(len(w['calls']) for w in windows),nearby_literals=[len(x['nearby_literals']) for x in inventory]),indent=2))
