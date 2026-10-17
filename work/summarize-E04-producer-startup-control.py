from pathlib import Path
import json,hashlib
p=Path('outputs/Digitone-E04-producer-startup-control-checks.json')
j=json.loads(p.read_text());a,b=j['cases']
assert a['passed'] and b['passed']
original=Path('work/os144/emulator-E04-main.bin').read_bytes()
control=Path('work/os144/PC_ONLY-E04-producer-bypass-main.bin').read_bytes()
offset=0x400947ec-0x40000400
assert original[:offset]==control[:offset] and original[offset+8:]==control[offset+8:]
summary={'only_changed_interval':['0x400947ec','0x400947f4'],'calls':[],'all_checks_passed':True}
for x,y in zip(a['producer_calls'],b['producer_calls']):
 regs=['d'+str(i) for i in range(8)]+['a'+str(i) for i in range(8)]+['sr']
 assert all(x['inputs'][k]==y['inputs'][k] for k in regs)
 assert all(x['outputs'][k]==y['outputs'][k] for k in regs)
 trace=x['isolated_replay']['memory'];bt=y['isolated_replay']['memory']
 sp=int(x['inputs']['a7'],16);source=int(x['inputs']['a3'],16);event=int(x['inputs']['a2'],16);track=int(x['inputs']['d4'],16)
 roots=[z for z in trace if z['pc']=='0x47be02b2'];scales=[z for z in trace if z['pc']=='0x47be02be']
 assert len(roots)==len(scales)==1
 assert int(roots[0]['address'],16)==source+track*0x3d0+0x3cb
 assert int(scales[0]['address'],16)==source+track*0x3d0+0x3ce
 assert roots[0]['bytes'] in ['43','3c'] and scales[0]['bytes']=='ff'
 expected_addresses={event+8,event+0x3c}
 assert len(bt)==2 and {int(z['address'],16) for z in bt}==expected_addresses
 assert all(z['kind']=='write' and int(z['value'],16)==track for z in bt)
 metadata=[z for z in trace if z['kind']=='write' and 0x47be1000<=int(z['address'],16)<0x47be1b74]
 assert len(metadata)==1
 assert int(metadata[0]['address'],16)==0x47be1a24+4*track
 expected=0x80000000|(track<<13)|int(roots[0]['bytes'],16)
 assert int(metadata[0]['value'],16)==expected
 for z in trace:
  addr=int(z['address'],16);size=z['size']
  allowed=sp-92<=addr and addr+size<=sp+1
  allowed=allowed or (0x47be1000<=addr and addr+size<=0x47be1b74)
  allowed=allowed or (addr in expected_addresses and size==4)
  allowed=allowed or (addr in {source+track*0x3d0+0x3cb,source+track*0x3d0+0x3ce} and size==1)
  assert allowed,z
 summary['calls'].append({'index':x['index'],'track_index':track,'source':hex(source),'event':hex(event),'root_byte':roots[0]['bytes'],'scale_byte':scales[0]['bytes'],'context_address':metadata[0]['address'],'context_word':metadata[0]['value'],'traced_data_accesses':len(trace),'bypass_data_accesses':len(bt),'max_observed_stack_bytes':sp-min(int(z['address'],16) for z in trace if sp-256<=int(z['address'],16)<sp+1),'register_inputs_and_outputs_match_control':True})
syx=Path('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx')
summary['E04_syx_sha256']=hashlib.sha256(syx.read_bytes()).hexdigest()
assert summary['E04_syx_sha256']=='76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c'
j['comparison']=summary
j['limits']+=['The continuous-run dynamically installed memory hooks miss some already-translated accesses; complete access lists are the isolated_replay records, installed before translation.','Each isolated replay clones the actual call CPU context and mapped source/private/event/stack bytes. No unexpected-access mapping, interrupts or time advancement are provided; register results match continuous execution.','The bypass is an eight-byte raw MAIN overlay using E04 flash data in the emulator, not a repackaged firmware or physical test.']
p.write_text(json.dumps(j,indent=2)+'\n')
print(json.dumps(summary,indent=2))
