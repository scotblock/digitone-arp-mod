from pathlib import Path
source=Path('work/package-E08C-controls-PC.py').read_text().replace('E08C','E08D')
exec(compile(source,'E08D-PC-package','exec'))
