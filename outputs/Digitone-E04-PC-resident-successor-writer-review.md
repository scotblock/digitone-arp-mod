# DMA successors and high-reach computed writers — PC audit

Firmware and resident overlay remain unchanged. This closes the observed successor-pointer gap and narrows specific computed-writer families; it does not establish exclusive physical ownership.

## Successors from executed transfers

The earlier observer saw partial register-programming states, and its software-channel wrapper did not see chains executed inside Digiemu's native fast engine. This run explicitly disables that fast DMA path for tracing. Software `_run` records descriptors before payload movement; SSI actual major completion records the descriptors it consumes. This is a disclosed model execution-path change, not a physical timing/equivalence claim.

The final workload runs 6.35 model seconds through panel notes, held voices, MIDI sustain/release and a confirmed pattern-backing replacement. It follows 371,475 software scatter-gather traversals through 39 concrete descriptor locations, with no refused transfer or software DMA error. Every observed successor address is readable, aligned and outside the queue. Its loaded descriptor's conservative payload destination envelope also avoids all eight modeled aliases of `47be2860..47be29f0`. Zero successor pointers from the earlier partial-programming screen are not reproduced as executed chains.

All observed minor-link targets are self-links on channels 30, 42 and 47; there is no observed link to a new unexamined channel. Their ESG successors are concrete. Non-ESG observed destinations are either modulo bounded or drifting outside DDR; no nonzero-DDR-drift example appears in this workload. The emulator counts but does not execute minor-link requests, so actual request/reload/arbitration, future reprogramming, extreme address wrap and physical effects remain unverified. This resolves target identities and observed destination topology, not hardware link scheduling.

## Highest-reach writes

The stock boot DDR clear at `400004b2` uses fixed `4028f000..4322ae60` bounds and 16-byte zero stores. The queue is above its exclusive end. Stock SRAM initialization at `4000045c` writes only `80000000..80010000` in two spans. These decoded fixed loops exclude the queue.

Generic memcpy/memset accept caller-provided destinations, so inspection of their bounded loops alone cannot prove ownership. Execution groups these calls by actual return address:

- Largest observed memcpy caller `4009bff8` uses fixed 1,184-byte copies and observed SRAM destinations. Caller instructions load size `04a0` and base offsets `05a0`.
- Pattern/data caller `4000a4b8` uses fixed 304-byte copy at `A2+2df6`; paired memset return `4000a4a6` clears 218 bytes at `A2+2f26`. Incoming A2 ownership across all callers is not certified.
- Caller `4001d68a` requests 12 bytes through malloc wrapper `400e96c0`, then copies exactly 12 bytes to its returned D0 pointer. It excludes the queue under the recovered intact primary-heap bounds.
- The nearest observed DDR copy destinations are the buffer family returning at `4018ab94`, up to 29 bytes, and the allocation/copy caller above. Their observed ends are below `41c1901a`, far below the queue. The buffer function has multiple incoming paths; its universal pointer provenance remains unresolved.

No guest write, host API write or monitored bulk destination reached the queue. Dynamic destinations and lengths are workload facts, not global bounds for every possible base pointer. Malformed lengths, corrupted allocator metadata and unknown computed/interior entries remain outside this proof.

## Remaining focused work

Trace the incoming A2/base-pointer ownership for the fixed pattern/data copies and the multiple buffer paths near `4018ab94`. Extend topology evidence to configurations outside the exercised workload. Physical self-link behavior, all DMA/device writers, cold-only copier provenance and global ownership remain unresolved; no hardware-ready build was produced.

Evidence: `Digitone-E04-PC-resident-successor-writer-summary.json`, `Digitone-E04-PC-resident-DMA-successor-writers.json`, `Digitone-E04-PC-resident-high-reach-writer-bounds.json`, and `Digitone-E04-PC-resident-bulk-caller-windows.json`.
