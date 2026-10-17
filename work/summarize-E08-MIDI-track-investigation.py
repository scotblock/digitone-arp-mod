from pathlib import Path
import json,hashlib
root=Path.cwd();r=json.loads(Path('outputs/Digitone-E08-MIDI-track-queue-trace.json').read_text());rel=json.loads(Path('work/os144/E07-MIDI-relocation.json').read_text())
assert r['failure'] is None and r['halted'] is None
wire=r['wire'];on=[x for x in wire if x['bytes'][0]&240==144 and x['bytes'][2]>0];off=[x for x in wire if x['bytes'][0]&240==128 or (x['bytes'][0]&240==144 and x['bytes'][2]==0)]
assert len(on)==len(off)==2
assert all(a['bytes'][1]==b['bytes'][1] and a['bytes'][0]&15==b['bytes'][0]&15 for a,b in zip(on,off))
p=Path('outputs/Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx');sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha=='a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'
report={'investigation_only':True,'no_new_firmware':True,'E07_unchanged_sha256':sha,'user_reported_E07_hardware_observation':{'date':'2026-10-14','source':'User message in this conversation','boot_and_arp_MIDI_output_recorded_in_Ableton':True,'independent_hardware_measurement':False},'PC_baseline':{'track':'M1','native_UI_programmed_single_C_trig':True,'note_pairs':2,'gate_ms':[b['ms']-a['ms'] for a,b in zip(on,off)],'arp_selector_calls':r['counts'].get('0x40097e46',0),'arp_offset_hook_calls':r['counts'].get('0x40098116',0),'queue_types_observed':r['queue_counts'],'failure':None},'insertion_candidate':'0x400f42da MIDI task queued note handling; per-track gates, channel selection and transpose follow. Candidate only, not yet an implemented hook.','observed_native_note_packet_append':{'entry':'0x400f3e70','note_on_return':'0x400f4858','timed_note_off_return':'0x400f4ab0'},'static_event_fields':{'track_index':'+0x04','note_count':'+0x10','note_bytes':'+0x14 onward','gate_duration':'+0x1c','velocity_byte':'+0x23','timestamp':'+0x24','additional_pointer':'+0x28; lifetime and meaning require tracing'},'synth_engine_constraints':['Selection uses 40-byte records at 0x413915f4 and synth-specific held-note structures. Existing contracts cover four records.','Arp settings are read from synth Sound offsets, including +0x10f, +0x113 and +0x114; MIDI parameter records have a different format.','Calling the existing selector with MIDI indexes 4-7 is not established as valid and would index beyond the four selected records.'],'existing_E07_padding_bytes_remaining':sum(b-a for a,b in rel['remaining_gaps']),'largest_remaining_gap_bytes':max(b-a for a,b in rel['remaining_gaps']),'recommendation':'PC-only one-MIDI-track chord arp prototype, separate state, host-disclosed settings fixtures initially, stock gate/output behavior; then determine UI and persistence before packaging. Reuse verified scale-degree arithmetic where useful.','next_concrete_checks':['Trace the note queue producer and timing-message fields; establish clock/rate and ownership needed for repeated generated notes.','Prototype M1 OFF versus UP mode with a real three-note native chord and matching note-offs, stop and replacement cancellation.','Choose per-MIDI-track settings/scale storage and user controls without changing stock project serialization.','Resolve code/state capacity, since only 340 fragmented bytes remain in the E07 allocation plan.'],'limits':['Single MIDI-track, single-note baseline, not an arp implementation.','Two other observation runs used some tentative or historical probe addresses; zero hits there are not eligibility evidence. Correct 1.44 selector and offset-hook addresses are used in the queue-trace run.','Physical feasibility, UI, pattern settings persistence, independent four-track timing, note collisions and mute/reset cleanup remain unverified.']}
Path('outputs/Digitone-E08-MIDI-track-feasibility.json').write_text(json.dumps(report,indent=2))
text='''# Independent MIDI-track arp investigation

E07 remains unchanged. The user reports that E07 runs on the physical Digitone and its synth arp MIDI output records in Ableton. This is a user observation, not a complete hardware timing or ownership certification.

## What was observed

A continuous PC run used E07 with a MIDI track selected through the native UI, enabled M1 channel 1 and recorded a C trig. It emitted two C note-ons and two matching velocity-zero note-offs. The observed gates were approximately 123 and 125 ms. Neither the actual 1.44 synth arp selector nor its offset hook executed in that workload. Earlier exploratory probes included historical or tentative addresses; their zero-hit counts are not used as proof.

The actual MIDI task consumes queued descriptors, applies track gates/channel selection/transposition, emits notes through its stock packet buffer, and schedules timed releases. The note-on packet append returned to 0x400f4858 and its matching timed release append returned to 0x400f4ab0. Candidate interception at 0x400f42da is before these steps; no interception has been implemented.

The existing synth selector indexes four 40-byte records and reads arp settings from a Sound structure. MIDI parameter records have a different layout. Merely opening the synth arp menu on MIDI tracks or passing indexes 4–7 is not an established implementation route.

## Proposed first prototype

Use a separate M1 arp state, initially with explicit PC settings fixtures: OFF preserves the stock chord; UP turns a three-note chord into successive notes. Feed generated notes into the stock MIDI scheduling/output path, with finite gates and cancellation when the source ends, playback stops or a new pattern replaces it. Reuse E06 scale-degree mathematics after MIDI root/scale ownership is traced. Extend to M2–M4 after the first independent engine works.

Settings must eventually be editable and survive pattern/project operations. Synth arp parameters are part of Sounds; MIDI tracks do not have a matching Sound container. The settings page, storage format and reset rules require a deliberate design. Stock project serialization will not be changed based only on apparent unused bytes.

## Space constraint and next target

The E07 allocation plan has only 340 fragmented padding bytes left, with a largest gap of 256 bytes. That is a concrete layout constraint, not a total-device free-space measurement. An independent engine cannot be assumed to fit there. Code consolidation or another audited placement will be needed once the prototype's actual size is known.

Next: trace the queued chord producer and stock MIDI timing messages, then run a one-track UP prototype with native chords, release and stop cancellation. No new firmware has been packaged.

## Evidence

'''
for name in ['Digitone-E08-MIDI-track-queue-trace.json','Digitone-E08-MIDI-track-feasibility.json']:
 text+='- ['+name+']('+str(root/'outputs'/name).replace('\\','/')+')\n'
text+='\nOfficial stock feature reference: [Digitone manual, arp and MIDI-track sections](https://elektron.se/wp-content/uploads/2024/09/Digitone_User_Manual_ENG_OS1.41_231108.pdf).\n'
Path('outputs/Digitone-E08-MIDI-track-investigation.md').write_text(text,encoding='utf-8')
print('saved investigation; E07 preserved; remaining padding',report['existing_E07_padding_bytes_remaining'],'gate ms',report['PC_baseline']['gate_ms'])
