"""E11 loader-derived copier/init/logo; includes new UI strings/code checks."""
from pathlib import Path
s=Path('work/test-PC-E10-package-startup.py').read_text(encoding='utf-8').replace('PC_ONLY-E10-package','PC_ONLY-E11-package').replace('Digitone-E10-PC-package-loader.json','Digitone-E11-PC-package-loader.json').replace('Digitone-E10-PC-package-startup.json','Digitone-E11-PC-package-startup.json').replace('work/E10-package-startup-','work/E11-package-startup-')
exec(compile(s,'E11-loader-derived-startup','exec'))
