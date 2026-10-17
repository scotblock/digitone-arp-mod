from pathlib import Path
import json,struct,hashlib

path=Path('outputs/Digitone-E08-M1-native-playback.json')
r=json.loads(path.read_text())
assert r['failure'] is None and r['halted'] is None
assert r['MIDI_received']==r['MIDI_delivered']
assert r['native_initialization_executed'] and r['native_code_preserved']

def vl(n):
    parts=[n&127];n>>=7
    while n:parts.insert(0,(n&127)|128);n>>=7
    return bytes(parts)

cases=[]
for phase in r['phases']:
    active={};ons=[];offs=[]
    track=bytearray(b'\x00\xff\x51\x03\x07\xa1\x20');last=0
    for event in phase['wire']:
        assert len(event['bytes'])%3==0
        for i in range(0,len(event['bytes']),3):
            packet=event['bytes'][i:i+3];status,note,velocity=packet
            assert status&240 in [128,144]
            key=(status&15,note)
            if status&240==144 and velocity>0:
                assert key not in active
                active[key]=event['ms'];ons.append({'ms':event['ms'],'note':note})
            else:
                assert key in active
                start=active.pop(key);offs.append({'ms':event['ms'],'note':note,'gate_ms':event['ms']-start})
            tick=round((event['ms']-phase['begin_ms'])*.96)
            track+=vl(tick-last)+bytes(packet);last=tick
    assert not active and not phase['active_scheduler_at_end'] and phase['arena_busy_at_end']==0
    notes=[x['note'] for x in ons];name=phase['phase']
    if name=='UP_live_release':
        assert notes==[60,64,67] and phase['native_held_count_at_end']==0
        assert phase['native_counters'][3]==1
        assert ons[-1]['ms']<phase['release_request_ms']<offs[-1]['ms']<phase['release_request_ms']+40
        assert offs[-1]['gate_ms']<50 and phase['end_ms']-offs[-1]['ms']>400
    else:
        caps=[x for x in r['captures'] if x['phase']==name]
        assert caps and all(sorted(x['notes'])==[60,64,67] for x in caps)
        if name=='OFF':
            assert notes==[60,64,67] and max(x['ms'] for x in ons)-min(x['ms'] for x in ons)<2
        else:
            assert len(notes)>=(6 if name=='UP_release' else 2)
            assert notes==([60,64,67]*((len(notes)+2)//3))[:len(notes)]
            assert all(b['ms']>a['ms'] for a,b in zip(ons,ons[1:]))
            assert all(0<x['gate_ms']<120 for x in offs)
            if name=='UP_release':
                assert phase['native_counters'][1]==1
                assert max(x['ms'] for x in ons)<phase['stop_request_ms']-150
            else:
                assert phase['native_counters'][2]==1
                assert ons[-1]['ms']<phase['stop_request_ms']<=offs[-1]['ms']<phase['stop_request_ms']+80
                assert all(x['ms']<phase['stop_request_ms']+80 for x in ons)
    track+=b'\x00\xff\x2f\x00'
    mid=Path('outputs',f'Digitone-E08-M1-{name}-NATIVE-PC.mid')
    mid.write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,480)+b'MTrk'+struct.pack('>I',len(track))+track)
    cases.append({'phase':name,'notes':notes,'note_on_count':len(ons),'note_off_count':len(offs),'no_hanging_notes':True,'ons':ons,'offs':offs,'MIDI_file':str(mid.resolve()),'passed':True})

