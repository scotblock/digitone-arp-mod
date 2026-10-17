from pathlib import Path
import json,hashlib
order=json.loads(Path('outputs/Digitone-E04-PC-startup-producer-order-startup.json').read_text())
handler=json.loads(Path('outputs/Digitone-E04-PC-startup-note-admission-probes.json').read_text())
irq=json.loads(Path('outputs/Digitone-E04-PC-startup-DIN-interrupt-probes.json').read_text())
queued=json.loads(Path('outputs/Digitone-E04-PC-startup-queued-DIN-startup.json').read_text())
settled=json.loads(Path('outputs/Digitone-E04-PC-startup-settled-MIDI-probes.json').read_text())
assert all(x['passed'] for x in [order,handler,irq,queued,settled])
assert len(order['cases'])==len(queued['cases'])==2 and len(handler['cases'])==14 and len(irq['cases'])==6
for c in order['cases']:
 gates=[w for w in c['startup_gate_writes'] if w['address']=='0x41368d88' and w['value']==1]
 assert gates and gates[0]['READY']==0 and gates[0]['admission']==0x434f4c44
 ev=c['startup_order_events'];normal=next(e for e in ev if e['pc']=='0x4008d31e');final=next(e for e in ev if e['pc']=='0x4008d3ec')
 assert normal['READY']==final['READY']==1 and normal['admission']==final['admission']==0x494e4954
 assert not c['producer_entries']
