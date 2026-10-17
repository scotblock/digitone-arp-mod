"""Freeze only after the concrete PC menu/package/playback checks pass."""
from pathlib import Path
import json,hashlib
read=lambda p:json.loads(Path(p).read_text())
names=['Digitone-E08E-PC-menu-fix-contracts.json','Digitone-E08E-PC-menu-panel.json',
 'Digitone-E08E-PC-menu-frame-comparison.json','Digitone-E08F-PC-container-verification.json',
 'Digitone-E08F-packed-loader.json','Digitone-E08F-PC-startup-comparison.json',
 'Digitone-E08F-packaged-menu-panel.json','Digitone-E08F-packaged-panel-playback.json']
checks={n:read('outputs/'+n) for n in names}
assert all(c.get('passed') for c in checks.values())
r=checks[names[-1]];status=None;pending=[];active={};ons=[];offs=[]
for e in r['wire']:
    for b in e['bytes']:
        if b>=0xf8:continue
        if b&128:status=b;pending=[];continue
        assert status is not None
        pending.append(b)
        if len(pending)!=(1 if status&0xf0 in [0xc0,0xd0] else 2):continue
        if status&0xf0 in [0x80,0x90]:
            key=status&15,pending[0]
            if status&0xf0==0x90 and pending[1]:
                assert key not in active,(key,e)
                active[key]=e;ons.append({'phase':e['phase'],'note':pending[0],'channel':key[0]+1})
            else:assert key in active,(key,e);active.pop(key);offs.append(key)
        pending=[]
assert not active and len(ons)==len(offs) and len(ons)>=12
assert [e['note'] for e in ons if e['phase']=='OFF_chord']==[60,64,67]
for phases in [{'UP_start','UP_1_32_gate80','tempo_plus400_1_32','tempo_minus800_1_32'},{'UP_second','UP_1_16_gate50'}]:
    notes=[e['note'] for e in ons if e['phase'] in phases]
    assert len(notes)>=6 and notes==([60,64,67]*((len(notes)+2)//3))[:len(notes)],notes
old=Path('work/os144/E08E-PC-layout-payload.bin').read_bytes()
new=Path('work/os144/E08F-PC-layout-payload.bin').read_bytes()
fix=read('work/os144/PC_ONLY-E08E-menu-fix-layout.json')
allowed=set()
for reg in fix['regions']:allowed.update(range(reg['base']-fix['base'],reg['base']-fix['base']+reg['span']))
changed=[i for i,(a,b) in enumerate(zip(old,new)) if a!=b]
assert len(old)==len(new) and set(changed)<=allowed
native=read('work/os144/E08F-PC-install-layout.json')
before=Path('work/os144/E08E-PC-layout-main.bin').read_bytes();after=Path('work/os144/E08F-PC-layout-main.bin').read_bytes()
off=native['copy_source']-0x40000400
assert before[:off]==after[:off] and after[off:]==new
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(Path('outputs/Digitone_OS1.44E08E_M1_ARP_PC_ONLY.syx').read_bytes())=='74219ea223999ae190f5c935973b96bf67eea60148416a1009565af6f48dd3a3'
source=Path('work/os144/E08F-PC-path-candidate.syx');dest=Path('outputs/Digitone_OS1.44E08F_M1_ARP_MENU_FIX_PC_ONLY.syx')
dest.write_bytes(source.read_bytes())
out={'PC_only':True,'passed':True,'hardware_ready':False,'device_update_performed':False,
 'candidate':str(dest.resolve()),'sha256':sha(dest.read_bytes()),'bytes':dest.stat().st_size,
 'parent':'E08E','changed_payload_bytes':len(changed),'changes_limited_to_two_UI_helpers':True,
 'payload_size_unchanged':True,'RAM_state_and_arena_unchanged':True,
 'MIDI_note_ons':len(ons),'matched_note_offs':len(offs),'checks':names,
 'limits':['No physical cache/timing/RAM ownership certification.','M1 live-input playback repeated; internal MIDI sequencer-chord/project persistence gaps are not closed by this menu fix.','No new physical device test or installation occurred.']}
Path('outputs/Digitone-E08F-menu-fix-review.json').write_text(json.dumps(out,indent=2))
Path('outputs/Digitone-E08F-menu-fix-notes.md').write_text('''# E08F menu correction — PC candidate

16 October 2026. For original Digitone / Digitone Keys OS 1.44. This is a Digiemu/PC candidate, not a hardware-certified release. No firmware has been transmitted to the Digitone.

## What changed

E08E replayed a stock page-selection instruction with the wrong offset: -14 instead of -20. Ordinary page buttons therefore selected pages six positions too far along. This explains the reported effects pages before any generated test project was loaded.

E08F restores the stock offset. It also limits custom page opening and marking to M1 with FUNC + SYN2. Bare SYN2 follows stock behavior. Synth arp pages and other MIDI tracks keep their stock routing. MODE, RATE and GATE remain on the custom M1 page.

Only the two menu helpers changed within the existing payload. Payload length, RAM state, arena, initialization, arp processing and Stop/release helpers are unchanged. E08E, E07 and stock recovery files remain preserved. The OS version display remains 1.44; identify this build by its filename and SHA-256.

## What passed on the PC

- 96 isolated routing cases and 96 marker cases across all eight selected tracks, six page buttons and both modifier states, including nonzero upper register bytes.
- Actual panel checks on M1, M2 and T1. All 18 normal menu bodies match stock; 15 full frames match exactly, with transient differences confined to the title/status strip in the other three frames in the shorter UI-only run.
- The M1 custom shortcut, M2's stock effects shortcut, synth arp opening, return to M1 Source and synth arp opening after closing the custom page.
- Independent SysEx framing, checksums, padding and exact MAIN decompression. Non-MAIN sections remain stock.
- Loader-derived MAIN entry, native copying/initialization and startup to the UI, followed by menu execution without host-loading the corrected helpers.
- The repeated live M1 panel/playback test, with balanced MIDI note-ons/note-offs, release, MODE/RATE/GATE edits and tempo changes.

The first attempted broad panel test failed because it entered the M1 shortcut while still in an effects page. A focused trace showed the modifier byte and corrected shortcut worked from normal MIDI pages. The final panel test establishes a normal page before each shortcut and checks return/re-entry explicitly. This distinction is retained; arbitrary starting-page shortcut behavior is not claimed.

## Try in Digiemu

Add Digitone_OS1.44E08F_M1_ARP_MENU_FIX_PC_ONLY.syx as a separate firmware entry. Confirm TRIG opens Trig Parameters, SYN1 opens MIDI Source, FLTR opens CC Value, AMP opens CC Select and LFO opens its LFO page on M1. Bare SYN2 follows the stock MIDI source-page behavior. Then try FUNC + SYN2 from an ordinary MIDI parameter page: it should open M1 MIDI ARP. Press NO, then SYN1 to return to MIDI Source. Check a synth track's normal arp page too.

M2–M4 arps are not implemented. The generated project's full settings persistence and sequenced MIDI chord playback gaps remain separate. This menu correction does not certify physical timing, cache coherence, exclusive RAM/DMA ownership or arbitrary reset/input overlap, and is not a request to flash the device.

'''+f"SHA-256: `{out['sha256']}`. Size: {out['bytes']:,} bytes. Live test: {len(ons)} note-ons / {len(offs)} matched note-offs.\n",encoding='utf-8')
print(json.dumps(out,indent=2))
