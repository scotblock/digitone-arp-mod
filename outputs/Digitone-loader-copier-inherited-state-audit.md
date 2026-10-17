# Digitone OS 1.42: inherited loader state and early copier

The full loader-to-copier chain passes in the native PC engine for the tested normal boot route. Physical cache coherence remains unverified. No firmware file was changed or generated for installation.

## What ran

The original bootstrap and updater executed against emulated SPI flash, using modeled Digitone panel responses and board straps. The original MAIN image reached its entry at `0x400004e8` with every decoded byte matching. This includes the stock reader, checksum and decompression path; it is no longer an isolated loader-tail fixture.

A second run placed an extended MAIN image only in process memory and emulated flash. It contained the PC overlay hooks, early copier and 2,324-byte optimized helper/table image. All other container sections retained their original bytes, with section offsets adjusted in memory. MAIN used an all-literal compressed stream with a valid length, byte sum and end marker. This tests acceptance of that specific stream and container layout; it does not validate a future production compressor or the firmware-update receive/write path.

The native loader reconstructed the entire extended MAIN exactly. The same machine then continued into the early copier without replacing registers, boot flags, MAIN bytes or the extension source. The loader supplied boot flags `0x00140000` naturally.

## Observed handoff

| Point | CACR write/state map | ACR0 | Result |
|---|---|---|---|
| Loader MAIN decompression | `0xa508e000` | `0x4003e000` | DDR region uses write-through data caching |
| Loader-to-MAIN entry | `0x0008c000` | `0` | Data cache and store buffer disabled |
| Copier entry and return | `0x0008c000` | `0` | Same inherited copy conditions |
| Stock cache setup after copy | `0xa50ce100` | then `0x4007e020` | Invalidation requests, followed by DDR copyback mapping |

The full route's inherited CACR is `0x0008c000`. The earlier isolated-tail fixture produced `0x000cc100`; it is not evidence of the state on this observed full route.

The copier executed all 581 longword stores, including the complete 420-byte lookup table. The source matched before and immediately after copying. The copied destination matched again after stock RAM clearing and cache setup, at `0x40000568`. Metadata contained the expected magic, version and size, with readiness still zero pending initialization.

The original source is subsequently reclaimed by stock clearing at `0x400004d2`. That is expected: its lifetime ends after the early copy. The reserved destination remains intact in this run.

## Coherence interpretation

The observed copy uses neither the data cache nor the store buffer. The loader also executes the synchronizing NOP at `0x80000632` before its final control changes. Stock setup requests both data and instruction invalidation after copying and before the resident helper's later use.

NXP documents that disabled store buffering makes writes wait for external transfer completion; NOP and supervisor instructions drain pending push/store buffers. Invalidation removes valid cache entries but is not a substitute for pushing dirty copyback data. These rules support coherence for the observed sequence; the copied bytes are not dirty copyback contents discarded by that invalidation. See [MCF5441x Reference Manual](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf), §§6.3.1, 6.3.2, 6.4.4.2.2 and 6.4.6.

A small trace-derived value model passes the observed sequence and rejects controls that retain stale cache entries, discard dirty copyback data, or leave delayed writes undrained. This checks the interpretation of the rules, not physical implementation or timing.

The emulator's control map records MOVEC writes, including invalidate request bits that hardware would clear automatically. It does not implement physical cache tags, cache-line data, store-buffer completion or DDR visibility. Serial-reset loading is represented by preloaded SRAM; peripheral completion and board responses are modeled. This run stops after early cache setup, before the full initializer and playback. Earlier startup/playback tests began from supplied MAIN state and cannot be presented as one continuous loader-derived run.

## Next step

Carry this loader-derived machine state through the full initializer and playback, including first execution and lookup reads from the copied helper. That closes the next PC continuity gap. Physical certification still requires independent evidence for real cache/DDR behavior; these PC results alone do not establish it.

Both runs made no emulated flash program/erase operations. Original SysEx SHA-256 before and after: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`.

Evidence: `Digitone-stock-loader-cache-continuity.json`, `Digitone-continuous-loader-copier.json` and `Digitone-inherited-cache-checks.json` in this output directory.
