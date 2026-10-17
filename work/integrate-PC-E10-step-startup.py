"""Join E10 overlays to the inherited copier/cold-success path, PC MAIN only."""
from pathlib import Path
import json,struct,hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
PB=0x47be0000;MB=0x40000400;COPY_SOURCE=0x4029c5b0
c=json.loads(Path('work/os144/E09A-PC-install-layout.json').read_text())
main=bytearray(Path('work/os144/E09A-PC-layout-main.bin').read_bytes())
payload=bytearray(Path('work/os144/E09A-PC-layout-payload.bin').read_bytes())
old_length=len(payload);regions=list(c['regions']);data_regions=list(c['data_regions']);patches=[]
life=json.loads(Path('work/os144/PC_ONLY-E10-step-lifetime.json').read_text())
END=life['bank']+life['bank_bytes'];payload.extend(bytes(END-PB-len(payload)))
for stem in ['engine','publication','editor','lifetime']:
 cfg=json.loads(Path('work/os144/PC_ONLY-E10-step-'+stem+'.json').read_text());blob=Path('work/os144/PC_ONLY-E10-step-'+stem+'.bin').read_bytes()
 offset=cfg['base']-PB
 assert offset>=old_length and offset+len(blob)<=len(payload)
 payload[offset:offset+len(blob)]=blob
 if 'regions' in cfg:regions+=cfg['regions']
 else:regions.append(dict(name='E10_atomic_settings_publication',base=cfg['base'],bytes=len(blob)))
 for p in cfg.get('patches',[]):
  i=p['site']-PB;assert payload[i:i+6].hex()==p['before'];payload[i:i+6]=bytes.fromhex(p['after']);patches.append(p)
 if stem=='editor':data_regions.append(dict(name='E10_step_editor_labels',base=cfg['strings_base'],bytes=cfg['strings_end']-cfg['strings_base']))
# Initialization is executable, not the copied seed. Leave state invalid until
# that initializer succeeds. The bank starts empty and has no stock aliases.
X=life['state'];payload[X-PB:X-PB+64]=bytes(64)
BOOT=0x47bec600;STATUS=0x47bed000
a=Asm();save(a);absolute(a,'4eb9',life['entries']['init']);absolute(a,'23c0',STATUS);a.emit('4a80');a.branch('6600','continue')
absolute(a,'42b9',X);absolute(a,'42b9',X+56)
a.label('continue');restore(a);absolute(a,'4ef9',0x40001df4);boot=a.done()
payload[BOOT-PB:BOOT-PB+len(boot)]=boot;regions.append(dict(name='E10_startup_initialize_and_bypass',base=BOOT,bytes=len(boot)))
old_boot=next(r for r in c['regions'] if r['name']=='cold_success_initialize');tail=old_boot['base']+old_boot['bytes']-6
assert payload[tail-PB:tail-PB+6].hex()=='4ef940001df4'
payload[tail-PB:tail-PB+6]=bytes.fromhex('4ef9')+struct.pack('>I',BOOT)
for p in patches:
 for r in regions:
  if r['base']==p['site']:
   # A six-byte JMP may cut through an old instruction. Decode only the live
   # replacement; retain the unreachable bytes for exact data readback.
   data_regions.append(dict(name=r['name']+'_unreachable_tail',base=r['base']+6,bytes=r['bytes']-6))
   r['bytes']=6
   break
main[0x4029c4be-MB:0x4029c4c2-MB]=struct.pack('>I',len(payload)//4)
main[COPY_SOURCE-MB:]=payload
assert len(payload)%4==0 and END<=0x47c00000
sha=lambda b:hashlib.sha256(b).hexdigest()
c.update(PC_only=True,parent_build='E09A',firmware_container_created=False,hardware_ready=False,base=PB,bytes=len(payload),payload_bytes=len(payload),copy_longwords=len(payload)//4,copy_source=COPY_SOURCE,copy_source_end=COPY_SOURCE+len(payload),copy_destination_end=END,regions=regions,data_regions=data_regions,E10=life,E10_bootstrap=BOOT,E10_status=STATUS,extra_bytes_over_E09A=len(payload)-old_length,main_sha256=sha(main),payload_sha256=sha(payload),native_project_persistence=False,automatic_pattern_binding=False,limitations=['Decompressed PC MAIN/payload only; no installable E10 firmware container.','Native cold copier and initialization integration; expanded RAM ownership, physical cache/timing and loader/container path are not certified.','Per-pattern RAM APIs are explicit and quiescent-only. Native project save/load and automatic pattern/copy/clear adapters remain unimplemented.'])
c.pop('firmware_modified',None)
c.update(E09A_firmware_unchanged=True,decompressed_PC_image_modified=True)
Path('work/os144/PC_ONLY-E10-startup-main.bin').write_bytes(main)
Path('work/os144/PC_ONLY-E10-startup-payload.bin').write_bytes(payload)
Path('work/os144/PC_ONLY-E10-startup-layout.json').write_text(json.dumps(c,indent=2))
assert sha(Path('outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx').read_bytes())=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c'
print('Separate PC MAIN:',len(payload),'copy bytes;',len(payload)-old_length,'additional; E09A unchanged')
