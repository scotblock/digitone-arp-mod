from pathlib import Path
source=Path('work/test-E08C-package-startup.py').read_text().replace('E08C','E09')
exec(compile(source,'E09-PC-package-path','exec'))
