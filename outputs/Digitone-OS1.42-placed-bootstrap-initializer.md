# Resident placement and full stock initializer — PC-only

54 checks passed. A concrete placement now fits within the previously identified resident interval, and a fetch-overlay test connects the early allocation to the entire recovered stock initializer. This establishes a bounded executable layout and initializer connection in the PC model, **not globally certified executable ownership or a complete device startup**. Firmware and decoded-image hashes remain unchanged. No flashable output was generated.

| Resident block | Address | Bytes |
|---|---|---:|
| Bootstrap, including unready owner publication | `40241ca0` | 392 |
| Relocation table | `40241e28` | 216 |
| First split clear | `40241f00` | 54 |
| Second split clear | `40241f36` | 54 |
| Startup continuation wrapper | `40241f6c` | 18 |
| Initializer dispatcher | `40241f7e` | 26 |
| Displaced initializer trampoline | `40241f98` | 16 |

The occupied interval ends at `40241fa8`: 776 bytes used, 88 remaining before `40242000`. Original bytes in this interval are zero. The counted 119-entry startup table ends at `40241c94`; its traversal excludes this layout. The original initialized-data copy sources and the BSS clear start at `40242000`, also excluding the layout. These are concrete boundary checks. Computed pointers, unknown consumers of padding, and physical cache/MMU behavior are not globally excluded by them.

The 166-byte initializer wrapper lives in the allocated code reserve after the existing 1,678 helper bytes. Code usage is now 1,844 of the reserved 4,096 bytes. The owner still requests `15c80` from the stock allocator and returns `419a38c0` in this cold fixture. All original records end at `owner+14100`; metadata ends at `owner+14c70`; code starts at `owner+14c80`.

The startup overlay replaces the ten bytes at `40000542..4000054c`: the original four-byte clear call and following six-byte LEA. Its wrapper calls the bootstrap, replays the LEA, and resumes at the intact instruction at `4000054c`. The real cache-control writes then execute. The successful bootstrap publishes the existing stock owner pointer at `4199d590` only after allocation, copying, relocation, header initialization and staging erasure. Readiness remains zero. No additional global pointer storage is introduced.

The initializer overlay replaces the ten displaced bytes at `400f0504..400f050e`. Its resident dispatcher finds the allocated RAM wrapper. That wrapper checks the actual argument (158), non-null owner, metadata magic, version and length before mutating stock state. It masks interrupts and clears the proposed readiness, busy/fault and context fields, including on reentry. It calls a trampoline that replays the original pushes and LEA, then executes the unchanged stock initializer from `400f050e` through its return. The stock non-null-owner branch skips its own allocation.

The real caller at `4009bcb8` is executed, including its argument push and cleanup. Both fixed-pool loops and the complete 64-record owner-linking loop execute. All links match the stock `504`-byte record stride. A separate run through the unmodified initializer with the same allocation produces identical original owner-record and fixed-pool/global bytes. Proposed code bytes survive initialization unchanged. The wrapper sets readiness to one only after stock return, restores saved status and callee registers, and balances the caller argument. The relocated resolver then reads the actual initialized owner successfully.

Reentry also passes. It resets proposed contexts because the stock initializer resets the original record identities. Wrong-argument, damaged-header and null-owner cases reach a masked terminal self-loop before any stock initializer mutation. This is proposed fail-closed behavior, not verified graceful recovery.

The outstanding connection is the application/scheduler path **between** cache handoff at `40000568` and the caller at `4009bcb8`. The test enters these recovered boundaries separately; it does not execute everything between them. Therefore preservation of the early allocation, owner pointer and heap state over that entire path remains unproved. The application entry creates a startup thread; its complete execution and startup callbacks still need tracing. Literal owner-pointer references in the main image are concentrated in the initializer, but that alone cannot exclude computed or bulk writes.

Next: execute or trace that intervening startup path and its callbacks, checking early owner/heap preservation before the initializer. Also complete executable-interval ownership and inherited cache-state audits. Physical cache coherence remains unverified, and this work does not establish readiness for flashing.

Detailed cases are in `Digitone-placed-bootstrap-initializer-results.json`; resident and RAM-wrapper disassembly is in `Digitone-placed-bootstrap-initializer-instructions.txt`. This uses instruction-fetch overlays, the project's custom interpreter, one modeled hardware register, and previously validated summaries for long clear loops. It does not write modified firmware bytes to disk.
