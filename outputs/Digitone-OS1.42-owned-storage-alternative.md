# Digitone OS 1.42 — explicitly owned storage alternative

Read-only investigation, 3 October 2026. No instructions, container sections or firmware bytes were changed; no flashable output was produced.

**The strongest candidate found is a 16-byte trailer explicitly added to the existing persistent payload-pool allocation.** It uses the pool's established owner pointer, avoids the uncertain queue sentinel bytes and does not require a separate spare global to hold a new pointer. This is a design proposal supported by byte evidence and PC specification checks, not an implemented or fully validated firmware change.

## Compare the approaches

| Approach | Ownership mechanism | Main complication | Assessment |
|---|---|---|---|
| New startup allocation | Existing allocator reserves a block until released | Still needs an owned, persistent location for its pointer, plus failure and initialization handling | Viable if a pointer holder is designed |
| Shrink or move the heap boundary | Original allocator is explicitly excluded from a reserved region | Buddy order, unit count, free-list construction and hardcoded free bounds must remain consistent | Larger change than eight bytes of state justify |
| Extend the existing persistent pool allocation with a trailer | Existing allocation owns both its records and the explicitly requested trailer | Need bounds/lifetime audit of the pool's record users and initialization integration | Preferred next investigation |

Changing only the stored heap-end word at `401fe59c` is not an established reservation mechanism. Allocation uses maximum order 20 and `0x100000` 16-byte units; the free path at `400dadae` also uses hardcoded `base + 0x00fffff0`. The recovered allocator lazily creates a whole free block from the unit count. A smaller end value alone would not make these mechanisms exclude a tail region. Reducing the maximum order by one would halve the managed heap, assuming the other fields were updated consistently; that is excessive for this feature.

## Existing allocation and proposed layout

Startup wrapper `4009bcb8` passes `0x9e` (158) to initializer `400f0504`. The initializer computes a record stride of `0x14 + 8 × 158 = 0x504` bytes and allocates 64 records:

| Item | Stock | Proposed |
|---|---:|---:|
| Record count | 64 | 64 |
| Record stride | `0x504` | `0x504` |
| Record area | `0x14100` = 82,176 bytes | Same |
| Explicit trailer | None | 16 bytes |
| Requested allocation | `0x14100` | `0x14110` = 82,192 bytes |
| Calculated buddy block | `0x20000` = 131,072 bytes | Same |

Let `P = *(4199d590)`, the existing persistent pool pointer. The proposed state lives at:

`P + 0x14100 .. P + 0x14110` (end excluded)

The last ordinary record starts at `P + 0x13bfc` and ends exactly at trailer start. The trailer is 16-byte aligned. Its first eight bytes can carry the previously proposed depth and readiness/fault words; the other eight can identify the layout and initialization state. The precise field encoding remains to be designed.

The stock allocator's request normalization and order selection at `400dac32..400dac66` support the calculated 128 KB block size for both requests. This arithmetic does **not** execute the actual allocator. Nevertheless, it identifies a useful property: the explicit reservation should not increase the rounded heap footprint under the recovered configuration. We should request the extra bytes explicitly rather than treat undocumented rounding slack as the feature's contract.

## Why the existing owner is useful

There are three exact references to persistent pointer `4199d590`: the allocation-present test, assignment and reuse load in `400f0504`. The recovered initializer skips allocation when that owner is already nonzero.

Its records are built from the base and stride. The final-record calculation at `400f05ba..400f05ca` recomputes `64 × stride - stride`; it does not use the allocation request variable. Therefore increasing the **request** without increasing the **stride or record count** need not enlarge the record free list into the trailer.

Record pop `400f05d6` takes entries from free head `4199fe98` through record `+10`. Reference release `400f05f8` returns records to that same pool; it does not free the enclosing heap allocation. Recovered direct calls to pop are `40093e90` and `400dc5c8`; recovered direct calls to release are `400f066e` and `400f06a8`. The expanded direct-transfer search finds only `4009bcbc` targeting the initializer. These are recovered routes, not proof against all computed callers.

The parameter-list producer at `40093bd4` has a concrete bound: it visits 79 source entries, writes four bytes in each eight-byte output slot starting at record `+14`, and stores the final count at `+08`. That recovered writer is comfortably inside a `0x504` record. Other payload users still require their bounds to be checked; the original 158-entry capacity is a layout contract, not a substitute for that audit.

## Initialization and failure handling

Normal audio setup calls the initializer through `4009bcec → 4009bcb8`, before queue initialization at `4009bd08` and audio-vector installation at `4009bd52`. This gives a concrete pre-audio initialization opportunity.

Stock code stores the allocated pointer into `4199d590` at `400f058c`, then clears the block at `400f0592`. The proposal must account for that publication order. A clean design would:

1. Allocate the explicitly extended block while retaining the returned pointer locally.
2. Validate allocation success before writing through it.
3. Initialize the record area and trailer, with snapshot capture unavailable.
4. Publish the initialized owner and finish the original free-list construction.
5. Enable snapshot capture only after setup completes, before installing the audio handler.

No actual instruction rearrangement is proposed as verified yet. Register preservation, stack use, call results and the final publication point need an integration audit. The allocator uses scheduler locking, so allocation belongs in setup; the audio capture path should only derive and read the trailer pointer, with the previously proposed short interrupt-protected snapshot operation.

Allocation exhaustion reaches a negative unit index and address translator `400da9e0` converts that to null. The stock pool initializer does not locally reject null before its clear and link writes. Our specification rejects a null owner and disables the feature, but that does not fix stock startup's existing allocation-failure behavior. A later implementation must choose an explicit failure path rather than claim the unmodified initializer handles it safely.

A nonzero owner during reinitialization reuses the allocation and reconstructs record lists. The proposed trailer must not be reset during a live transaction or while records are retained. Reinitialization requires invalidating readiness and proving quiescence. No live reset is authorized or implemented by this investigation.

## PC-only checks

The investigation verifies 42 exact instruction anchors and runs 17 layout/protocol checks:

- All 64 maximum-capacity record ranges and header writes exclude the trailer.
- All 79-entry writes of the recovered producer exclude it.
- The trailer fits at all 128 aligned whole-block placements inside the configured heap.
- 2,048 simulated full-record writes across recycling cycles preserve a 16-byte marker in the trailer.
- Null, partial initialization, active writer depth and a fault latch disable capture; completed initialization permits it.
- Original and extended requests have the same calculated rounded footprint.

These are specification and arithmetic checks. They are not firmware emulation, allocator stress testing, hardware canary validation or proof of every payload consumer. Detailed results are in `Digitone-owned-storage-alternative-results.json`.

## Next focused audit

The storage problem is now narrowed to an explicit existing allocation, instead of globally unused sentinel bytes. The next target is to trace **every recovered payload-record producer and consumer**, including pointers retained in playback events, and establish that their writes cannot extend past a record. Then confirm owner lifetime/reinitialization and design the initialization hook with register and failure-path preservation.

This approach still assumes a functioning stock allocator and valid original data structures. It provides an ownership mechanism against normal allocator reuse; it does not claim protection against arbitrary existing memory corruption. Exception cleanup and balanced pattern-writer guards remain separate implementation requirements.

Source hashes are unchanged:

- SysEx: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`
- Decoded section 3: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`
