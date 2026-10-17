"""Exact internal candidate through modeled stock startup receiver/updater."""
from pathlib import Path
s=Path('work/test-E04-startup-DIN-route.py').read_text()
s=s.replace('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/E08E-PC-path-candidate.syx')
s=s.replace('E04','E08E')
s=s.replace("==5 and len([a for a in m.actions if a[0]=='program'])==2472",
    "==(logical+0x3ffff)//0x40000 and len([a for a in m.actions if a[0]=='program'])==(logical+511)//512")
s=s.replace("a=args[0];m.actions.append(('erase',a))", "a=args[0];assert 0x80000<=a and a+0x40000<=0x380000;m.actions.append(('erase',a))")
s=s.replace("a,count,src=args;assert", "a,count,src=args;assert 0x80000<=a and a+count<=0x380000;assert")
exec(compile(s,'E08E-stock-startup-DIN-receiver','exec'))
