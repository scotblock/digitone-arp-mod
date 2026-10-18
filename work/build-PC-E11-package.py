"""Internal E11 container using the existing verified stock-dependent writer."""
from pathlib import Path
import json
s=Path('work/build-PC-E10-package.py').read_text(encoding='utf-8').replace('PC_ONLY-E10-life','PC_ONLY-E11-editor').replace('PC_ONLY-E10-package','PC_ONLY-E11-package').replace('Digitone-E10-PC-package-container.json','Digitone-E11-PC-package-container.json').replace('main_identical_to_lifecycle_image=True','main_identical_to_E11_startup_image=True')
exec(compile(s,'E11-stock-container-writer','exec'))
