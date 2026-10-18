"""Exact E11 PC container through modeled startup DIN receiver and programmer."""
from pathlib import Path
s=Path('work/test-E10-startup-DIN-route.py').read_text(encoding='utf-8-sig').replace('PC_ONLY-E10-package','PC_ONLY-E11-package').replace('outputs/Digitone-E10-PC-package-workflow-verification.json','outputs/Digitone-E11-PC-package-container.json').replace(".replace('E04','E10')",".replace('E04','E11')")
exec(compile(s,'E11-exact-startup-DIN','exec'))
