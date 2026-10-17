# Executed USB shutdown callback checks

## Result

Eight controlled PC cases pass against stock OS 1.44 instructions. Completion callbacks and deferred bulk-buffer release can enter replenishment during/after the tested shutdown routine. A host-only guard at the common replenishment entry blocks both tested routes; no firmware hook was installed.

This extends the static producer-stop review. Execution dependencies now import successfully following the user's Windows permission repair. That review's execution-access blocker is resolved; its physical and outer-path limitations remain.

## Execution boundary and fixtures

Stock routines executed: completion `4000472a`, replenishment `4000465a`, descriptor allocator `40005bfc`, lower-level submission `40005f1e`, endpoint query `40005f04`, descriptor cleanup `40005e42`, shutdown `40004806`, deferred queue enqueue/worker, USB bulk decoder and primary input consumer. The last two cases also execute stock buffer release `40004962` using a pool-address buffer at `4bc0d000`.

Initial states deliberately supply one descriptor with a completion callback and a positive payload containing a start/data pair, one outstanding count, and six available scratch descriptors. USB register shutdown acknowledgments are immediate host fixtures at the stock polling boundaries. Endpoint status/prime registers and descriptor completion fields are controlled. No hardware acceptance, interrupt pacing, or natural application/scheduler reachability is asserted. Earlier registry/heap/synchronization fixtures still apply. In the first six cases the bulk-buffer release is stubbed because the payload uses scratch RAM rather than a DMA-pool buffer; the last two remove that stub.

## Observations

| Case | Verified PC observation |
|---|---|
| Positive completion | Queues one deferred USB decoder item and makes two stock endpoint submissions; modeled outstanding count becomes two. |
| Zero-length completion | Queues no decoder item, but still makes two submissions. |
| Descriptor cleanup with positive completion | Invokes saved completion callback and makes two submissions; cleanup subsequently clears the endpoint head/tail. |
| Shutdown, receive gate open | Callback makes two submissions; shutdown clears outstanding count to zero and leaves one deferred work item. Consuming it changes the receive state/buffer. |
| Shutdown, receive gate closed | Same callback/submission/deferred sequence; consuming it leaves receive state/buffer unchanged. Closing the receiver gate is not a USB producer-stop mechanism. |
| Shutdown, lower-level endpoint submission blocked | Actual submit returns `ffffffff` twice. Replenishment still increments its count, and shutdown later clears it. A counter value is not sufficient evidence of accepted hardware descriptors. |
| Shutdown, actual bulk-buffer release | Shutdown returns with count zero, endpoint head zero and one deferred work item. Deferred decoding/release invokes replenishment again, makes two more submissions and ends with count two and a nonzero endpoint head. |
| Shutdown with host replenish guard and actual buffer release | Guard suppresses two replenishment entries: completion cleanup and later buffer release. No submissions occur, count/head remain zero, and queued input drains while frozen without receive-buffer changes. |

Submission here means stock software reached and executed its endpoint submit function under supplied register conditions. It does not mean a physical controller accepted a transfer. Similarly, the descriptor-head overwrite observation is a bounded fixture result, not a claim that stock firmware naturally enters this state or has a demonstrated device bug. Outer USB shutdown calls may establish protections absent from the isolated entry; their effects remain to be audited.

## Guard scope and next work

The guard is a host code hook that returns from `4000465a`; its lease is a test condition, not firmware metadata. It illustrates a common interception point for the recovered completion, periodic and buffer-release paths. The stock receive gate stays independently closed while payloads drain. No permission to reopen is inferred merely from queue count, endpoint head or outstanding count.

Next, execute the outer USB shutdown calls (`40003a1e`/`400044ec` and their prerequisites), establish the endpoint-disable/acknowledgment conditions and check late completion/periodic/initialization interleavings. Then extend the coordinator with producer-stop and gate-writer ownership across real failure exits. Secondary-cable input consumption, hardware timing/cache coherence, safe guard storage/startup and stock flash-error handling remain unresolved.

## Reproduce

- `work/test-E03-USB-shutdown-callbacks.py`
- `outputs/Digitone-OS1.44E03-USB-shutdown-callback-checks.json`

The script fails with a nonzero exit status on any failed assertion. Stock MAIN, E02 and E03 firmware hashes remain unchanged; no device I/O or flashable build was produced.
