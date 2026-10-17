# Final E02 firmware review — Digitone / Digitone Keys OS 1.44

**E02 remains a PC-only experimental image. It is not ready for hardware installation.** This review found a concrete flash-layout conflict in its current packaging, plus a startup failure policy that must be resolved deliberately. No firmware bytes or installed emulator files were changed during this review.

## Exact image reviewed

- E02 SysEx SHA-256: `8e1d9c4e384d30314255801d0e1ef70736a1f76ac1279a31f8e02d3285fe43ef`.
- Original 1.44 SHA-256: `d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659`.
- Original executable region changes exactly nine documented sites: early boot call, stock initializer entry, and seven arp/event hooks. Every other container section is unchanged. Main output independently decompresses to the recorded image and the container checksum passes.
- Executable growth is only 2,468 bytes: a 256-byte boot reservation (94 bytes used) and a 2,212-byte helper/table image. The much larger stored-image growth comes from the test builder’s all-literal encoding, not a multi-megabyte mod.

## Startup

The call at `0x40000538` redirects to the appended copier at `0x4029c4b0`. It copies 2,212 bytes from `0x4029c5b0` to `0x47be0000`, clears the private pointer/metadata area, installs the pointer and header, and leaves readiness zero. It then executes the displaced stock vector-base routine at `0x40001df4`.

Stock startup subsequently copies its SRAM sections and clears DDR from `0x4028f000` to `0x4322ae60`. The mod’s reserved destination lies outside that clear. Its appended source lies within the clear, so copy-before-clear ordering is essential and is present. The stock SRAM copy ends at the original `0x4029c4b0` boundary, excluding the appended copier and helpers. Stock cache-control setup follows these steps.

The reset hook at `0x400ffed0` enters `0x47be055c`. It saves registers/status, masks interrupts, validates argument 158, the non-null pointer and the three header constants, clears readiness and context data, and calls the original initializer body. Only after the stock initializer returns does it publish readiness 1 and restore status/registers. The aligned absolute-reference screen finds a stock caller at `0x4009c5a4` preceded by argument 158; this is not an exhaustive proof against computed or relative calls.

Fresh final-machine-code tests passed for ready, initially unready and repeated initialization. The copied code/table and adjacent canaries survive. A separate execution of the actual final appended copier verified its output, initial unready header and return through the displaced stock routine. Earlier E02 cold-start tests execute through application startup and playback. These PC observations do not establish complete physical loader/cache continuity.

## Memory

| Item | Address range, exclusive end | Size |
|---|---|---:|
| Helper code, alignment and lookup table | `47be0000..47be08a4` | 2,212 bytes |
| Private pointer | `47be1000..47be1004` | 4 bytes |
| Header and context records | `47be1004..47be1b74` | 2,928 bytes |
| Entire occupied span, including gap | `47be0000..47be1b74` | 7,028 bytes |

This fixed-RAM route performs no custom heap allocation. The private pointer’s compatibility value is `metadata_base - 0x14100`; it is not an allocated stock object. The reserved candidate interval is `47be0000..47c00000`, matching the locally pinned Elekloader Digitone profile for 1.43/1.44. That profile and bounded emulator observations are evidence for placement, not universal ownership certification.

The final 1.44 stock clear does not overlap the destination. Entry stack top is `0x48000000`. Neither the initial separation from that stack nor unused emulator pages proves every task’s high-water mark, interrupt stack depth, computed stock write, DMA access, project-load path or error path. Earlier comprehensive alias/watch reports mainly target 1.42 and cannot be presented as completed 1.44 certification. The bounded fault tests also suppress concurrent timer/IRQ/DMA producers.

## Failure behavior

- Runtime selector/pitch tests with bad magic, version, size, readiness or a null pointer bypass scale quantization and preserve the tested stock event/register/status behavior.
- **Startup reset failures behave differently.** Wrong argument, bad magic/version/size or a null pointer branch to `0x47be0640`, an infinite loop with interrupt mask 7. All five final-machine-code cases reached that loop without mutating the context region. There is no stock-startup fallback on these paths.
- Pointer validation checks non-null, then dereferences it. It does not certify arbitrary non-null pointer validity, bounds or ownership. Matching header constants are not a checksum of executable code or context data.
- The boot copy is fixed-length and has no checked copy-success result or runtime helper-image checksum. A bus fault, damaged code, corrupt stack, exception during initialization or initializer that never returns has no newly proven cleanup path.

Thus “guards work” does not mean “all faults recover.” The current startup loop is fail-stop behavior. Decide whether to retain a documented fail-stop policy or implement a stock-compatible fallback; verify that decision in PC fault injection before considering device tests. Interrupt masking alone does not stop an already-running DMA producer.

