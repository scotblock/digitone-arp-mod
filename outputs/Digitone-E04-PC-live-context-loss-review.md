# Live-note context loss: creation-to-pitch trace

The live note does not acquire context in this route. A different stock creator copies its descriptor into a freshly cleared pool event and immediately publishes it, bypassing the existing capture and copy hooks. Selection receives zero metadata and correctly disables retained context; the pitch helper subsequently returns the original note. This is a concrete patch-coverage gap in the observed PC workload, rather than evidence of an unexplained context corruption. Firmware remains unchanged.

## Observed path

The first selected live note is MIDI 64, the E in the injected C/E/G chord. Its event is `0x419ebf94`. The earlier C does not become this selected live event; event addresses are analyzed from their last allocation, not assumed to keep ownership across recycling.

| Stage | Evidence |
|---|---|
| Allocation | Stock live creator `400ff3ec` calls the allocator at `400ff4fe`, returning at `400ff504`. Its event slot `0x47be1038` is cleared by the existing allocation hook. |
| Descriptor copy | Call `400ff5f6 → 400fbad8` copies 72 stock bytes from `0x43221548` to `0x419ebf94`. Source and destination fields match immediately afterward; metadata is still zero. |
| Publication | Creator tail-jumps at `400ff60a` to the immediate publisher `40100252`; caller return is `400eb0a0`. This bypasses the ordered-timestamp publisher `40100178` used by the sequencer. |
| Capture coverage | No producer-capture call for this event generation and no nonzero write to its candidate slot. Existing `copy`/`first_copy` helpers are not entered in this run. |
| Selection snapshot | `47be0184` resolves the pool event to its recognized candidate slot and returns zero; slot recognition succeeds. |
| Commit | `47be004e` receives identity 2, word 0 and track 0 with busy count 1. It succeeds and replaces `[1, 800000be, 1, 80000000]` with `[2, 0, 0, 0]`. |
| Pitch read | At the first subsequent arp pitch, busy count and identity checks pass. Cookie comparison `47be0106` branches to `47be010e`, returning zero context because expected cookie `80000000` meets stored cookie 0. |

The valid sequencer event provides context `800000be` and changes 60 to 59. All 26 subsequent zero-context quantizer calls pass their original pitch through. The instrumented note/context signature matches the preceding uninstrumented mixed workload. No halt, DSP error or payload change is observed.

## Static producer layout

Creator `400ff3ec` builds live descriptors at `4321ff34 + track*2a18 + note_index*72 + 414`. For the selected track-0 note 64, this resolves to `43221548`. It then allocates a normal pool event, performs the raw descriptor copy and publishes through `40100252` under the stock publisher's interrupt mask. Two additional raw-copy sites, `400ff5ac` and `400ff5d4`, appear in the creator's alternate selection branch; neither executes in this workload.

The source descriptor is outside the helper's recognized event-pool/cache metadata map. Redirecting this copy to the existing metadata-copy helper alone would therefore still read zero source context. The missing operation must capture the live descriptor's correct pattern context or transfer an already owned snapshot, rather than borrowing the previous sequencer context.

## Verification and next step

22 automated evidence checks pass. The focused trace contains 282 boundary records, 2382 helper instruction entries and 1946 private-storage writes, below all recording limits. Original E04 hashes are reverified unchanged. No corrected package or additional helper overlay was generated.

Next audit which receiving pattern owns the input record passed to `400ff3ec`, and where its original root/scale can be captured before descriptor copying/publication. Cover its direct and alternate copy paths, note-off selection changes, allocation failure and pattern replacement before implementing a PC-only fix. Do not weaken the final cookie guard: it is correctly rejecting absent context.

Evidence: `Digitone-E04-PC-live-context-trace.json`, `Digitone-E04-PC-live-context-loss-summary.json`, `work/PC-context-helper-disassembly.txt`, and `work/PC-live-origin-disassembly.txt`. Physical startup failure, cache coherence, RAM ownership, timing and the corrected packaged-loader path remain outside this trace.
