from pathlib import Path
s=Path('work/test-os144-startup-fallback-design.py').read_text().replace('ENTRY=0x47f40000','ENTRY=0x47be08a4').replace('Digitone-OS1.44-startup-fallback-design-checks.json','Digitone-OS1.44-final-fallback-contract-checks.json')
exec(compile(s,'final-fallback-contracts','exec'))
