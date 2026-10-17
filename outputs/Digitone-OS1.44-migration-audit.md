# Digitone / Digitone Keys OS 1.44: first migration audit

The uploaded file matches the stock 1.44 fingerprint recorded by Elekloader. It is a viable new PC development baseline. The 1.42 arp integration cannot yet be carried over by changing addresses alone: the selector contains instruction changes, and startup, updater and RAM layout have changed. Neither firmware was modified, no flashable output was produced, and no device update was performed.

## Container and extraction

The file is 1,673,760 bytes, SHA-256 `d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659`. Its transport uses Elektron SysEx, 8-in-7 packing, numbered data packets and packet checksums. All 13,076 data packets pass; numbering is contiguous. The decoded preamble/content checksum agrees (`0x7586488b`), and final padding is zero.

The ELE3 container has seven section descriptors, versus six in 1.42. Packed sections use a length/checksum prefix and the existing Elektron LZ codec. Two Python implementations independently produce identical extracted bootstrap, main and new section-8 bytes, recognizing the stream terminators. This verifies decoding, not hardware execution.

| Section | Interpretation | Comparison with 1.42 |
| --- | --- | --- |
| 5 | Build timestamp/version metadata | Changed |
| 2 | Bootstrap; destination word is a version, not an executable load address | Changed; 29,230 unpacked bytes |
| 3 | Main ColdFire program, load base `0x40000400` | Changed; 2,736,304 unpacked bytes, 315,392 more |
| 4 | Updater, raw at `0x80000400` | Same size; 14,413 bytes differ |
| 6 | Second-CPU descriptor | Byte-identical |
| 7 | Second-CPU image | Byte-identical |
| 8 | Additional compressed payload | New; 159,948 unpacked bytes |

Section 8 contains USB/host, configuration and upgrade-related strings, including a `1.00E` version string. Its actual load/execution role remains unclassified; strings alone do not establish it.

Main-program SHA-256 is `fce648a97c6c5d93b961732e8f8db6b02e0820c6d344c7e2131fa05a4b3168e4`. Code decoding and the independently recognized image identify the same ColdFire executable family as our 1.42 baseline. This is an address-based firmware image, not an ELF with relocation metadata.

## Candidate port map

The following locations have multiple unique neighboring eight-byte anchors and matching ColdFire instruction lengths/operation/control classes over at least 128 bytes from each site. Absolute references were inspected separately. These are strong static correspondence candidates, not verified behavioral replacements or patch approvals.

| Role | 1.42 | 1.44 candidate |
| --- | --- | --- |
| Early startup call | `0x40000538` | `0x40000538` |
| Producer context capture | `0x40093ef4` | `0x400947ec` |
| First cache copy | `0x4009344e` | `0x40093d46` |
| Cache copy wrapper | `0x40093892` | `0x4009418a` |
| Before selector | `0x4009dda6` | `0x4009e68e` |
| Caller commit | `0x4009de46` | `0x4009e72e` |
| Pitch insertion | `0x4009df9a` | `0x4009e882` |
| Allocation/clear | `0x400f0626` | `0x400ffff2` |
| Pool initializer | `0x400f0504` | `0x400ffed0` |

The acceptance caller points directly to selector candidate `0x40097a94`; the commit neighborhood also calls the mapped allocation and later-pitch routines. The memcpy candidate is `0x400fbad8`, with the first 128 bytes identical to the old routine. Referenced event-pool base changes from `0x4199da94` to `0x419ebe2c`; queue-clock references change from `0x413360e8` to `0x413831ac`. Other globals also move. There is no single relocation offset for the whole program.

A fuller selector interval comparison covers 960 old bytes and 946 new bytes (317 versus 315 decoded instructions). It reveals register and stack-slot changes and changed event-list operations, including the absence in the aligned new sequence of the old `clr.l +8` and following global pointer store near `0x40097536`. Some differences may be compiler transformations. We have not established their behavioral effect or tied them to a particular bug fix. The original selector's first 128 bytes matching in instruction shape does not establish equivalence of the whole routine.

## Startup and existing tools

All eight stock-byte signatures in Elekloader's explicit 1.44 core port match the supplied main program, including its early bootstrap and render hooks. Its recorded whole-file and main-program hashes also match. This gives concrete evidence that its versioned extraction/integration framework applies to this file; it does not certify our custom arp code.

Directly checked startup operands show SRAM-copy source intervals beginning at `0x4028f000` and `0x402948f0`, ending at `0x402948f0` and `0x4029c4b0`. The stock initial clear uses `0x4028f000` through `0x4322ae60`. These actual 1.44 constants are 0x1000 above the clear endpoints described in the local Elekloader device commentary. Use the checked bytes, not that commentary's numeric bounds, for further modeling.

The proposed `0x47be0000` overlay remains above that initial clear interval. This proves only that this specific clear does not cover it. It does not establish exclusive ownership, later preservation, physical cache coherence or playback timing.

## Safest next step

Establish a clean **stock 1.44 PC execution baseline** and replay the changed selector's success, no-selection, allocation-failure, sustain/release and pattern-handoff paths. Confirm event-field ownership and the moved RAM references against actual execution. Then port the compact helpers as PC-only overlays, validate the new startup path, and repeat matched stock/overlay playback and timing tests.

Our 1.42 tests and prototype remain useful references. They are not 1.44 test results. No conclusion here resolves the previous modeled DMA timing regression or demonstrates physical hardware safety. Keep the hardware unchanged during this port audit.

Detailed evidence: `Digitone-OS1.44-inspection.json` and `Digitone-OS1.44-migration-comparison.json` beside this report. Both source firmware hashes and the extracted 1.42 main-program hash were checked unchanged after analysis.
