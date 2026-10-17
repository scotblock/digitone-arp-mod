"""Separate decompressed PC image with both native project persistence hooks."""
from pathlib import Path
import json,struct,hashlib
base=json.loads(Path('work/os144/PC_ONLY-E10-startup-layout.json').read_text())
full=json.loads(Path('work/os144/PC_ONLY-E10-startup-full-layout.json').read_text())
p=json.loads(Path('work/os144/PC_ONLY-E10-persistence-bridge.json').read_text());raw=Path('work/os144/PC_ONLY-E10-persistence-bridge.bin').read_bytes()
payload=bytearray(Path('work/os144/PC_ONLY-E10-startup-payload.bin').read_bytes());main=bytearray(Path('work/os144/PC_ONLY-E10-startup-main.bin').read_bytes());PB=base['base'];MB=0x40000400
assert PB+len(payload)<=p['base'];payload.extend(bytes(p['base']+len(raw)-PB-len(payload)));payload[p['base']-PB:]=raw
assert len(payload)%4==0 and PB+len(payload)<=0x47c00000
hooks=list(base['hooks'])
for h in p['hooks']:
 off=h['site']-MB;assert main[off:off+h['length']].hex()==h['before'];main[off:off+h['length']]=bytes.fromhex(h['after'])
 hooks.append(dict(site=h['site'],length=h['length'],original=h['before'],replacement=h['after']))
main[0x4029c4be-MB:0x4029c4c2-MB]=struct.pack('>I',len(payload)//4);main[0x4029c5b0-MB:]=payload
sha=lambda b:hashlib.sha256(b).hexdigest()
c={**base,'regions':base['regions']+p['regions'],'hooks':hooks,'persistence':p,'bytes':len(payload),'payload_bytes':len(payload),'copy_longwords':len(payload)//4,'copy_source_end':0x4029c5b0+len(payload),'copy_destination_end':PB+len(payload),'extra_bytes_over_E09A':len(payload)-34720,'main_sha256':sha(main),'payload_sha256':sha(payload),'native_persistence_bridge_installed':True,'automatic_pattern_binding':False,'firmware_container_created':False,'hardware_ready':False}
c.update(code_bytes=sum(r['bytes'] for r in c['regions']),native_project_persistence=True,limitations=['Decompressed PC MAIN/payload only; no E10 installable container or E10 loader-derived state.','Native project capture/emission is installed; editor-to-bank publication and automatic pattern recall are not connected.','Expanded RAM ownership, physical cache/timing, automatic power-loss persistence and asynchronous project replacement remain uncertified.'])
c['data_regions']=base['data_regions']+[dict(name='E10_persistence_metadata',base=p['meta'],bytes=32)]
Path('work/os144/PC_ONLY-E10-persistence-main.bin').write_bytes(main);Path('work/os144/PC_ONLY-E10-persistence-payload.bin').write_bytes(payload);Path('work/os144/PC_ONLY-E10-persistence-layout.json').write_text(json.dumps(c,indent=2))
rows={r['base']:r for r in full['regions']};rows.update({r['base']:r for r in c['regions']})
components={r['base']:r for r in full['components']};components.update({r['base']:r for r in p['regions']+c['data_regions']})
full={**full,**c,'regions':list(rows.values()),'components':list(components.values())};Path('work/os144/PC_ONLY-E10-persistence-full-layout.json').write_text(json.dumps(full,indent=2))
assert sha(Path('outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx').read_bytes())=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c'
print('Separate PC persistence image:',len(payload),'copied bytes. E09A unchanged; no container.')
