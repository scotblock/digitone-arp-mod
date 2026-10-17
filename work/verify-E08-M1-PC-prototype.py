from pathlib import Path
import json,struct,hashlib
p=Path('outputs/Digitone-E08-M1-PC-prototype.json');r=json.loads(p.read_text())
assert r['failure'] is None and r['halted'] is None,(r['failure'],r['halted'])
assert r['MIDI_received']==r['MIDI_delivered']
def vl(n):
 parts=[n&127];n>>=7
 while n:parts.insert(0,(n&127)|128);n>>=7
 return bytes(parts)
results=[]
for phase in r['phases']:
 active={};ons=[];offs=[];events=[];last=0;track=bytearray(b'\x00\xff\x51\x03\x07\xa1\x20')
 packets=[]
 for ev in phase['wire']:
  assert len(ev['bytes'])%3==0,ev
  packets += [{'ms':ev['ms'],'bytes':ev['bytes'][i:i+3]} for i in range(0,len(ev['bytes']),3)]
 for ev in packets:
  packet=ev['bytes']
  status,note,vel=packet;assert status&240 in (128,144),packet
  key=(status&15,note);is_on=status&240==144 and vel>0
  if is_on:
   assert key not in active,(phase['phase'],'duplicate note',key)
   active[key]=ev['ms'];ons.append({'ms':ev['ms'],'note':note,'velocity':vel,'channel':(status&15)+1})
  else:
   assert key in active,(phase['phase'],'orphan note-off',key)
   start=active.pop(key);offs.append({'ms':ev['ms'],'note':note,'gate_ms':ev['ms']-start})
  tick=round((ev['ms']-phase['begin_ms'])*.96);track+=vl(tick-last)+bytes(packet);last=tick
 assert not active and not phase['active_scheduler_at_end'],(phase['phase'],active)
 notes=[x['note'] for x in ons]
 caps=[x for x in r['captures'] if x['phase']==phase['phase']]
 assert caps and all(sorted(x['notes'])==[60,64,67] for x in caps),(phase['phase'],caps)
 if phase['phase']=='OFF':
  assert notes==[60,64,67],notes
  assert max(x['ms'] for x in ons)-min(x['ms'] for x in ons)<2
 else:
  assert len(notes)>=(6 if phase['phase']=='UP_release' else 2) and notes==[60,64,67]*(len(notes)//3)+[60,64,67][:len(notes)%3],notes
  assert all(b['ms']>a['ms'] for a,b in zip(ons,ons[1:]))
  assert all(x['gate_ms']>0 and x['gate_ms']<120 for x in offs),offs
  cancels=[x for x in r['cancellations'] if x['phase']==phase['phase']]
  if phase['phase']=='UP_release':
   assert len(notes)>=6 and any(x['reason']=='source_gate_expired' for x in cancels),cancels
   assert max(x['ms'] for x in ons)<phase['stop_request_ms']-150
  else:
   assert any('stop' in x['reason'] for x in cancels),cancels
   assert ons[-1]['ms']<phase['stop_request_ms']<offs[-1]['ms'],(phase['stop_request_ms'],ons[-1],offs[-1])
   assert offs[-1]['ms']<phase['stop_request_ms']+80
   assert all(x['ms']<phase['stop_request_ms']+80 for x in ons)
 track+=b'\x00\xff\x2f\x00';mid=Path('outputs',f"Digitone-E08-M1-{phase['phase']}-PC.mid");mid.write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,480)+b'MTrk'+struct.pack('>I',len(track))+track)
 results.append({'phase':phase['phase'],'note_on_count':len(ons),'note_off_count':len(offs),'notes':notes,'ons':ons,'offs':offs,'no_hanging_notes':True,'MIDI_file':str(mid.resolve()),'passed':True})
sha=hashlib.sha256(Path('outputs/Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx').read_bytes()).hexdigest();assert sha=='a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'
r['verified_cases']=results;r['passed']=True;r['E07_unchanged_sha256']=sha
r['limits']=['Host Python implements sorting, state, admission, expiry and step scheduling; no guest machine-code arp helper is tested here.','Host installs a disposable descriptor arena at 0x47be6000 and bypasses stock freeing for that arena only; storage ownership is not established for hardware.','Native MIDI input/grid recording creates the source chord. A disclosed source-gate fixture multiplies the native gate by eight in all three cases.','The native firmware performs channel/transpose/output, gate scheduling, MIDI packet production and stop flushing. No outgoing note packets are injected by the host.','Release case means finite sequencer source-gate expiry; sustained live keyboard release, mute, replacement, resets and other tracks remain untested.','Tick polling gives timing granularity; native tempo-derived gate values are used, but physical timing and cache/DMA behavior are not validated.','No new firmware or modification to E07; prototype is not installable.']
p.write_text(json.dumps(r,indent=2));print([(x['phase'],x['notes'],len(x['offs'])) for x in results])
text='''# E08 M1 ascending arp — PC behavior prototype

This is a host-assisted PC prototype, not an installable firmware build. E07 is unchanged.

The firmware's native MIDI input and grid-recording path creates a C–E–G trig on M1. The source hold is extended to eight native default gates through a disclosed test fixture. In OFF mode, the stock firmware sends the three-note chord unchanged. In UP mode, a Python scheduler snapshots and sorts the chord and supplies one-note descriptors to the stock MIDI task. The firmware handles MIDI output, transposition/channel selection, timed note-offs and stop cleanup. The host does not inject outgoing packets.

## Results

'''
for x in results:text+=f"- {x['phase']}: {x['note_on_count']} note-ons, {x['note_off_count']} matching note-offs; notes {x['notes']}; no hanging notes.\n"
text+='''
UP_release stops generating when the finite source gate expires, before the later STOP request. UP_stop interrupts an active cycle through the native transport/stop path. The step order is C E G repeated. These tests use one continuous guest session and the same native recorded chord.

## What remains

The scheduler and state management must be ported to actual ColdFire helpers before this is a firmware implementation. The temporary PC descriptor arena and retirement bypass are harness mechanisms, not a verified allocation strategy. Live held-note release and sustain, pattern replacement, mute/reset routes, other MIDI tracks, editable settings and persistent storage remain untested. E07's existing 340 bytes of fragmented padding are not assumed sufficient.

Next: execute the scheduler as machine code in isolated PC tests and connect it to the MIDI task with explicit descriptor ownership, then test live release and pattern cancellation. No E08 flashable file is produced.

## Artifacts

'''
for x in results:text+='- ['+Path(x['MIDI_file']).name+']('+x['MIDI_file'].replace('\\','/')+')\n'
text+='- [Detailed results]('+str(p.resolve()).replace('\\','/')+')\n'
Path('outputs/Digitone-E08-M1-PC-prototype.md').write_text(text,encoding='utf-8')
