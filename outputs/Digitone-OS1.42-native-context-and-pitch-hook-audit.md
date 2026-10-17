# Digitone OS 1.42 — native context and pitch overlay test

The PC-only hooks now execute successfully in the patched native Digiemu engine. A real running arp path captured its context, accepted it, read the retained context at the pitch hook, and changed 11 notes according to the independent scale table. Firmware files remain unchanged. This is a bounded emulator result, not hardware certification.

## Running firmware evidence

The stock and overlay sessions began from the same settled stock GUI snapshot. Each ran 10.07 emulated seconds with Play, four track/trig input sequences, pattern 2 then pattern 1, and Stop. Both completed without halting after the instruction correction.

| Recovered stock boundary | Overlay hits |
|---|---:|
| Fixed-pool allocation | 1594 |
| Sequencer producer finalization | 20 |
| Arp/event acceptance | 21 |
| Retained-copy commit | 1 |
| Shared coarse pitch boundary | 31 |

All 18 eligible producer captures matched the root, raw scale and track read from their actual backing pointer. Two producer events were outside the supported fixed pool (`419a304c`, `419a3124`); the helper intentionally stores no candidate for them. The capture observer initially misclassified these as mismatches; the corrected observer classifies them explicitly. Supporting these events remains separate work.

The stock pattern's real arp path was on zero-based track 2 (user track 3), initially chromatic. An additional controlled playback fixture changed that source track's RAM root to 61 and raw scale to 0 immediately before producer capture. It then changed the source to root 62/raw scale 5 after capture. No event flags, arp selection state, acceptance return or note value was fabricated in this playback fixture.

The real acceptance committed context `800040bd`, bound to identity 1 and track 2. Eleven subsequent actual pitch-hook calls still read that retained word despite the later source edit. They produced `57 → 56`, `69 → 68`, and `81 → 80`, exactly matching the independent scale-table oracle. All 31 observed pitch outputs also matched the stock fixed-point conversion at `4009dfa8`. The coarse input sequence matched the stock baseline.

This validates retention after this explicit source edit. It does not establish behavior for every pattern switch, writer race, queued live note or other producer.

## Native instruction correction

The first overlay halted on an illegal instruction at `47be0158`: immediate comparison with a memory operand. The earlier custom interpreter had accepted that encoding. The native CPU check exposed it.

Ten such comparisons were lowered to register comparisons with a saved scratch register. Local branches and absolute intra-code targets were relocated, and the corrected helper image grew from 1,712 to 1,892 bytes. It still fits below the private pointer at `47be1000`. This correction is confined to scratch helper construction and emulator RAM. The prior startup/bootstrap fixture has not yet been rebuilt and tested with this expanded native image.

## Controlled native checks

* 162 quantizer cases covered six scale values, three roots, MIDI boundaries and off-scale pitches against an independent table oracle.
* Four track fixtures executed the actual producer hook and compared all data/address registers, SR and resulting event bytes with the displaced stock instructions.
* Four track fixtures executed the actual pitch hook through the stock fixed-point boundary, verified changed output, compared all other registers and SR with stock, and tested invalid-context fallback.
* A paired actual allocator call from the same stock snapshot matched stock registers, SR and pool bytes, while clearing a deliberately stale candidate.

Explicit selection/cache/event fields were supplied in these isolated fixtures. They validate the hook bodies and continuation ABI; they do not establish those preconditions independently.

## Memory and firmware checks

The final playback watched guest writes through all eight DDR aliases, including a margin for accesses crossing the region edge. No unexpected watched write occurred. Code bytes and the unused reserved region/guards remained intact. Expected metadata writes came from helper instructions. The stock owner remained `419c38c0`; private context storage did not replace it.

The complete original SysEx hash before and after was `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`. Main section hash remained `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`. No modified firmware, update container or flashable image was produced; only temporary RAM overlays and helper scratch bytes were used.

## Remaining limits and next step

The chromatic overlay produced the same observed coarse pitches as stock, but its captured audio hash differed. The added instructions can affect this engine's scheduling, but the cause of the audio difference has not been established. Bit-for-bit audio transparency therefore remains unproven.

The test uses Digiemu commit `24a1dcfbb53de52c42b0d3f2f2a2f5029873f0d2`, its patched native Unicorn engine, and a local exact-hash OS 1.42 profile. OS 1.42 is not an upstream supported profile. Engine device/HLE/completion assumptions remain; physical caches, DMA, interrupts and worst-case timing are unverified. Full reserved-region ownership is still unproven. Persistent guard comparison cannot exclude transient native DMA changes that bypass callbacks and later restore the bytes.

Startup was bypassed by installing an explicitly ready private header in a restored settled session. Pattern writer hooks and queued/held-live capture/copy coverage are incomplete. Neither the trailer nor a deployable startup hook was implemented.

The next focused step is to rebuild the PC bootstrap/copy layout around the corrected 1,892-byte code and run cold startup into this native playback test. In parallel with that lifecycle check, investigate the chromatic audio difference by comparing note dispatch values and timestamps; do not infer hardware readiness from the passing coarse-pitch tests.

## Evidence files

* `Digitone-native-arp-overlay-results.json`: final guarded scale-fixture playback.
* `Digitone-native-arp-controlled-results.json`: isolated native quantizer/producer/pitch comparisons.
* `Digitone-native-allocator-overlay-results.json`: paired allocator comparison.
* `Digitone-native-arp-overlay-chromatic-results.json`: completed chromatic playback.
* `Digitone-native-arp-overlay-first-attempt.json`: stock baseline and initial illegal-instruction failure.
* `Digitone-native-arp-overlay-summary.json`: consolidated assertions and hashes.
