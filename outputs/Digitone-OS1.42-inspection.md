# Digitone / Digitone Keys OS 1.42 — read-only first pass

Inspected the attachment recovered from the referenced conversation. The supplied `/mnt/data/…` path is not present on this Windows host; the recovered attachment has the requested filename. No source firmware was changed and no flashable output was generated. Extracted analysis bytes are kept under `work/`.

## Identity

- File size: 1,396,768 bytes.
- SHA-256: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`.
- Embedded version: `1.42`; build text: `60095`.
- Metadata section: ASCII `241008 20:10:33`, plausibly a build timestamp (interpretation, not independently authenticated).
- Source hash was checked again after analysis and remained unchanged. Matching internal checksums establishes consistency, not official provenance.

## SysEx transport

10,914 complete messages: a start marker, 10,912 data packets, and an end marker. No bytes outside those frames.

Manufacturer bytes are `00 20 3C`; device ID is `0D`, identified as Digitone / Digitone Keys by the public tool's device table. Data command is `7E`; marker command is `7F`, with kinds `01` and `02`.

Start body: `00 20 3c 0d 00 7f 01 08 00 01 72 00 55 20`.
End body: `00 20 3c 0d 00 7f 02 08 00 01 72 00 55 20`.

Each data message occupies 128 bytes including F0/F7. Its 126-byte body contains a 9-byte header, 116 encoded payload bytes, and a checksum byte. Payload encoding carries seven full bytes in eight MIDI-safe bytes: a high-bit mask followed by seven low-seven-bit values, mask bits used most-significant first. Each packet decodes to 101 bytes.

The block/sequence counter starts at block 1, sequence 0x72 and progresses continuously, wrapping the sequence every 128 packets. Marker count `00 55 20`, interpreted as three 7-bit digits, equals 10,912.

Packet checksum, using body-relative offsets: `(base + sum(body[6+i] XOR (base+i), i=0..118)) & 0x7f`; base is `08`. All 10,912 checks pass.

Decoded stream: 1,102,112 bytes. First eight bytes are a big-endian container length and content checksum. Container length is 1,102,032; the remaining 72 transport-padding bytes are zero.

Container checksum: sum, modulo 2^32, of each big-endian 32-bit word XOR its one-based word index. Stored and calculated values both equal `B77A7EEE`.

## ELE3 container

All interpreted numeric fields are big-endian. Magic `ELE3` is at container offset 0; build text begins at 0x07, version at 0x13, section count at 0x1c, and the table at 0x20. Count is six. Each 16-byte entry contains ID, container-relative offset, stored length, and destination field.

| ID | Offset | Stored bytes | Destination field | First-pass interpretation |
|---|---:|---:|---|---|
| 5 | 0x90 | 15 | 0 | ASCII metadata |
| 2 | 0xa0 | 15,772 | 0x02000800 | Compressed bootstrap candidate |
| 3 | 0x3e40 | 925,444 | 0x40000400 | Compressed main OS candidate |
| 4 | 0xe5d50 | 32,776 | 0x80000400 | Raw executable/updater candidate |
| 6 | 0xedd60 | 1,492 | 0 | Raw boot-stub candidate |
| 7 | 0xee340 | 126,352 | 0 | Raw code/blob candidate |

Role names are reverse-engineered conventions, not Elektron documentation. In particular, section 2 should not automatically be called a DSP image: its extracted text includes `STARTUP MENU`, `OS UPGRADE`, and `BOOTSTRAP UPGRADE`.

Last section ends at 0x10d0d0. Container ends at 0x10d0d0 + 32. A 32-byte trailer is present at the position the public tool interprets as HMAC-SHA256. Its HMAC was **not verified**: the tool's anchor-based key-material search did not produce a matching digest from the inspected payloads. This does not establish corruption or prove a different algorithm; compatibility of that part remains unresolved.

## Compression and executable clues

Sections 2 and 3 match the tool's aPLib-like LZ77/interlaced Elias-gamma decoder. Each begins with `[32-bit compressed-stream length][32-bit byte sum]`.

- Section 2 stream length 15,764; stored/calculated sum `001A10D7`; decoded output 28,766 bytes.
- Section 3 stream length 925,434; stored/calculated sum `05ED890D`; decoded output 2,420,912 bytes. Its table length includes two bytes beyond the eight-byte header plus declared stream.

Both decodes exhausted their input without an explicit end marker. The public decoder supports this through `allow_trunc`; therefore these are provisional decoded sizes, not proof of a fully terminated stream. Code and meaningful strings were recovered, but completeness needs a second implementation or the compiled C tool.

Main payload begins `400004e8 00000000 00000000 00000000 46fc2700 …`. This is a raw memory image, not an ELF or PE header. `46fc2700` is consistent with a 68k-family supervisor/status-register instruction; bootstrap and blob prefixes also contain recognisable 68k-family patterns such as `4e73`. Together with the public tool's cross-image observations, **big-endian ColdFire/68k-family code is the likely target**. Exact CPU model and instruction variant are not established in this pass.

Main image has C++ RTTI/type-name strings, including `ArpSetupMenuView`, `ArpPatternCopy`, and `ScaleMenuView`, plus musical-scale names. These are useful analysis anchors, not a complete symbol table or located note-processing routines. `ScaleMenuView` alone does not prove pitch quantization: Elektron also uses “scale” for sequencer timing/length.

Useful main-image file offsets include:

- 0x1b7acb: `ArpSetupMenuView`.
- 0x1b7adc: `T%d ARPEGGIATOR`.
- 0x1bce13: `ScaleMenuView`.
- 0x1c242a: `PENTATONIC MINOR`, followed by other musical-scale labels.

Do not turn these into runtime addresses until the load map and any image prefixes are checked.

## Tool applicability and next step

Reviewed source of [mischa85/elektron-firmware-tool](https://github.com/mischa85/elektron-firmware-tool), revision `a5bce9a6af644386d900924082993a805e812874`. Its transport, ELE3 table parser, section byte sums, and compression decoder closely match this file. This analysis used a small local Python implementation of those read-only operations; the C executable was not built or run. HMAC support for this exact image remains unproven. [Source for container parsing](https://github.com/mischa85/elektron-firmware-tool/blob/a5bce9a6af644386d900924082993a805e812874/container.c), [codec](https://github.com/mischa85/elektron-firmware-tool/blob/a5bce9a6af644386d900924082993a805e812874/aplib.c), and [integrity](https://github.com/mischa85/elektron-firmware-tool/blob/a5bce9a6af644386d900924082993a805e812874/integrity.c).

Safest next step is still offline: independently verify extraction with the compiled tool, resolve stream termination and the trailer verification, then import the main image into Ghidra with a provisional big-endian ColdFire configuration. Validate the load map and disassembly before tracing arpeggiator string references into note generation and tracing musical-scale tables into keyboard handling. Identify the final arp note emission and the actual selected-key/scale storage before designing any change.

V1 feasibility is not yet established. First define whether offsets remain semitones followed by scale snapping, or become scale degrees; these are different behaviours. For minimal scope, semitone offsets followed by deterministic snapping is a reasonable candidate, pending the user's choice and code evidence. Test that musical rule offline, including negative offsets, octave crossings, MIDI bounds, and chromatic mode.

No rebuilding is necessary for this next phase. A later explicitly scoped stage could test unchanged byte-exact repacking and hardware recovery procedures, before any modified image or hardware test. Neither successful checksum validation nor the existence of startup-upgrade code demonstrates reliable recovery from arbitrary firmware changes.
