from pathlib import Path
import json
port=json.loads(Path('work/os144/helper-port.json').read_text())
s=Path('work/test-packed-outer-ABI.py').read_text()
for old,new in port['mapping'].items():s=s.replace(old,new)
s=s.replace("pathlib.Path('work/'+name+'.bin')","pathlib.Path('work/os144/'+name+'.bin')")
s=s.replace('Digitone-packed-context-outer-ABI.json','Digitone-OS1.44-outer-helper-ABI.json')
exec(compile(s,'OS1.44-outer-helper-ABI','exec'))
