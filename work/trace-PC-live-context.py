from pathlib import Path
exec(compile(Path('work/test-PC-restored-arp-DSP.py').read_text().split("exec(compile(s,'restored-live-arp-DSP','exec'))")[0],'build-live-trace','exec'))
s=s.replace("[('ordinary','corrected'),('ordinary','stock_sites'),('scale','corrected')]","[('scale','corrected')]")
s=s.replace('Digitone-E04-PC-restored-arp-DSP.json','Digitone-E04-PC-live-context-trace.json')
s=s.replace("   r['passed']=True", "   r['passed']=True")
s=s.replace("   s.tap(s.code('PLAY'),hold_ms=100,after_ms=500)","   r['trace_stage']='sequencer'\n   s.tap(s.code('PLAY'),hold_ms=100,after_ms=500)")
s=s.replace("   def send(data):", "   def send(data):\n    r['trace_stage']='MIDI '+bytes(data).hex()")
probe=r'''
    from unicorn.m68k_const import UC_M68K_REG_D0,UC_M68K_REG_A0,UC_M68K_REG_A7,UC_M68K_REG_SR,UC_M68K_REG_PC
    from unicorn import UC_HOOK_MEM_WRITE
    r['trace']=[];r['metadata_writes']=[]
    r['allocations']=[]
    regids=[('D'+str(i),UC_M68K_REG_D0+i) for i in range(8)]+[('A'+str(i),UC_M68K_REG_A0+i) for i in range(8)]
    def event(uc,e):
     if not 0x40000000<=e<0x48000000:return None
     try:fields=list(struct.unpack('>18I',uc.mem_read(e,72)))
     except Exception:return None
     slot=None
     if 0<=e-0x419ebe2c<9216 and (e-0x419ebe2c)%72==0:slot=0x47be1024+(e-0x419ebe2c)//72*4
     elif 0<=e-0x419f182c<288 and (e-0x419f182c)%72==0:slot=0x47be1a24+(e-0x419f182c)//72*4
     return {'address':hex(e),'fields':fields,'slot':hex(slot) if slot else None,'context':hex(rd(uc,slot)) if slot else None}
    def observe(uc,pc,label):
     if 'trace_stage' not in r or len(r['trace'])>=6000:return
     regs={k:uc.reg_read(i) for k,i in regids};sp=regs['A7'];args=list(struct.unpack('>10I',uc.mem_read(sp,40)))
     if label in ['resolve','resolve return','slot','slot return','allocate_clear']:return
     if label=='candidate_store' and args[0]==0x47be054a:return
     if label=='candidate_store return' and pc==0x47be054a:return
     if label=='stock allocated_return':
      r['allocations'].append({'ms':session.now_ms(),'stage':r['trace_stage'],'event':hex(regs['A0']),'stack':args[:8]});return
     if label=='stock release' and rd(uc,args[1])>=2:return
     if label=='stock queue_publish' and rd(uc,args[1])>=2:return
     candidates=set([regs['A0'],regs['A2'],regs['A3'],args[0],args[1],args[2]])
     r['trace'].append({'label':label,'pc':hex(pc),'stage':r['trace_stage'],'ms':session.now_ms(),'regs':regs,'sr':uc.reg_read(UC_M68K_REG_SR),'stack':args,'events':[v for e in candidates if (v:=event(uc,e)) is not None],'private_prefix':bytes(uc.mem_read(0x47be1000,36)).hex(),'cache_contexts':list(struct.unpack('>4I',uc.mem_read(0x47be1a24,16))),'private_tail':bytes(uc.mem_read(0x47be1a34,0x140)).hex()})
    returns={};return_hooks=set()
    def entered(uc,pc,n,d,label):
     observe(uc,pc,label)
     ret=rd(uc,uc.reg_read(UC_M68K_REG_A7))
     if 0x40000000<=ret<0x48000000:
      returns.setdefault(ret,[]).append(label)
      if ret not in return_hooks:
       def exit_hook(uc,pc,n,d):
        labels=returns.get(pc)
        if labels:observe(uc,pc,labels.pop()+' return')
       session.at(ret,exit_hook);return_hooks.add(ret)
    for name in ['begin','cancel','commit','read','resolve','capture','candidate_store','snapshot','slot','copy','first_copy']:
     session.at(info['layout'][name]['address'],lambda uc,pc,n,d,name=name:entered(uc,pc,n,d,name))
    for name in ['before','after','caller_commit','producer_capture','allocate_clear','pitch_hook','quantize']:
     session.at(info['layout'][name]['address'],lambda uc,pc,n,d,name=name:observe(uc,pc,name))
    for pc,name in [(0x400ff5ac,'live raw copy branch1'),(0x400ff5ae,'live raw copy branch1 done'),(0x400ff5d4,'live raw copy branch2'),(0x400ff5d6,'live raw copy branch2 done'),(0x400ff5f6,'live raw copy direct'),(0x400ff5fc,'live raw copy direct done'),(0x40100252,'stock immediate publish')]:
     session.at(pc,lambda uc,pc,n,d,name=name:observe(uc,pc,name))
    mapping=json.loads(Path('work/os144/stock-probe-map.json').read_text())['sites']
    for name in ['producer','queue_publish','acceptance','selector_return','allocated_return','release']:
     if name in mapping:
      session.at(int(mapping[name]['new'],16),lambda uc,pc,n,d,name=name:observe(uc,pc,'stock '+name))
    # Preserve the full executed branch sequence of the retain/resolve helpers.
    for name in ['begin','commit','read','snapshot','pitch']:
     lo=info['layout'][name]['address'];hi=lo+info['layout'][name]['size']-1
     def path(uc,pc,n,d,name=name):
      if 'trace_stage' in r and len(r.setdefault('helper_paths',[]))<20000:
       r['helper_paths'].append({'name':name,'pc':hex(pc),'ms':session.now_ms(),'stage':r['trace_stage'],'D0':uc.reg_read(UC_M68K_REG_D0),'A0':uc.reg_read(UC_M68K_REG_A0),'sr':uc.reg_read(UC_M68K_REG_SR)})
     uc.hook_add(UC_HOOK_CODE,path,begin=lo,end=hi)
    def written(uc,access,a,n,value,d):
     if 'trace_stage' in r and len(r['metadata_writes'])<10000:r['metadata_writes'].append({'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'ms':session.now_ms(),'stage':r['trace_stage'],'address':hex(a),'size':n,'before':bytes(uc.mem_read(a,n)).hex(),'value':value})
    uc.hook_add(UC_HOOK_MEM_WRITE,written,begin=0x47be1000,end=0x47be1b73)
'''
anchor="   s=Session(case['ui_snapshot']"
assert anchor in s;s=s.replace(anchor,probe+'\n'+anchor)
# A trace-only run does not have a paired ordinary control.
s=s[:s.index("out['ordinary_comparisons']=[]")]+"out['passed']=all(c['passed'] for c in out['cases']);dest.write_text(json.dumps(out,indent=2));assert out['passed']\n"
exec(compile(s,'live-context-trace','exec'))