assert len(cases)==4
sha=hashlib.sha256(Path('outputs/Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx').read_bytes()).hexdigest()
assert sha=='a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'
contract=json.loads(Path('outputs/Digitone-E08-M1-native-contracts.json').read_text())
layout=json.loads(Path('work/os144/E08-PC-native-M1-layout.json').read_text())
assert contract['passed']
limits=[
    'Sorting, capture, step selection, held-note state, descriptor construction and retirement execute ColdFire instructions; Python only supplies disclosed inputs/configuration and observations.',
    'Host loads extra code/state in disposable PC RAM and calls the native initializer in a temporary frame; no loader-to-copier/startup installation.',
    'Finite chord source gate is extended eight times by a disclosed equal fixture in OFF and UP cases.',
    'Step interval/output gate are explicit positive configuration fixtures; general tempo synchronization, settings UI and persistence are unresolved.',
    'M1 only. Sustain, partial release, mute/reset, pattern handoff, channel collisions and other tracks remain unverified.',
    'No hardware ownership/cache/timing proof or flashable E08 candidate.'
]
r.update(passed=True,verified_cases=cases,E07_unchanged_sha256=sha,limits=limits)
path.write_text(json.dumps(r,indent=2))
summary={'PC_only':True,'passed':True,'firmware_unchanged':True,'installable_E08_produced':False,'native_scheduler':True,'code_bytes':layout['code_bytes'],'state_bytes':layout['state_bytes'],'arena_bytes':layout['arena_bytes'],'isolated_contract_groups':contract['groups'],'continuous_cases':4,'cases':cases,'E07_sha256':sha,'limits':limits}
dest=Path('outputs/Digitone-E08-M1-native-results.json');dest.write_text(json.dumps(summary,indent=2))
text="""# E08 M1 native machine-code prototype

The M1 scheduler now executes as ColdFire instructions in the PC engine. Python no longer sorts notes, chooses steps, constructs generated descriptors or bypasses retirement. The native consumer hook, scheduler and retirement hook perform those operations. E07 is unchanged; no installable E08 was produced.

Code loading and configuration remain explicit PC fixtures. The native initializer clears and seeds the additional state in a temporary call frame; it is not connected to the firmware startup copier. This placement is outside E07's copied payload and is not certified for hardware.

## Results

"""
for c in cases:text+=f"- {c['phase']}: {c['note_on_count']} note-ons / {c['note_off_count']} matching note-offs; {c['notes']}; no hanging notes.\n"
text+=f"\n{contract['groups']} isolated native contract groups passed: initialization, sorting/dedup, finite expiry, arena busy preflight, transport stop, live zero-gate sources and actual release descriptors, invalid timing configs, invalid notes, M2 bypass, eight-note bounds, clock wrap, consumer register preservation and ordinary retirement. All custom regions passed the retained strict ColdFire instruction checks.\n"
text+="""
## Descriptor ownership

The helper snapshots value fields and clears borrowed pointer/link fields in the retained template. One busy-guarded temporary descriptor links back to the original native descriptor. Its exact-pointer retirement hook clears busy and prevents the private descriptor entering the stock free list. Ordinary descriptors retain the stock push/free path. The continuous run ends with busy clear and all notes retired, and verifies native code remains unchanged in memory.

This proves bounded behavior of the PC-owned arena in these controls. It does not establish exclusive ownership of that address on hardware or coverage of every callback/reset route.

## Remaining integration

The overlay uses 1,096 code bytes, 320 state bytes and a 64-byte descriptor arena. E07's existing padding plan has only 340 fragmented bytes free, so this layout cannot simply be inserted there. A placement/copying/initialization design is still needed before packaging.

Step interval and output gate are positive configuration fixtures; live source gate zero means held, not an arp rate. Tempo synchronization, settings UI/persistence, sustain, partial release, pattern replacement, mute/reset, channel collisions and M2–M4 remain unresolved.

Next: derive the rate/gate settings from stock MIDI timing and establish an installation layout before a flashable candidate. Keep M1 scope until that integration is verified.

## Artifacts

"""
for c in cases:text+='- ['+Path(c['MIDI_file']).name+']('+c['MIDI_file'].replace('\\','/')+')\n'
text+='- [Combined results]('+str(dest.resolve()).replace('\\','/')+')\n'
Path('outputs/Digitone-E08-M1-native-prototype.md').write_text(text,encoding='utf-8')
print('PASS',[(c['phase'],c['notes'],c['note_off_count']) for c in cases])
