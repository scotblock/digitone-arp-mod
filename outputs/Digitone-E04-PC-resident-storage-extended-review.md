# Extended deferred-storage ownership audit

Firmware and resident overlay remain unchanged. This audit extends the relocated queue checks for `47be2860..47be29f0`.

## New execution coverage

One restored native-initialized session ran approximately 8.15 model seconds with panel notes, a held multi-note workload, MIDI CC64/note release, transport and an observed pattern-backing change. No forced semaphore unblock was enabled. The queue remained entirely zero in this LIVE workload.

Guest stores through all modeled DDR aliases, host `mem_write` API calls and the known native bulk routines were monitored. None wrote the queue. There were 259,850 observed memcpy entries and 63 memset entries, with no destination interval overlapping the queue. These are known bulk entries, not a claim that every possible memory writer was intercepted.

DMA screening read initial TCDs, guest TCD writes (including incoming field values), and software transfer entries. The 92,124 distinct descriptor/programming observations span 11 channels. Conservative destination envelopes did not intersect any modeled alias of the queue. The report is condensed by channel with overlap/unknown counts and examples; aggregate min/max per channel is not a single actual transfer range.

Partial register-programming observations include scatter-gather flags with zero next-descriptor addresses. They are not proof of active zero-link transfers, and no successor-chain exclusion is certified. Host API watching cannot certify DMA/device writes outside this model. Physical DMA configuration, cache behavior and transfer timing remain unvalidated.

## Copier path

The aligned caller screen finds exactly one direct call to `4029c4b0`: startup JSR at `40000538`, with return `4000053e`. The second literal at `4000049a` belongs to a CMPA exclusive-end bound for the stock SRAM initialization copy; it is not another function-pointer reference. No reset-stub/copier entry occurred in the extended playback/confirmed-handoff session.

This bounds observed normal execution. It does not exclude computed or interior calls, reconstructed targets, or full reset-vector replay. Earlier negative controls already show an actual recopy clears the queue; cold-only provenance or explicit epoch/invalidation remains necessary.

## Static computed-write screen

Rooted stock 1.44 disassembly from startup, recovered interrupt/input/UI/release paths and prior task entries reached 40,307 instructions without hitting the screening budget. It inventories 11,934 candidate computed-memory destinations, 2,743 unresolved indirect control edges and 159 unknown decode boundaries. These counts are a worklist, not resolved alias results: unsupported ColdFire instructions and indirect flow limit the decoder's coverage. Even a zero literal hit cannot establish exclusive ownership.

**Result:** no conflicting writer, observed DMA envelope or copier replay was found in the new execution coverage. Native initialization remains established in the earlier PC runs. Global computed-write ownership, scatter-gather successors, cold-only replay provenance and physical DMA remain open. No hardware-ready build was produced.

Evidence: `Digitone-E04-PC-resident-storage-extended-runtime.json`, `Digitone-E04-PC-resident-copier-callers.json`, `Digitone-E04-PC-resident-computed-write-screen.json`, and `Digitone-E04-PC-resident-storage-extended-summary.json`.
