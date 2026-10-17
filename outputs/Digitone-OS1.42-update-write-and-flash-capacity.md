# Digitone OS 1.42 — update/write limits and flash space

The recovered write paths accommodate a **4,096-byte increase in the stored container** without an additional erase unit. Both stock instruction loops passed PC execution checks to simulated erase/program boundaries. This removes a size objection to the proposed extension; it does not certify a modified update or identify the physical flash capacity of the user's device.

## Update write ranges

Two separate implementations agree:

- Section 2, SRAM-linked bootstrap: **80003f6a..80003fd8**, erase wrapper **80002f48**, program wrapper **80002edc**.
- Main application: **4008ad76..4008ad9c** and **4008ae3c..4008aec2**, erase wrapper **400edbbe**, program wrapper **400edb42**.

Both start the OS container at flash offset **00080000**. They calculate `ceil(length / 0x40000)` erase units and `ceil(length / 0x200)` program calls. Each program call supplies 512 bytes, including the last call: it is not shortened to the remaining container bytes. Source addresses advance correspondingly from **40000008** in the bootstrap and **4bc47088** in the main application. Therefore a future producer must supply readable final-block padding as well as correct framing and checksums.

| Container case | Bytes | 256 KB erase units | Erase end, exclusive | 512-byte program calls | Program end, exclusive |
|---|---:|---:|---|---:|---|
| Current decoded container length | 1,102,032 | 5 | 001c0000 | 2,153 | 0018d200 |
| Conservative +4 KB stored growth | 1,106,128 | 5 | 001c0000 | 2,161 | 0018e200 |

The +4 KB case is a size fixture, not a repacked image. Compressed growth has not yet been measured for the actual helpers. No locally enforced slot-end comparison appeared in these two write loops. An oversized fixture of **00300001 bytes** proceeds to erase an additional unit beyond **00380000**; this was observed only at simulated call boundaries and does not establish that a complete receiving session can reach that state.

## Normal update receiving limit

At **4008abc4**, `a4` is assigned **400d9e26**. The subsequent setup at **4008ac80..4008ac8e** supplies buffer **4bc47080** and capacity **001e0000** (1,966,080 bytes). The setter publishes capacity at **41924418** and buffer at **4192441c**.

The actual positive-length comparison at **400d9fca..400d9fd4** rejects when `length + 7 >= capacity`. The largest accepted positive fixture is therefore **001dfff8**, or **1,966,072 bytes**. Its successor is rejected. Both the current container length and +4 KB fixture are accepted by this branch. The +4 KB fixture leaves **859,944 bytes** below this receiving threshold.

This is a configured transport-buffer limit, not a flash-chip size or a universally verified update limit. The full receiver, every transport, signed/overflow cases, checksums, and update completion have not been executed end to end.

## Occupied flash boundaries

Main stock code actively reads/writes data at **00380000**: examples **4008a348..4008a358** (read) and **4008a3f2..4008a40e** (erase/program). A separate stock record is read/written at **003c0000**, including **4008a580..4008a590**. The bootstrap also reads a 22-byte record at **003c0000** in **80004904** and validates its integrity through **8000228c**.

Thus **00380000 is an observed occupied boundary to avoid**, earlier than the 003c0000 record. The interval from the OS start 00080000 to 00380000 is **00300000 bytes (3 MiB)**. This is a conservative non-overlap ceiling inferred from these stock users, not proof that the whole interval is exclusively reserved for OS storage. The current and +4 KB erase footprints end at 001c0000, leaving **001c0000 bytes** before that observed occupied boundary. The normal receiving-size threshold is tighter still.

## Flash identification and physical capacity

A correction to the earlier candidate interpretation: **800070d8 contains the JEDEC manufacturer byte**, not capacity. **800070d4** holds the next two identification bytes; **800070dc** is erase geometry; **800070e0** is program geometry. **80002fc6** returns the manufacturer byte after initialization.

Actual initializer branches at **80002ba8** were executed with supplied identification bytes. Recognized fixtures included **01/2018**, **ef/4017**, **ef/4018**, **c2/2017**, **c2/2018**, and **9d/6017**. The first fixture has an additional configuration byte selecting 512-byte/256 KB geometry or 256-byte/64 KB geometry; the others tested select 256-byte/64 KB geometry. These observations prove those code branches and field meanings, not which chip is fitted to this Digitone.

The recovered ordinary read/program/erase command framing sends three address bytes. That establishes a 24-bit wire address, not installed capacity. No physical capacity value or complete device-specific flash map has been certified here.

## Verification and next step

**68 checks across 25 recorded cases passed.** Actual instructions ran through both update count/address loops, the receiving-size comparison, and the flash geometry initializer. Hardware identification was supplied at its query boundary. Erase/program calls and display calls were simulated or skipped explicitly; no device connection or flash operation occurred. Full write-wrapper/MMIO execution was not included in this check.

The original SysEx SHA-256 remains **0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda**. No original, decoded firmware, or flashable package was modified.

Next: follow the complete normal-update receiver through checksum/completion and into the write path, checking final 512-byte padding and failure propagation. Then connect that evidence to the proposed extension's startup-copy/cache handoff in a PC-only integrated fixture. Physical device capacity and the broader flash ownership map remain separate unverified facts; neither needs to be guessed to continue testing a small extension within the current erase footprint.


Subsequent scope correction (receive-completion audit): the receiver configured with capacity 001e0000 is the binary/service path, with a recovered registration gated by application mode bit 0x20. Its bound is not yet verified for every ordinary SysEx or Elektron Transfer route. See Digitone-OS1.42-update-completion-checks.md.
