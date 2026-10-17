from pathlib import Path
import json,hashlib
r=json.loads(Path('outputs/Digitone-E04-PC-removal-bypass-controls.json').read_text());refs=json.loads(Path('outputs/Digitone-E04-PC-removal-reference-scan.json').read_text());old=json.loads(Path('outputs/Digitone-E04-PC-reinitialization-policy-summary.json').read_text())['hashes'];cfg=json.loads(Path('work/os144/PC_ONLY-atomic-storage-layout.json').read_text())
checks={'ten_controls_pass':r['passed'] and len(r['cases'])==10,'original_images_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in old.items()),'raw_PC_candidate_unchanged':hashlib.sha256(Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes()).hexdigest()==cfg['main_sha256'] and hashlib.sha256(Path('work/os144/PC_ONLY-atomic-storage-payload.bin').read_bytes()).hexdigest()==cfg['payload_sha256'],'guard_uninstalled':not r['native_guard_installed']}
assert all(checks.values());Path('outputs/Digitone-E04-PC-removal-bypass-summary.json').write_text(json.dumps({'passed':True,'PC_only':True,'hardware_ready':False,'checks':checks,'reference_scan':refs},indent=2))
report='''# Direct-removal bypasses and their callers

Ten bounded native PC controls pass. The direct-removal caller recovered from stock 1.44 MAIN is an abort operation for **UI Test View**, not a confirmed removal path for **AudioTestMenuView**. A mutex-protected local false-return continuation is now tested, including strong-reference cleanup. No native guard or latch is installed; firmware containers and current raw PC candidate are unchanged (hash checked).

## Recovered references and route

The aligned direct/relative-call candidate scan and literal scan of stock MAIN recover one call to `400e64b0`, at `4008de68`. Its instruction boundary is validated by actual execution in the caller controls. No direct/relative candidate or literal target is recovered for `400e65dc` or the nearby selection wrapper `400e656e`. Absence of these references does not prove absence of a computed target or establish dead code.

The sole recovered directed-removal chain is:

`#ABORT_UI_TEST` match -> command call `4008c1b4 -> 4008ddca` -> closure target `4008de1e` submitted by `40018bc4` -> application singleton `4014b4d8` -> manager at application +40 -> lookup `400e610e` using name `401dfe30` ("UI Test View") -> `4008de68 -> 400e64b0`.

The target pointer `4008de1e` is loaded into the queued callable at `4008dde6`. This is a registered/deferred callback, not a direct command-to-removal execution proof. Callback submission/dispatch scheduling is statically traced here; the native caller control starts at the callback entry and executes the singleton getter, lookup, removal refusal and cleanup.

The UI-test constructor `4008fe9a` passes that same "UI Test View" constant to its base constructor, which stores the page name at +28. The audio-test constructor at `400b2b5e` uses `401e197a`, "AudioTestMenuView". Native lookup controls with these two controlled names confirm: the audio-test page is not selected by this UI-abort callback; the UI-test page is selected. This narrows the known route and avoids assuming that a generic remover's ability to remove an audio page establishes an actual audio-page caller. Names, manager/list/reference/task state are fixtures; all runtime naming writers and computed routes are not certified.

## Direct-removal refusal and cleanup

`400e64b0` has an existing pre-lock false-return path `400e64c8 -> 400e6564`. Two controls exercise it without changing page, node, pool/context hashes or handle reference counts, with balanced saved registers/stack/interrupt control. This proves its epilogue, not a safe concurrent page-inspection point before acquiring ownership.

A stronger candidate boundary is **400e6500**, after the actual manager mutex is acquired, the weak handle is resolved into a strong temporary by `4015ed74`, and call arguments are cleaned up. In the controlled valid-handle case, the native reference count rises from 2 to 3. Rejection supplies D3=0 and follows **400e654c** to release that temporary, unlock and return false. It deliberately skips `400e6546`/selection recomputation, which could otherwise change selected-page state despite refusing removal.

Uncontended and recursive-mutex controls restore the original strong count, mutex ownership/recursion, registers, stack and interrupt control. Linked page/node bytes and watched note state plus pool/context hashes remain unchanged. The host supplies the admission result and branch; no guard machine code executes. A real guard must validate the resolved page, match the appropriate protected identity and preserve these cleanup contracts. A null or expired handle must follow the stock validity logic; this task's locked controls use valid handles.

## Outer caller does not honor the refusal

Four continuous callback controls execute `4008de1e` with UI/audio names and both mutex states. The actual lookup and caller reference-copy/release operations execute. In UI-name cases the mutex-protected refusal above is supplied; all temporary strong/weak references return to their starting counts and the page stays linked. In audio-name cases the remover is never reached.

**Regardless of lookup success or false removal return, the caller clears UI-test global `4137c72c` at `4008de9a`.** It never tests the remover's result. Thus a local refusal is balanced but is not a whole UI-abort transaction veto. If V1 must refuse this UI-test abort operation, denial belongs at the matched command boundary before `4008ddca` queues the callback, with an explicit rejection response; the already tested diagnostic command message/loop cleanup pattern is a candidate, not a tested ABORT_UI_TEST enforcement branch.

This UI-test flag is separate from the diagnostic flag `402a0e50`. The recovered name-specific caller is not evidence that the audio-test page triggers this abort route. There is no reason in these results alone to prohibit ordinary, unrelated UI-page removal.

## Front-node remover

`400e65dc` takes the manager's +18 tail node, unlinks it, releases its stored shared reference, frees the node and recomputes selection under the manager mutex. It does not invoke the removed page's virtual exit callback. Two native controls use an actual stock-heap-allocated node and execute the full function, actual unlink/reference release/free/recompute/unlock, with both mutex states. The node is removed, its strong count drops from 2 to 1, and watched note state/pool/context are preserved. The diagnostic exit callback is not called.

Consequently this function is not a demonstrated note-pool reinitialization path by itself. It could still orphan page/handler state if a protected live page were removed through it; that requires caller and object-lifetime evidence. No actual caller was recovered, so its live reachability is unproven. A caller-safe rejection cannot be certified by fabricating a void return from a function with unknown caller expectations.

## What is closed and what remains

Closed within these PC fixtures: the recovered directed caller's target-name restriction, its complete local reference cleanup, its unconditional UI-test flag clear, a mutex-protected local rejection continuation, and the front remover's absence of exit-callback invocation during full controlled execution.

Remaining for enforcement: actual AudioTestMenuView selection/caller handling, any computed direct/front-removal callers, explicit treatment of already-pending close requests, and boot-lifetime latch/common initializer protection. This task narrows two suspected bypasses; it does not certify every page transition, global RAM ownership, physical cache coherence, timing or hardware readiness.

Evidence: `Digitone-E04-PC-removal-reference-scan.json`, `Digitone-E04-PC-removal-bypass-controls.json`, `Digitone-E04-PC-removal-bypass-summary.json`. Reproduce with `work/scan-PC-removal-callers.py` and `work/test-PC-removal-bypass-controls.py`.
'''
Path('outputs/Digitone-E04-PC-removal-bypass-review.md').write_text(report)
with Path('outputs/Digitone-E04-hardware-startup-incident.md').open('a') as f:f.write('\n\n## Twentieth follow-up: direct-removal bypass callers\n\nTen native PC controls pass. Sole recovered directed-removal caller aborts "UI Test View", with native name-lookup controls skipping "AudioTestMenuView". Locked refusal balances strong reference and mutex cleanup but the caller still clears the separate UI-test flag. Unreferenced front remover executes without an exit callback in constructed heap-backed controls; computed callers remain unproven. No guard installed, original and raw candidate hashes unchanged. See `Digitone-E04-PC-removal-bypass-review.md`.\n')
print('PASS ten native controls and unchanged-file checks; report saved')
