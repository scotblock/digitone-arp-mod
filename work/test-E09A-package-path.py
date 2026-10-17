from pathlib import Path
source=Path('work/test-E08C-package-startup.py').read_text().replace('E08C','E09A')
exec(compile(source,'E09A-PC-package-path','exec'))
