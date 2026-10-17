from pathlib import Path
source=Path('work/verify-E08E-container.py').read_text().replace('E08E','E09A')
exec(compile(source,'E09A-independent-container-checks','exec'))
