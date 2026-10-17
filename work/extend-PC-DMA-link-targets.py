from pathlib import Path
p=Path('work/test-PC-resident-DMA-successor-writers.py');s=p.read_text()
s=s.replace("'bulk_callers':{}", "'bulk_callers':{},'DMA_link_targets':{}")
anchor="   if td[10]&16:"
extra="""   minor=edma_sw.link_channel(td[6]);major=((td[10]>>8)&63) if td[10]&32 else None
   for kind,target in [('minor',minor),('major',major)]:
    if target is not None:
     key=kind+':'+str(channel)+'->'+str(target);report['DMA_link_targets'][key]=report['DMA_link_targets'].get(key,0)+1
     if target!=channel:descriptor(target,bytes(u.mem_read(0xfc045000+target*32,32)),'linked target concrete configuration')
"""
assert anchor in s;s=s.replace(anchor,extra+anchor)
# Wait for an observed replacement instead of assuming the shorter request
# interval completed one. This continues the same actual input workload.
s=s.replace("text=text.replace('Digitone-E04-PC-resident-storage-extended-runtime.json'", "text=text.replace(\"s.run_ms(2000);after=rd(u,0x4138f214)\",\"s.run_ms(400);after=rd(u,0x4138f214)\\n for wait in range(8):\\n  if after!=before:break\\n  s.run_ms(500);after=rd(u,0x4138f214)\")\ntext=text.replace('Digitone-E04-PC-resident-storage-extended-runtime.json'")
# Earlier replacement has changed the literal to run_ms(400); match it also.
s=s.replace("exec(compile(text,'actual-DMA-successor-writers','exec'))", "text=text.replace(\"s.run_ms(400);after=rd(u,0x4138f214)\",\"s.run_ms(400);after=rd(u,0x4138f214)\\n for wait in range(8):\\n  if after!=before:break\\n  s.run_ms(500);after=rd(u,0x4138f214)\",1)\nexec(compile(text,'actual-DMA-successor-writers','exec'))")
p.write_text(s)
