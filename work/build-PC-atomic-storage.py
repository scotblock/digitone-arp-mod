from pathlib import Path
import json,struct,hashlib
old=json.loads(Path('work/os144/PC_ONLY-live-storage-layout.json').read_text());code=Path('work/os144/PC_ONLY-atomic-live-copy.bin').read_bytes();payload=bytearray(Path('work/os144/PC_ONLY-live-storage-payload.bin').read_bytes());payload.extend(bytes(0x3600+len(code)-len(payload)));payload[0x3600:]=code;payload.extend(bytes((-len(payload))%4))
main=bytearray(Path('work/os144/PC_ONLY-live-storage-main.bin').read_bytes());base=0x40000400
for site,op in [(0x400ff5f6,'4eb9'),(0x400ff5a6,'4bf9')]:
 assert main[site-base:site-base+6]==bytes.fromhex(op)+struct.pack('>I',old['live']['layout']['live_copy']['address']);main[site-base:site-base+6]=bytes.fromhex(op)+struct.pack('>I',0x47be3600)
main[0x4029c4be-base:0x4029c4c2-base]=struct.pack('>I',len(payload)//4);main[0x4029c5b0-base:]=payload
Path('work/os144/PC_ONLY-atomic-storage-main.bin').write_bytes(main);Path('work/os144/PC_ONLY-atomic-storage-payload.bin').write_bytes(payload)
cfg=dict(old);cfg.update(atomic_address=0x47be3600,atomic_bytes=len(code),payload_bytes=len(payload),copy_longwords=len(payload)//4,main_sha256=hashlib.sha256(main).hexdigest(),payload_sha256=hashlib.sha256(payload).hexdigest());cfg['regions']=old['regions']+[(0x47be3600,len(code))];cfg['live']=dict(old['live']);cfg['live']['hooks']=[dict(h) for h in old['live']['hooks']]
for h in cfg['live']['hooks']:
 if h['name']=='live_copy':h['replacement']=h['op']+struct.pack('>I',0x47be3600).hex()
Path('work/os144/PC_ONLY-atomic-storage-layout.json').write_text(json.dumps(cfg,indent=2));print('Separate PC candidate:',len(payload),'resident bytes')
