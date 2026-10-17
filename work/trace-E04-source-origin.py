from pathlib import Path
s=Path('work/trace-E04-source-startup.py').read_text()
s=s.replace("s=s.replace(old,'for name,syx,imgfile,cardfile in '+repr(cases)+':')","cases=cases[-1:]\ns=s.replace(old,'for name,syx,imgfile,cardfile in '+repr(cases)+':')")
s=s.replace('Digitone-E04-source-startup-checks.json','Digitone-E04-source-origin-checks.json')
s=s.replace("work/source-startup-","work/source-origin-")
anchor='   def fieldwrite(uc,access,address,size,value,data):'
extra=r'''   row.setdefault('serialized_track_entries',[]);row.setdefault('card_reads',[]);row.setdefault('card_writes',[])
   if not hasattr(mm,'esdhc'):return # Storage origin instrumentation applies to the cold engine.
   original_data_for=mm.esdhc.card.data_for
   def data_for(idx,arg=0,length=None):
    if idx==18:row['card_reads'].append({'stage':stage,'offset':hex(arg*512),'length':length,'pc':hex(mm.uc.reg_read(UC_M68K_REG_PC)),'estimated_instructions':done})
    return original_data_for(idx,arg,length)
   mm.esdhc.card.data_for=data_for
   original_write_data=mm.esdhc.card.write_data
   def write_data(idx,arg,payload):
    row['card_writes'].append({'stage':stage,'command':idx,'offset':hex(arg*512),'length':len(payload),'pc':hex(mm.uc.reg_read(UC_M68K_REG_PC)),'estimated_instructions':done})
    return original_write_data(idx,arg,payload)
   mm.esdhc.card.write_data=write_data
   def serialized(uc,pc,size,data):
    sp=uc.reg_read(UC_M68K_REG_A7);words=[int.from_bytes(uc.mem_read(sp+i*4,4),'big') for i in range(3)]
    ret,dst,src=words
    if any(base<=dst<base+0xf40 for base in [0x407fd414,0x40813531]):row['serialized_track_entries'].append({'stage':stage,'return':hex(ret),'destination':hex(dst),'serialized_source':hex(src),'serialized_tail':read(src+0x3c0,16),'estimated_instructions':done})
   mm.uc.hook_add(UC_HOOK_CODE,serialized,begin=0x40008c3c,end=0x40008c3c)
'''
assert anchor in s;s=s.replace(anchor,extra+anchor)
needle="exec(compile(s,'E04-source-startup','exec'))"
assert needle in s
s=s.replace(needle,"s=s.replace(\"  row.update(cold_pc=hex(pc),\",\"  row['flash_reads']=st['reads']\\n  row.update(cold_pc=hex(pc),\")\n"+needle)
exec(compile(s,'E04-source-origin-wrapper','exec'))
