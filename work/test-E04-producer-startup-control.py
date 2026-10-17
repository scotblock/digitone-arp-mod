from pathlib import Path
import json, hashlib
port=json.loads(Path('work/os144/helper-port.json').read_text())
h=next(x for x in port['hooks'] if x['name']=='producer_capture')
stock=Path('work/os144/section-3.bin').read_bytes()
e04=Path('work/os144/emulator-E04-main.bin').read_bytes()
offset=int(h['site'],16)-0x40000400
assert stock[offset:offset+h['length']].hex()==h['stock_bytes']
control=bytearray(e04);control[offset:offset+h['length']]=stock[offset:offset+h['length']]
control_path=Path('work/os144/PC_ONLY-E04-producer-bypass-main.bin');control_path.write_bytes(control)
s=Path('work/test-E04-native-startup-delay.py').read_text()
old="for name,syx,imgfile in [('stock','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx','work/os144/section-3.bin'),('E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin')]:"
assert old in s
s=s.replace(old,"for name,syx,imgfile in [('E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin'),('E04_bypass','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/PC_ONLY-E04-producer-bypass-main.bin')]:")
s=s.replace("name=='E04'","name.startswith('E04')")
s=s.replace("root=Path('work/native-delay-'+name)","root=Path('work/producer-control-'+name)")
s=s.replace("dest=Path('outputs/Digitone-E04-native-startup-delay-checks.json')","dest=Path('outputs/Digitone-E04-producer-startup-control-checks.json')")
s=s.replace("from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE","from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ,UC_HOOK_MEM_INVALID,UC_MEM_WRITE")
s=s.replace("from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_A7,UC_M68K_REG_SR","from unicorn.m68k_const import *")
s=s.replace("from unicorn import UC_HOOK_CODE,", "from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,")
addition=r'''  row['producer_calls']=[];row['helper_entries']={};row['intro_exit_seen']=False
  row['main_sha256']=hashlib.sha256(image).hexdigest()
  row['syx_sha256']=hashlib.sha256(Path(syx).read_bytes()).hexdigest()
  def install_capture_watch(mm,stage):
   state={'active':None,'hooks':[]}
   regs={**{'d'+str(i):globals()['UC_M68K_REG_D'+str(i)] for i in range(8)},**{'a'+str(i):globals()['UC_M68K_REG_A'+str(i)] for i in range(8)},'sr':UC_M68K_REG_SR}
   def snapshot(uc):
    r={k:hex(uc.reg_read(v)) for k,v in regs.items()}
    sp=uc.reg_read(UC_M68K_REG_A7)
    r['stack_64_bytes']=bytes(uc.mem_read(sp,64)).hex()
    r['private_header']=bytes(uc.mem_read(0x47be1000,32)).hex()
    return r
   def memory(uc,access,address,size,value,data):
    call=state['active']
    if call is None:return
    record={'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'kind':'write' if access==UC_MEM_WRITE else 'read','address':hex(address),'size':size}
    if access==UC_MEM_WRITE:record['value']=hex(value)
    else:
     try:record['bytes']=bytes(uc.mem_read(address,size)).hex()
     except Exception as ex:record['read_error']=str(ex)
    call['memory'].append(record)
   def invalid(uc,access,address,size,value,data):
    if state['active'] is not None:state['active']['invalid_accesses'].append({'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'access':access,'address':hex(address),'size':size})
    return False
   def entry(uc,pc,size,data):
    assert state['active'] is None
    call={'index':len(row['producer_calls'])+1,'stage':stage,'before_intro_exit':not row['intro_exit_seen'],'inputs':snapshot(uc),'memory':[],'invalid_accesses':[]}
    row['producer_calls'].append(call);state['active']=call
    # Replay the exact captured CPU context in a separate engine. All RAM
    # below is copied from this call's real modeled startup, not fabricated.
    rr=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);rr.ctl_set_cpu_model(UC_CPU_M68K_CFV4E)
    regions=[(0x40094000,0x1000),(0x47be0000,0x2000),(uc.reg_read(UC_M68K_REG_A3),0xf40),(uc.reg_read(UC_M68K_REG_A2),0x48),(uc.reg_read(UC_M68K_REG_A7)-256,512)]
    pages=set()
    for start,length in regions:
     for base in range(start&~4095,(start+length+4095)&~4095,4096):
      if base in pages:continue
      rr.mem_map(base,4096);rr.mem_write(base,bytes(uc.mem_read(base,4096)));pages.add(base)
    rr.context_restore(uc.context_save())
    replay={'memory':[],'invalid_accesses':[],'mapped_pages':[hex(p) for p in sorted(pages)]}
    def replay_memory(ru,access,address,size,value,data):
     item={'pc':hex(ru.reg_read(UC_M68K_REG_PC)),'kind':'write' if access==UC_MEM_WRITE else 'read','address':hex(address),'size':size}
     if access==UC_MEM_WRITE:item['value']=hex(value)
     else:item['bytes']=bytes(ru.mem_read(address,size)).hex()
     replay['memory'].append(item)
    def replay_invalid(ru,access,address,size,value,data):
     replay['invalid_accesses'].append({'pc':hex(ru.reg_read(UC_M68K_REG_PC)),'access':access,'address':hex(address),'size':size});return False
    rr.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,replay_memory)
    rr.hook_add(UC_HOOK_MEM_INVALID,replay_invalid)
    rr.emu_start(pc,0x400947f4,count=1000)
    replay['continuation']=hex(rr.reg_read(UC_M68K_REG_PC))
    replay['outputs']=snapshot(rr)
    assert replay['continuation']=='0x400947f4' and not replay['invalid_accesses']
    call['isolated_replay']=replay
    state['hooks']=[uc.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,memory),uc.hook_add(UC_HOOK_MEM_INVALID,invalid)]
   def exit(uc,pc,size,data):
    if state['active'] is None:return
    call=state['active'];call['outputs']=snapshot(uc)
    call['replay_matches_live_registers']=all(call['outputs'][k]==call['isolated_replay']['outputs'][k] for k in regs)
    assert call['replay_matches_live_registers']
    call['changed_registers']={k:[call['inputs'][k],call['outputs'][k]] for k in regs if call['inputs'][k]!=call['outputs'][k]}
    for hook in state['hooks']:uc.hook_del(hook)
    state['active']=None;state['hooks']=[]
   mm.uc.hook_add(UC_HOOK_CODE,entry,begin=0x400947ec,end=0x400947ec)
   mm.uc.hook_add(UC_HOOK_CODE,exit,begin=0x400947f4,end=0x400947f4)
   mm.uc.hook_add(UC_HOOK_CODE,lambda uc,pc,size,data:row.__setitem__('intro_exit_seen',True),begin=0x40091b0c,end=0x40091b0c)
   for label in ['producer_capture','capture','resolve','candidate_store','slot']:
    address=port['layout'][label]['address']
    def helper(uc,pc,size,data,label=label):row['helper_entries'][label]=row['helper_entries'].get(label,0)+1
    mm.uc.hook_add(UC_HOOK_CODE,helper,begin=address,end=address)
  install_capture_watch(m,'cold')
'''
anchor='  done=0;timer=Dtims(m,channels=(1,),clear_stale=False)'
assert anchor in s;s=s.replace(anchor,addition+anchor)
s=s.replace("   held['ev']=ev","   held['ev']=ev\n   install_capture_watch(mm,'intro')")
s=s.replace("  row['passed']=True","  assert len(row['producer_calls'])==8\n  assert all(set(c['changed_registers'])<= {'sr'} and not c['invalid_accesses'] for c in row['producer_calls'])\n  assert row['helper_entries'].get('producer_capture',0)==(8 if name=='E04' else 0)\n  row['passed']=True")
exec(compile(s,'E04-producer-capture-startup-control','exec'))
