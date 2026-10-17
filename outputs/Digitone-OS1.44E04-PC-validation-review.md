# Digitone 1.44 E04: packaged PC candidate

E04 integrates the tested startup fallback at its planned address. The actual packaged candidate passes independent integrity/decompression checks, the stock loader instruction path, copying/cache-control ordering and loader-derived application startup into playback. It is **PC-only**, with physical cache coherence, audio/DMA timing and a real installation/recovery trial still unvalidated. No device was accessed.

Candidate: `Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx`.

SHA-256: `76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c`.

The instrument display version remains **1.44**. Use the filename and checksum to distinguish E04 from stock or other experiments. E03 and the original helper image remain unchanged.

## Change from E03

E04 changes the startup copier's count from 553 to 623 longwords, redirects initializer entry `400ffed0` from `47be055c` to `47be08a4`, and appends the 280-byte fallback. The combined helper/table/fallback payload occupies `47be0000..47be09bc`, leaving 1,604 bytes before the owner pointer at `47be1000`.

The existing scale/context helpers and table are byte-identical to E03. Invalid startup metadata or an invalid private pointer now disables context and continues through the stock initializer instead of entering the old interrupt-masked failure loop. This continuation handles its tested metadata failures; it does not recover corrupted executable code, a bus fault or a non-returning stock initializer.

Only the MAIN section contents change. Other section contents and destinations remain identical to official 1.44; offsets/checksums/padding necessarily change when MAIN is recompressed. No application USB receive freeze or audio synchronization workaround is added.

| Size | E03 | E04 |
|---|---:|---:|
| MAIN executable | 2,738,772 | 2,739,052 |
| Packed MAIN stream | 985,177 | 985,290 |
| Advertised container | 1,265,664 | 1,265,664 |
| SysEx file | 1,604,128 | 1,604,128 |

Compression at the previously tested effort level 2 adds only 113 stored bytes. Logical container padding absorbs the increase, keeping the advertised size unchanged and divisible by 512. The builder also reproduces official unchanged firmware byte for byte when given its original sections.

## Packaged-loader validation

The C compressor/decompressor round trip and independent Python decompression reproduce the exact new MAIN. Independent C integrity verification and Python framing checks pass for all 12,532 data packets, sequencing, packet checksums, container checksum and compressed-section sums. Three corruption/truncation controls are rejected by the exercised host validators. Non-MAIN section contents remain unchanged.

Every independent decompression token is checked against the staged source at `40200000` and output at `40000400`. The minimum distance from the first unread source byte to the latest output write is 342,359 bytes; no unread compressed input is overwritten.

The stock bootstrap/updater instructions load **this E04 file directly**, with no code or payload overlay. They reach MAIN entry `400004e8`, with all 2,739,052 executable bytes exact and no modeled flash writes during boot. That state continues into the actual copier: all 623 destination stores occur while the traced cache-enable bits are clear. The header starts unready. After stock clearing and cache setup at `40000568`, the complete payload still matches, with CACR `a50ce100` and ACR0 `4007e020`.

This closes the earlier gap where E03 loaded first and the extension was supplied afterward in PC memory. Cache-control ordering is observed; physical cache coherence is not simulated.

Cache-description correction from the subsequent audit: the `a0000000` mask tests the data-cache and store-buffer enables. It does not test the instruction-cache enable. Inherited CACR `0008c000` has instruction caching enabled during copying. Stock CACR `a50ce100` requests data, instruction and branch invalidation after the copy; the first helper executes afterward. See the E04 physical-cache/timing assessment for this distinction and its model tests.

## Startup through playback

The loader's pre-application handoff is saved and applied to the application engine, carrying its CPU, RAM, control-register and relevant MMIO state. Three runs use separate initialized PC-drive copies. The successful run has no firmware-code overlay. The failure controls inject bad magic or pointer `ffffffff` at the new initializer entry.

All three reach a settled interface and play pattern 2 for 1.5 seconds, then stop. The successful case retains pointer `47bccf04`; both failures retain zero. Each records 17 producer captures, 752 allocation-clear entries, two copies and 12 pitch-hook entries. Pitches and PCM match the corresponding tested final-placement overlay. The recorded task-stack and DMA envelopes still avoid the reservation.

These are staged emulator continuations, not a single physical power-on. They use a prepared drive and disclosed root/scale fields; they do not newly exercise fresh factory installation, project loading or a playing pattern replacement with sustained/queued notes. Existing helper evidence covers some of those behaviors separately.

The stock update-loop instructions also process this candidate in the simulated programming fixture: five 256 KiB erases and 2,472 complete 512-byte writes. All source reads stay inside the advertised container, programmed bytes match exactly, and data guards at `380000` and `3c0000` remain intact. Flash/display calls are simulated; this is not a completed MIDI receiving, physical programming or recovery trial.

## Practical status

E04 is a concrete new candidate for PC/emulator testing. The tested fallback is now part of its packaged executable. Physical timing/cache behavior and an actual installation/recovery exercise remain outside this result. The previously diagnosed emulator packet-age effect remains; no synchronization change was introduced to imitate stock PCM timing.

Machine-readable evidence: `Digitone-OS1.44E04-validation-summary.json`, packaging, independent checks, stock-loader check, three startup records and update-boundary checks alongside this report. Build/test scripts are under `work/build-os144-E04-pc.py`, `work/validate-os144-E04-independent.py`, `work/validate-os144-E04-loader.py`, `work/validate-os144-E04-startup.py` and `work/summarize-os144-E04.py`.
