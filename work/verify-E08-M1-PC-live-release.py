from pathlib import Path
import json,struct,hashlib
p=Path('outputs/Digitone-E08-M1-PC-live-release.json');r=json.loads(p.read_text())
assert r['failure'] is None and r['halted'] is None and r['MIDI_received']==r['MIDI_delivered']
phase=r['phases'][0];assert not phase['active_scheduler_at_end'] and not phase['held_at_end']
assert [(x['note'],x['on']) for x in r['live_inputs']]==[(60,True),(64,True),(67,True),(60,False),(64,False),(67,False)]
assert all(int.from_bytes(bytes.fromhex(x['raw'])[0x1c:0x20],'big')==0 for x in r['live_inputs'] if x['on'])
active={};ons=[];offs=[];track=bytearray(b'\x00\xff\x51\x03\x07\xa1\x20');lasttick=0

def vl(n):
 parts=[n&127];n>>=7
 while n:parts.insert(0,(n&127)|128);n>>=7
 return bytes(parts)
for x in phase['wire']:
 assert len(x['bytes'])%3==0
 for i in range(0,len(x['bytes']),3):
  packet=x['bytes'][i:i+3];status,note,velocity=packet;assert status&240 in [128,144]
  key=(status&15,note);on=status&240==144 and velocity>0
  if on:
   assert key not in active;active[key]=x['ms'];ons.append({'ms':x['ms'],'note':note})
  else:
   assert key in active;start=active.pop(key);offs.append({'ms':x['ms'],'note':note,'gate_ms':x['ms']-start})
  tick=round((x['ms']-phase['begin_ms'])*.96);track+=vl(tick-lasttick)+bytes(packet);lasttick=tick
assert not active and [x['note'] for x in ons]==[60,64,67] and len(offs)==3
assert ons[-1]['ms']<phase['release_request_ms']<offs[-1]['ms']<phase['release_request_ms']+30
assert offs[-1]['gate_ms']<40
assert any(x['reason']=='native_source_key_release' for x in r['cancellations'])
assert phase['end_ms']-offs[-1]['ms']>400
assert all(x['native_gate']>0 for x in r['generations'])
track+=b'\x00\xff\x2f\x00';mid=Path('outputs/Digitone-E08-M1-UP_live_release-PC.mid');mid.write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,480)+b'MTrk'+struct.pack('>I',len(track))+track)
r['passed']=True;r['verified_case']={'phase':'UP_live_release','notes':[60,64,67],'note_on_count':3,'note_off_count':3,'no_hanging_notes':True,'native_input_keys_released':True,'final_key_release_to_note_off_ms':offs[-1]['ms']-phase['release_request_ms'],'final_note_shortened_by_native_release':True,'quiet_after_release_ms':phase['end_ms']-offs[-1]['ms'],'MIDI_file':str(mid.resolve()),'passed':True};r['limits']=['Host Python implements held-note membership and arp scheduling. This is not a guest machine-code helper.','Live input gate zero means held; explicit PC interval=5400000 and note gate=1350000 clock units are disclosed fixtures (approximately 125/62.5 ms in this model). These are not general tempo synchronization.','MIDI input processing, release descriptor production, output packet production and note termination execute the native firmware.','The PC-only scratch descriptor arena/free bypass has no hardware storage ownership proof.','One M1 chord and complete key release only; sustain, partial release, mute, pattern replacement and other tracks remain untested.'];p.write_text(json.dumps(r,indent=2))
baseline=json.loads(Path('outputs/Digitone-E08-M1-PC-prototype.json').read_text());assert baseline['passed']
sha=hashlib.sha256(Path('outputs/Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx').read_bytes()).hexdigest();assert sha==baseline['E07_unchanged_sha256']
summary={'PC_only':True,'passed':True,'firmware_unchanged':True,'installable_E08_produced':False,'E07_sha256':sha,'implementation':'Host-assisted scheduler linked to native MIDI task; guest machine-code scheduler remains to be built','cases':baseline['verified_cases']+[r['verified_case']],'model_fixes':['MIDI descriptors use the full 0x80004614 clock domain, not a halved timestamp.','Live source gate zero means held; arp interval and generated finite gate must be independent and positive.'],'next':'Port sorting/state/timing helpers to ColdFire in isolated PC tests, establish descriptor ownership, then integrate; settings persistence and code space remain unresolved.'}
Path('outputs/Digitone-E08-M1-prototype-results.json').write_text(json.dumps(summary,indent=2))
readme=Path('outputs/Digitone-E08-M1-PC-prototype.md');text=readme.read_text(encoding='utf-8');text=text.replace('Live held-note release and sustain, pattern replacement, mute/reset routes, other MIDI tracks, editable settings and persistent storage remain untested.','A separate native-input live test also passed: C E G were played as an ascending arp, all three source keys were released, and the active G ended 5.33 ms after the release request. No further notes appeared during the following 480 ms. Sustain, partial release, pattern replacement, mute/reset routes, other MIDI tracks, editable settings and persistent storage remain untested.')
text=text.replace('## What remains','## Live key-release control\n\nThree native MIDI note-ons created the held C E G set. Three native note-offs removed it. This control ran while transport was stopped, so held-note admission did not depend on playback being active. Live source gate zero means held, and the prototype uses an explicit positive step-rate fixture rather than dividing that zero gate.\n\nThe first prototypes exposed and corrected two model errors: using half the MIDI timestamp clock and treating a held source gate as an arp rate. These were prototype errors, not changes to E07.\n\n## What remains')
text+='\n- [Live release MIDI]('+str(mid.resolve()).replace('\\','/')+')\n- [Combined four-case results]('+str(Path('outputs/Digitone-E08-M1-prototype-results.json').resolve()).replace('\\','/')+')\n';readme.write_text(text,encoding='utf-8')
print('PASS: four cases; native live release delay',r['verified_case']['final_key_release_to_note_off_ms'],'ms; E07 unchanged')
