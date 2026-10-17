# Digitone 1.44: continuous fallback and focused RAM checks

The scratch startup continuation passed three reset-to-interface-to-playback PC runs: valid metadata, bad magic, and an out-of-region pointer. Both failures disabled private context and retained stock note pitches. The specific heap, task-stack and observed DMA-range checks found no overlap with the proposed `47be0000..47c00000` reservation. This closes the bounded checks described here; it does not certify all possible RAM users or physical timing.

E03 and the existing helper image are unchanged. The continuation remains a 280-byte PC overlay at `47f40000`, outside its proposed final placement. No firmware was built or sent to a device.

## Startup and fallback

The overlay redirects the actual initializer entry `400ffed0` before execution. The existing E03 copier still installs the original helpers and metadata. The fault fixture changes either metadata magic or the pointer when the new initializer wrapper is entered, before its validation. The wrapper calls the actual stock initializer through the tested trampoline.

Each run starts from direct MAIN reset with a separate copy of an already initialized PC +Drive. State carries through the emulator's cold-boot, intro and settled-interface snapshots into playback. The loader prefix is outside this test. Fresh factory installation runs were interrupted after reaching the interface because excessively detailed heap logging slowed them; they are not counted as completed playback tests. The completed runs filter the allocation counter from logging.

The test selects pattern 2 while stopped, starts playback for 1.5 seconds, then stops. The root/scale fixture changes the source pattern fields on all four tracks to root 61/raw scale 0; events and context slots are not injected.

| Mode | Pointer at interface and after playback | Outcome |
|---|---|---|
| Valid | `47bccf04` | Context remains available; pitch output changes. |
| Bad magic | Zero | Stock initializer returns; interface and playback run; pointer stays disabled. |
| Bad pointer `ffffffff` | Zero | Same successful fallback, without dereferencing the bad pointer. |

Each completed run observes 17 producer-capture entries, 752 allocation-clear entries, two copies and 12 pitch-hook entries. In independent replays from each failure case's settled snapshot, restoring stock instruction bytes at the hook sites produces the same 12 fixed-point pitches as fallback. Those controls isolate playback hook behavior; they are not separate complete stock cold boots.

The failure cases' PCM hash is `f5ae8326ea1ad348efa609664ac7d7aee81752e314faa1d4819bfdeb47c571fe`; the stock-site controls produce `d2cc6e6fced9c68e2fce7729f754f49044d2a5992e403d976d945898eba8489f`. Identical pitches do not imply identical audio. The cause of this difference was not isolated in this task. These runs use the existing instruction-timed engine and host accelerations; they do not establish real DMA deadlines or audio equivalence.

## Focused RAM evidence

**Heap:** The stock MAIN image itself initializes `4024005c=419f20a0`, depth `40240068=20`, and unit count `4024006c=100000`. The implied extent is `419f20a0..429f20a0`, 16 MiB in 16-byte units. `40240064` holds the matching end value but has no recovered direct reference; the allocator uses the rank/count structure. Initialization at `400e9468..400e94c8` seeds this fixed heap. Allocation searches through rank 20, returns null when no eligible rank remains, and converts a nonnegative unit index to `base + index*16` at `400e9298`. No heap-growth operation appears in that recovered path.

Seven isolated calls to stock `400e9444` with intact captured metadata returned within the configured heap or null: 16, 64, 4096, 1 MiB and 16 MiB returned the base; 16 MiB + 1 and 32 MiB returned null. The completed continuous runs record only the initialization flag changing among the watched configuration words; base/count/depth remain unchanged. These are bounded intact-state tests, not certification against arbitrary metadata corruption or integer-overflow inputs.

**Stacks:** Probing the actual constructor entry, rather than only its literal callers, records 13 constructed tasks in the completed prepared-drive runs. All stack intervals are below the reservation. The other three literal constructor sites have explicit ranges verified in stock instructions: `40320ebc..40324ebc`, `4199ffb8..419a7fb8`, and `419cade4..419cede4`. Together they account for the recovered 16-site inventory. During these runs the lowest observed guest write in the upper 4 MiB is `47ffffcc`, near the initial `48000000` stack top. This is an observation, not a worst-case interrupt-nesting or overflow bound.

**DMA:** The probe records CSR configuration writes, including byte writes, and captures descriptors when firmware starts a software transfer through `FC04401e`. The valid run records 8,097 distinct descriptor states across channels 29, 30, 34, 35, 36, 37, 42, 47, 52, 54 and 59. Conservative source/destination envelopes account for strides, iteration counts and modulo spans, folding the configured 128 MiB DDR aliases. No envelope intersects the reservation. The highest observed DDR envelope ends at `43ea78a0`; software/audio exchange also uses the separate `1000xxxx` shared-memory and `8000xxxx` SRAM regions. No scatter-gather descriptor was observed. This is configuration/range evidence, not a hardware DMA bus trace or coverage of unexercised modes.

**Reservation stores:** Across all eight modeled DDR aliases, every observed guest store into the reservation belongs to the existing copier, metadata helpers, new scratch continuation, or stock memset deliberately called by that continuation. Every recorded store lies within the occupied span `47be0000..47be1b74`. Host-side injection is not counted as a guest store. DMA ownership is assessed separately using descriptors; CPU write hooks alone cannot prove it.

## Next concrete work

Place the tested continuation in the existing gap after `47be08a4` and before `47be1000`, update its copied extent/cache handoff in a PC overlay, and repeat the startup controls with that final placement. The current scratch placement is not suitable evidence of an integrated build. Then investigate the matched-pitch PCM difference with the timing controls before treating audio behavior as equivalent. Project-load/reset variants and worst-case interrupt nesting remain outside this workload; physical cache coherence and timing remain hardware-validation questions.

The chosen startup-menu DIN installation route is unchanged. This result does not require reopening the application USB-freeze investigation.

Machine-readable summary: `Digitone-OS1.44-fallback-and-RAM-completion-checks.json`. Supporting records: three `Digitone-OS1.44-fallback-continuous-*.json` files, `Digitone-OS1.44-fallback-stock-playback-comparison.json`, and `Digitone-OS1.44-heap-bounds-checks.json`.
