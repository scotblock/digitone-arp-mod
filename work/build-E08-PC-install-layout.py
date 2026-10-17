from pathlib import Path
import json,struct,hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
c=json.loads(Path('work/os144/E08-PC-tempo-M1-layout.json').read_text());blob=Path('work/os144/E08-PC-tempo-M1-code.bin').read_bytes();PB=0x47be0000;MB=0x40000400
old=Path('work/os144/E07-PC-payload.bin').read_bytes();payload=bytearray(old);payload.extend(bytes((-len(payload))%16));alloc={};mapped_regions=[];cursor=PB+len(payload)
for r in c['regions']+c['data_regions']:
 alloc[r['base']]=cursor;mapped_regions.append({**r,'base':cursor,'old_base':r['base']});cursor+=r['bytes'];cursor=(cursor+1)&~1
cursor=(cursor+23)&~15;newstate=cursor;cursor+=c['state_bytes'];cursor=(cursor+23)&~15;newarena=cursor;cursor+=c['arena_bytes'];cursor=(cursor+15)&~15;boot=cursor
ranges=[(r['old_base'],r['bytes'],r['base']) for r in mapped_regions]+[(c['state'],c['state_bytes'],newstate),(c['arena'],c['arena_bytes'],newarena)]
def remap(v):
 for a,n,target in ranges:
  if a<=v<a+n:return target+v-a
 return v
payload.extend(bytes(cursor-PB-len(payload)))
relocations=[]
for r in mapped_regions:
 data=bytearray(blob[r['old_base']-c['base']:r['old_base']-c['base']+r['bytes']])
 if r['name']!='rate_table':
  for off in range(0,len(data)-3,2):
   value=int.from_bytes(data[off:off+4],'big');target=remap(value)
   if target!=value:data[off:off+4]=struct.pack('>I',target);relocations.append({'region':r['name'],'offset':off,'from':hex(value),'to':hex(target)})
 off=r['base']-PB;payload[off:off+len(data)]=data
entries={k:remap(v) for k,v in c['entries'].items()}
a=Asm();save(a);absolute(a,'4879',0x4138f208);absolute(a,'4eb9',entries['init']);a.emit('588f');restore(a);absolute(a,'4ef9',0x40001df4);bootstrap=a.done();payload.extend(bootstrap);payload.extend(bytes((-len(payload))%4))
site=0x47be3bb2;before=payload[site-PB:site-PB+6];assert before.hex()=='4ef940001df4';payload[site-PB:site-PB+6]=bytes.fromhex('4ef9')+struct.pack('>I',boot)
main=bytearray(Path('work/os144/E07-PC-main.bin').read_bytes());main[0x4029c4be-MB:0x4029c4c2-MB]=struct.pack('>I',len(payload)//4)
hooks=[]
for h in c['hooks']:
 off=h['site']-MB;assert main[off:off+h['length']].hex()==h['original'];replacement=bytes.fromhex('4ef9')+struct.pack('>I',remap(h['target']));main[off:off+6]=replacement;hooks.append({**h,'target':remap(h['target']),'replacement':replacement.hex()})
main[0x4029c5b0-MB:]=payload
Path('work/os144/E08-PC-layout-main.bin').write_bytes(main);Path('work/os144/E08-PC-layout-payload.bin').write_bytes(payload)
region_rows=[{k:v for k,v in x.items() if k!='old_base'} for x in mapped_regions if x['name']!='rate_table']+[{'name':'cold_success_initialize','base':boot,'bytes':len(bootstrap)}]
cfg={**c,'base':PB,'bytes':len(payload),'code_bytes':sum(x['bytes'] for x in region_rows),'state':newstate,'arena':newarena,'entries':entries,'regions':region_rows,'data_regions':[x for x in mapped_regions if x['name']=='rate_table'],'hooks':hooks,'old_payload_bytes':len(old),'payload_bytes':len(payload),'additional_copy_bytes':len(payload)-len(old),'copy_longwords':len(payload)//4,'copy_source':0x4029c5b0,'copy_source_end':0x4029c5b0+len(payload),'copy_destination_end':PB+len(payload),'bootstrap':boot,'cold_success_patch':{'site':site,'before':before.hex(),'after':payload[site-PB:site-PB+6].hex()},'main_sha256':hashlib.sha256(main).hexdigest(),'payload_sha256':hashlib.sha256(payload).hexdigest(),'relocations':relocations,'installable_firmware_produced':False,'limits':['Only decompressed PC MAIN/payload images; no packed container or physical install candidate.','Existing copier count is extended; original cold-seed success path initializes M1 before existing stock cache handoff. Physical coherence and new RAM ownership remain unverified.','Warm copy replay has inherited hazards; UI/reset guards have not been fully retested for the extension.','M1 arp defaults OFF. No user-facing settings UI or persistence yet.']}
Path('work/os144/E08-PC-install-layout.json').write_text(json.dumps(cfg,indent=2));print('Layout:',len(payload),'copied bytes, extension',len(payload)-len(old),'state',hex(newstate),'arena',hex(newarena),'boot',hex(boot))
