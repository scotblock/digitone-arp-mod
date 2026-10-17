# OS 1.44 continuous PC hook integration

The producer, allocation, copy and caller/pitch hooks are connected in PC RAM. Two stock/helper pairs pass the functional playback, sustain, cancellation and confirmed pattern-handoff checks. Firmware remains unchanged and startup installation is not implemented. Audio equivalence and physical timing are not established.

## Execution and context handling

Both pairs start from the same fresh stock 1.44 snapshot and execute about 6.085 emulated seconds without resetting through the playing handoff. They use the same panel-action order and MIDI bytes; realized action times differ slightly because this engine advances instruction-paced time.

All seven hook sites are installed in the helper sessions. Producer capture, allocator clearing, normal raw copy, before/after selector, caller commit and pitch execute. The separate first-copy wrapper is not entered in these scenarios; it retains only its previous isolated ABI evidence.

The non-chromatic pair sets the source pattern's root/raw scale to 61/0 and receiving pattern's to 59/5 **before** stopped pattern selection and note generation. These are explicit PC pattern-data fixtures. No event eligibility, selected identity or context word is injected. Helper metadata comes from the executed producer/copy/commit paths.

- Sixteen producer captures match the corresponding pattern's root/scale encoding.
- All 1,357 observed eligible allocation returns have a cleared context slot.
- Both observed 72-byte cache-to-pool copies propagate their nonzero context exactly.
- Eleven quantizer calls match an independent oracle built from the extracted 1.44 scale rows; their actual fixed-point pitch outputs agree.
- Code, unused reserved-region bytes and guards remain intact, with no unexpected writes to the watched region.

## Sustained and cancelled notes

In stock and helper runs, MIDI note-off leaves the sustained-note flag/list populated through the actual pattern replacement. Pedal release clears both, and a fresh receiving note reaches pitch output.

The delayed type-0 source note is still cancelled. With helpers installed, its `+0x0C` is `0xFFFFFFFF` at release and its return site is the same stock consumer cleanup path. It never reaches acceptance or pitch output for that allocation generation. Retained context does not reactivate it.

## Eligible cached replay after replacement

The receiving pattern is published at 3220.455344 ms. At 3246.666719 ms, event `0x419ebfdc` (generation 18) on track 2 reaches pitch output with a non-null descriptor, selected identity 1 and the stock eligibility flag set. Its cached-selection state is read through helper scratch pointer `0x4139305c`. It uses retained word `0x800040bd`, captured for source root 61/raw scale 0. The event address is resolved from the original caller entry; A3 inside quantize has a different scratch role.

Its input note 69 becomes 68 under that source scale. The receiving root 59/raw scale 5 would leave it at 69. This demonstrates old-scale retention for this **eligible cached type-1 replay in the PC run**. It does not demonstrate survival of the separately delayed type-0 queued note.

## Audio and remaining coverage

The ordinary stock/helper pitch sequences match and both runs produce 1,168,256 audio bytes, but their audio hashes differ. That difference remains unexplained. Because realized input times also differ, these controls do not isolate its cause. Non-chromatic audio differences additionally include the intended pitch changes.

These finite sessions do not certify timing, cache coherence or exclusive reserved-memory ownership. Startup/bootstrap installation, reset shutdown ordering, allocation failures, all copy paths and longer voice-heavy playback remain outside this check. The late scale control that changed fields after candidate generation is excluded from the non-chromatic capture evidence.

Next, isolate the ordinary audio difference with tighter phase/input controls and repeat 1.44 render/DMA timing checks. Also exercise the first-copy route in continuous execution before treating copy coverage as complete. Keep startup installation separate.

Evidence: `Digitone-OS1.44-continuous-hook-summary.json` and the four `ordinary-stock`, `ordinary-helpers`, `early-scale-stock`, and `early-scale-helpers` continuous trace JSON files beside this report.
