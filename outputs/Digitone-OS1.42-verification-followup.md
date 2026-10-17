# OS 1.42 verification follow-up

Continued offline without modifying the source or producing a flashable image.

## Compiled decoder verification

Compiled the public tool's C transport, container, codec, and integrity modules using the installed Microsoft C compiler, with a small read-only inspection harness. A copied header was adapted to remove GCC's packed-struct attribute; these packet structures contain only byte fields and their original size assertions passed. The original downloaded source remains intact. The rebuild-capable command-line program was not run.

The C implementation independently confirmed the earlier Python port's output:

| Section | Decoded bytes | SHA-256 |
|---|---:|---|
| Bootstrap candidate, ID 2 | 28,766 | `add6888d665622d3123f3e6290971e5d1f9968adf760df7c3716658afcd25128` |
| Main OS, ID 3 | 2,420,912 | `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6` |

Packet checksums, declared packet count, and container checksum all pass. The tool finds no digest key and leaves its digest verdict at “absent/unchecked”; its overall checksum-success flag must not be read as authentication success.

This checks the Python port against the actual C implementation, not against an unrelated codec. Both tolerate input exhaustion. The bootstrap's first word is `0x7056` = 28,758; adding its apparent eight-byte image header gives 28,766, exactly the decoded size. That is additional evidence for complete bootstrap extraction, although the header semantics still need verification. There is no comparable confirmed decoded-size field for the main image yet.

## Trailer clarification

The final 32 container bytes are **all zero**. The previous report described their position as an apparent HMAC-SHA256 trailer; this follow-up establishes that there is no populated digest in that position for this image. Do not characterize it as a failed HMAC or authenticated firmware. Whether Digitone 1.42 uses that field differently, leaves it unused, or enforces integrity elsewhere requires code analysis.

## Code and scale anchors

Assuming the main image is loaded at its section destination `0x40000400`, absolute references point to the expected strings. For example, `48 79 40 1b 7e cb` is a 68k-family `PEA` of the `ArpSetupMenuView` string. This supports the proposed base and CPU family, but does not establish the exact ColdFire variant or full memory map.

| Anchor | Main-image file offset | Provisional runtime address | Reference file offsets |
|---|---|---|---|
| `ArpSetupMenuView` | 0x1b7acb | 0x401b7ecb | 0x4eb48 |
| `T%d ARPEGGIATOR` | 0x1b7adc | 0x401b7edc | 0x4ecf4, 0x4f292 |
| `ScaleMenuView` | 0x1bce13 | 0x401bd213 | 0xaece2 |
| `PENTATONIC MINOR` | 0x1c242a | 0x401c282a | 0x1fff98 |

The `PENTATONIC MINOR` reference is in a series of pointers to nearby scale-name strings. It is a useful musical-scale UI table anchor, not yet a proven pitch-class mask or quantizer. The arpeggiator references likewise identify UI code first; tracing through storage and note events is still necessary.

## Safest next step

No Ghidra installation was found in the checked standard program locations or Downloads. Continue with a full disassembler capable of ColdFire: import the verified main image as raw bytes at the provisional base, confirm startup instructions and function boundaries, then follow the arp UI/storage references and musical-scale table references into note processing. Avoid assuming the sequencer “scale” page is the musical-key implementation.

The next concrete milestone is a documented pair of functions: the arp's final pitch calculation/emission and the musical key/scale mapping, with their parameters and storage locations. Only then can we judge whether a small scale-lock change is practical. Stream completeness and the update integrity rules remain relevant before any future rebuilding.

Reference source: [elektron-firmware-tool revision a5bce9a6af644386d900924082993a805e812874](https://github.com/mischa85/elektron-firmware-tool/tree/a5bce9a6af644386d900924082993a805e812874).
