# Digitone OS 1.42: payload reuse and retained-template execution audit

The next checks now execute the stock payload/event allocation, release, copy and memory-copy helper instructions in a bounded PC interpreter. They confirm that reference-count behavior can cross record generations when a cache retains an address after publication. An arp template protects a record initially, but does not provide a separate reference for every raw replay.

These are controlled execution traces of selected helper code, not a reproduced device defect. Cache selection, event ordering and arp acceptance are scenario inputs. No firmware was changed or rebuilt.

## What actually ran

The interpreter reads the unchanged decoded firmware bytes and decodes each executed instruction. It executes the used instructions from:

- `400f05d6`: pop a payload record;
- `400f05f8`: release a payload record;
- `400f0626`: allocate a fixed event;
- `400f065c`: release an event and its type-zero payload;
- `400f0690`: release the destination payload, retain the source payload, then copy the event;
- `400ec23c`: the actual memory-copy loop, including its 16-byte, 4-byte and byte-tail paths.

The test RAM contains constructed stock-shaped 64-record and 128-event free lists, cached events and retained templates. Record addresses are genuinely reused by the executed free-list instructions; they are not assigned fresh monotonically increasing identities. The proposed 16-byte trailer is a test sentinel after the 64-record region, not a firmware patch.

The full cache builder, parameter producer, scheduler, audio dispatch and arp setup routine are not executed here. Their previously recovered behavior supplies the controlled scenarios.

## Record reuse changes the failure

### Before reuse

1. A fresh record is transferred to a queued type-zero event.
2. Event completion releases its reference to zero and returns it to the free list.
3. The cached event still holds the record's address.
4. A raw replay copies that address without retaining it.
5. The executed release helper subtracts one from zero, producing `ffffffff`.

The record remains on the free list. A subsequent pop increments `ffffffff` to zero, so it can return an allocated record whose reference count is already zero. This is the helper's concrete behavior for this supplied ordering.

### After reuse

The free list is LIFO. A newly popped record can immediately reuse that same address. The old cached pointer then reads the **new parameter data**, rather than preserving the original note's data.

The executed trace establishes this sequence:

`A completes → its address is reused for B → cached A is replayed → replay completion frees B's record while B's event still points to it`

Reusing the address again for C allows B's later completion to free C's live record. Thus a stale address can affect both data selection and another generation's lifetime. The test intentionally supplies this ordering; it does not establish that every outer firmware gate permits it on a device.

## Retained templates do not automatically balance replay

The common copy helper retains an initiating event's payload for a template. After the initiating event completes, the template's reference keeps the record off the free list. This normal protection was verified.

Two later cases were tested:

| Template behavior | Executed result |
|---|---|
| Existing identity remains; additive note does not replace the template | A raw replay has no new reference. Completing that replay can free the record while the template still points to it. |
| Template is replaced with a different record | The old record is released and can become reusable; its old cache address remains stale. |

A later common template-to-event copy can increment a stale record's count, but it does not remove that record from the free list. In the supplied trace, releasing that copied event then inserts the record at a head that already points to itself, producing a self-cycle.

The arp acceptance rules matter here. Previous static analysis showed that a same-priority, same-settings additive note does not necessarily replace the template; the test therefore includes both template outcomes instead of assuming replacement on every note. Those acceptance decisions remain supplied inputs in this interpreter.

## Unselected notes and allocation failures

The first publication of an unpublished cache is different: its original pop reference is still available. The actual raw memory copy followed by one event release returns that record correctly. There is no justification for adding an unconditional retain to every cache copy.

If an unpublished cache is discarded before publication, its pointer can be cleared while the record still has a positive reference and is absent from the free list. That local orphan condition was tested; external cleanup is not executed here.

The event allocator was also exhausted with all 128 fixed events held, while a payload record remained available. Its actual null return confirmed both outcomes:

- Freeing an event and publishing the cache later can complete the first transfer correctly.
- Discarding that cache instead leaves the positive payload reference unreleased in the controlled test.

With exactly one event available, the departing-note copy can be allocated while the replacement allocation returns null. This matches the previously recovered partial-publication branch. Scheduler publication itself is not emulated.

## Validation and limits

Fifty assertions passed across twelve lifecycle scenarios, thirteen independent byte-copy comparisons, preserved-register checks, and 128 balanced lifecycle cycles. The recorded lifecycle scenarios executed 37,852 stock instruction steps in the custom interpreter.

Memory-copy comparisons check the expected bytes, source preservation, surrounding guards and returned destination across lengths that exercise all three loop sizes. Helpers restore the tested nonzero callee-preserved registers and interrupt-mask bits. Type-one borrowed payloads bypass common retain/release as expected.

All lifecycle scenarios preserve the trailer sentinel, including the modeled ownership failures. This supports the trailer's separation from ordinary record-header operations, but does not certify all firmware writers or fault paths.

An additional null-head payload-pop check intercepts a read at address `00000010` in unmapped test memory. This is evidence of an unchecked null-record access, not a claim that the physical device necessarily raises the same memory exception.

The interpreter is custom and has not been independently checked against ColdFire hardware or another emulator. It does not run task scheduling, interrupts, exception handling, the DSP, controller loops or full pattern transitions. The original SysEx and decoded section 3 hashes are unchanged.

## Consequence for V1

Treat `+38` as an insufficient guarantee of original-note data or lifetime. Keep proposed root/scale context independent of that payload record's reference history, and derive the owned trailer from the persistent enclosing pool pointer.

Do not modify stock retain/release behavior based on these traces alone. The remaining discriminating question is now execution ordering: can the actual cache builder and event-dispatch/arp-acceptance path reach these supplied schedules under persistent selected-step state? Extending the bounded execution to those producer/consumer paths is the next useful check; repeating abstract ownership tests would not resolve it.
