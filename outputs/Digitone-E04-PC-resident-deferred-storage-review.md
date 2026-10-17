# Deferred-release storage: native initialization and bounded ownership

The former `47fa2000` queue was an outside-region test fixture. A separate PC-only variant relocates its 400 bytes to `47be2860..47be29f0` (end exclusive), inside the existing payload's zero padding. Earlier firmware, code and fixture binaries remain unchanged. Only the resident variant embeds the new queue addresses.

## Native initialization established in the PC path

The existing payload and its embedded copy source already contain 400 zero bytes at this interval. Source address is `4029ee10`; the interval is within the unchanged copy extent. No extra native memset or firmware extension is needed for its initial zero contents.

Three native cold startup runs (default, restored project, optional feature disabled) begin with deliberately dirty `a5` queue bytes. Guest copier instruction `4029c4c2` performs 100 longword writes, and the entire queue is zero at `4029c518`, before COLD is seeded and before the initializer consumes admission. The new completion dispatcher then reaches normal LIVE. Queue fields, entries, final code and hook bytes were checked in saved UI pages. Tests explicitly report dirty host setup rather than host zero initialization.

Four panel sessions use those native-initialized snapshots without clearing the queue from the host. They preserve the one/two-note cleanup results, pending-release replay and later fresh input. The ordinary LIVE session has no queue writes. Closed/replay sessions have only expected writes from the resident deferred helper code. Sixteen neighboring bytes on each side remain unchanged.

## Ownership evidence and its boundary

- No overlap with the known metadata/context span, sidecar/pending storage, admission word, live-capture code, fallback or copy helper.
- Even-offset longword candidate screen across stock main, previous modified main and previous payload finds no values naming this interval or its eight modeled DDR aliases. This is a literal screen, not complete instruction/data-flow analysis.
- CPU write watches cover interval overlap through all eight modeled aliases during cold startup and native panel sessions. Every observed writer is the original copier or deferred helper.
- The previously recovered stock heap range (`419f20a0..429f20a0`) is below the candidate. This bounds the tested intact allocator, not all computed pointers or corrupted allocator metadata.
- Direct actual fallback/reset controls preserve these bytes in INITIALIZING, LIVE and FAILED. They deliberately bypass setup admission to characterize clear extents; preserving bytes does not prove old note ownership remains valid after a pool reset.
- Recovered LIVE setup/initializer refusals preserve both queue and monitored note storage.

## Unclosed lifetime boundary

Actual copier replay clears pending releases. Fresh-cold provenance or an explicit epoch/invalidation policy is therefore still required before relying on this lifetime on hardware. A reset that reconstructs note storage can also make a preserved pending record stale; only the recovered refused LIVE paths were tested, not every computed/interior bypass.

Global exclusive ownership is not certified. The watches account for executed guest writes, not all unexercised computed/bulk stores or physical DMA/device writes. Existing stack/DMA bounds are finite earlier workload evidence, not a new worst-case physical proof. Native executable delivery/cache handoff for the new helper remains host-modeled.

**Result:** native zero initialization of the relocated queue is established in the tested PC startup path. Bounded layout and runtime ownership checks pass. Physical/global ownership and cold-only lifetime provenance remain unresolved; no hardware-ready firmware was produced.

Evidence: `Digitone-E04-PC-deferred-storage-screen.json`, `Digitone-E04-PC-resident-deferred-startup-startup.json`, `Digitone-E04-PC-resident-deferred-controls.json`, `Digitone-E04-PC-resident-deferred-panel.json`, `Digitone-E04-PC-resident-deferred-lifetime.json`, and `Digitone-E04-PC-resident-deferred-storage-summary.json`.
