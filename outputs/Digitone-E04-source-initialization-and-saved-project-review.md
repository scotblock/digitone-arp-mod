# E04 source initialization and saved-project startup

8 October 2026. PC-only investigation. Stock 1.44 remains installed on the physical Digitone. E04 and the original saved emulator files are unchanged.

## Result

9 October clarification: the subsequent `Digitone-E04-restore-versus-replace-review.md` identifies the real restore mirror banks at `0f400000` and `0f800000`, validates retained RAM's existing header and successfully cold-restores it with stock and E04. The `0fc00000` region discussed below is special project index 128; its write-before-read ordering did not itself identify the restore decision. The actual old-test default selection is now confirmed by invalid mirror headers and failed modeled SPI recovery.

The eight early producer captures use root/scale fields that stock code has already initialized in the tested startup. No capture-before-initialization is observed.

The more consequential finding is a gap in saved-project coverage. Cold-starting from a copy of the user's saved emulator drive does **not** restore the enabled-scale pattern held in the user's saved RAM session. The modeled startup writes a replacement working project before its first read of that working-project area. A successful cold run with this drive therefore cannot be counted as successful restoration of the user's saved project, or as reproduction of the physical device's startup state.

The physical logo freeze remains unreproduced and unexplained.

## Executed comparisons

Four independent cold starts use stock 1.44 or unchanged E04 with either the previously initialized factory drive or the saved stock emulator drive. Every run uses a separate sparse card copy, direct MAIN entry with loader-matching flags, native DTIM1 completion and no host delay-semaphore kicks. Cold snapshots continue through intro with general forced semaphore completion disabled.

| Firmware | Card copied from | UI reached | Native DTIM1 interrupts | Early captures |
|---|---|---:|---:|---:|
| Stock 1.44 | Factory emulator drive | Yes | 3 | 8 |
| E04 | Factory emulator drive | Yes | 3 | 8 |
| Stock 1.44 | User's saved stock emulator drive | Yes | 3 | 8 |
| E04 | User's saved stock emulator drive | Yes | 3 | 8 |

Each reaches one intro exit and 138 main-loop entries. All eight captures use source `407fd414`, with track indices alternating 0 and 3. All E04 captures see private ready=1. The complete normal producer routine is entered 16 times: stock selection produces only eight arrivals at the capture site. These are not 16 eligible capture events.

## Source selection and initialization

The actual producer function is `4009451e`. At entry, its stack arguments include track index and source object; it loads the supplied source into A3 at `40094528`. The observed caller returns to `40094d72`. The corresponding call at `40094d6e` pushes the source from global `4138f214` at `40094d66`; that global matches A3 in every observed capture.

Stock selection publishes `407fd414` to `4138f214` at `40094f4a`. The track fields are populated earlier by the stock conversion routine entered at `40008c3c`, returning to `4000908c`:

- Root is read from serialized track offset `3c6` and written to runtime offset `3cb` at `40008d0a`.
- Scale is read from serialized offset `3c9` and written to runtime offset `3ce` at `40008d5a`.
- The recovered conversion code range-checks these fields; the observed outputs are ordinary valid root bytes and the disabled-scale sentinel `ff`.

The additional origin trace records the first four destination track bases `407fd414`, `407fd7e4`, `407fdbb4`, `407fdf84`, paired with serialized source bases `405561f8`, `405565c8`, `40556998`, `40556d68`. Their roots are 67, 84, 84 and 60; all scales are `ff`.

The root/scale stores occur around modeled instruction estimate 69.1 million. Private initialization is entered around 105.0 million; the first capture is around 106.2 million. These estimates are coarse block-budget coordinates, not hardware timing measurements. The write watches were installed before execution and each capture retains the last observed guest writer for every track's root/scale byte. No late replacement of those fields appears in the observed interval.

This establishes ordering and the argument chain for this PC startup. It does not certify all source-object ownership, all saved projects or physical input values.

## Saved RAM is different from cold restoration

Both retained stock and modified GUI resume snapshots hold `4138f214 = 407fd414`. Their first track has root 60 and raw scale 0, an enabled scale. Their pattern hashes differ from one another, while their alternate patterns match. These snapshots begin after boot; executing them would skip the restoration path under investigation.

Both saved drive files also differ from the factory drive: 5,384 sectors differ, all within byte offsets `0fc00000..0fea7600`. The saved stock working-project header at `0fc00000` begins `beefbace0000000e` and contains `NEW PROJECT`; the separate project-slot-0 header at `10000000` contains `PRESETS`. Card settings-sector probes at `0f400000` and `0f800000` read zeroes.

The origin run using E04 and the saved stock drive observes:

1. Track conversion and all eight early captures use the same disabled-scale startup pattern as the factory-drive controls.
2. Stock programming writes the working-project region beginning at `0fc00000` using command 25. The first write is 65,536 bytes, at `400f5e54`, around estimate 118.3 million.
3. Thirty-nine writes in that region occur before its first read.
4. The first command-18 read of `0fc00000`, at `400f5c4c`, occurs around estimate 119.0 million, after the replacement writes.

Consequently that first read cannot demonstrate restoration of the original saved bytes. These writes affect only the disposable test copy, not the user's original card files.

The cold engine's `build_flash` constructs a zero-filled 16 MiB flash image and places only the SYX container at offset `80000`. The traced configuration/header reads at offsets `3c0000`, `400000`, `800000` and `c00000` therefore return zeroes; they are not a dump of the physical instrument's persisted settings. This is an identified model-state difference. The exact firmware branch connecting those settings/header checks to working-project replacement still needs tracing; blank values alone do not establish every causal branch.

## Consequence and next focused target

The prior early-capture access pass remains valid for the captured disabled-scale inputs. The new runs establish that those inputs are initialized before capture. They provide **no new certification of saved-project restoration** and no diagnosis of E04's physical startup failure.

Next trace the decision that chooses working-project restoration versus replacement, including its settings/header validity checks and selected project state. Reproduce the existing-project branch with documented PC state before drawing conclusions from further cold-start passes. Do not insert guessed metadata, merge unrelated resume state into boot, or treat an after-boot RAM resume as a restoration test. The underlying physical saved-project state is not available in these emulator artifacts.

## Evidence and preservation

- `Digitone-E04-source-startup-checks.json`: all four cold/intro runs, source writers, producer arguments, selection-pointer writes and capture inputs.
- `Digitone-E04-source-origin-checks.json`: successful extra E04 cold/intro run, serialized-track entries, card read/write ordering and cold flash reads. Storage-origin instrumentation is cold-stage only; the four comparison runs also watch intro.
- `Digitone-E04-saved-project-state-checks.json`: original card hashes/differences and read-only resume-state inspection.
- `Digitone-E04-source-startup-summary.json`: passing ordering/comparison assertions and preservation hashes.
- Scripts: `work/trace-E04-source-startup.py`, `work/trace-E04-source-origin.py`, `work/inspect-saved-project-state.py`, `work/summarize-E04-source-startup.py`.

An origin-trace observer initially assumed the intro engine exposed its card as `m.esdhc`, which it does not. That instrumentation error was corrected by limiting storage-origin watching to the cold engine; the complete origin test was rerun successfully. It was not a firmware execution failure.

All original emulator card hashes remain unchanged. E04 SYX SHA-256 remains `76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c`. No firmware was rebuilt or transmitted.
