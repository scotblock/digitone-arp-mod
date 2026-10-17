# Digitone OS 1.42: context initialization and reset lifetime

Firmware remains unchanged. No allocation extension, context hook, firmware patch or flashable image was produced.

## Findings

The proposed context storage should have the lifetime of the persistent pool allocation, rather than the lifetime of an individual note, queue or pattern. Ordinary recovered playback reset preserves the trailer area. Pool reinitialization is a different operation and cannot safely follow from an empty queue alone.

The proposal remains an explicitly requested 16-byte trailer at `P+14100..P+14110`, where `P=*(4199d590)`. The owner must come from that global, never from an event's `+38` pointer. The stock request is still `14100`; the trailer is a PC canary in these tests, not an implemented allocation extension.

## Cold initialization: actual instruction execution

The bounded interpreter executes stock initializer `400f0504` and the actual clear primitive `400ec284`. At the allocator call `400dab8c`, the test explicitly supplies either a valid controlled base or zero; the allocator itself is not executed.

With the valid base, the initializer requests 82,176 bytes, clears that record area, links all 64 records at stride 1,284 and leaves the adjacent 16-byte marker untouched. Its final `d0` remains the base pointer. The actual clear primitive also returns the destination, supporting the previously proposed local-pointer route.

An observation immediately before the clear confirms that stock has already published the owner at `400f058c`, while the first record byte still contains the test's `a5` marker and the payload free head has not been built. Publication at that point is not a sufficient readiness signal for a new context reader.

The recovered normal setup calls the initializer at `4009bcec`, before publishing the audio handler at `4009bd52`. This supplies a local setup opportunity; it does not establish that every possible producer/task is inactive.

For the proposed integration, the required order is: allocate the explicitly extended block, reject failure, retain the base locally, initialize records and trailer with capture unavailable, finish linking, then expose completed context state. The record count and stride must remain unchanged. Delaying the owner publication and using an explicit readiness gate are design requirements; no instruction rearrangement has been implemented or certified.

## Ordinary playback reset: actual wrapper and callback

The test creates a real retained template at `41345f08`, publishes a counted event copy, and executes normal reset wrapper `4009bd6a`, including callback `4009ba94`, queue drain `400f08f0`, arp reset `4009713c` and cache reset `400ef9d0`.

Before reset the record has two counted owners: the queued copy and the template. Reset empties the queue and releases the queued copy, leaving count one. The template's payload pointer and the separately staged cached pointer both survive. The trailer marker survives too.

The callback executes its type-zero return branch in this case. Its type-three external-pool path is not tested here.

This is concrete execution evidence that queue drain plus bitmap reset does not establish complete pool quiescence. Ordinary reset need not reconstruct or clear persistent context storage. A reset should not zero an active writer-depth counter as a substitute for balanced writer completion.

## Pool reentry: destructive even when the trailer survives

The reuse branch skips allocation and block clearing, but still rebuilds the event, scheduling-node and payload free lists. Executed quiescent reuse preserves the trailer.

As a negative control, the same initializer is called after the normal reset while the template still retains a payload. It sets that record's count to zero without clearing the template pointer. The next actual pop returns the same address for new data. The physical trailer survives, but surviving bytes do not make the surrounding pool lifetime safe.

There is an earlier integration hazard: `400f0534` clears the queue head before the existing-owner test at `400f0572`. An entry condition checked only beside the owner-reuse branch would therefore be too late to preserve a live queue. Any rejection or controlled shutdown must occur before the initializer's first pool mutation.

The additional recovered setup caller at `4009bdec` still prevents assuming initialization is cold-only. Its complete computed reachability remains unresolved. These tests deliberately invoke reentry; they do not establish that normal hardware operation reaches it live.

## Allocation failure

With a supplied null allocator return, the stock initializer proceeds to clear through address zero. The bounded memory model rejects that write. This is a missing local failure branch, not a prediction of the device's physical exception behavior.

Disabling only the musical feature is insufficient: this allocation also supplies stock playback's payload pool. Failure requires stopping setup or reaching a verified existing fatal/error continuation before pool consumers and audio activation. No such continuation has yet been selected. Delayed owner publication alone does not resolve this failure path.

## Required lifetime contract

- Cold initialization must keep context readers unavailable until both record setup and trailer initialization complete.
- Ordinary playback/pattern reset should preserve the persistent allocation and its guard state; snapshot data follows its separately audited queue/event lifetime.
- Pool reinitialization must be refused or preceded by a verified shutdown before any pool mutation. That shutdown must account for queued events, templates, cached descriptors, producers/consumers in flight and active pattern writers.
- Any allowed reconstruction needs capture disabled before reconstruction and enabled only after complete setup. Existing nonzero ownership cannot itself signal readiness during that interval.
- Allocation failure must prevent subsequent missing-pool use.

These are integration obligations, not installed protections. The tests support the preferred allocation's physical separation and local initialization sequence, but do not fully certify storage placement or reset safety.

## Validation and next step

27 assertions passed across five recorded execution cases and eight proposed-protocol intermediate-state checks. Recorded valid-path cases execute 36,655 instruction steps; the null-allocation path is also attempted and diagnosed. Both source hashes match the unchanged originals.

The custom interpreter is not independently validated against ColdFire hardware. The allocator, interrupt/task interleaving, type-three reset callback and all computed initialization callers remain outside these results.

The next focused task is to identify a verified setup-failure continuation and audit every recovered initializer entry for a usable pre-mutation shutdown/guard point. Until those are established, keep the proposed trailer and startup hook unimplemented.

Detailed checks are in `Digitone-context-init-reset-results.json`; the PC harness is `work/execute-context-init-reset.py`.