## Packaging and flash conflict — concrete blocker

The stored E02 container is **3,361,440 bytes**, versus a **3,145,728-byte** interval from OS flash offset `0x80000` to observed stock data at `0x380000`. E02 exceeds that interval by **215,712 bytes**.

This is reconfirmed against 1.44, rather than inferred solely from 1.42. Stock 1.44 instructions at `0x4008a72e`, `0x4008a758`, `0x4008a7aa` and `0x4008a7c0` pass `0x380000` to stock flash read/erase/program functions. They also access a separate `0x3c0000` record. The 1.44 update loop at `0x4008b60e..0x4008b75e` rounds the supplied image length to 256 KiB erases and 512-byte writes, beginning at `0x80000`.

If that loop is reached with E02’s container length, its arithmetic gives 13 erase units ending at **`0x3c0000`**, and 6,566 full program blocks ending at **`0x3b4c00`**. Both footprints intersect stock data at `0x380000`. This is conditional analysis of the recovered loop, not an assertion that every receiver would accept E02. Receiver rejection would not make a different accepting route safe.

A recovered 1.44 service receiver configuration at `0x4008b524` supplies a 1,966,080-byte buffer, also smaller than E02. Its ordinary USB/SysEx applicability and full acceptance chain remain unverified; do not generalize that service buffer into a universal transfer limit.

The final 512-byte write needs 352 bytes of padding beyond the logical container, while the decoded SysEx stream supplies only 34 transport-padding bytes. Those serve different purposes. A verified zero-initialized receive buffer might supply the remainder, but E02’s complete receiving-buffer initialization and final write source have not been proven. The resulting physical loader/update path is not tested by Digiemu importing and decompressing a file directly.

**Next PC task:** use a verified, size-efficient compressor/container writer for 1.44, then independently decode it and enforce flash/receiver bounds and final-block padding. Check in-place decompression’s reader/writer separation at every step; fitting the overall size is not sufficient. Keep this as a PC test artifact until the remaining checks pass.

## What still needs PC work, and what requires hardware evidence

| Requirement | Remaining evidence | Where to resolve it |
|---|---|---|
| Packaging fits the stock image slot | Proper compression, non-overlapping erase/program footprint, complete receive/completion/checksum/padding chain | PC first; actual device updater acceptance later |
| Startup failure policy | Defined fallback or deliberate fail-stop, corrupt/non-null pointer and code faults, repeated entry, real exception behavior | PC first; recovery robustness remains device-specific |
| Actual loader state reaches the copier | 1.44 bootstrap/updater continuity and in-place depacking with final bytes | PC first; inherited physical cache state needs device evidence |
| Reserved RAM remains owned | 1.44 computed writes, aliases, DMA, project loads, modes and stack stress | Broader PC tracing, then device-specific observations |
| RAM instructions are physically executable/coherent | Loader-to-cache handoff, copied code visibility, D/I-cache behavior and aliases | Real hardware or a trustworthy hardware debugger/trace |
| Added work meets audio deadlines | Complete 1.44 cycle-aware hook workload and memory/DMA costs, followed by actual loaded playback | PC estimates plus device timing/audio measurements |
| Context behavior covers real input paths | Queue/sustain/recycle/copy/remap stress; natural producer of the first-copy status packet | Extend PC traces, then hardware workload matrix |
| Recovery and update failure handling | Exact device/OS recovery route, backups, readback/integrity where available, real flash geometry and failure outcomes | Verify before any experimental hardware installation |

Recorded scale-locked pitches are functional evidence. Clean PC PCM after an emulator host-thread fix is not evidence of physical cache correctness or hardware audio deadlines. Audio recording from Ableton can help detect wrong notes and audible glitches after a separately justified device test, but cannot establish RAM ownership or prove cache/recovery behavior.

## Review evidence

- `Digitone-OS1.44E02-final-image-review.json`: independently checked final bytes, layout and flash arithmetic.
- `Digitone-OS1.44E02-startup-failure-review-checks.json`: eight reset/fault/reentry cases and execution of the actual appended copier.
- `Digitone-OS1.44-real-selector-context.json`: bounded runtime stock-fallback comparisons.
- `Digitone-OS1.44E02-emulator-validation.json`: prior final-image PC cold start and constrained playback.
- `Digitone-OS1.44-audio-copy-audit.md`: explicitly supplied first-copy status input and physical producer limitation.

Original and E02 firmware hashes are unchanged after this review. No new firmware build, device transfer or flash operation was performed.
