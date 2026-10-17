from pathlib import Path
import json,hashlib
path=json.loads(Path('outputs/Digitone-E08-loader-startup-playback-results.json').read_text())
menu=json.loads(Path('outputs/Digitone-E08-stock-menu-bypass.json').read_text())
assert menu.get('failure') is None and menu['halted'] is None
lookups=[x for x in menu['sound_lookups'] if x['phase'] in ['arp_menu','arp_mode']]
assert lookups and all(x['requested_index']==4 for x in lookups)
assert all(int(x['sound_handle'],16)==int(x['base'],16)+0x60+3*0x328 for x in lookups)
e07=Path('outputs/Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx')
assert hashlib.sha256(e07.read_bytes()).hexdigest()=='a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'
summary={**path,'stock_arp_menu_bypass':{'PC_control_only':True,'M1_requested_sound_index':4,'actual_sound_index_after_clamp':3,'lookups_checked':len(lookups),'native_menu_safe_for_MIDI':False},'device_controls_requested':True,'device_controls_implemented':False,'saved_settings_implemented':False,'planned_M1_controls':{'entry':'M1 SYN2 page, pending native routing implementation','mode':['OFF','UP'],'rate':['1/4','1/8','1/16','1/32','1/48','1/96','1/8T','1/16T'],'gate_percent':[1,99],'defaults':['OFF','1/16',50],'persistence':'Per-pattern/project; storage format and save/reload path not yet established'}}
Path('outputs/Digitone-E08-loader-controls-results.json').write_text(json.dumps(summary,indent=2))
report='''# E08: packaged loader, startup, playback and device controls

The internal PC container passed independent decompression and the actual stock bootstrap/loader model. Its MAIN image matched the intended E08 bytes at entry 0x400004e8, after 59,004,824 modeled loader instructions and no flash writes. The loader's registers, SRAM, boot flags and controller state were saved before MAIN executed and consumed by the startup engine. No replacement MAIN overlay was applied after that handoff.

The native copier copied the 20,244-byte payload. The cold initializer seeded M1 OFF, rate 1/16, gate 50%, and an empty private event arena. Native timer completion allowed application startup and the logo/UI transition with the restored-project fixture. Code and lookup-table bytes survived initialization into playback. The playback session used that startup snapshot: it did not host-load helpers, patch consumer hooks, or call the initializer in a temporary frame.

M1 live C–E–G playback produced 64 note-ons and 64 matching note-offs. The verified runs changed the native musical clock rate and the requested division/gate, with step cadence following the clock. Final release left active, held-note count and arena-busy state zero. Mode enable, rate/gate requests and the MIDI input gate were disclosed host configuration fixtures; they are not device controls. This test does not establish all sustain, stop, pattern-handoff or reset behavior through the packaged path.

State continuity crosses a loader handoff, a cold-start snapshot and a UI snapshot. These preserve modeled state; this is not a hardware boot. Flash, DDR, timers, DMA and instruction compatibility are modeled. Physical cache coherence, timing and exclusive RAM ownership remain unverified.

## Device controls: concrete finding

Normal MIDI SYN2 selection is ignored in the observed native UI. SYN1, FLTR, AMP and LFO already hold MIDI channel/program, CC values, CC selection and modulation controls. These page assignments agree with the [Elektron Digitone manual](https://www.elektron.se/wp-content/uploads/2024/09/Digitone_User_Manual_ENG_OS1.41_231108.pdf). SYN2 is a candidate entry point for a new MIDI arp page; an ignored selection alone does not establish spare saved storage.

Simply enabling the existing synth arp menu is incorrect. A disposable RAM-only control replaced the MIDI refusal branch at 0x4003fc3e with NOPs. The native menu then requested sound index 4 for M1. The stock getter at 0x4001dcf2 clamps that index to 3 and returns base + 0x60 + 3*0x328, the fourth synth sound handle. All 17 observed arp-menu lookups followed that alias. Therefore, removing the refusal does not create independent MIDI arp controls and could expose a synth sound's settings.

The bypass was used only in the disposable PC session; it is absent from the packaged E08 candidate. No physical firmware was changed. E07's published hash remains unchanged.

## Implementation still required

The selected direction is Digitone controls with settings saved in its projects. For the first M1 version: MODE OFF/UP, the eight existing rate divisions, and GATE 1–99%, defaulting to OFF / 1/16 / 50%. The proposed entry is MIDI SYN2. The page must use a MIDI-specific settings accessor, never the synth sound getter. It must publish complete settings to the MIDI consumer rather than alter an active descriptor.

Usable native controls and saved settings have not been implemented. The next concrete work is to identify the MIDI parameter object's serialized storage and its save/load/copy accessors, then either establish explicitly available fields or add a defined settings record. Tests must edit settings through the new panel page, save/reload the project, and prove that a second pattern, synth T4, and existing MIDI controls retain their own values. A host JSON preset or a RAM snapshot would not satisfy this persistence requirement.

Evidence: Digitone-E08-packed-loader.json; Digitone-E08-PC-startup-comparison.json; Digitone-E08-loader-playback.json; Digitone-E08-loader-startup-playback-results.json; Digitone-E08-stock-menu-bypass.json; Digitone-E08-MIDI-controls-trace.json. Internal package: work/os144/E08-PC-path-candidate.syx, SHA-256 321dde0431caa936a485d3e4ea48c316644257cf6974a1284fdfb7c88fa056f2. This is a PC test package, not a hardware release.
'''
Path('outputs/Digitone-E08-loader-controls-review.md').write_text(report)
print('Packaged path passed; native menu alias confirmed; controls/persistence remain outstanding')
