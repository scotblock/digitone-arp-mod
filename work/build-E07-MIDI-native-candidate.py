from pathlib import Path
import json,struct,hashlib
oldcfg=json.loads(Path('work/os144/PC_ONLY-synth-arp-MIDI-layout.json').read_text());oldpayload=Path('work/os144/E06-PC-payload.bin').read_bytes();PB=0x47be0000
gaps=[(PB+0xb2e,PB+0xc00),(PB+0xc92,PB+0xd00),(PB+0xf30,PB+0x1000),(PB+0x1b80,PB+0x2000)]
for a,z in gaps:assert oldpayload[a-PB:z-PB]==bytes(z-a),(hex(a),hex(z))
alloc={}
def place(name,size,align=2):
 for j,(lo,hi) in enumerate(gaps):
  lo=(lo+align-1)//align*align
  if lo+size<=hi:alloc[name]=lo;gaps[j]=(lo+size,hi);return lo
 raise ValueError((name,size,gaps))
for r in sorted(oldcfg['regions'],key=lambda r:-r['bytes']):place(r['name'],r['bytes'])
state=place('private_state',160,16)
mapping={'TX':'DIN_try_send','SERVICE':'service_release','OFF':'release_voice','ON':'start_voice','PUMP':'pump_releases','MARK':'mark_arp_event','START':'accepted_voice_hook','REL1':'allocator_release_hook','REL2':'gate_release_hook','POLL':'MIDI_task_pump_hook','CLEAR':'retire_event_marker'}
src=Path('work/build-PC-synth-arp-MIDI.py').read_text().split('blob=bytearray')[0]
src=src.replace('BASE=0x47be5000','BASE=0x47be0000')
for offset in [0,4,8]:src=src.replace(f'47be5c{offset:02x}',f'{state+offset:08x}')
anchor='parts=[];regions=[]';src=src.replace(anchor,'\n'.join(k+'='+str(alloc[v]) for k,v in mapping.items())+'\n'+anchor)
ns={};exec(src,ns)
payload=bytearray(oldpayload);regions=ns['regions'];tail=ns['tail']
assert len(tail)==146
for addr,code in ns['parts']:payload[addr-PB:addr-PB+len(code)]=code
payload[state-PB:state-PB+160]=struct.pack('>II',0x53414d31,1)+bytes(152)
payload[0xc00:0xc00+len(tail)]=tail
main=bytearray(Path('work/os144/E06-PC-main.bin').read_bytes());hooks=[]
for site,length,target in [(0x4009e930,6,alloc['accepted_voice_hook']),(0x4009f0c6,8,alloc['allocator_release_hook']),(0x4009fa56,10,alloc['gate_release_hook']),(0x400f4c7e,6,alloc['MIDI_task_pump_hook']),(0x4009d7d8,6,alloc['retire_event_marker'])]:
 off=site-0x40000400;before=main[off:off+length];replacement=bytes.fromhex('4ef9')+struct.pack('>I',target)+bytes.fromhex('4e71')*((length-6)//2);main[off:off+length]=replacement;hooks.append({'name':'MIDI_mirror_'+hex(site),'site':site,'length':length,'previous':before.hex(),'replacement':replacement.hex()})
main[0x4029c5b0-0x40000400:]=payload
assert len(payload)==len(oldpayload) and len(main)==Path('work/os144/E06-PC-main.bin').stat().st_size
Path('work/os144/E07-PC-main.bin').write_bytes(main);Path('work/os144/E07-PC-payload.bin').write_bytes(payload)
cfg=json.loads(Path('outputs/Digitone-E06-PC-candidate-layout.json').read_text());cfg.update(candidate='pending',hardware_ready=False,main_sha256=hashlib.sha256(main).hexdigest(),payload_sha256=hashlib.sha256(payload).hexdigest(),MIDI_route='DIN only: synth arps mirrored on configured synth-track channels; pending note-offs retain original destinations',MIDI_state=state,MIDI_state_bytes=160,MIDI_markers=state+16,MIDI_records=state+32,MIDI_entries={k:alloc[v] for k,v in mapping.items()},MIDI_code_bytes=sum(r['bytes'] for r in regions))
for key in ['regions','components']:
 for r in cfg[key]:
  if r['name']=='arp_degree_tail_hook':r['bytes']=146
 cfg[key]+=regions
cfg['components']+=[{'name':'MIDI_private_state_seed','base':state,'bytes':160}];cfg['hooks']+=hooks
cfg['degree_hook_bytes']=146
Path('outputs/Digitone-E07-PC-candidate-layout.json').write_text(json.dumps(cfg,indent=2))
Path('work/os144/E07-MIDI-relocation.json').write_text(json.dumps({'allocations':alloc,'remaining_gaps':gaps,'code_bytes':cfg['MIDI_code_bytes'],'state_bytes':160,'payload_bytes_unchanged':len(payload),'copier_unchanged':True,'copied_state_seed_has_magic_enable_and_zero_owners':True},indent=2))
print('E07 native layout fits:',cfg['MIDI_code_bytes'],'code bytes, state',hex(state),'payload unchanged',len(payload))
