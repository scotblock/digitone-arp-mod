# E03 compressed packaging — PC verification

**PC-only. E03 is not approved for hardware installation.** It fixes the E02 packaging-size problem while retaining exactly the same executable, startup/reset helper, context handling and pitch hooks. No scale-locking logic or startup failure policy changed.

| Item | E02 | E03 |
|---|---:|---:|
| Stored container | 3,361,440 bytes | 1,265,664 bytes |
| Packed main section | 3,081,134 bytes | 985,177 bytes |
| SysEx file | 4,260,128 bytes | 1,604,128 bytes |
| Executable | Same 2,738,772 bytes | Same 2,738,772 bytes |

The size-efficient compressor is the locally available `elektron-firmware-tool` codec at effort level 2. Its C decoder reproduces the input, an independent Python decoder agrees, and the actual stock 1.44 bootstrap/updater instructions decompress the result exactly in the PC model. These are independent checks of the candidate, not a claim that the host compressor produces Elektron’s original compressed bitstream.

The container/SysEx writer reproduces the unchanged original firmware byte for byte when given its original packed sections. E03 changes only the main stored stream, section offsets/lengths, checksums and required padding. All other section contents and destinations are unchanged. The display version remains 1.44; E03 is identified by filename and SHA-256.

## Explicit final-block padding

E03 extends the logical ELE3 container with zero tail bytes to a 512-byte boundary. This adds 176 bytes beyond the ordinary 16-byte-aligned section end. The advertised container length and checksum include those zeros. SysEx packet count remains canonical for that advertised length; transport padding is separate.

The stock loader model accepts this exact length, tail and checksum. The actual 1.44 update-loop instructions, with simulated flash/display calls, perform 2,472 full 512-byte writes. Every source read lies inside the advertised container, including the final block. No uninitialized trailing receive-buffer bytes are needed for this fixture. This does not prove the complete ordinary receiver accepts the packet stream or passes the same length to the updater.

## Update and loader results

- Five modeled 256 KiB erases end at `0x1c0000`; programmed bytes end at `0x1b5000`, below stock data at `0x380000`. Guards at both `0x380000` and `0x3c0000` remain intact. Programmed container bytes compare exactly.
- The actual recovered 1.44 positive-length service-buffer comparison accepts 1,265,664 bytes and rejects the larger E02 image. Boundary fixtures accept 1,966,072 and reject 1,966,073. This is a service-path comparison, not universal USB/MIDI acceptance.
- The stock bootstrap/updater instruction model reaches MAIN entry `0x400004e8` with the entire executable exact and no modeled flash writes during boot. A full stock boot checksum/decompression path is exercised; serial reset hardware, DSPI, flash geometry, panel and PLL/DDR hardware remain modeled.
- That same loader-created CPU/RAM/control-register state continues through the appended copier and stock clear/cache setup to `0x40000568`. All 553 four-byte helper copy stores occur while the tested cache/store-enable bits are clear, the header starts unready, and code/table bytes survive stock clearing. This closes that PC prefix continuity gap for E03; it is not full application/playback continuation or physical cache-coherence proof.
- Every independent decompression token was checked against the staged source at `0x40200000` and destination `0x40000400`. The smallest distance from the last output write to the first unread compressed byte is 342,527 bytes. No unread input is overwritten. Actual stock decoding also reproduces the entire executable.
- Independent C verification passes packet count/checksums, container checksum and compressed-section sums. Python separately checks framing, contiguous sequencing, section contents, logical alignment and output. Corrupt packet checksum, truncated end marker and corrupted transport content are rejected by the exercised validators. Those negative host checks do not certify device receiver rejection before erase.

## What remains

The current package-size and final-block source-bound problems are resolved in these PC checks. The next useful task is tracing and exercising the ordinary 1.44 USB/MIDI receiving route through checksum/completion into the updater, with this exact image. Verify correct length publication, packet failures/cancellation, and rejection before any modeled erase.

Before considering hardware, also resolve or deliberately document startup fail-stop behavior, extend 1.44 RAM/stack/DMA ownership coverage, and establish hardware cache/audio timing and recovery evidence. The existing reset wrapper still loops with interrupts masked on invalid startup metadata. E03 has not changed that behavior.

## Artifact identity

Candidate: `Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx`.

SHA-256: `8775320f161cb02efa8f51b2671034baf73eeec95f4bb66ffc20a29e9b0a2a3d`.

Main executable SHA-256, unchanged from E02: `fb5e4d89a0c0e830660f4c9ffc8dd3b98c64b8d42383fe4b0048de7bfbe35826`.

Evidence: packaging manifest, independent checks, update-boundary checks and stock-loader check JSON files alongside this report. No device I/O or real flash operation occurred. Original 1.44 and E02 files remain unchanged.
