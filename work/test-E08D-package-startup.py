from pathlib import Path
source=Path('work/test-E08C-package-startup.py').read_text().replace('E08C','E08D')
source=source.replace("cfg['state']+312,b'\\xa7'*24", "cfg['state']+312,b'\\xa7'*32")
source=source.replace("cfg['state']+312,24))==bytes(24)","cfg['state']+312,32))==bytes(32)")
exec(compile(source,'E08D-PC-startup-controls','exec'))
