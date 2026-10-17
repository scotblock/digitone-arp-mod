from pathlib import Path
import json,hashlib,shutil
load=lambda p:json.loads(Path('outputs',p).read_text())
cfg=load('Digitone-E07-PC-candidate-layout.json');start=load('Digitone-E07-PC-startup-comparison.json');contracts=load('Digitone-E07-MIDI-contracts.json');play=load('Digitone-E07-MIDI-native-playback.json');container=load('Digitone-E07-PC-container-verification.json');reset=load('Digitone-E07-PC-diagnostic-reset-controls.json')
assert all(r['passed'] for r in [start,contracts,play,container,reset]);assert play['internal_pitches_equal_E06_and_mirror_off']
on,off=play['cases'];assert on['balanced_note_pairs']>0 and off['balanced_note_pairs']==0 and on['dropped_note_ons']==0 and on['no_active_mirrored_notes_at_stop'] and on['pattern_handoff']['completed']
assert len(start['cases'])==5 and len(reset['cases'])==9
source=Path(cfg['candidate']);sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha==cfg['candidate_sha256']==container['sha256']
old={'outputs/Digitone_OS1.44E06_SCALE_DEGREE_ARP_PC_ONLY.syx':'9677c2434429016b1861ebcbb5cfbefcaa0a863c076e123acd84abf120a068d3','outputs/Digitone_OS1.44E05_SCALE_ARP_PC_ONLY.syx':'17fbe13d6b2aad9c096df7ac20fd4499a7bb0951e146fd0fd0aaeace4037e474','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx':'d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'}
for p,h in old.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
dest=Path('outputs/Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx');shutil.copyfile(source,dest);Path(str(dest)+'.sha256').write_text(sha+'  '+dest.name+'\n')
evidence=['Digitone-E07-PC-candidate-layout.json','Digitone-E07-MIDI-contracts.json','Digitone-E07-PC-startup-comparison.json','Digitone-E07-MIDI-native-playback.json','Digitone-E07-PC-container-verification.json','Digitone-E07-PC-diagnostic-reset-controls.json','Digitone-synth-arp-MIDI-lifecycle.json']
report={'candidate':str(dest.resolve()),'sha256':sha,'PC_only':True,'hardware_ready':False,'route':'Five-pin DIN MIDI OUT only','channels':'Configured synth-track MIDI channels; OFF suppresses new mirrored notes','new_independent_MIDI_arps':False,'same_payload_size_and_RAM_range_as_E06':True,'native_MIDI_code_bytes':cfg['MIDI_code_bytes'],'native_MIDI_private_state_bytes':cfg['MIDI_state_bytes'],'startup_cases':5,'reset_refusal_cases':9,'isolated_contract_groups':len(contracts['checks']),'native_playback_cases':2,'note_on_count':on['balanced_note_pairs'],'matching_note_off_count':on['balanced_note_pairs'],'dropped_note_ons':on['dropped_note_ons'],'all_notes_released_at_stop':True,'internal_pitch_sequence_matches_E06_and_mirror_off':True,'pattern_handoff_completed':on['pattern_handoff']['completed'],'native_copy_supplied_MIDI_helpers':not on['mirror_code_host_loaded'],'previous_firmware_preserved':old,'limits':['Actual continuous playback exercises T1; all four channels, shared-voice ownership and congestion handling have isolated native controls, not a four-track simultaneous physical trial.','USB output is not implemented. New arps on MIDI tracks are not implemented.','No physical boot, cache, DMA contention, MIDI pacing or audio timing validation for E07.','Exclusive ownership of newly used padding and other computed/global aliases remains unproven, despite unchanged reserved-RAM extent and bounded code/state preservation checks.','Unknown shutdown/mute/reset bypasses may require additional note-off cleanup. Diagnostic mode stays disabled as in E06.','Other MIDI-track sequences using the same destination channel/note do not share this mirror ownership table.'],'evidence':evidence}
Path('outputs/Digitone-E07-MIDI-candidate-results.json').write_text(json.dumps(report,indent=2))
text=f'''# E07 — synth arp to DIN MIDI, PC-only candidate

Firmware: `{dest.name}`

SHA-256: `{sha}`

E07 retains E06's scale-degree synth arps and mirrors generated arp notes through five-pin DIN MIDI OUT. This candidate is for Digiemu testing first. E07 has not run on physical hardware. E06, E05 and stock recovery files remain unchanged. The on-screen version still reads 1.44.

## Behavior

Each synth arp uses that synth track's configured MIDI channel (normally T1–T4 use channels 1–4). With a channel set to OFF, no new mirrored notes are emitted. The existing MIDI output selection must include MIDI/DIN; USB-only output does not enable this mirror. This version does not mirror over USB and does not add arps to the four independent MIDI tracks.

The emitted pitch is the accepted final synth pitch, including E06's scale-degree calculation and later stock transposes. Velocity comes from the synth note event. Note-offs follow observed native voice retirement paths, including ordinary gate expiry and allocator replacement. Shared/unison voices send one note-on per destination channel/note, then one note-off when the last mirrored voice retires. The note-off retains the original channel if settings change while a note is active.

When the native DIN ring is full, a new note-on is declined without claiming an external note. A blocked note-off remains pending and the stock MIDI task retries it. This handling passed isolated native controls; physical congestion timing remains unmeasured.

## Implementation and validation

The {cfg['MIDI_code_bytes']:,}-byte helper set and 160-byte state table fit in previously zero padding within E06's existing {cfg['payload_bytes']:,}-byte copied payload. The copier, payload length, source interval and reserved-RAM extent are unchanged. The native copier supplies both code and initial state; the final tests do not host-load the MIDI helpers or inject outgoing packets. E05/E06's startup, input, release/sustain and reset refusal protections remain in place.

- Five matched startup cases passed, including fresh/restored candidate startup and E06 feature fallback. The native-copy checks include the new helpers and state seed.
- Nine stopped-state diagnostic/reset refusal controls passed.
- Seventeen isolated MIDI controls passed, including all four configured channels, shared voices, original-destination release after channel change, inactive/invalid controls and output congestion. The isolated transport endpoint is a stub; continuous playback uses the real stock transmitter.
- Two continuous packaged sessions passed: mirroring enabled and a disclosed mirror-disabled control. The enabled run emitted {on['balanced_note_pairs']} note-ons and {on['balanced_note_pairs']} matching note-offs, dropped none, and ended with no active mirrored notes. Its MIDI notes include C D E F G A B C. Sustain, release, completed pattern replacement and fresh notes were exercised.
- The internal pitch sequence matches E06 and the mirror-disabled control. This does not establish audio byte equality or physical audio deadlines.
- Transport framing/checksums, compressed MAIN checksum, exact independent decompression and unchanged non-MAIN sections passed.

Continuous playback currently covers T1. Four simultaneous arps, mute/panic paths, rare reset/destruction routes, USB mirroring, physical queue timing and exclusive ownership of all newly used padding remain unverified. The selected RAM is within the old copied range; that fact is not an exclusive-ownership proof. Use separate destination channels for independent MIDI-track sequences: their channel/note ownership is not coordinated with the mirror table.

## First emulator test

Add E07 as a separate firmware entry and keep E06 available. Select a MIDI output or loopback port in Digiemu. In MIDI CONFIG → PORT CONFIG, set OUT PORT FUNC to MIDI and OUTPUT TO to MIDI or MIDI+USB. Use T1's configured synth MIDI channel as the receiver channel. For the first arp-only test, set TRIG KEY DEST to INT to avoid also transmitting raw keyboard notes. Record MIDI in Ableton and leave the recording track's MIDI output unassigned to avoid echoing notes back into the emulator.

Use C major/Ionian, a held C and offsets 0–7. Verify C D E F G A B C, then stop and inspect that every note has an end. Repeat release/sustain and pattern-change tests. In a later physical trial, the intended connection would be Digitone MIDI OUT to Rubix22 MIDI IN, with Rubix22 connected to the computer; E07's mirror does not use Digitone USB MIDI.

Do not install E07 on the physical Digitone as part of this PC test. No E07 hardware trial was performed or authorized here.

## Evidence

'''
for p in evidence:text+='- ['+p+']('+str(Path('outputs',p).resolve()).replace('\\','/')+')\n'
Path('outputs/Digitone_E07_PC_ONLY_README.md').write_text(text,encoding='utf-8');print('CREATED',str(dest.resolve()),'SHA256',sha,'MIDI pairs',on['balanced_note_pairs'])
