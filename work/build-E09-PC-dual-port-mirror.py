"""PC-only parallel DIN/USB voice owners, preserving E08F files."""
from pathlib import Path
import json,struct,hashlib
full=json.loads(Path('outputs/Digitone-E08F-PC-path-layout.json').read_text())
PB=0x47be0000;B=0x47be7e00;S=B+0x900
src=Path('work/build-PC-synth-arp-MIDI.py').read_text().split('# Called from inside E06')[0]
src=src.replace('STATE=0x47be5c00;RECS=STATE+32;MARKERS=STATE+16;BASE=0x47be5000',f'STATE={S};RECS=STATE+32;MARKERS={full["MIDI_markers"]};BASE={B}')
for offset in [0,4,8]:src=src.replace(f'47be5c{offset:02x}',f'{S+offset:08x}')
src=src.replace("a.emit('2039419c5df4028000000001')","a.emit('2039419c5df4028000000002')")
start=src.index("a=Asm();a.emit('4fefffd8")
end=src.index('# service(record)',start)
tx=r'''
# The main CPU's IPL is masked by the existing owner wrappers. Do not enter
# the USB pool-wait path when no descriptor is immediately available.
a=Asm();saveall(a);a.emit('242f0044262f0048282f004c0c8300000080');a.branch('6400','no');a.emit('0c8400000080');a.branch('6400','no')
a.emit('7001b0b940529244');a.branch('6600','no');a.emit('4ab9fc0b01c4');a.branch('6700','no')
a.emit('2039429f23b8028000000020');a.branch('6600','no')
a.emit('2079405293884a88');a.branch('6700','no');a.emit('082800070007');a.branch('6600','no')
a.emit('2a39405292480c8500000ffb');a.branch('6200','no')
a.emit('20394052924c0c8000000ffc');a.branch('6200','no');a.emit('028000000003');a.branch('6600','no')
a.emit('4feffff81f4200001f4300011f440002486f000048780003');absolute(a,'4eb9',0x40004bcc);a.emit('4fef0010')
# A failed endpoint submit executes the stock cleanup callback synchronously,
# undoing the pending-byte increment. Successful queue admission adds four.
a.emit('20394052924890850c8000000004');a.branch('6600','no');a.emit('7001');a.branch('6000','end')
a.label('no');a.emit('7000');a.label('end');a.emit('2f400000');restoreall(a);a.emit('4e75');add('USB_try_send',TX,a,256)
'''
src=src[:start]+tx+'\n'+src[end:]
ns={};exec(compile(src,'E09-USB-owner-copy','exec'),ns)
payload=bytearray(Path('work/os144/E08F-PC-layout-payload.bin').read_bytes())
payload.extend(bytes(S+160-PB-len(payload)))
for addr,code in ns['parts']:payload[addr-PB:addr-PB+len(code)]=code
payload[S-PB:S-PB+160]=struct.pack('>II',0x53414d31,1)+bytes(152)
Asm=ns['Asm'];saveall=ns['saveall'];restoreall=ns['restoreall'];absolute=ns['absolute']
old=full['MIDI_entries'];bridges=[]
for name,count,oldaddr,newaddr,addr in [('start_both',5,old['ON'],ns['ON'],B+0x600),('release_both',1,old['OFF'],ns['OFF'],B+0x680),('pump_both',0,old['PUMP'],ns['PUMP'],B+0x700)]:
 a=Asm();saveall(a)
 for target in [oldaddr,newaddr]:
  for _ in range(count):a.emit('2f2f'+struct.pack('>H',0x40+count*4).hex())
  absolute(a,'4eb9',target)
  if count:a.emit('4fef'+struct.pack('>H',count*4).hex())
 restoreall(a);a.emit('4e75');code=a.done();assert len(code)<=128
 payload[addr-PB:addr-PB+len(code)]=code;bridges.append({'name':name,'base':addr,'bytes':len(code)})
targets={old['ON']:B+0x600,old['OFF']:B+0x680,old['PUMP']:B+0x700};patches=[]
for name in ['accepted_voice_hook','allocator_release_hook','gate_release_hook','MIDI_task_pump_hook']:
 r=next(r for r in full['regions'] if r['name']==name);off=r['base']-PB
 code=bytes(payload[off:off+r['bytes']]);before=code
 for oldaddr,newaddr in targets.items():code=code.replace(bytes.fromhex('4eb9')+struct.pack('>I',oldaddr),bytes.fromhex('4eb9')+struct.pack('>I',newaddr))
 assert code!=before;payload[off:off+len(code)]=code;patches.append({**r,'before':before.hex(),'after':code.hex()})
cfg={'PC_only':True,'firmware_container_created':False,'base':PB,'bytes':len(payload),'USB_state':S,
 'USB_records':S+32,'shared_event_markers':full['MIDI_markers'],'USB_entries':{k:ns[k] for k in ['TX','SERVICE','OFF','ON','PUMP']},
 'DIN_entries':old,'bridge_entries':{r['name']:r['base'] for r in bridges},'regions':ns['regions']+bridges,
 'patches':patches,'payload_sha256':hashlib.sha256(payload).hexdigest(),
 'limits':['Host installation/initialization only; no startup integration or ownership certification for the added RAM.','USB descriptor availability and queue limits checked before the native writer; real hardware concurrency is unproven.','New USB owners remain independent from DIN owners so pending releases survive output-selection changes.']}
Path('work/os144/E09-PC-dual-port-payload.bin').write_bytes(payload)
Path('work/os144/E09-PC-dual-port-layout.json').write_text(json.dumps(cfg,indent=2))
print('PC-only dual-port owner payload',len(payload),'bytes, USB state',hex(S))
