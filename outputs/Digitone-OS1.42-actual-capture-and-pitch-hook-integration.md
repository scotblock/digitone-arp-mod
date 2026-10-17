# Digitone OS 1.42: actual capture and coarse-pitch hook integration

3 October 2026. PC-only machine-code fixtures and read-only firmware analysis. Firmware remains unchanged; no modified or flashable image was produced.

## Result

The **pooled sequencer-event path** now connects root/scale capture instructions to actual stock arp acceptance, actual stock selection and a coarse-pitch hook. The test enters the recovered sequencer finalization boundary with its backing pointer and track registers, captures bytes from that backing, and carries the resulting word through accepted metadata into pitch processing.

**5,475 assertions passed**, including 5,256 quantizer comparisons, all four synth tracks through the connected path, guard failures, negative stock selection returns, ordinary-note preservation and event recycling. This advances the instruction prototype; it is not complete producer coverage or a hardware result.

**The complete tested layout no longer fits the established resident candidate.** The prior resident bodies occupy 844 bytes, and these additions require 834 bytes: 1,678 total versus 864 available. The shortfall is 814 bytes. New bodies therefore run at synthetic addresses beginning at `50010000`; no physical executable ownership is implied.

## Actual capture

The sequencer builder's recovered finalization boundary at `40093ef4` has:

- a2: event being finalized;
- a3: actual source pattern backing B;
- d4: source track t.

The fixture replaces the two track-field stores with a wrapper, then replays them and resumes at `40093efc`. The capture instructions read unsigned root at `B + 3d0*t + 3cb` and signed raw scale at `B + 3d0*t + 3ce`. They validate track, pointer, root and raw scale and produce the previously tested snapshot encoding, with raw -1 represented as scale index zero.

Capture checks the allocated metadata header, readiness, writer-busy and capture-fault words. It saves/restores SR and masks interrupts during the bounded read. Invalid or unavailable capture yields zero. **The busy/fault words are test inputs; writer-side hook coverage is not implemented by this experiment.** Masking this read alone cannot certify that a writer was not already paused midway through a pattern transaction.

The candidate writer stores into the separate metadata slot only when the destination exactly matches one of the 128 fixed playback events. It does not use stock event union bytes. Held-template, sequencer-cache and delayed-queue address classes are not connected by this writer.

The event allocator now has a fixture wrapper that clears candidate metadata before returning a newly allocated slot. The allocator takes no arguments, allowing an extra return frame without shifting argument offsets. Null allocation remains a stock zero return. A recycle test establishes that the same event address cannot inherit its old snapshot after actual free/reallocation.

The producer tests deliberately set the current global pattern pointer to a different backing before capture. The result still uses the producer's B. They then edit B after capture; the accepted word remains the captured value. This tests source ownership and snapshot persistence without supplying the encoded snapshot from Python.

The full sequencer builder is not executed from `40093c26`: these tests enter its recovered finalization boundary, and other note/settings fields are controlled inputs. Cached synth type-one pitch reading is tested, but its cache producer/copy route is not connected here. Live held-input and streamed delayed-input capture remain outstanding.

## Pitch hook

The insertion window is the eight bytes at `4009df9a`: push d3, load seven into d5, then load event flags. The wrapper runs the new reader/quantizer, updates only the saved d6 slot, restores the remaining registers and SR, replays all three displaced instructions, and resumes at `4009dfa2`. Stock fixed-point conversion then runs unchanged.

The reader validates synth event type 0 or 1, note-on state, playback track, arp flag, nonzero identity, matching stock state identity, nonempty active list, and matching retained event type/state/track/identity/arp flag. It then resolves the metadata header and reads the accepted record using its identity and playback binding.

Stock guards and the metadata read run in a short interrupt-masked section. The reader restores the previous interrupt state **before** quantization, which uses only the copied snapshot and immutable membership data. Completed accepted context remains usable when new capture is busy or faulted; that state does not erase an older accepted snapshot.

