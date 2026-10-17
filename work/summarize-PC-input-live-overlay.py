from pathlib import Path
import json,hashlib
controls=json.loads(Path('outputs/Digitone-E04-PC-input-live-controls.json').read_text())
startup=json.loads(Path('outputs/Digitone-E04-PC-input-live-startup-startup.json').read_text())
settled=json.loads(Path('outputs/Digitone-E04-PC-input-live-settled-MIDI.json').read_text())
handoff=json.loads(Path('outputs/Digitone-E04-PC-input-live-IRQ-handoff.json').read_text())
transition=json.loads(Path('outputs/Digitone-E04-PC-input-live-MIDI-transition.json').read_text())
assert all(x['passed'] for x in [controls,startup,settled,handoff,transition])
assert len(startup['cases'])==len(settled['cases'])==3
for c in startup['cases']:
 assert [w['value'] for w in c['admission_word_writes']]==[0,0x434f4c44,0x494e4954,0x4c495645]
 assert next(e for e in c['startup_order_events'] if e['pc']=='0x4008d3ec')['admission']==0x4c495645
 assert c['intro']['up']
 if c['image']=='E04_disabled':assert c['private_after_cold'][:8]=='00000000' and c['private_after_cold'][32:40]=='00000000'
assert settled['cases'][0]['published'] is False
assert settled['cases'][1]['published'] and settled['cases'][2]['published']
expected=json.loads(Path('outputs/Digitone-E04-PC-persistent-admission-summary.json').read_text())['hashes']
for manifest,blob in [('work/os144/PC_ONLY-persistent-admission.json','work/os144/PC_ONLY-persistent-admission.bin'),('work/os144/PC_ONLY-cold-admission-overlay.json','work/os144/PC_ONLY-cold-admission-overlay.bin')]:expected[blob]=json.loads(Path(manifest).read_text())['sha256']
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in expected.items())
summary={'PC_only':True,'passed':True,'native_overlay_bytes':492,'closed_phase_entry_controls':len(controls['denial_cases']),'LIVE_stock_parity_pairs':len(controls['stock_parity']),'completion_controls':len(controls['completion_cases']),'continuous_native_cold_startup_cases':3,'settled_receiver_sessions':3,'IRQ_handoff_control':True,'functional_closed_to_LIVE_MIDI_handoff':True,'native_seed_claim_and_LIVE_publication_joined':True,'input_guard_sites':['400eb2d2 packet wrapper','400eb166 cached selector','400eae5c live producer'],'optional_context_failure_preserves_stock_input':True,'all_producer_routes_certified':False,'warm_reset_command_admission_installed':False,'packaged_code_delivery_verified':False,'hardware_ready':False,'existing_artifacts_unchanged':True,'hashes':expected}
Path('outputs/Digitone-E04-PC-input-live-summary.json').write_text(json.dumps(summary,indent=2))
review='''# Input guards and LIVE transition: PC overlay review

A separate 492-byte host-loaded overlay now guards three recovered input entries and publishes LIVE after the last visible synchronous normal startup call returns. All targeted tests pass: 18 closed-phase entry controls, four LIVE/stock parity pairs, nine completion controls, three continuous native cold startup cases, three settled MIDI sessions, one publication/IRQ control and one controlled closed-to-LIVE receiver handoff. Existing firmware, raw candidates and older guard blobs are unchanged by verified hashes.

## Guard behavior

Exact LIVE is required at packet wrapper `400eb2d2`, cached selector `400eb166`, and live producer `400eae5c`. CLOSED/INITIALIZING/FAILED and tested zero/poison/corruption return before any original prologue or input argument dereference. The denial is a no-op at the recovered function boundary, preserving registers, incoming SR and caller stack. It does not create a note, update cache/context or enter allocation/publication. Unknown callers' expectations still require audit; no general boolean error contract is asserted.

The packet and selector guards cover the cached publications found before the later live producer. Direct live-producer entry is also guarded. LIVE restores saved state, replays each displaced prologue and resumes original execution. Four paired calls match stock CPU/queue/pool/context state and routes, with and without optional context, including the earlier cached publications and later live producer. These parity calls have no concurrent timers, so they do not measure added timing cost.

## Normal completion and fallback

The new completion wrapper replaces normal startup call `4008d3f4`. It executes complete stock `40019444` first, then requires its observed return `4008d3fa`, INITIALIZING, normal boot/test flags, both recovered setup flags at 1 and installed normal audio vector `4009d120`. It publishes through the native phase helper under IPL7 and restores incoming registers/SR before returning to startup idle.

Optional context is checked independently: invalid/missing PTR, metadata or READY disables PTR/READY and still permits LIVE for stock behavior after the normal stock conditions pass. Bad phase/mode/setup flags/audio vector/return enter the earlier proposed masked PC failure stop. This remains a bounded completion contract using observed fields, not universal error/exception certification or hardware recovery.

Default, restored-project and injected-owner-failure startups all execute guest stores zero -> COLD -> INITIALIZING -> LIVE exactly once and reach modeled UI. The injected owner failure follows the real fallback/stock initializer and ends with optional context disabled. Three settled paced DIN sessions preserve stock receive settings: default USB-only rejects DIN; restored and feature-disabled configurations accept and publish notes, all under LIVE.

## Input around publication

The startup cases also offer DIN bytes before note initialization and continue through native startup, with unchanged receive/note gates. Like the earlier controls, these early bytes do not produce an observed note during startup/intro. This is not a promise to discard every raw byte received before LIVE: the guards act when input reaches the guarded functions. Upstream transports may queue raw input and process it later.

A retained, fully started checkpoint from the earlier overlay naturally remains INITIALIZING. With the new guards installed, paced DIN reaches the actual packet wrapper but stops before cached/live processing and note publication. The test then pauses that session, runs the native phase helper with declared success argument 1, restores task CPU/stepper state, and sends another note. That note reaches the cached selector, live producer and queue under LIVE. No host phase write opens input. This is a functional phase-handoff control; actual bootstrap completion checks and full final call are established by the separate continuous startup cases.

At the native completion state's LIVE store, a controlled DIN interrupt offer is rejected under IPL7. After the helper restores the interrupt mask, explicitly offering it again takes vector 156 and consumes all three ring bytes with phase LIVE. Actual peripheral request latching/retry and physical byte timing are not certified.

## Remaining scope

Code lives at fixture-only `47fa0600`, alongside earlier host-loaded bootstrap helpers. No packaged loader/copy delivery, physical executable placement/cache handoff or timing claim is made. These are functional instruction/model checks with the existing cold/intro/playback shortcuts.

CC/sustain, release/panel/sequencer bypasses, upstream USB queues, callback overlap and every unknown computed caller are not fully covered by these three entry guards. The previously isolated UI guards are not patched into this joined startup overlay. Warm initializer and command admission remain absent; input would still be allowed in LIVE during an unguarded warm pool rebuild. Cold replay provenance, global/physical RAM ownership and hardware cache/timing remain unresolved. Do not install this experiment on a device.

The next focused task is auditing note-off/sustain and panel/direct dispatch around this guard, including already queued input, then joining the previously tested UI refusal guards with the startup overlay before claiming complete V1 admission.
'''
Path('outputs/Digitone-E04-PC-input-live-review.md').write_text(review)
p=Path('outputs/Digitone-E04-hardware-startup-incident.md');marker='## Thirty-second follow-up: guarded input and native LIVE publication'
if marker not in p.read_text():p.write_text(p.read_text()+'\n\n'+marker+'\n\nSeparate 492-byte host-loaded overlay guards packet, cached selector and live-producer entry, then publishes LIVE after full final startup call with observed normal conditions. Eighteen denials, four stock-parity pairs, nine completion controls, three native cold startups (including context-disabled fallback), three settled MIDI sessions, an IRQ publication control and a controlled receiver phase handoff pass. Native stores zero/COLD/INITIALIZING/LIVE join in startup; optional failure retains stock input. All-route and warm reset/command admission, packaged code delivery and physical provenance/storage/cache/timing remain unresolved. Firmware/raw/older overlay hashes unchanged. See `Digitone-E04-PC-input-live-review.md`.\n')
policy=Path('outputs/Digitone-E04-PC-reinitialization-protection-policy.md');marker='## Joined input/LIVE PC overlay'
if marker not in policy.read_text():policy.write_text(policy.read_text()+'\n\n'+marker+'\n\nThree recovered note input entries now read exact LIVE in a separate host-loaded overlay. Native normal startup publishes LIVE after full final stock call and observed normal fields; optional context failure disables the feature and preserves stock input. Targeted cold/closed/LIVE/IRQ/receiver controls pass. Producer coverage is bounded: CC/sustain/panel/sequencer and warm initializer/command guards remain incomplete. Prior UI guards remain separately tested, not joined. See `Digitone-E04-PC-input-live-review.md`.\n')
print(json.dumps(summary,indent=2))
