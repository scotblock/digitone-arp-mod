from pathlib import Path
s=Path('work/test-E04-producer-startup-control.py').read_text()
s=s.replace('work/producer-control-','work/restored-capture-control-')
s=s.replace('Digitone-E04-producer-startup-control-checks.json','Digitone-E04-restored-capture-control-checks.json')
s=s.replace("len(row['producer_calls'])==8","len(row['producer_calls'])==4")
s=s.replace("(8 if name=='E04' else 0)","(4 if name=='E04' else 0)")
s=s.replace("  row['producer_calls']=[];","  row['restore_events']=[];row['producer_calls']=[];")
s=s.replace("    r['private_header']=", "    r['event_bytes']=bytes(uc.mem_read(uc.reg_read(UC_M68K_REG_A2),0x48)).hex()\n    r['context_slots']=bytes(uc.mem_read(0x47be1a24,16)).hex()\n    r['private_header']=")
s=s.replace("    assert call['replay_matches_live_registers']", "    assert call['replay_matches_live_registers']\n    call['replay_matches_live_memory']=all(call['outputs'][k]==call['isolated_replay']['outputs'][k] for k in ['event_bytes','context_slots','private_header','stack_64_bytes'])\n    assert call['replay_matches_live_memory']")
anchor="   state={'active':None,'hooks':[]}"
addition=r'''   def restore_event(uc,pc,size,data):
    row['restore_events'].append({'stage':stage,'pc':hex(pc),'d0':hex(uc.reg_read(UC_M68K_REG_D0)),'d2':hex(uc.reg_read(UC_M68K_REG_D2)),'global_flags':bytes(uc.mem_read(0x402296f0,4)).hex()})
   for pc in [0x400a838c,0x400a8402,0x400a83f4,0x400a8410]:mm.uc.hook_add(UC_HOOK_CODE,restore_event,begin=pc,end=pc)
'''
assert anchor in s;s=s.replace(anchor,addition+anchor)
s=s.replace("replay={'memory':[]", "replay={'instructions':[],'memory':[]")
anchor='    rr.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,replay_memory)'
addition=r'''    def instruction(ru,pc,size,data):
     replay['instructions'].append({'pc':hex(pc),'size':size,'bytes':bytes(ru.mem_read(pc,size)).hex()})
    rr.hook_add(UC_HOOK_CODE,instruction)
'''
assert anchor in s;s=s.replace(anchor,addition+anchor)
needle="exec(compile(s,'E04-producer-capture-startup-control','exec'))"
assert needle in s
s=s.replace(needle,"s=s.replace(\"source=Path('work/os144-emulator-E02-engine/plusdrive.img')\",\"source=Path('work/os144/PC_ONLY-saved-mirror-valid_first.img')\")\n"+needle)
exec(compile(s,'E04-restored-capture-control-wrapper','exec'))
