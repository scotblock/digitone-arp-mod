"""Execute the stock loader on the separate internal E10 package."""
from pathlib import Path
s=Path('work/test-E08-packed-loader.py').read_text(encoding='utf-8')
for a,b in [('work/os144/E08-PC-path-candidate.syx','work/os144/PC_ONLY-E10-package-loader-test.syx'),('work/os144/E08-PC-layout-main.bin','work/os144/PC_ONLY-E10-package-main.bin'),('work/os144/E08-PC-loader-handoff.bin','work/os144/PC_ONLY-E10-package-loader-handoff.bin'),('outputs/Digitone-E08-packed-loader.json','outputs/Digitone-E10-PC-package-loader.json')]:s=s.replace(a,b)
exec(compile(s,'E10-stock-loader-continuity','exec'))
p=Path('outputs/Digitone-E10-PC-package-loader.json');r=json.loads(p.read_text());assert r['passed']
r.update(E10_container_bootstrapped=True,firmware_release_created=False,hardware_ready=False)
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
