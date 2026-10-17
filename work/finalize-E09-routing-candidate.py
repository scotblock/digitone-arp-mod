"""Freeze tested routing-only E09; MIDI-track expansion remains investigation."""
from pathlib import Path
import json,hashlib,sys
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from dt2.container import sections
names=['Digitone-E09-stock-output-fanout.json','Digitone-E09-PC-dual-port-mirror.json','Digitone-E09-PC-dual-port-ISA.json',
 'Digitone-E09-M1-both-ports.json','Digitone-E09-synth-both-ports.json','Digitone-E09-PC-container-verification.json',
 'Digitone-E09-packed-loader.json','Digitone-E09-PC-startup-comparison.json','Digitone-E09-reset-refusal.json',
 'Digitone-E09-packaged-M1-both-ports.json','Digitone-E09-packaged-synth-both-ports.json','Digitone-E09-four-track-sequencer-audit.json']
checks={n:json.loads(Path('outputs',n).read_text()) for n in names}
assert all(x.get('passed') for x in checks.values())
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(Path('outputs/Digitone_OS1.44E08F_M1_ARP_MENU_FIX_PC_ONLY.syx').read_bytes())=='085ef1cae6d22878da74acf4a756dd9a22389971f211208e9bd67ff349e146f8'
old=Path('work/os144/E08F-PC-layout-payload.bin').read_bytes();new=Path('work/os144/E09-PC-layout-payload.bin').read_bytes()
dual=json.loads(Path('work/os144/E09-PC-dual-port-layout.json').read_text())
allowed=set()
for r in dual['patches']:allowed.update(range(r['base']-dual['base'],r['base']-dual['base']+r['bytes']))
assert all(i in allowed for i,(a,b) in enumerate(zip(old,new)) if a!=b)
for name in ['M1_SYN2_open','mark_M1_view']:
 cfg=json.loads(Path('work/os144/E08F-PC-install-layout.json').read_text());r=next(r for r in cfg['regions'] if r['name']==name);o=r['base']-cfg['base'];assert old[o:o+r['bytes']]==new[o:o+r['bytes']]
path=Path('outputs/Digitone-E09-PC-path-layout.json');layout=json.loads(path.read_text())
container,_=sections(Path(layout['candidate']));layout.update(container_bytes=len(container),syx_bytes=Path(layout['candidate']).stat().st_size);layout.pop('codec_roundtrip',None);path.write_text(json.dumps(layout,indent=2))
source=Path(layout['candidate']);dest=Path('outputs/Digitone_OS1.44E09_DUAL_PORT_ARP_PC_ONLY.syx');dest.write_bytes(source.read_bytes())
synth=checks['Digitone-E09-packaged-synth-both-ports.json'];midi=checks['Digitone-E09-packaged-M1-both-ports.json']
assert synth['helpers_host_loaded'] is False and synth['extra_USB_state_host_initialized'] is False
out={'passed':True,'PC_only':True,'hardware_ready':False,'device_update_performed':False,'candidate':str(dest.resolve()),
 'sha256':sha(dest.read_bytes()),'bytes':dest.stat().st_size,'parent_build':'E08F',
 'synth_matching_note_pairs_per_port':synth['matching_note_pairs'],'M1_matching_note_pairs_per_port':midi['matching_note_pairs'],
 'payload_bytes':len(new),'added_payload_bytes':len(new)-len(old),'added_USB_owner_state_bytes':160,
 'owner_driver_cases':len(checks['Digitone-E09-PC-dual-port-mirror.json']['cases']),
 'implemented':['Synth arp follows the DIN/USB/both output mask, with independent pending release ownership on each port.','Existing M1 stock output fanout verified on both ports.'],
 'not_implemented':['M2–M4 arps','MIDI arp step editor','New project step-storage schema'],
 'checks':names,'limits':['USB endpoint acceptance/readiness and queue failures use fixtures. Physical host delivery, cache behavior, timing and added RAM ownership are unverified.','Arp/pattern fields and routing/input gates in the continuous synth test include disclosed fixtures.','The added USB sidecar is copied at startup and protected in the tested reset refusals; arbitrary lifetime/exception paths are not certified.','Normal sequencer-driven MIDI chord behavior and project persistence are separate gaps.']}
