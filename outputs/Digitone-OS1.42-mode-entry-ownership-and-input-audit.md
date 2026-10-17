# Digitone OS 1.42: mode-entry ownership and input audit

Firmware remains unchanged. The proposed trailer and setup/reset hooks remain unimplemented.

## Result

The recovered mode-entry callback does not establish the required ownership or producer-stop conditions. In bounded execution it switches audio handlers while preserving a controlled queued event, retained template, cached payload pointer and ordinary MIDI receive-enable bits.

With the receive gate enabled before mode entry, the actual first-queue dispatch branch still reaches the Note On handler afterward. With that gate disabled, Note On bypasses dispatch, but SysEx still reaches its handler. These are task-admission results, not execution of complete note production or SysEx processing.

No full mode-entry shutdown contract is certified. The trailer and hook should remain unimplemented.

## Mode-entry route and ownership

The constructor registers entry invoker `400ae458`, which tail-calls `400d95cc`. That helper installs alternate audio handler `400d924e`, timer callback `400d920c` and interrupt-priority value 5. It does not locally release the payload pool, drain the normal scheduler queue or clear retained arp templates.

The PC test starts with an actually published type-zero event and an actual counted template copy at `41345f08`, giving two references to one record. A controlled cached pointer is placed at the recovered track-zero cache location `0x431d1758 + 0x414 + 60*0x48 + 0x38`. Executing the registered entry invoker preserves both counted references, the queue head, template pointer and cache pointer. The caller's SR mask is also preserved.

This tests the existing invoker/helper with deliberately supplied preexisting owners. It does not establish that a real outer page transition permits those owners at entry. The surrounding mode-entry task and child-page operations remain outside execution.

The common entry-callback dispatcher `400d6d46` clears the page's close-request byte, stores its manager and invokes entry callbacks. Its local body does not itself supply a record-ownership check or receive-task acknowledgement.

## MIDI receive gates

The confirmed receive-task graph at `400db15a..400db300` dispatches packets from two queues:

- First queue: ordinary messages test mask `0x1` of `4131ba1c` at `400db220..400db228`.
- Second queue: ordinary messages test mask `0x2` at `400db286..400db28e`.
- Both queue branches admit status `f0` before those enable-bit tests.

The registered mode-entry callback leaves a supplied gate value of 3 unchanged. Separate runs also preserve supplied first-queue enabled/disabled values across entry.

The bounded packet tests begin after dequeue, with a controlled valid packet record and the actual status-dispatch table `401aade0`. They execute to these boundaries:

1. Enabled first-queue Note On: actual indirect dispatch at `400db246` reaches `400dc8c4`.
2. Disabled first-queue Note On: bypasses dispatch and reaches `400db24c`.
3. Disabled ordinary receive gate with SysEx: still dispatches through the table's status-15 entry.

No complete handler or hardware MIDI input is executed. The second queue is inspected structurally, not executed here. Even a proposed clearing of ordinary receive bits would therefore need separate treatment of SysEx and other producers/writers.

The local receive-task graph does not read the audio vector or test-mode flag `40253e80`. Exact absolute-literal discovery finds only the two gate reads; writers may use containing-object offsets or computed pointers, so the gate's complete writer/lifetime provenance remains open.

## Test-mode entry

The command text is `#ENTER_TEST_MODE`. Its recovered matched path sets `40253e80` and calls `4008dfd2`, which clears diagnostic channel/buffer bookkeeping and installs alternate test handlers `4008dce0` and `4008d974`.

Confirmed graphs for that helper and its two clearing routines use diagnostic base `429a3c14`. Their local bodies contain no payload-owner, retained-template or ordinary receive-gate references. The test-mode flag itself has only the recovered entry store and exit clear in the exact-literal search.

These structural results do not certify every upstream command-handler action or computed alias. They identify handler diversion and diagnostic reset, rather than a demonstrated payload cleanup or receive-task stop.

## What remains before a usable barrier

Switching the normal audio vector can divert the normal queue consumer, but does not prove that all owners have been retired or prevent additional input from being dispatched. The page-manager mutex from the previous audit serializes page operations; it is not an established shared lock for the MIDI receive task.

The missing contract is still explicit exclusion or completion of every relevant producer/consumer, retained template/cache accounting, and completion of active pattern writers before any pool reconstruction. Ordinary receive bits alone do not cover that contract.

These results neither demonstrate a stock-device failure nor prove the real transition normally carries live records. They reject using the recovered mode-entry helper alone as proof of safe pool quiescence.

## Validation

14 execution checks passed across four recorded cases totaling 70 instruction steps. Nine structural checks passed across nine confirmed-entry graphs covering 296 instructions. Source SysEx and decoded image hashes remain unchanged.

The custom interpreter is not independently validated against ColdFire hardware. Full UI/task scheduling, complete note and SysEx handlers, the second receive queue and transitive child-page behavior remain outside execution.

The next focused evidence gap is the live note handler's suppression conditions after packet admission, together with the writer provenance of the receive-enable field. Keep the storage extension and hooks unimplemented while those conditions are traced.

Details: `Digitone-mode-entry-ownership-input-results.json` and `Digitone-mode-entry-input-graphs.json`.
