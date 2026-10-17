# Digitone OS 1.42 — audio difference investigation

The reproduced audio mismatch is timing-sensitive. A PC detour that executes only the displaced stock instructions reproduces the fast-mode mismatch, with unchanged note values and dispatch arguments. A separate exact-instruction run confirms DMA reading a right-channel output word immediately before its pending store. Scale arithmetic and context storage are not required to produce this symptom.

Firmware files remain unchanged. This explains a concrete reproduced mechanism in the engine; it does not establish hardware timing headroom or make the mod audio-transparent.

## Controls and first divergence

The runs use the same settled stock snapshot, synthetic card, input timing, pinned native engine and nominal audio configuration. Short Play/Stop sequences reproduce the issue before the longer pattern-switch test is needed. No scale fixture is injected: these are chromatic/fallback comparisons.

| Comparison | Result |
|---|---|
| Stock repeated, 1.8 seconds | Audio and DSP packets identical |
| Helpers installed but no stock hook patched | Audio identical to stock |
| All hooks, fast clock | First audio difference at 642.979 ms |
| Pitch hook alone, fast clock | Same first audio difference |
| Allocator hook alone, fast clock | Same first audio difference |
| Stock-instruction detour, fast clock | Same first audio difference and changed DSP bytes |
| Stock-instruction detour, exact instruction counting | Audio differs at 448.583 ms; DSP inputs and voice blocks identical |
| Actual pitch hook, exact instruction counting | Audio differs at 51.5 ms; later DSP parameter differences also occur |

The detour consists of an absolute jump into PC RAM, the three displaced stock instructions, and an absolute jump back. It adds two jumps. It contains no context access, quantizer, new register-save logic or interrupt-mask change. Identical note values and dispatch arguments therefore do not guarantee identical audio under this engine's timing.

In the 1.8-second fast-clock runs, all four observed note values, nine captured dispatch argument words per call, and observed dispatch timestamps matched stock. The first DSP packet difference was render index 961 at 641.462 ms, with changed bytes at offsets `291` and `311..313`. The pure detour changed those same bytes to the same values, and the first output PCM difference was frame 30,863 at 642.979 ms. The semantic meaning of those parameter offsets has not been assigned.

All-hook and allocator-only fast runs rendered 2,699 DSP blocks versus stock's 2,700; pitch-only still rendered 2,700. A block-count difference alone is not the complete explanation.

The fast clock estimates instructions from basic-block entries using a fixed factor. The exact-count controls remove that estimator, but still differ, so the issue cannot be attributed solely to the estimator. Neither mode models full physical instruction/cache/bus costs.

## Buffer boundary proof

The repeated exact-count stock/detour experiment recorded 1,124 DSP render inputs and voice output blocks per run over 750 emulated milliseconds. Their complete input packet and voice-output sequences matched. Notes and dispatch arguments matched too. Main-CPU render windows differed before the audio mismatch.

At the first differing DMA output chunk, index 672:

| Observation | Stock | Detour |
|---|---|---|
| DMA capture clock | 448.666672 ms | 448.666672 ms |
| CPU instruction | `40096c30`, loop branch after sample stores | `40096c28`, before right-channel conversion/store |
| Output cursor A0 | `80001ae8` | `80001ae4` |
| Remaining loop count D4 | 3 | 4 |
| Captured right word | `fff913e0` | `0003a683` |
| PCM frame 21,532 | left −1769, right −1773 | left −1769, right 934 |

The DMA descriptor's post-copy source was `80001b00`; the captured chunk was 256 bytes. Its frame 28 right-channel word is:

`80001b00 − 256 + 28 × 8 + 4 = 80001ae4`

That address exactly matches the detour's pending A0 store. The next stock instructions are conversion at `40096c2a` and the right-channel store at `40096c2c`. Stock had already advanced past that store. Only that four-byte right-channel word differed in this first chunk; the left sample matched. The first differing PCM frame appears at 448.583 ms because the later chunk capture contains the preceding samples.

This localizes the first exact-detour difference to DMA capture overlapping the main CPU's output-buffer write loop. The stock run is also still processing the buffer tail at that capture, so a stock-like audio hash is not itself evidence of ample timing margin.

## What this establishes

The original fast-mode symptom is reproducible without the metadata or scale algorithm. Its earliest packet and PCM changes are reproduced by the stock-instruction detour. The exact-count control demonstrates that added control flow changes main-render scheduling and which output word DMA observes. The actual pitch helper's earlier exact-count mismatch shows that its greater work and interrupt masking need their own timing assessment.

No emulator timer, DMA rule, interrupt rule or firmware hook was changed to force a matching result. The investigation used diagnostics and temporary CPU-memory variants only. There is no basis yet to call the mismatch harmless on the device, to declare a physical underrun, or to claim all longer-session differences have this sole cause.

## Next focused task

Measure main-render deadline margin with a cycle-aware clock and equivalent stock/detour/full-hook runs. Track pending interrupts and output-buffer completion relative to DMA reads. Establish whether the stock profile itself meets the modeled deadlines before using it to judge hook overhead. Optimization or hook relocation should follow that evidence rather than an audio-hash target.

The PC startup and scale-output tests remain passed. This investigation narrows the open issue to timing and output-buffer scheduling; queued/held live capture, writer coverage, global RAM ownership and physical cache behavior remain separate unfinished work.

Evidence files: `Digitone-native-audio-investigation.json`, `Digitone-native-audio-timing-controls.json`, `Digitone-native-audio-render-controls.json`, `Digitone-native-audio-buffer-boundary.json`, and `Digitone-native-audio-investigation-summary.json`.

Original SysEx SHA256 before/after: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`. No modified firmware or flashable container was produced.
