# Pattern-copy and buffer-copy pointer provenance — PC audit

Firmware and the resident deferred-release overlay remain unchanged. This audit narrows destination provenance; it does not certify exclusive physical RAM ownership.

## Buffer family at 4018ab94

The recovered normal-entry function is 4018ab1a. Equal start/end inputs return the stock empty singleton at 419f0ea0 without payload copying. For a nonempty valid range, it computes length = end - start, calls 40189354, moves the returned header into A4, and sets destination A3 = A4 + 12. Length one has a direct byte store. Other lengths pass that same destination and length to memcpy. After copying it writes a terminator at destination + length and updates the header.

The alternative allocation branch also assigns A4 from the allocation result and A3 from A4 + 12; it clears the copy length. It does not introduce a caller-controlled destination. The allocator rejects lengths above 3ffffffc on its error path and requests at least length + 13 bytes on recovered normal successful paths. These conclusions do not establish actual exception cleanup or behavior after a corrupted allocation return.

In an 8.15-second modeled restored-project workload, 32,023 copies from this caller matched observed allocation headers, used header + 12, had room for the terminator, and stayed inside the recovered stock heap 419f20a0..429f20a0. None reached the queue 47be2860..47be29f0 or its watched aliases. The workload included panel notes, MIDI sustain/release, transport and a confirmed pattern-backing replacement. This run uses the existing native fast DMA model, unlike the preceding Python-path descriptor audit; its descriptor screen is not new physical DMA evidence.

Five separate native-routine controls passed: non-null empty, one byte, 29 bytes, 4,096 bytes, and null empty. One-byte output used its direct store; the ordinary and large cases used the allocator-derived bulk path. Empty cases returned the singleton and did not allocate or bulk-copy.

For valid normal entries and an intact stock allocator, this buffer family's destination provenance is resolved sufficiently to exclude the proposed queue. Universal fault behavior, unknown interior entry, corrupt allocator metadata and physical memory aliases remain outside that conclusion.

## Pattern conversion at 4000a1a6

A2 comes from the first caller argument, loaded at 4000a1ae. The paired operations remain fixed: 218-byte memset at A2 + 2f26 and 304-byte memcpy at A2 + 2df6. Four recovered direct callers have distinct provenance:

- 40011456 supplies an object-buffer getter result after construction of a 3010-byte heap object with a 3000-byte interior buffer. This route is allocation-derived for the recovered successful constructor/getter path.
- 4002c1ee supplies field +4 of a retained callback descriptor. It is not a newly allocated payload destination.
- 4002f498 supplies incoming D3, the caller's destination argument. Its fresh 2fec-byte allocation in D2 is the source passed to conversion, not the destination. Treating that allocation as destination ownership would be incorrect.
- 4009220a supplies A6 - 3000, a local stack buffer. Its validity depends on the task's stack ownership, not heap bounds.

The observed workload exercised the retained callback twice. Both conversions used destination 407ef9f4, source 41368cd8; both paired bulk operations matched the entry base, used the expected offsets, and avoided the queue.

A separate continuous trace joined callback construction, later dispatch and conversion: 4002f80c retained the exact caller-supplied destination in an eight-byte descriptor at field +4; 4002c1d2 consumed that field; conversion received the same pointer. The recovered clone at 4002c240 copies the two scalar fields, preserving the pointer rather than allocating a new destination buffer. This proves the observed publication/consumption identity, not general pointee lifetime.

The additional outer-dispatch trace distinguishes the pointer origin from a separate caller parameter: 401533aa loads D0 from object +20 at 401533bc and passes it as the second argument to virtual method +44. In the exercised class this reaches 4002f80c, which retains that second argument. The outer second argument was 40553cd4 on one entry and zero on another; it is not the retained destination 407ef9f4. The restored object at 41a720d0 has vtable 40195bd8 and its inherited +20 field contains 407ef9f4. The base constructor 401530fe clears +20 at 40153168, so later publication of this field still needs tracing. The field's nonzero value is an inherited-state observation, not proof of its writer or lifetime.

## Limits and next focused target

The buffer-copy family is conditionally closed under the recovered successful allocator contract. Pattern-copy lengths and the observed retained-pointer chain are resolved, but every caller's base ownership is not. Trace the nonzero publication and replacement writers of the retained owner's +20 field, plus the caller-supplied D3 route, including buffer/stack ownership and lifetime. Do not substitute observed distance below the queue for universal ownership proof.

Physical DMA scheduling, physical cache behavior, unknown computed writers and later copier replay remain separate unresolved questions. No new flashable firmware was produced.

Evidence: Digitone-E04-PC-copy-pointer-provenance-summary.json; Digitone-E04-PC-copy-pointer-provenance-runtime.json; Digitone-E04-PC-pattern-retained-provenance-runtime.json; Digitone-E04-PC-buffer-copy-branch-controls.json; Digitone-E04-PC-copy-pointer-static-windows.json; Digitone-E04-PC-pattern-outer-pointer-runtime.json; Digitone-E04-PC-pattern-owner-inherited-fields.json.
