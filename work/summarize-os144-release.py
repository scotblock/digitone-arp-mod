import json,hashlib
from pathlib import Path
def load(name):return json.loads(Path('outputs/'+name+'.json').read_text())
a=load('Digitone-OS1.44-release-guards');b=load('Digitone-OS1.44-release-no-handoff')
assert a['failure'] is None and b['failure'] is None
f=a['delayed_queue_fixture'];assert f==b['delayed_queue_fixture']
def lifetime(r):return [e for e in r['events'] if e.get('event')==f['event'] and e.get('generation')==f['generation']]
la,lb=lifetime(a),lifetime(b)
assert not any(e['kind'] in ('acceptance','pitch') for e in la)
assert any(e['kind']=='acceptance' for e in lb)
pitch=next(e for e in lb if e['kind']=='pitch');assert pitch['coarse_pitch']==59
calls=a['invalidation_calls'];assert [x['arguments'][1] for x in calls]==list(range(8))
assert calls[3]['before_fields'][3]==1 and calls[4]['before_fields'][3]==0xffffffff
assert all(x['return_to']=='0x40100164' for x in calls)
release=a['target_release'];control_release=b['target_release']
assert release['fields'][3]==0xffffffff and control_release['fields'][3]==1
assert release['fields'][:3]==f['original_fields'][:3] and release['fields'][4:]==f['original_fields'][4:]
assert control_release['fields']==f['original_fields']
writes=[w for w in a['target_writes'] if w['ms']<release['ms']]
assert len(writes)==1 and writes[0]['offset']==12 and writes[0]['pc']=='0x40093656' and writes[0]['value']=='0xffffffff'
assert not any(w['offset']==12 and w['ms']<control_release['ms'] for w in b['target_writes'])
path=[x['pc'] for x in a['consumer_branches']]
assert path==['0x4009d480','0x4009d570','0x4009d760','0x4009d762','0x4009d766','0x4009d76a','0x4009d76c','0x4009d7d8','0x4009d7de']
guards=[g for g in a['cancel_guard_points'] if g['pc']=='0x40095ba2']
assert len(guards)==8 and all(g['active_pattern']=='0x407fd414' and g['alternate_pattern']=='0x40813531' and g['guard_byte']=='00' for g in guards)
assert all(g['stack_words'][1]==0x4009363c for g in guards)
hashes={}
for version,path,expected in [('1.44','inputs/Digitone_and_Digitone_Keys_OS1.44.syx','d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'),('1.42','inputs/Digitone_and_Digitone_Keys_OS1.42.syx','0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda')]:
 hashes[version]=hashlib.sha256(Path(path).read_bytes()).hexdigest();assert hashes[version]==expected
