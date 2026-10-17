# Digitone OS 1.42: producer/consumer ordering check

The recovered cache builder and queue publisher permit the previously failing sequences. The result now includes execution of their actual instructions; cache selection and publication decisions are no longer supplied by the earlier Python model. Consumer retirement still follows the recovered firmware order through executed release helpers, rather than running the complete audio ISR.

Firmware remains unchanged. No flashable V1 has been produced.

## Ordering evidence

The MIDI receive task's confirmed local graph at `400db15a..400db300` dispatches input handlers at `400db246` and `400db2ac`, then continues processing or returns to its wait loop. There are no explicit status-register instructions in that local graph. This does not certify every called queue/helper routine, but supplies no recovered task-level mask spanning successive external notes.

Task initialization builds a frame containing status word `2000` at `4000173a..40001740`. Audio-handler installation publishes `4009c838` to vector slot `400002fc` at `4009bd52`.

The actual publisher `400f0886` masks interrupts while it links an event and restores the saved mask before returning. Immediate nodes have type 1. The audio queue entry at `4009cb8e..4009cb94` admits these nodes without the timestamp test used for type-zero scheduling nodes.

Event completion at `4009cef0..4009cf00` saves the next event pointer, releases the current event through `400f065c`, and advances. Node retirement subsequently updates the queue head and recycles the scheduling node at `4009cf04..4009cf1a`. This allows payload release before later input calls, with the cached slot surviving separately.

## Executed producer sequences

The bounded interpreter now runs `400efa20` itself, its actual last/lowest/highest selectors, list updates, raw memory copies, event allocation, queue publication, and pool helpers. RAM contains the actual cache layout at `431d1758`; sound settings, descriptors and free-list storage are controlled inputs.

For modes 2 and 3, all three selectors permitted:

`press A → consume A → press B → consume B → release B`

The interpreter's actual builder published the departing B event first and then replayed cached A. The replay carried a non-null payload address whose count was zero. LIFO reuse had changed the data at that address to B's data. Executed event retirement then underflowed that counter.

**The sequence does not depend on an interrupt arriving inside the builder.** A second run completed all producers before any consumption:

`press A → press B → release B → consume the published chain`

The actual publisher produced four events: A-on, B-on, B-off and A-replay. A's payload had two queued copies but only its initial reference. Retirement in recovered chain order underflowed the count on the second A release. Serializing a whole producer burst therefore does not, by itself, repair this ownership case.

## Consumer condition checked

The actual disabled-arp branch of `4009719e` was executed with settings byte `+10f` zero. It returned zero identity and cleared its mode output. The recovered consumer guard at `4009de12..4009de14` bypasses template capture when that returned identity is zero. Thus an arp template is not a mandatory extra owner in the supplied disabled-arp scenario.

This check does not execute the complete consumer, voice allocation, synthesis callbacks, DSP or interrupt entry/exit. It narrows the missing condition rather than reproducing a hardware failure.

## Other outcomes

- An unselected note's first publication used its still-live initial reference and retired normally.
- Exhausting the fixed event pool made the actual builder update its cache but publish nothing. A subsequent departure cleared the pointer while its record retained a positive count.
- With one event available, actual note-off construction published the departing event but failed to allocate the remaining-note replay.
- Ordinary modes 0/1 did not publish an alternate cached-note replay on departure.
- Payload-free controls followed the selected-note routing without altering payload reference counts.

Fifty-one assertions passed. Twelve recorded cases executed 14,368 instruction steps; additional payload-free/control checks also ran. Seventeen ordering/consumer byte anchors match the stock image. The original SysEx and decoded section 3 hashes remain unchanged.

## What is now settled, and what remains

At the recovered local producer/publisher level, ordering does **not** exclude these ownership failures. Both consumption between notes and consumption after the entire input burst can expose them. Keeping interrupts masked for a producer burst would not be a sufficient ownership argument.

The complete upstream descriptor construction, selected-step UI interaction, enabled-arp acceptance, full audio consumer and task/interrupt interleaving are not all executed. The custom interpreter is also not independently validated against ColdFire hardware. Therefore this is a concrete bounded execution result, not a declaration of a reproduced stock-firmware defect.

For V1, retain the decision to keep root/scale context independent of the cached `+38` record's reference history. Do not patch the stock reference counts based on this check alone. The remaining execution check is the complete type-zero consumer path under these controlled settings, particularly whether it changes event ownership before common retirement. The owned-storage initialization/publication audit remains a separate implementation prerequisite.
