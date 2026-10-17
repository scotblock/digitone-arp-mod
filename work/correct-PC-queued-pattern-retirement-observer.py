from pathlib import Path
p=Path('work/test-PC-queued-pattern-retirement.py');s=p.read_text()
s=s.replace("if descriptor in descriptor_ids:event('callback_selected',", "if descriptor and rd(u,descriptor)==0x41a720d0 and rd(u,descriptor+4)==0x407ef9f4:\n     descriptor_ids.add(descriptor);event('callback_selected',")
s=s.replace("s.at(0x4002c1d2,callback)", """s.at(0x4002c1d2,callback)
   def clone(u,pc,n,d):
    ptr=u.reg_read(UC_M68K_REG_D0)
    if ptr and rd(u,ptr)==0x41a720d0 and rd(u,ptr+4)==0x407ef9f4:
     descriptor_ids.add(ptr);event('descriptor_clone',descriptor=hex(ptr),retained_destination=hex(rd(u,ptr+4)))
   s.at(0x4002c25a,clone)""")
s=s.replace("if ptr in descriptor_ids:event('descriptor_free',descriptor=hex(ptr))", "if ptr in descriptor_ids:\n     event('descriptor_free',descriptor=hex(ptr));descriptor_ids.remove(ptr)")
s=s.replace("assert kinds.index('queue_published')<kinds.index('callback_selected')<kinds.index('native_conversion')<kinds.index('descriptor_free')", "assert kinds.index('queue_published')<kinds.index('callback_selected')<kinds.index('native_conversion')\n  selected=next(x for x in row['events'] if x['kind']=='callback_selected')['descriptor'];completion=next(i for i,x in enumerate(row['events']) if x['kind']=='descriptor_free' and x['descriptor']==selected);assert kinds.index('native_conversion')<completion")
p.write_text(s)
