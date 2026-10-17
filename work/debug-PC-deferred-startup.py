from pathlib import Path
p=Path('work/test-PC-deferred-release-startup.py');s=p.read_text();s=s.replace(" if path.name=='test-PC-joined-UI-startup.py':", " if path.name=='test-PC-ISA-corrected-startup.py':\n  text=text.replace(\"exec(compile(s,'PC-ISA-corrected-startup','exec'))\",\"Path('work/generated-deferred-startup-debug.py').write_text(s);exec(compile(s,'PC-ISA-corrected-startup','exec'))\")\n if path.name=='test-PC-joined-UI-startup.py':")
p.write_text(s)