assert all(c['interrupt_taken'] and c['DIN_read_index_after']==3 and not c['producer_reached'] for c in irq['cases'])
assert all(c['startup_DIN_injection']['interrupt_taken'] and not c['producer_entries'] for c in queued['cases'])
assert all(c['producer_reached'] for c in handler['cases'])
assert all(c['queue_publisher_reached'] for c in handler['cases'] if c['full_handler'])
assert settled['cases'][0]['published'] is False and settled['cases'][1]['published'] is True
assert all(e['phase']=='0x494e4954' for e in settled['cases'][1]['events'])
expected=json.loads(Path('outputs/Digitone-E04-PC-persistent-admission-summary.json').read_text())['hashes']
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in expected.items())
summary={'PC_only':True,'passed':True,'startup_trace_cases':2,'early_queued_DIN_continuation_cases':2,'direct_handler_probes':14,'saved_DIN_interrupt_probes':6,'settled_MIDI_sessions':2,'note_gate_enabled_before_initializer':True,'handler_eligible_before_initializer':True,'receiver_interrupt_active_before_initializer':True,'actual_receiver_to_note_before_initializer_proven':False,'actual_settled_receiver_to_note_while_INITIALIZING':True,'late_normal_startup_candidate':'4008d3fa after final synchronous startup call 40019444 returns','LIVE_publication_implemented':False,'phase_aware_input_guard_implemented':False,'safe_all_producer_activation_boundary_certified':False,'hardware_ready':False,'existing_artifacts_unchanged':True,'hashes':expected}
Path('outputs/Digitone-E04-PC-startup-producer-order-summary.json').write_text(json.dumps(summary,indent=2))
review='''# Startup completion and first input admission: PC findings

Four loader-derived startup runs pass: default/restored with no external input, then default/restored with three DIN note bytes offered before note initialization. Four checkpoints per normal run capture actual state before note setup, after full audio/note setup, before the later worker startup, and at the normal startup idle point. Fourteen handler probes, six saved-state interrupt probes and two settled input sessions also pass. Existing firmware/raw/previous UI-overlay hashes are unchanged.

## Stock gates open before note initialization

Stock configuration deserialization writes receive gate `41368d64` at `40009b0a` and note gate `41368d88` at `40009bde`. Default receive gate becomes 2 (USB only); restored receive gate becomes 3 (DIN and USB). Both note gates become 1 while admission is still COLD and context READY is zero. The later native cold claim changes phase to INITIALIZING but does not change either stock gate.

DIN receive vector `40000270` already points at `400025c8`, its ring DADDR is `4bc00000`, and the saved INTC permits interrupt level 4 at the pre-initializer snapshot, where SR is `2000`. The phase word therefore is not an effective input barrier.

## Handler eligibility versus transport production

Direct, controlled calls to actual note wrapper `400eb2d2` with unchanged stock gates reach producer `400eae5c` before initialization. Those pre-initializer probes stop before note-pool writes. After normal setup returns at `4008d31e`, complete handler calls publish queued notes while phase remains INITIALIZING. Some cached-path publications occur before reaching `400eae5c`, so a guard only at that later producer would miss them.

The saved DIN IRQ controls offer vector 156 under saved SR/INTC conditions, consume all three bytes through actual ISR `400025c8` and callback `400e842c`, then return. They do not reach the note producer. The separate continuous cold runs inject the same bytes before setup, take the actual interrupt, finish startup and reach modeled UI without observing note-handler/producer publication from those bytes. This does not establish why the early bytes fail to produce notes, or prove a universal startup input exclusion. In particular, USB and panel producer timing remain untested.

Once the modeled UI is settled, paced DIN input on the restored configuration executes the real receiver/worker/handler and publishes a note while admission is still INITIALIZING. Default USB-only configuration rejects DIN as the stock setting requires. No gate or phase value is changed to authorize either session. Thus the native seed/claim experiment alone does not implement the policy's producer closure or transition to LIVE.

## Completion boundaries

`4008d31e` follows completion of normal note/audio setup: stock initializer has returned, context READY is 1 and normal audio vector is installed. Later startup work still remains. Startup `4008d3dc` calls the next worker initializer, then `4008d3ee` starts the input worker through `400eb3e6`, and `4008d3f4` calls `40019444` to create/start the application worker. The normal path then reaches `4008d3fa -> 4008d3ec` (idle).

`4008d3fa`, after the last visible synchronous startup call returns, is a late candidate for LIVE publication. Reaching the idle point on the normal branch in both runs establishes observed completion of these calls, not an explicit checked success/error contract. At these checkpoints the current task is `4137465c`, matching the recorded startup task at priority 1; the input worker is created at priority 7. These task observations do not certify all scheduler/IRQ overlap or hardware preconditions.

A late publication cannot by itself hold earlier input closed: stock note gates already authorize the direct handler, receiver callbacks are active earlier, and workers are made runnable before that final boundary. Conversely, publishing LIVE immediately after the note initializer would mislabel later startup as complete. No LIVE store is added by this investigation.

## Concrete next step

Add a PC-only phase-aware check before input dispatch can enter either cached publication or live-note production, and cover panel/direct routes separately. Then test publishing LIVE at the normal completion boundary together with these guards, including feature-disabled stock fallback and input offered before/during/after the handoff. The completion condition must distinguish stock setup completion from optional context availability. Exact graceful failure handling, non-replayable boot provenance, global/physical storage ownership and hardware cache/timing remain unproven.
'''
Path('outputs/Digitone-E04-PC-startup-producer-order-review.md').write_text(review)
incident=Path('outputs/Digitone-E04-hardware-startup-incident.md');marker='## Thirty-first follow-up: startup completion versus input activation'
if marker not in incident.read_text():incident.write_text(incident.read_text()+'\n\n'+marker+'\n\nFour startup runs, fourteen handler probes, six DIN interrupt probes and two settled input sessions pass. Stock config opens note gate before initializer; direct handler can reach producer before initialization and cached publication precedes the later live producer. Early DIN IRQ drains bytes without observed note production, but settled restored DIN input publishes while phase remains INITIALIZING. Late normal completion candidate is 4008d3fa after final startup call; LIVE/input-phase guards remain unimplemented. No universal transport/IRQ exclusion or hardware readiness claim. Existing firmware/raw/old UI blob hashes unchanged. See `Digitone-E04-PC-startup-producer-order-review.md`.\n')
print(json.dumps(summary,indent=2))
