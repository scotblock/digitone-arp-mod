"""Exact E10 candidate through the modeled stock startup-menu DIN updater."""
from pathlib import Path
import json,hashlib
candidate=Path('work/os144/PC_ONLY-E10-package-loader-test.syx')
proof=json.loads(Path('outputs/Digitone-E10-PC-package-workflow-verification.json').read_text(encoding='utf-8'))
assert proof['passed'] and hashlib.sha256(candidate.read_bytes()).hexdigest()==proof['candidate_sha256']
s=Path('work/test-E04-startup-DIN-route.py').read_text(encoding='utf-8')
s=s.replace('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx',candidate.as_posix()).replace('E04','E10')
s=s.replace("==5 and len([a for a in m.actions if a[0]=='program'])==2472", "==(logical+0x3ffff)//0x40000 and len([a for a in m.actions if a[0]=='program'])==(logical+511)//512")
s=s.replace("a=args[0];m.actions.append(('erase',a))", "a=args[0];assert 0x80000<=a and a+0x40000<=0x380000;m.actions.append(('erase',a))")
s=s.replace("a,count,src=args;assert", "a,count,src=args;assert 0x80000<=a and a+count<=0x380000;assert")
exec(compile(s,'E10-exact-startup-DIN-receiver','exec'))
