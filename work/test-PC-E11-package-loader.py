"""Stock bootstrap of the separate E11 UI package, with serialized handoff."""
from pathlib import Path
s=Path('work/test-PC-E10-package-loader.py').read_text(encoding='utf-8').replace('PC_ONLY-E10-package','PC_ONLY-E11-package').replace('Digitone-E10-PC-package-loader.json','Digitone-E11-PC-package-loader.json')
exec(compile(s,'E11-stock-loader','exec'))
