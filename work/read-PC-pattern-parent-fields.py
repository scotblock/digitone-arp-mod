from pathlib import Path
import json,sys,zlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import snapshot
r=json.loads(Path('outputs/Digitone-E04-PC-resident-deferred-startup-startup.json').read_text());ui=next(x for x in r['cases'] if x['image']=='E04_restored')['ui_snapshot'];blob=snapshot._load_blob(ui)
def read(a,n):
 base=max(x for x in blob['pages'] if x<=a);data=zlib.decompress(blob['pages'][base]);return data[a-base:a-base+n]
for a in [0x41a720a0,0x41a720c0,0x41a720d0,0x41a720f0]:print(hex(a),read(a,4).hex())