summary={'firmware_modified':False,'custom_context_hooks_connected':False,'specific_release_decision_closed':True,'fixture_identical_in_controls':True,'fixture':f,'handoff_cancel':{'writer':writes[0],'guard_points':guards,'track_callback_calls':calls,'consumer_path':a['consumer_branches'],'release':release},'no_handoff_control':{'invalidation_calls':b.get('invalidation_calls',[]),'pitch':pitch,'release':control_release,'playing_pattern_changed':b['actual_playing_handoff']},'explanation':'A stock track-filtered future-queue scan sets event +0x0c to -1. The consumer compares this field to -1 and branches directly to release, bypassing note acceptance/pitch. In this observed case the scan is reached through active/alternate pattern pointer mismatch and a zero guard byte after handoff. The identical delayed event without handoff reaches pitch 59.','hooks_requirement':'Preserve this upstream cancellation gate; metadata must not reactivate cancelled events.','remaining_limits':['This explains the one captured type-0 note and its controls, not all queue types or all replacement paths.','The generic cancellation callback also handles type 3; that type was inspected statically but not the target in these tests.','Future-queue timestamp delay and MIDI enable remain disclosed PC fixtures.','The same published event is matched across controls, but later CPU phases are not required to be identical and timings are not hardware measurements.','Tracked memory writes after release include subsequent allocation clearing before the generation counter increments; those writes are excluded from old-event ownership evidence.','Uncancelled old-pattern notes retaining custom scale context across replacement remain unverified; helpers were not connected.','Physical timing, cache coherence, and exhaustive storage ownership remain unverified.'],'firmware_hashes_after':hashes,'next_step':'Port the 1.44 context capture and pitch helper contracts in isolated PC tests, retaining stock +0x0c cancellation. Separately establish an uncancelled eligible queued-note path before claiming old-scale retention across replacement.'}
Path('outputs/Digitone-OS1.44-release-decision-summary.json').write_text(json.dumps(summary,indent=2))
change=next(e for e in a['events'] if e['kind']=='pattern_pointer_write' and e['ms']>1000)
doc=f'''# OS 1.44 delayed-note release decision

The specific release is explained by an executed stock cancellation path. It is not evidence of a damaged event or an allocator failure. The same stock-produced delayed event reaches acceptance and pitch output when the pattern is kept unchanged. No custom context hooks were connected, and both source firmware hashes were checked unchanged.

## Captured chain

The event is `{f['event']}`, allocation generation {f['generation']}, type 0, track 3. It is published at {f['publication_ms']:.6f} emulated ms with `+0x0C = 1` and a non-null descriptor at `+0x38`. Only its queue timestamp is delayed by the disclosed PC fixture.

1. Stock writes the receiving pattern pointer at {change['ms']:.6f} ms: `0x40813531` becomes `0x407fd414`.
2. At {writes[0]['ms']:.6f} ms, the preparation path compares the alternate pattern pointer at `0x4138f21c` with active pointer `0x4138f214`. They differ. Its byte guard through A4 is zero, so the executed path reaches `0x40095ba2`, calling the future-queue visitor `0x40100118` with callback `0x4009363c` and a track index.
3. The visitor calls that callback for tracks 0 through 7. The callback accepts event types 0 or 3, compares event `+0x08` with its track argument, and writes `-1` into `+0x0C` at `0x40093656` when they match. The observed target is type 0, track 3: calls for tracks 0–2 leave it unchanged, track 3 invalidates it, and later calls observe the invalid value. This scan is supervisor interrupt-masked in its stock implementation.
4. At {release['ms']:.6f} ms, the render consumer reaches the note dispatch at `0x4009d760`. It reads `+0x0C`, compares it with `0xFFFFFFFF` at `0x4009d76a`, and takes the equality branch at `0x4009d76c` to `0x4009d7d8`. That path calls release at `0x4009d7de`, returning to `0x4009d7e4`. It bypasses the acceptance and pitch sites.

The invalidation changes only `+0x0C` before release; the recorded descriptor, flags and other event fields retain their published values. The event is not silently reused before this decision. Memory-watch records from later allocation clearing are excluded from this event's lifetime: the generation probe runs after those clear stores, so its counter alone must not attribute them to the still-live old note.

## Unchanged-pattern control

The control suppresses the playing pattern-change request while preserving the stopped pattern-2 setup, delayed timestamp and MIDI sustain scenario. Its published event fixture is exactly identical: same address, allocation generation, publication time, timestamp, original fields and source pattern backing.

Without replacement, the target receives no invalidation callback or `+0x0C` invalidation write. It retains `+0x0C = 1`, reaches stock acceptance and pitch output at {pitch['ms']:.6f} ms, and produces coarse pitch {pitch['coarse_pitch']}. Its later release is normal cleanup after processing, not the rejection observed with replacement. Subsequent scheduling phases differ; these times are functional emulator observations, not physical timing measurements.

Sustain is independent evidence: the retained MIDI sustain-list object is a different object from this queued event. Pedal state/list persistence does not mean the cancelled arp event should be played.

## Consequence for V1

The proposed context handling must preserve stock cancellation. A saved root/scale must never reactivate a note that stock has marked `-1`. Our producer/context and pitch hooks should retain the original consumer's eligibility gate and release behavior.

This closes the cause of this particular failed replay. It does **not** prove that every queued note is cancelled on every pattern change, or that an eligible old-pattern note can retain custom scale context across a replacement. The callback's other types, other guards and alternate producer/copy routes still need their own coverage.

Next, adapt the 1.44 helper contracts in isolated PC tests while preserving this gate. Separately find an uncancelled eligible queue path before claiming old-scale retention across replacement. Physical timing, cache coherence and complete reserved-memory ownership remain unverified.

Evidence: `Digitone-OS1.44-release-guards.json`, `Digitone-OS1.44-release-no-handoff.json`, and `Digitone-OS1.44-release-decision-summary.json` beside this report. Traces and helpers are PC-only; neither stock firmware file was modified and no flashable image was produced.
'''
Path('outputs/Digitone-OS1.44-release-decision.md').write_text(doc)
print('PASS: identical published-event controls; handoff invalidation gate and release branch traced; no-handoff acceptance and pitch 59 verified; source firmware unchanged.')
