"""Separate internal package layout; leaves E08C and E07 unchanged."""
from pathlib import Path
import json,struct,hashlib
folder=Path('work/os144');PB=0x47be0000;MB=0x40000400
c=json.loads((folder/'E08D-PC-M1-controls-layout.json').read_text())
base=json.loads((folder/'E08C-PC-install-layout.json').read_text())
full=json.loads(Path('outputs/Digitone-E08C-PC-path-layout.json').read_text())
assert json.loads(Path('outputs/Digitone-E08D-owner-guard-contracts.json').read_text())['passed']
payload=bytearray((folder/'E08C-PC-layout-payload.bin').read_bytes())
main=bytearray((folder/'E08C-PC-layout-main.bin').read_bytes())
blob=(folder/'E08D-PC-M1-controls.bin').read_bytes()
trampolines=[(a,bytes(payload[a-PB:a-PB+14])) for a in [0x47be6e00,0x47be6e20]]
offset=c['base']-PB;assert offset+len(blob)<=len(payload)
payload[offset:offset+len(blob)]=blob
for a,data in trampolines:
    assert payload[a-PB:a-PB+14]==bytes(14)
    payload[a-PB:a-PB+14]=data
init=base['entries']['init'];region=next(r for r in base['regions'] if r['base']==init)
code=bytes(payload[init-PB:init-PB+region['bytes']]);assert code.count(bytes.fromhex('7254'))==1
payload[init-PB:init-PB+len(code)]=code.replace(bytes.fromhex('7254'),bytes.fromhex('7256'))
assert base['state']+344<=base['arena']
assert bytes(payload[base['state']-PB+336:base['state']-PB+344])==bytes(8)
main[base['copy_source']-MB:]=payload
replacements={r['name']:r for r in c['regions']}
def regions(old):
    result=[replacements.get(r['name'],r) for r in old]
    names={r['name'] for r in old}
    return result+[r for r in c['regions'] if r['name'] not in names]
sha=lambda data:hashlib.sha256(data).hexdigest()
common={'state_bytes':344,'owner_offset':336,'request_owner_offset':340,
        'owner_guard_entries':c['entries'],'main_sha256':sha(main),'payload_sha256':sha(payload),
        'ownership_guards_integrated':True,'installable_firmware_produced':False,
        'limits':['Internal PC-only ownership candidate; no hardware release.',
                  'Consumed context/eligible note sources establish owner identity; retained identities are not dereferenced.',
                  'Physical storage/cache/timing, in-place record reuse and all project/reset overlaps remain unproven.']}
new={**base,**common,'regions':regions(base['regions'])}
new['code_bytes']=sum(r['bytes'] for r in new['regions'])
merged={**full,**new,'regions':regions(full['regions']),'components':regions(full['components']),
        'candidate':None,'candidate_sha256':None,'hardware_ready':False,'PC_only':True}
(folder/'E08D-PC-layout-main.bin').write_bytes(main)
(folder/'E08D-PC-layout-payload.bin').write_bytes(payload)
(folder/'E08D-PC-install-layout.json').write_text(json.dumps(new,indent=2))
Path('outputs/Digitone-E08D-PC-path-layout.json').write_text(json.dumps(merged,indent=2))
print('PC ownership layout:',len(payload),'copied bytes; state',344,'bytes; arena unchanged.')
