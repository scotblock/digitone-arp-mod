"""Reuse bounded native loader/startup controls for distinct E08F artifacts."""
from pathlib import Path
source=Path('work/test-E08C-package-startup.py').read_text().replace('E08C','E08F')
exec(compile(source,'E08F-package-path-control','exec'))
