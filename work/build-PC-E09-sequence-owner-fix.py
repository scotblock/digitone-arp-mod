"""PC-only E09 owner correction; do not create or alter firmware containers."""
from pathlib import Path
import json,struct,hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
n=json.loads(Path('work/os144/E09-PC-install-layout.json').read_text())
region=next(r for r in n['regions'] if r['name']=='eligible_source_settings_owner')
source=Path('work/build-E08D-owner-guards.py').read_text()
source=source[source.index('# Eligible M1 note-on'):]
source=source[:source.index("\n'''\n")]
bad="a.emit('202800284a80');a.branch('6600','return');absop(a,'2039',0x419c5b14);a.emit('4a80');a.branch('6600','return');absop(a,'2039',0x419c5b10)"
assert source.count(bad)==1
# +28 and 0x419c5b14 are parameter-lock list pointers. They are not MIDI
# runtime parameter records, and cannot supply our tagged +0x9e settings.
source=source.replace(bad,"absop(a,'2039',0x419c5b10)")
parts=[]
def absop(a,op,v):absolute(a,op,v)
def js(a,v):absop(a,'4eb9',v)
def done_void(a):restore(a);a.emit('4e75')
def add(name,address,a,limit):
    code=a.done();assert address==region['base'] and len(code)<=region['bytes'];parts.append(code)
exec(compile(source,'E09-PC-sequence-owner-helper','exec'))
code=parts[0]
payload=Path('work/os144/E09-PC-layout-payload.bin').read_bytes()
before=payload[region['base']-n['base']:region['base']-n['base']+region['bytes']]
overlay=code+bytes.fromhex('4e71')*((len(before)-len(code))//2)
assert len(overlay)==len(before)
Path('work/os144/PC_ONLY-E09-sequence-owner-helper.bin').write_bytes(overlay)
out={'PC_only':True,'firmware_container_created':False,'region':region,'executed_bytes':len(code),'overlay_bytes':len(overlay),
     'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(overlay).hexdigest(),
     'behavior':'Eligible M1 sources select the consumed KitActive M1 runtime record. Parameter-lock lists never supply arp settings.',
     'limits':['Context ordering and queued-note pattern ownership need continuous checks. No hardware validation or candidate packaging.']}
Path('work/os144/PC_ONLY-E09-sequence-owner-helper.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