The quantizer calls actual stock membership function `40106b6c`. It searches lower candidates before equally distant upper candidates, giving downward ties. Chromatic or missing/malformed context preserves the coarse note. It constrains the already transposed 0..127 note, while leaving allocation identity and later octave/bend handling intact. It does not implement the prototype's optional full-width overflow rejection before the two stock byte stores; stock byte narrowing remains in this experiment.

The hook's successful-selection provenance is exercised through the actual initial selection route. Real disabled-step and stale-identity selection returns take stock negative branches, zero the note count and never enter the hook. This is not exhaustive recovery of every branch into the shared note loop.

## Connected execution examples

Controlled notes start at 64, use a stock arp step offset of +2, and then a global transpose of -5. Stock allocation note is therefore 66 and coarse pitch is 61.

| Playback track | Captured major-scale root | Coarse pitch after hook | Allocation note |
|---|---:|---:|---:|
| 0 | 60 | 60 | 66 |
| 1 | 61 | 61 | 66 |
| 2 | 62 | 61 | 66 |
| 3 | 63 | 60 | 66 |

All four cases execute stock setup, retained copy, selection, timed tick publication and the note loop through the fixed-point conversion boundary. Selection is no longer supplied by a Python model. The first case distinguishes captured C major from the different current D-major backing, which would allow coarse 61 unchanged.

The producer wrapper matches unmodified execution for every register, exact SR and all event bytes. The pitch wrapper matches the unmodified path for every register except its intended d6 change, exact SR, stack and event bytes. d1 retains the stock allocation note. Actual voice allocation, audio rendering and downstream pitch processing are not executed by these connected cases.

Guard tests cover invalid event/retained types, release state, unsupported track, absent arp flag, zero/stale identities, empty head, invalid metadata binding, busy metadata, missing/corrupt snapshot and unavailable owner/header. Remapped input context does not override the destination track's accepted snapshot. An ordinary non-arp event matches stock execution exactly.

## Space accounting

| New fixture body | Bytes |
|---|---:|
| Root/scale capture | 140 |
| Fixed-event candidate store | 70 |
| Quantizer using stock membership | 184 |
| Validated pitch reader | 256 |
| Sequencer finalization wrapper | 66 |
| Pitch insertion wrapper | 58 |
| Allocation invalidation wrapper | 60 |
| **Additional total** | **834** |

Even an optimistic estimate that shortens every four-byte branch to two bytes leaves 1,524 bytes overall, still 660 bytes above the resident capacity. This is a lower-bound estimate for branch shortening alone, not an implemented compact layout. More substantial compaction or another justified executable interval is required.

Four larger runs were screened. The 1,040-byte FF run at `40209f1c..4020a32c` has both bounds passed as existing resource arguments. The 878-byte zero run at `4023c302..4023c670` contains existing pointer targets. The 2,064-byte zero run at `401fd47c..401fdc8c` includes an explicitly read word and neighboring table references, so it is not available wholesale. A 1,024-byte run at `401fbf8c..401fc38c` has no even-aligned absolute reference in this screen, but follows floating-point data and still requires indexed-owner analysis. No new code cave was certified.

## Remaining limits and next step

New executable placement, held/cache/queue producer and copy coverage, complete pattern-writer guards and hardware timing remain unresolved. The bounded custom interpreter does not simulate CPU caches, DMA, asynchronous producers, exception cleanup or real audio deadlines. The prior cold allocation/initialization fixture remains separate from this suite; caller tests supply an initialized owner/header. No full Digitone emulation is claimed.

The next focused placement target is the 1,024-byte candidate's table boundaries and indexed readers, alongside meaningful code compaction. In parallel with later integration, the held/queued capture and metadata propagation hooks need the same instruction-level treatment. The successful pooled sequencer path does not establish those input paths automatically.

Evidence: `Digitone-actual-capture-and-pitch-instruction-results.json` contains assertions, examples, new-body disassembly and the exact size ledger. `Digitone-capture-pitch-hooks-and-space-audit.json` records seven original hook anchors and larger-space findings. The reproduction script is `work/test-actual-capture-and-pitch.py`.

Original SysEx SHA256 remains `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`; decoded main SHA256 remains `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.
