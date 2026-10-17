# Digitone OS 1.42: outer protection for pattern replacement

**Follow-up:** [Busy-marker storage and fallback](Digitone-OS1.42-busy-marker-storage-and-fallback.md) identifies a provisional end-record payload storage candidate and tests nested-update, failure and missing-context behavior. The candidate's global ownership remains uncertified.

**No complete-update guard was recovered in the explicit UI replacement, fallback reset and import routes examined here.** These routes can select the canonical backing corresponding to the receiving pattern and overwrite it directly. There is no demonstrated inactive-bank build-and-publish transaction on these paths. The proposed root/scale reader must not assume an existing outer guard.

This is a bounded static finding, not proof that every indirect caller or runtime configuration lacks protection. It is also not an observed stock-firmware defect: the new queued root/scale snapshot reader remains a proposal. Original firmware and decoded executable hashes are unchanged; no firmware was edited, rebuilt, repacked, transmitted or flashed.

## 1. A concrete UI replacement route

Screen construction at `4003e4ca` installs vtable `40177ba8`. Its relevant entries are:

| Slot | Function | Recovered role |
|---|---|---|
| `+08` | `4003c8a0` | Screen input handler |
| `+30` | `4003b480` | Record capture operation |
| `+34` | `4003b50e` | Try replacement, otherwise capture and reset |
| `+38` | `4003b4ac` | Try replacement, otherwise capture |

The handler's jump table sends event codes 10, 11 and 12 to `4003d63e`. That branch calls `400d6974`, which selects slots `+30`, `+34` and `+38`, respectively, then tail-calls the selected method. The screen entry and these dispatch branches contain no explicit SR mask or audio-suppression call. Generic screen dispatch `400d6efc` tail-calls virtual slot `+08`; it contributes no such guard either.

The previously recovered input-task route reaches that generic screen dispatch. Its input-queue critical section restores SR before screen handling. The task's recovered initial mask is zero and the audio service is level five. Consequently, the queue-pop mask cannot be treated as an update-wide guard. Capture eligibility still depends on runtime mode and descriptor availability.

Both replacement methods obtain an index through:

`4012fe8e → 400a9ca4 → 40093b72`

`40093b72` reads the receiving backing pointer at `41342150`, then its index at `+16119`; `400a9ca4` clamps the index to 0..127. The methods obtain the project manager and pass that index to `40025628` at `4003b4d8` or `4003b53a`.

The index ties selection to the receiving pattern, but exact backing identity still matters. In the already established canonical-bank install case, the selected backing can be the active receiving backing. An alternate installed copy with the same index does not automatically alias it.

## 2. Record acquisition does not establish a protected commit

`40025628` obtains a stored record, checks its identity/index, resolves the selected pattern object's backing and copies **0x1611d bytes** into it at `400256ec`. Source is the acquired record at `record+4`; destination is the returned pattern backing. Subsequent operations copy additional associated data and notify objects.

Thus the acquired record is a source for an **in-place destination update**, not evidence that the receiving destination was constructed elsewhere and atomically published.

The record lookup helper `40137012` uses type checking and reference-management calls. No update-wide SR mask, receiving-pointer publication or known audio-suppression call was recovered in that helper's visible body. Reference acquisition protects an object's lifetime only to the extent its reference rules guarantee; it does not by itself establish exclusion of the interrupt reader. Called-helper internals and computed aliases are not all transitively certified by this finding.

The replacement method and its two direct UI callers contain no explicit SR operation spanning the copy. Notification and messages after the copy cannot establish protection during the copy.

## 3. The fallback reset route also reaches live backing

If `4003b50e` cannot restore a stored record, it calls `40025ada` at `4003b560` with reset enabled. That wrapper first captures the existing pattern into a record, then invokes `400208a0` at `40025bc4`.

`400208a0` retrieves the actual pattern backing and calls `400134e4` at `400208bc`. That initializer writes track defaults separately and iterates all eight tracks; notification follows it. The temporary record preserves previous content, but the reset itself still targets the selected backing.

No local SR mask or known audio-suppression call occurs in the recovered wrapper, pattern-default method or direct UI caller. Other reset callers include startup iteration and confirmation callbacks; their existence does not prove the ordinary UI reset is restricted to startup or inactive storage.

## 4. Import reaches the same class of destination

Confirmation callback `4003ac86` calls `4002528c` at `4003aca6`. The callback pointer is explicitly installed at `4003cee8`; it is not inferred from a coincidental function resemblance.

`4002528c` checks the input and, when pattern import is enabled, calls `400242ba` at `4002531e`. That method allocates and reads serialized input, retrieves project backing, computes the selected current-pattern destination and calls converter `40008de0` at `40024384`.

The converter writes expanded current storage directly. The temporary allocation holds input data; it does not establish an inactive destination transaction. The callback, import wrapper and converter caller contain no explicit SR mask or known audio-suppression call around this update. The complete modal-callback dispatch and storage-I/O internals remain outside the transitively proved set, so import has a broader caller uncertainty than the direct replacement UI route.

## 5. Existing suppression and mode mechanisms

There really is an audio suppression pair: `400eef48` saves the audio vector and substitutes a stub, while `400eef72` restores it. Neither was called by the recovered routes above. The raw executable pointer inventory also finds no literal pointers to either entry. This supports a lack of a recovered use; it is not a proof against computed/indirect calls or other suppression mechanisms.

The audio descriptor path also has an observed mode gate: mode 6 bypasses its handling. Direct stores to the mode variable `404dc2fc` were found in mode-setting functions `400071d6` and `4000722c`. These are separate from the examined replacement/reset/import routines, and no explicit calls to these setters were recovered in the local update routes. Mode changes elsewhere can suppress capture at a particular time, but no update-scoped set/restore bracket was established.

Similarly, the examined writers do not explicitly substitute the receiving backing pointer at `41342150` while they perform these writes. That is not a universal pointer-alias proof; it rules out treating the visible copy/reset sequence itself as an established inactive-build publication scheme.

The direct whole-pattern copy method `40022552` remains a separate reachability gap. No literal reference or decoded direct/PC-relative caller was recovered for that entry. Its body shows a direct backing-to-backing copy, but its presence alone does not prove a live runtime operation. It must not be counted as an independently demonstrated active UI route.

## Verification and implication for V1

Verification passed **29 exact executable byte anchors**, three UI jump-table cases and **13 local instruction-range scans**. The scans found no explicit SR operation or direct call to the known suppression pair in those ranges. They deliberately do not claim transitive coverage of all callees. The existing transaction/handoff model was rerun: all **12 scenarios** passed, including individual pair consistency versus a complete multi-track transaction. Detailed results are in `Digitone-outer-protection-check-results.json`.

SHA-256 remains:

- Original SysEx: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`
- Decoded section 3: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`

For V1, **do not rely on a stock outer transaction guard**. The safest next design audit is a concrete missing-context policy and bounded invalidation mechanism covering the recovered replacement, reset and import destinations, together with safe storage and cleanup. A short reader-side mask cannot repair an interrupted in-place update. An ISR must never wait for the paused writer. A full-copy interrupt mask is not justified without an audio timing budget.

Before implementing any mechanism, establish where its state can safely live, whether it must cover an entire pattern generation or just each track's complete pair, how nested or failed updates restore validity, and whether all relevant producers/writers participate. These remain static/PC-model tasks; no flashable output is warranted.
