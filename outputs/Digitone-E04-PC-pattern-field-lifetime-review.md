# Retained pattern pointer: publication and buffer lifetime

Firmware and all existing PC overlay binaries remain unchanged. This audit identifies the actual publisher and accounts for the observed stock destination's lifetime. It does not certify every computed writer or exclusive physical ownership of the proposed queue.

## Actual stock publisher

The child owner is 41a720d0, inside parent 41a720a0 at offset 30. The parent's project-base field at +20 (41a720c0) contains 40555ff4. Parent binding function 40028354 takes that project base as its second argument, stores it at parent +20, adds 299a00, and calls child binding function 4002c1a0 on parent +30. The child writes the supplied destination into its own +20 at 4002c1b0. It also binds dependent interior views; it does not allocate or free this backing.

A fresh continuous PC cold-start run observed the sequence:

1. The stock DDR initialization clears the future owner field.
2. Base construction clears the field again; the decoded constructor store is 40153168. Fast-engine memory hooks can report the constructor's block-entry PC 401530fe for that store.
3. Child binding 4002c1a0, called from parent binding with return 40028380, publishes 407ef9f4 into 41a720f0. Its previous value was zero.

This is actual publication, not inference from the later snapshot. A separate replay from the parked cold checkpoint reproduced UI startup with no further field writes. The parked checkpoint already contained the published pointer, explaining why intro-only tracing could not reveal its origin.

## Buffer address and lifetime

For this stock route:

    project base          40555ff4
    pattern offset        00299a00
    pattern destination   407ef9f4
    3000-byte region end  407f29f4 (exclusive)

The project address is a literal in stock instructions, not a caller's transient stack address. Stock code copies a 2a7404-byte project image starting there, ending at 407fd3f8. The pattern region and the audited fixed tail operations lie inside that extent, which is below the stock DDR-clear end 4322ae60 and far below the proposed queue 47be2860..47be29f0. This identifies the backing as part of the stock permanent-address project storage, not a separate buffer allocation whose free operation would determine its lifetime.

The 8.15-second restored workload included panel notes, sustained MIDI notes, transport and a confirmed pattern-backing replacement from 407fd414 to 40813531. The retained destination stayed 407ef9f4. Two native callbacks consumed it. There were no observed owner-field writes, setter/clear calls, or frees of the owner/exact destination in that workload. Exact-address free watches alone cannot exclude freeing a containing allocation; the fixed stock address and pointer-expression evidence are what distinguish this route from an allocation-derived lifetime.

The address remains usable across the tested pattern handoff; its contents need not remain unchanged. A full DDR reinitialization/reboot is a different lifetime boundary. The test does not establish cancellation of retained callbacks at every reset or project rebind.

## Replacement and clearing contracts

The relevant recovered paths are:

- The actual class-specific binding at 4002c1a0 (vtable +30) ignores a null destination; a non-null destination replaces the field and updates interior bindings.
- Conditional override 40153060 (vtable +34) replaces the field only when both condition and supplied pointer are nonzero.
- Explicit clear 40153078 (vtable +38) zeros the field. It does not invalidate an already-created descriptor.
- Base constructor clears the field. Constructor redispatch and destruction remain different from an ordinary binding call.
- A generic non-null setter 40152ffe exists in related vtables; it was not the observed publisher for this concrete child class.

Seven isolated native controls passed, including null binding, disabled override, successful override, specific rebinding and explicit clear. Two controls executed the actual retained callback after clearing or rebinding the owner field. In both cases it still converted into the previously captured old destination; the new test buffer remained untouched. These controls used deliberately modified PC state and are not evidence that the device naturally schedules that overlap.

The descriptor therefore retains a raw destination pointer independently of the owner's current field. Field clearing/rebinding is not a cancellation barrier. The observed original destination is still backed by permanent-address stock project storage, so these controls did not create a dangling buffer. For a different caller supplying a temporary or freed buffer, that same raw-pointer behavior would require an independent lifetime proof.

## What this closes, and what remains

The observed retained pattern-copy route now has a recovered publisher, a concrete parent-base expression, an identified stock buffer extent, and native evidence that the address survives startup and a completed pattern handoff. Its audited copy/clear destinations exclude the proposed queue for this stock binding.

This is not a universal bound for arbitrary incoming bases. Parent binding accepts a caller-supplied non-null project base; the conditional override can also accept another pointer. Other computed/interior routes, every reset/project-rebind cancellation sequence, malformed pointers and physical DMA/cache behavior remain outside this result. The other conversion caller at 4002f498 still supplies its destination through incoming D3 and requires its own base-ownership proof. Global queue ownership and later copier replay are not certified by this audit.

Evidence: Digitone-E04-PC-pattern-field-lifetime-summary.json, Digitone-E04-PC-pattern-field-actual-publisher.json, Digitone-E04-PC-pattern-field-intro-publication.json, Digitone-E04-PC-pattern-field-lifetime-runtime.json and Digitone-E04-PC-pattern-field-retention-controls.json. The first cold-publication run is retained separately as Digitone-E04-PC-pattern-field-cold-publication.json; the second adds the actual class-specific publisher entry hook.