Path('outputs/Digitone-E09-routing-review.json').write_text(json.dumps(out,indent=2))
Path('outputs/Digitone-E09-routing-and-next-features.md').write_text(f'''# E09 — DIN + USB arp routing (PC candidate)

17 October 2026. E08F remains the preserved user-reported working baseline. E09 is a separate PC/Digiemu candidate; no tool transmitted firmware or updated the Digitone.

## Routing change

Both arp types follow the normal output selection: DIN MIDI, USB MIDI, or both. Enable both outputs when testing both connections. A USB cable is not required for DIN operation. The M1 arp already uses the stock MIDI-track fanout; the synth arp mirror previously bypassed it and wrote only to DIN.

The synth mirror now has independent DIN and USB voice ownership. If the output channel/selection changes during a held note, each accepted output keeps its original release destination. A full/unavailable port does not prevent the other from operating. Pending note-offs retry only on their own port. Shared synth voices still emit one note pair per port. The working E08F menu corrections are byte-for-byte preserved.

The candidate adds {len(new)-len(old):,} copied bytes, including 160 bytes of USB owner state, inside the proposed reservation. This is not proof of physical ownership of the expanded region.

## PC evidence

The actual stock fanout and drivers passed the off/DIN/USB/both matrix. Seventeen native ownership/driver cases cover channel/route changes, shared voices, blocked ports, USB disconnect, pool exhaustion/busy descriptors, endpoint rejection, pending note-off retries and USB buffer wrap. The native USB packetizer, descriptor allocator and failure cleanup execute; endpoint acceptance is a fixture.

The packaged loader reaches MAIN, native copying/initialization reaches the UI, and nine stopped diagnostic/reset cases preserve the complete watched payload, including a pending USB-owner fixture. On the packaged startup state, continuous synth playback produces **{synth['matching_note_pairs']} matching note pairs on each port**, and M1 produces **{midi['matching_note_pairs']} matching pairs**. No routing helper is host-loaded in these final packaged checks. These are data/pairing results, not physical USB delivery or timing measurements.

## M2–M4 investigation

The actual stock MIDI handle getter was executed for all four tracks. Each has a separate parameter record and output channel. The extension currently hardcodes M1's handle, cache slot, settings owner and one scheduler/arena. Broadening the menu predicate alone would share held notes, timing and settings incorrectly.

The next implementation needs four independent held/sustain sets, rate/gate/step cursors, source/request owners and retiring event arenas. At the current sizes, three extra states/arenas would add at least 1,224 bytes before step data. The UI must bind to the page's intended MIDI track and preserve all ordinary menus. Stop must retire all four tracks; releasing one must leave the others playing. These features are **not added in E09**.

## Synth-style MIDI arp sequencer

Two separate behaviors need coverage: ordinary pattern chord trigs feeding the arp, and an arp editor with programmable pitch offsets, rests and sequence length. A 16-step editor needs at least 19 new saved bytes per MIDI track (16 signed offsets, a 16-bit enable/rest mask and one length byte), before metadata/versioning. The existing two-byte MODE/RATE/GATE tag cannot hold that sequence.

New owned serialized storage, native save/load/import handling and per-track editor accessors are required. Reusing synth arp callbacks would repeat the earlier synth-T4 alias problem; taking CC fields would displace existing MIDI features. Pitch-offset semantics and MIDI root/scale access also need explicit validation before claiming E06-style scale degrees. No MIDI step editor or new saved-project schema is implemented in E09.

## Next checks

Use Digiemu first to check both output paths and the unchanged menus. Physical dual-port recording remains outstanding. Continue with sequenced MIDI chord production/context capture before implementing M2–M4, then add the step editor and saving as a separate change. The generated test project remains a draft; this routing change does not certify its import or settings persistence.

File: `{dest.name}`. SHA-256: `{out['sha256']}`.
''',encoding='utf-8')
print(json.dumps(out,indent=2))
