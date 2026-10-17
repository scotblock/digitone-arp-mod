from pathlib import Path
import json,hashlib
model=json.loads(Path('outputs/Digitone-E04-PC-reinitialization-policy-model.json').read_text());native=json.loads(Path('outputs/Digitone-E04-PC-reinitialization-admission.json').read_text());old=json.loads(Path('outputs/Digitone-E04-PC-live-capture-summary.json').read_text())['hashes'];hashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in old};candidate=json.loads(Path('work/os144/PC_ONLY-atomic-storage-layout.json').read_text())
checks={'model_assertions_pass':model['passed'],'pre_mutation_admission_control_passes':native['passed'],'rejected_command_keeps_native_state':native['cases'][0]['queue_flags_handler_metadata_pool_and_CPU_preserved'],'initializer_only_return_is_not_an_abort':not native['cases'][1]['zero_return_aborts_whole_setup'],'no_native_guard_installed':not model['native_guard_installed'] and not native['native_guard_installed'],'original_images_preserved':hashes==old,'guarded_PC_candidate_preserved':hashlib.sha256(Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes()).hexdigest()==candidate['main_sha256'] and hashlib.sha256(Path('work/os144/PC_ONLY-atomic-storage-payload.bin').read_bytes()).hexdigest()==candidate['payload_sha256']}
out={'PC_only':True,'policy_defined':True,'native_guard_installed':False,'hardware_ready':False,'checks':checks,'passed':all(checks.values()),'hashes':hashes};Path('outputs/Digitone-E04-PC-reinitialization-policy-summary.json').write_text(json.dumps(out,indent=2));assert out['passed']
text='''# V1 protection policy before note-storage reinitialization

V1 will initialize this note-event pool once per fresh startup and refuse live reconstruction. It will reject the whole diagnostic/setup operation before any stock flags, handlers, selected page or pool state change. An empty queue, disabled input gate or ready flag is not a permit to rebuild a running pool.

This is a defined and tested PC admission policy, not an installed machine-code guard. Firmware containers and the current raw guarded PC candidate remain unchanged. Diagnostic entry/exit and audio-test page transitions that require reconstruction are outside this V1 policy while running; resetting this storage requires a fresh startup. This restriction needs a concrete native rejection/notification implementation before any candidate can claim to enforce it.

## Lifecycle contract

| Phase | Pool reconstruction | Producer admission | Feature context |
|---|---|---|---|
| Fresh cold startup | One permit may be consumed by the normal startup transaction | Closed | Unavailable |
| Initialization in progress | Only the admitted initializer may enter once | Closed | Unavailable |
| Normal running | Always refused, including apparently empty/idle states | Normal stock admission | Available after successful context setup |
| Context setup unavailable but stock startup completed normally | Always refused; the boot permit stays consumed | Normal stock admission | Unavailable |
| Stock setup incomplete or mode not normal | Refused; no retry grants a new cold permit | Closed in the specification | Unavailable |

A fresh boot is a new lifetime, not a transition created by clearing ready or observing zero owner counts. The initialization permit is consumed before mutation and is not restored by failure, reentry, empty queues or a caller retry. The specification represents it with a per-boot capability; native code must implement a boot-lifetime latch and trusted bootstrap provenance, not a caller-supplied boolean or return address alone.

The latch must sit outside the descriptor/pending areas cleared by the reset routine. The early copier may initialize it for a fresh boot; ordinary initializer/reset helpers must never clear it. Any additional word's physical RAM ownership and writer aliases must be audited before selecting its final location. No native address for this new latch is certified by this task.

## Rejection boundaries

1. Diagnostic commands: reject ENTER_TEST_MODE and EXIT_TEST_MODE at the command-operation boundary. For the recovered exit match, `4008b88a` precedes the store clearing `402a0e50`; guarding only `4008b890`, `4009d0ea` or the pool initializer is already after part of the transition. Rejection must report failure/defer and complete request cleanup through a verified balanced continuation; it must not claim success or strand a packet/lock.
2. Audio-test UI: refuse entry/selection before selected-child or audio-handler mutation. Preventing entry avoids a page whose exit depends on a forbidden live rebuild. A close request for any already active diagnostic page still needs whole-operation rejection/defer before page-manager close/removal mutation. Returning from its void exit callback without setup is not a verified veto: the remover can continue unlinking the page while its alternate handler remains installed.
3. Normal setup: allow the one admitted cold transaction before the stores in `4009d0d8`. Repeated or computed setup requests must not silently resume their outer callers. The common initializer at stock `400ffed0` (PC reset helper `47be3400`) repeats the admission check before clearing readiness or any storage, as a last-line invariant check.
4. Unknown route: fail closed in the PC model before writes and retain a diagnostic reason. A verified native error/abort continuation must be selected before translating that rejection to machine code. No interrupt-masked busy wait, spin loop or unbalanced return is approved by this policy.

Rejection preserves the note pool and free lists, queued events, cached/retained notes, context records, pending snapshots, audio vector, mode flags, page selection and the caller's stack/lock contract. It does not stop normal notes, drop release/sustain events, clear writer counters or attempt to reclaim owners. Ordinary pattern handoffs, STOP and release operations keep their existing pool lifetime and remain supported.

## Why initializer-only rejection is insufficient

A native command fixture executes stock parsing/comparison and pauses at the reset hook. The negative control injects an initializer return of zero. The actual caller returns through `4009c5aa` and continues directly to setup call `400982d8`, without testing zero; the diagnostic flag has already been cleared. Therefore a new early return from the initializer cannot be treated as a complete transaction abort.

The positive admission control pauses at `4008b88a`, before that flag change. The PC policy refuses to invoke the stock transition. Fingerprints of the pool, queue, mode/handler flags, descriptor/pending context and CPU state remain unchanged. This is host-model admission on native state; no firmware branch, completed native command cleanup or UI veto is executed. That distinction is an implementation blocker, not an installed protection claim.

## PC checks

The state model checks one-time initialization, nested/forged/replayed permits, failures that cannot reopen boot admission, normal running with the feature unavailable, unknown operations and preservation under rejected requests. Cases include visible queued notes, retained ownership, pending snapshots and an in-flight producer; an apparently empty state is also refused. Pattern changes, STOP, note release and sustain release remain admitted without reconstruction. There are 175 policy assertions; they specify the desired contract and do not establish native owner enumeration or concurrency.

The native controls verify pre-mutation state preservation under model denial and the invalidity of initializer-only zero-return propagation. Seven summary checks pass, including unchanged original image and current PC candidate hashes. No new flashable firmware or native latch/helper is produced.

## Next concrete implementation work

Verify the complete command rejection continuation and the earliest audio-test selection/close veto, including request cleanup, return/status handling and mutex balance. Then add the persistent boot latch and common-entry check in a separate PC-only overlay and repeat cold startup, ordinary playback/pattern handoff and refused-diagnostic controls. If no usable outer veto is found, leave that native route unimplemented; do not downgrade to an initializer-only return.

Supporting live reconstruction later would require a different protocol: close all relevant producer admissions, let in-flight work finish without blocking its scheduler, retire queue/template/cache owners with balanced releases, exclude remaining writers/consumers, then rebuild and reopen. No complete owner inventory or shared exclusion mechanism exists yet, so a counter or an empty queue cannot certify that future protocol.

Physical reserved-RAM ownership, cache coherence, timing and startup behavior remain open. The stock diagnostic-lifecycle results are bounded PC evidence and do not establish a device fault during ordinary use.

Evidence: `Digitone-E04-PC-reinitialization-policy-model.json`, `Digitone-E04-PC-reinitialization-admission.json`, `Digitone-E04-PC-reinitialization-policy-summary.json`; specification model `work/digitone_reinitialization_policy.py` and tests `work/test-PC-reinitialization-policy.py`, `work/test-PC-reinitialization-admission.py`.
'''
Path('outputs/Digitone-E04-PC-reinitialization-protection-policy.md').write_text(text,encoding='utf-8')
incident=Path('outputs/Digitone-E04-hardware-startup-incident.md');entry='\nEighteenth follow-up completed on 9 October: `Digitone-E04-PC-reinitialization-protection-policy.md` defines V1 as one initialization per fresh boot with no live pool reconstruction. Whole-operation rejection must precede command flags or page/handler changes. PC policy assertions and native state controls pass; injected initializer-only zero return is ignored by the actual setup caller. This is a specification/admission model, not an installed native guard. Command cleanup/return continuation, UI entry/close veto and persistent latch integration remain required. Original images and current guarded raw candidate remain unchanged.\n'
if entry.strip() not in incident.read_text():
 with incident.open('a',encoding='utf-8') as f:f.write(entry)
print('PASS',len(checks),'summary checks; policy defined, native enforcement not installed')
