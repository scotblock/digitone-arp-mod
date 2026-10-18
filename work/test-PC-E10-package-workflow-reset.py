"""Packaged E10 nonempty-bank warm and diagnostic reset refusal controls."""
from pathlib import Path
s=Path('work/test-PC-E10-life-reset-refusal.py').read_text(encoding='utf-8')
s=s.replace('PC_ONLY-E10-life','PC_ONLY-E10-package').replace('Digitone-E10-PC-life-startup.json','Digitone-E10-PC-package-startup.json').replace('Digitone-E10-PC-life-copy-cache.json','Digitone-E10-PC-package-workflow-copy.json').replace('Digitone-E10-PC-life-reset-refusal.json','Digitone-E10-PC-package-workflow-reset.json')
exec(compile(s,'E10-packaged-populated-reset-refusals','exec'))
