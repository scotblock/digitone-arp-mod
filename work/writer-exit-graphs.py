exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
import json
specs=[('metadata_restore',0x40034a8c,0x40034c78,0x40034bb4),('metadata_record_restore',0x40034c78,0x40034d9c,0x40034d00),('metadata_reset',0x40035268,0x400353f8,0x40035356),('track_defaults',0x4001330c,0x40013370,0x40013314),('pattern_defaults',0x400134e4,0x40013564,0x400134f8),('pattern_parameter_clear',0x40013478,0x400134e4,0x40013488),('pattern_default_method',0x400208a0,0x400208da,0x400208b8),('pattern_import',0x40008de0,0x40008eb0,0x40008e04),('track_import',0x400089fa,0x40008b70,0x40008a16),('pattern_copy',0x40022552,0x400225ec,0x400225c2),('record_replacement',0x40025628,0x40025796,0x400256dc)]
results=[]
for name,s,e,entry in specs:
 todo=[(s,False)];seen=set();exits=set();calls={};branches=[];errors=[];instructions={}
 while todo:
  a,entered=todo.pop()
  if (a,entered) in seen:continue
  seen.add((a,entered))
  if not s<=a<e:exits.add((a,entered,'outside_range'));continue
  item=next(md.disasm(b[a-base:a-base+16],a,count=1),None)
  if item is None:errors.append(hex(a));continue
  instructions[a]=f'{item.mnemonic} {item.op_str}'
  if a==entry:entered=True
  m=item.mnemonic.split('.')[0];n=a+item.size
  targets=re.findall(r'\$([0-9a-f]+)',item.op_str)
  target=int(targets[0],16) if targets else None
  if m in ['rts','rte','rtr']:
   exits.add((a,entered,m));continue
  if m=='jmp':exits.add((a,entered,'direct_tail' if target is not None else 'indirect_tail'));continue
  if m in ['jsr','bsr']:
   calls.setdefault(a,dict(instruction=instructions[a],resolved_target=f'{target:08x}' if target else None,entered_states=[]))
   if entered not in calls[a]['entered_states']:calls[a]['entered_states'].append(entered)
   todo.append((n,entered));continue
  if m=='bra':
   assert target is not None
   branches.append((a,target))
   if s<=target<e:todo.append((target,entered))
   else:exits.add((a,entered,f'tail_to_{target:08x}'))
   continue
  if m.startswith('b') and m in ['beq','bne','bgt','bge','blt','ble','bcs','bcc','bhi','bls','bpl','bmi','bvc','bvs']:
   assert target is not None
   branches.append((a,target));todo.extend([(n,entered),(target,entered)]);continue
  todo.append((n,entered))
 assert not errors,(name,errors)
 result=dict(name=name,start=f'{s:08x}',end_exclusive=f'{e:08x}',proposed_entry=f'{entry:08x}' if entry else None,reachable_instruction_count=len(instructions),state_count=len(seen),exits=[dict(address=f'{a:08x}',entered=entered,kind=kind) for a,entered,kind in sorted(exits)],call_sites={f'{a:08x}':v for a,v in calls.items()},limitation='Branches are structural, not proven feasible; normal-return calls only, no exception edges; tail transfers require continuation handling')
 results.append(result)
 print(name,'instructions',len(instructions),'exits',result['exits'],'calls',len(calls),'unresolved',sum(v['resolved_target'] is None for v in calls.values()))
pathlib.Path('work/writer-exit-graphs.json').write_text(json.dumps(results,indent=2))

