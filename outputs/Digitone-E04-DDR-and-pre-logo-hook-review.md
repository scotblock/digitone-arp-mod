# E04 reserved address and hooks before logo exit

8 October 2026. PC-only investigation. The physical instrument remains restored to working stock 1.44. No firmware was rebuilt or transmitted.

## Result

The stock DDR configuration is consistent with a 128 MiB region containing the proposed reservation. This removes a simple configured-capacity mismatch from the current evidence; it does not certify physical backing, exclusive ownership or absence of cache/alias problems.

The important startup attribution result is that the producer capture hook **does execute before the logo clears**. Eight producer capture calls occur after private initialization marks the context ready. Pitch, allocation-clear and copy hooks are not reached in this modeled startup workload. Those early producer calls are now a concrete next target, rather than testing hooks that are not running yet.

## DDR configuration

The decoded bootstrap sections in stock and E04 are byte-identical. The prior exact E04 loader trace retains these guest-written DDR registers:

| Register | Written value | Relevant decoded setting |
|---|---|---|
| CR04 | `00010101` | 8 banks |
| CR07 | `00000001` | Port range protection disabled |
| CR08 | `01000001` | 8-bit memory datapath |
| CR12 | `01030303` | Chip select enabled |
| CR15 | `02000103` | ADDPINS 2: 16 − 2 = 14 row bits |
| CR16 | `02000407` | COLSIZ 2: 12 − 2 = 10 column bits |

Using the documented fields gives `2^14 × 2^10 × 8 × 1 byte = 134,217,728 bytes`, or 128 MiB. The CPU SDRAM aperture begins at `40000000`; the corresponding first contiguous 128 MiB window ends at `48000000`. The MCU's register definitions and address mapping are in [NXP's MCF5441x manual, chapters 14 and 21](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf). This is an inference from programmed geometry, not identification of the physical DRAM part.

The full proposed reservation `47be0000..47c00000` lies at offsets `07be0000..07c00000`, inside that configured window. Its occupied portion ends at `47be1b74`. Four MiB remain between the full reservation's end and the window's end. This distance is not a worst-case stack bound.

The protection-enable bit is clear in the retained CR07 write, so the configured port-protection ranges do not themselves explain denial of access to this high address. The source code used for the modeled loader leaves the bootstrap DDR setup unchanged in E04.

The emulator still forces DDR initialization-complete status. It does not train or probe the physical chip, verify retention, measure bus faults or test actual high-address aliases. Correct configured capacity is separate from ownership. Higher CPU addresses can alias when unused address bits are ignored; folding them by the configured size remains a model rather than a physical measurement.

## Hook attribution through actual modeled startup

A new E04 run starts from direct MAIN entry with matched loader flags and the initialized synthetic drive. It executes the native DTIM1 completion handlers with host completion kicks disabled, saves the cold state and continues through the actual intro-exit instruction `40091b0c`. Intro general forced semaphore completion is disabled.

Every helper entry in the recovered 1.44 layout is watched, with counts split before/after the observed intro exit. The successful run reports:

| Entry before intro exit | Count | State |
|---|---:|---|
| Startup fallback `47be08a4` | 1 | Pointer `47bccf04`, ready 0 at entry |
| Original initializer trampoline `47be0642` | 1 | Ready still 0 at entry |
| Producer capture `47be04ac` | **8** | Ready 1 |
| Capture helper `47be0274` | 8 | Ready 1 |
| Resolve helper `47be0114` | 16 | Ready 1 |
| Candidate store `47be02ec` | 8 | Ready 1 |
| Slot helper `47be0652` | 8 | Ready 1 |

All these hits occur during the cold stage before the intro continuation. No additional helper hits are observed during the intro or its short post-exit interval. The run reaches a live UI, with one observed intro exit and 138 main-loop entries.

The watched pitch/quantizer, allocation-clear, copy/first-copy and selector/commit helpers have zero entries in this workload. Do not generalize that zero to other projects or hardware startup states. The first-entry trace's stack word at producer capture is an argument/context word in a tail-jump hook, not a reliable return address; no caller identity is inferred from it.

## Consequence for diagnosis

Copier-only and initializer-only controls excluded ordinary runtime hooks. Their previous success therefore did not test these eight early producer captures. Full E04 startup passes on the PC with them, but that pass does not explain the physical failure. Initialization of source objects and the legality of every capture dereference on the real device remain specific questions.

Next isolate **producer capture during startup**, retaining the tested copier and initializer, and inspect its input objects and memory accesses before pattern initialization completes. Compare a PC-only control that bypasses that hook with unchanged E04. Do not produce an installable diagnostic build or propose another device trial just because the reservation fits configured DDR.

## Evidence

- `Digitone-E04-DDR-reservation-checks.json`: register decoding, stock/E04 bootstrap comparison and bounds.
- `Digitone-E04-pre-logo-hook-checks.json`: successful native-delay startup and entry counts through intro.
- `work/audit-E04-DDR-reservation.py`, `work/trace-E04-pre-logo-hooks.py`.
- Existing heap/stack/DMA review remains bounded supporting ownership evidence, not a consequence of this capacity calculation.
