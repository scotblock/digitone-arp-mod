# Digitone OS 1.42: actual early allocator and source-copy audit

**The full stock allocator works in the recovered post-clear, pre-scheduler PC fixture.** Stock copying and source erasure also work within its returned allocation. The remaining gap is the proposed startup installation sequence and loader acceptance, rather than an assumed allocator return.

## Actual allocator execution

Entered **400dab8c** with supervisor SR=2700, a zero current-thread pointer at 429a39a8, cleared heap/bitmap/lock/free-list storage, and the original allocator configuration bytes at 401fe590. No allocator return value or allocator helper result was supplied. The fixture executes the actual lock routines, lazy initialization, free-list helpers, splitting, bitmap changes, and return path. It uses sparse RAM to represent the cleared 16 MB heap.

| Request | First allocation | Second allocation | Verified footprint |
|---|---|---|---|
| 14c70 (existing proposed owner) | 419a38c0 | 419c38c0 | 20000-byte block |
| 15c80 (owner plus 4 KB code reserve) | 419a38c0 | 419c38c0 | 20000-byte block |

The enlarged cold request executed **1,145 stock instructions**. The bitmap marks the end of the 128 KB block, and the next allocation begins at that block's end. Both paths preserve the stack and SR control bits, leave the current-thread pointer zero, and avoid scheduler traps. Observed allocator writes exclude the proposed source staging interval.

An independent cold case allocated the complete 16 MB heap, then attempted the enlarged request. The latter returned **null** through stock code. The word at **401fe5a8** increments even on this failed call; it is an allocation-call counter in these paths, not a successful-allocation count. These results do not exercise hardware exceptions, concurrent callers, or the entire device boot.

## Stock copy and erasure

For an allocated owner, the proposed code destination is **owner+14c80**, here **419b8540**. Executed stock memcpy **400ec23c** and memset **400ec284** with lengths **0, 15, 16, 17, 1,678, and 4,096**. The copy returns the destination, reproduces every source byte, preserves both destination guards, and leaves the source intact. Subsequently erasing the complete 4 KB staging interval restores its zero contents, preserves its guards, and leaves copied destination bytes unchanged.

Source bytes in these tests are deterministic synthetic RAM data. They are not a firmware extension, relocated helper implementation, or executable installation. The allocator/copy/erase audit passed **71 checks across three allocator cases and six copy cases**.

## Source preservation and startup ordering

The proposed temporary source interval is **4024f4b0..402504b0**, immediately after the original loaded main image. Both boundaries align to the stock clear loop's 16-byte stores. The original clear covers the entire interval. Simply appending bytes remains invalid because the unchanged clear erases them.

A proposed split-clear can preserve exactly this temporary interval:

1. Clear 40242000..4024f4b0.
2. Clear 402504b0..431dc690.
3. Allocate and initialize the explicit enlarged owner, copy and relocate the source into its code reserve, and validate the completed destination.
4. Clear 4024f4b0..402504b0, restoring the original zero-initialization contract before ordinary application startup.
5. Continue stock startup and publish executable readiness only after the required control/cache sequence.

The three clear intervals partition the original clear exactly, with no added or omitted byte. Allocation writes observed in the fixture do not overlap the temporary source. The code destination lies in the heap, which the first two clear phases would already have cleared. Allocation must follow those phases: clearing the heap after allocation would destroy its bookkeeping and destination.

The split-clear hook itself is **unimplemented and unexecuted**. Its proposed safety depends on there being no ordinary application access to the preserved BSS interval before step 4. The existing sequence calls the clear at **40000542**, then continues hardware/cache setup from **40000546**, before entering **4012b344**. This gives a specific insertion boundary to test, not proof of every alternate entry or exception path. Null allocation must leave dispatch disabled, restore staging zeroes, and take a verified continuation; no usable failure continuation is claimed yet.

## Earlier cache installation is a useful refinement

Section 2 has recovered writes of CACR=0008C000 after its main depack routine, and CACR=000CC100 before a recovered image-entry call. Main startup subsequently writes CACR=A50CE100 at **40000554**. Under the [official NXP MCF5441x manual](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf), these pre-entry values disable the data cache; the main value initiates data, instruction, and branch invalidation while enabling caches. Installing before that main write may therefore use stock invalidation after copying. This remains conditional on the actual handoff and inherited control state; it is not a cache-emulation result. A later installation into copyback heap memory still requires explicit coherency handling.

## Next concrete verification

Execute the proposed split-clear/bootstrap sequence at the recovered startup boundary, with success and allocation-failure paths, and demonstrate that all original BSS bytes are zero before continuing. In parallel with that sequence audit, trace the loader's main-section size and decompression limits to establish whether a source extension is accepted. Then bind relocated helpers to the actual allocated address and execute them there. Bootstrap placement and resident dispatch size must also fit their justified interval.

No original firmware bytes were edited, no repacked or flashable file was produced, and no device I/O occurred. Original SysEx and decoded-image hashes still match. Evidence: **Digitone-early-allocator-and-source-copy-results.json** in this output directory. The custom interpreter provides instruction-level PC evidence, not hardware certification.
