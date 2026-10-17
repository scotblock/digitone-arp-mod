# E04: separate startup components and inherited cache assumptions

8 October 2026. PC-only controls; no SysEx candidate built, changed or transmitted. The physical Digitone remains restored to stock 1.44.

## Result

The copier alone, initializer alone with explicit RAM seeding, and copier plus initializer all complete native startup timer waits and reach the interface. No control reproduces the physical stall. This does not identify either component as physically safe or clear the remaining arp hooks; it narrows the observations to these isolated modeled mechanisms.

## Controls and scope

Each control starts from stock MAIN and changes only the selected startup sites. It uses stock flash contents for emulator flash reads, a direct MAIN reset with matched boot flags, the same initialized drive source and the modeled cache-control values from the saved exact E04 loader handoff. The full loader, SRAM/MMIO handoff and physical drive are not part of these new controls.

| Control | Early copier | Initializer wrapper | Private RAM source | Outcome |
|---|---|---|---|---|
| Copier only | E04 redirect and appended source | Stock | Guest copier | Live UI; ready flag remains 0 |
| Initializer only | Stock | E04 wrapper | Host supplies exact payload and unready metadata before boot | Live UI; ready becomes 1 |
| Copier + initializer | E04 | E04 | Guest copier | Live UI; ready becomes 1 |

All ordinary runtime arp hook sites remain stock in these three controls. The initializer-only case is deliberately artificial: it cannot demonstrate installation or cache coherence because the host supplies private RAM bytes. Its purpose is to separate wrapper behavior from copying. Only raw PC control images are saved under `work/os144/PC_ONLY-*-main.bin`; they are not installable firmware and must not be transmitted.

Each control observes three native DTIM1 interrupts and semaphore wakes, zero host completion kicks, zero intro general semaphore satisfactions, one intro exit and 138 main-loop entries. The guest-copied payload stays exact in the copier controls. Before the copier, inherited CACR is `0008c000`; post-copy startup and initializer execute under modeled CACR `a50ce100`. Chunk estimates do not measure physical timing or prove instruction-stream equality.

## Inherited cache state

The saved exact E04 loader handoff contains CACR `0008c000`, ACR0/ACR1 zero, VBR `80000000` and RAMBAR `80000235`. CACR enables instruction cache while disabling data cache and the data store buffer. Missing other control-register entries are not proof of their physical values.

The decoded section-2 bootstrap actually contains:

- `80000634`: clear D0.
- `80000636` / `8000063a`: write zero to control indexes 4/5 (ColdFire ACR0/ACR1).
- `8000063e`: load D0 with `0008c000`.
- `80000644`: write D0 to CACR.

These opcodes corroborate the traced handoff on its tested path. Section 4 later occupies the same SRAM address range; it must not be substituted for the section-2 bytes when interpreting this earlier cache write. Generic m68k disassembler names for the control registers differ from ColdFire names, so raw indexes and the hardware reference govern interpretation.

E04 then performs aligned longword copying from `4029c5b0..4029cf6c` to `47be0000..47be09bc`. It clears `47be1000..47be1b74`. All copying precedes stock CACR `a50ce100` and ACR0 `4007e020` setup and the first helper execution. The source and destination do not overlap. This rationale assumes valid DDR backing at the destination and the documented visibility semantics; the emulator cannot establish physical backing, aliases or all competing writers.

## Concrete cache dependency

NXP distinguishes pushing modified cache data to memory from invalidating it: copyback writes can stay only in modified cache lines, and invalidation can lose that modified data. [MCF5441x reference manual, cache chapter](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf).

A small logical sensitivity test therefore checks the following separately from firmware execution:

| Hypothetical copy state | RAM retains payload after invalidation? |
|---|---|
| Data cache off, matching traced loader | Yes |
| Data cache on, write-through | Yes |
| Data cache on, copyback, no prior push | **No** |
| Copyback with push before invalidation | Yes |

This exposes a real prerequisite of the present copier, not an observed device diagnosis. The traced loader explicitly disables data cache before the copy, and no evidence here shows the physical device entering with the hypothetical copyback state. Do not label this as the cause of the logo hang or add a cache patch solely on this synthetic model.

Instruction caching is already enabled while copying. The old instruction/branch tags require the stock post-copy invalidation sequence; earlier tests cover those logical dependencies. The new controls merely inherit control-register values. They still do not emulate silicon tags, pending writes, pipeline synchronization or precise memory attributes.

## Status and next bounded target

No startup component has been shown faulty in these PC controls. Successful controls are evidence about modeled behavior, not a reason to reinstall E04. The full E04 runtime hooks are excluded from this isolation and their actual execution before logo exit remains a separate attribution question.

Next map the physical reservation assumptions against the stock DDR initialization and address decoding, rather than relying solely on the emulator's configured 128 MiB alias model. Also count which E04 runtime hooks execute before intro completion, so any further isolation is aimed at code actually reached. Those checks can distinguish an unsupported destination/mapping assumption from a later hook or unmodeled physical cache effect without another device update.

## Evidence

- `Digitone-E04-startup-component-controls.json`: three completed controls.
- `Digitone-E04-inherited-cache-input.json`: exact saved loader controls used as fixtures.
- `Digitone-E04-copier-cache-assumption-checks.json`: bootstrap opcodes, spans and four logical sensitivity cases.
- Prior `Digitone-OS1.44E04-loader-cache-controls.json`: full packaged-loader trace.
- Scripts: `work/compare-E04-startup-components.py`, `work/audit-E04-copier-cache-assumptions.py`.
