from pathlib import Path
import json,hashlib
r=json.loads(Path('outputs/Digitone-E04-PC-rejection-continuations.json').read_text());old=json.loads(Path('outputs/Digitone-E04-PC-reinitialization-policy-summary.json').read_text())['hashes'];cfg=json.loads(Path('work/os144/PC_ONLY-atomic-storage-layout.json').read_text())
checks={'nine_native_controls':r['passed'] and len(r['cases'])==9,'original_images_preserved':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in old.items()),'raw_candidate_preserved':hashlib.sha256(Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes()).hexdigest()==cfg['main_sha256'] and hashlib.sha256(Path('work/os144/PC_ONLY-atomic-storage-payload.bin').read_bytes()).hexdigest()==cfg['payload_sha256'],'guard_not_installed':not r['native_policy_installed']}
assert all(checks.values())
Path('outputs/Digitone-E04-PC-rejection-continuations-summary.json').write_text(json.dumps({'passed':True,'PC_only':True,'checks':checks,'hardware_ready':False},indent=2))
report='''# Command cleanup and page rejection continuations

The tested stock continuations can reject matched diagnostic commands and selected page-manager operations without entering pool reconstruction. Nine bounded native PC controls pass. The host supplies the admission decision, message pointer or predicate result; no native guard or boot latch has been installed. Original firmware containers, E04 files and the current raw PC candidate are unchanged (hash checked).

## Command worker

Matched ENTER and EXIT operations are paused at `4008b85a` and `4008b88a`, before their diagnostic-flag stores. The proposed rejection follows the stock message-call path `4008b86a -> 4008b870 -> 4008cbe6 -> 4008cbe8 -> 4008b4ae`, supplying a PC fixture string "UNSUPPORTED: restart required" instead of the original "OK". Actual message-call, stack cleanup and loop instructions execute. This must be implemented with a dedicated rejection string; the stock success response is unsuitable. Jumping to `4008cbe6` without having pushed the message argument remains invalid. A quiet continuation can use the branch at `4008cbe8` without that argument, but offers no response by itself.

Two isolated post-parse controls preserve the watched queue, context, gates, audio vector and mode flag. A stronger continuous worker control executes its actual prologue/initialization, queue dequeue, parser, command comparisons, message call and return to the loop for two consecutive ENTER/EXIT requests. Both are removed once; the queue count becomes zero and read index advances twice, with no stack drift or diagnostic mutation. Queue/ring/packet contents are constructed host fixtures; there is no transport input.

The dequeue at `40001d6c` advances the ring and returns the pointer; it does not free that packet. The tested worker iteration has no separate packet destructor on this path. This verifies worker-level consumption and local stack cleanup, not end-to-end USB/MIDI producer ownership, packet reuse or response delivery. The test checks the message-call return, not a user-visible error protocol.

## Page selection

Manager `400e6352` acquires its actual stock mutex. A proposed denial at `400e637c`, after its lock-call argument cleanup and before child lookup/replacement, supplies false in D2 and follows `400e649a` through the real unlock/return epilogue. Uncontended and recursive-lock controls return false, restore saved registers, balance the stack and incoming interrupt control, and preserve the linked page and watched note state.

This verifies the manager's local refusal continuation. The complete application caller, earlier object construction/preparation and caller handling of false have not executed. The admission check must be early enough to exclude those earlier changes, or those callers must be verified separately. Refusing the later entry callback `400b25bc` alone is insufficient because manager list/selection mutation precedes that callback.

## Close request and already pending close

Close-request helper `400e5442` already has a refusal branch: its predicate at `400e5454` can lead to `400e5470`, restoring A2 and returning before setting page close flag +30 or requesting manager work. A supplied predicate result exercises this refusal with page/manager bytes unchanged in both lock fixtures. This is a usable local pre-mutation rejection point, not a native policy implementation.

For an already pending close, removal `400e6634` can skip a protected page after the close predicate, at `400e668a`, following its existing no-close branch to the next node and then the normal unlock epilogue. In both lock fixtures the page remains linked, its close flag stays set, and the diagnostic exit callback is never called. Saved registers, stack and mutex balance pass.

**Deferral has an observable side effect:** stock removal clears manager dispatch byte +22. A page that remains flagged may be reconsidered if removal is invoked again, but automatic retry/notification is not established. Thus this is a tested defer continuation, not a complete whole-operation rejection protocol. An explicit policy must prevent new diagnostic close requests or define how existing pending requests are retired/reported; clearing the page flag casually is not a tested solution.

The actual virtual-exit call at `400e6698` is followed directly by unlink/destruction; no return-value test grants it a veto. There are also other removal routes: `400e64b0` calls a page's exit directly at `400e651e` then unlinks it, and `400e65dc` removes a list node directly. A guard only in `400e5442` or the periodic remover does not cover those routes. Their caller reachability and pre-mutation refusal boundaries remain to be audited.

## Concrete result and next work

Local command cleanup and page-manager rejection/deferral continuations are now exercised in native PC execution. This narrows the blocker from unknown returns to **outer route coverage**: verify application selection caller handling, directed removal/destruction and pending-close policy before installing enforcement. A persistent cold-start latch and common initializer fail-closed continuation still require their own implementation and checks. Do not substitute a void callback return or initializer-only return for transaction rejection.

These controls use constructed state and host-selected branches. They do not prove live scheduler/interrupt interleavings, all RAM aliases, physical cache behavior or timing, and they do not establish hardware readiness.

Evidence: `Digitone-E04-PC-rejection-continuations.json`, `Digitone-E04-PC-rejection-continuations-summary.json`; reproduction: `work/test-PC-rejection-continuations.py`.
'''
Path('outputs/Digitone-E04-PC-rejection-continuations-review.md').write_text(report)
with Path('outputs/Digitone-E04-hardware-startup-incident.md').open('a') as f:f.write('\n\n## Nineteenth follow-up: local rejection continuations\n\n'+report.split('## Command worker')[0].split('\n',2)[2]+'\nSee `Digitone-E04-PC-rejection-continuations-review.md`. Outer selection/direct removal coverage and pending-close handling remain unresolved; no native guard installed.\n')
print('PASS nine controls and unchanged-image checks; report saved')
