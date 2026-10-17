from pathlib import Path
p=Path('work/validate-E03-continuous-queue-action.py').read_text().replace("['valid','content_corrupt','missing_end','busy_view']","['valid','content_corrupt','missing_end','busy_view','restart_before_worker']")
p=p.replace("  entry=int.from_bytes(m.uc.mem_read(MAN+0x2c,4),'big');end=", "  if name=='restart_before_worker':\n   m.uc.mem_write(MSG,bytes(packets[0]));call(m,0x400eaac8,[MSG,len(packets[0]),8],stack_top=STACK,limit=100000);consume(m)\n   assert call(m,0x400eab94,[],stack_top=STACK,limit=10000)==0\n  entry=int.from_bytes(m.uc.mem_read(MAN+0x2c,4),'big');end=")
p=p.replace("'trace_counts':", "'trace_counts':")
Path('work/validate-E03-continuous-queue-action.py').write_text(p)
