# Corrected E04 overlay: loader-derived startup and playback

Both default and restored-project startup pass from the saved actual E04 loader handoff. The three default-state playback tests pass. Restored-state playback produces notes with the controlled pattern fixture, but does not reach the arp quantizer: its nonempty arp-coverage assertions fail. Original E04 and stock firmware remain unchanged; no new flashable image was produced.

## Startup scope

The original loader previously reconstructed E04 MAIN. These tests restore that saved handoff and verify its complete MAIN bytes before applying the corrected raw overlay. The overlay preserves all checked CPU registers, control registers, stack contents and the complete SRAM hash. The existing guest copier then installs the corrected resident payload; the payload is not seeded directly into its destination.

Both cases execute three modeled DTIM1 interrupts, with zero host completion-semaphore kicks and zero general intro semaphore satisfactions. The stock initializer runs once, metadata reaches ready, and the intro exits into the live UI. Strict custom-instruction checks remain clean. The intro still uses the emulator's PIT phase policy and idle-yield stand-in. Cold startup, intro and playback are connected by snapshots.

## Playback results

| Startup | Scenario | Hooks | Playback ms | Pitch outputs | Oracle checks | Changed notes | Capture checks |
|---|---|---|---:|---:|---:|---:|---:|
| E04_default | ordinary | corrected | 11201 | 71 | 43 | 0 | 32 |
| E04_default | ordinary | stock_sites | 11201 | 71 | 0 | 0 | 0 |
| E04_default | scale | corrected | 11201 | 71 | 43 | 33 | 32 |
| E04_restored | ordinary | corrected | 4201 | 13 | 0 | 0 | 16 |
| E04_restored | ordinary | stock_sites | 4201 | 13 | 0 | 0 | 0 |
| E04_restored | scale | corrected | 4201 | 13 | 0 | 0 | 16 |

Playback retains the snapshot's no-forced-semaphore policy. Every corrected-run capture check and completed quantizer result matches its independent expected value. Code/pitch lookup payload stays byte-exact and readiness stays set. Every run collects audio buffers without a modeled halt, but all buffers are zero-filled. The default-state enabled-scale fixture produces actual note changes. Default-state runs inject only pattern root/scale fields. Restored-state runs additionally copy a known factory-pattern descriptor from the default-state engine into the pattern-2 source RAM before panel selection. Event allocation, publication and helper execution remain guest-produced.

The originally restored selected pattern produced no pitches in either corrected or stock-site controls. Those three initial 11.2-second runs had no halt, retained payload/ready state and rendered silence; they failed the nonempty pitch-coverage assertion. They are preserved separately in `Digitone-E04-PC-ISA-empty-pattern-controls.json`, and are not counted as evidence of pitch behavior.

Ordinary controls restore the stock arp hook-site bytes in independent replays of the same startup snapshot. These controls isolate runtime hooks; they are not independent stock loader/startup runs.
- E04_default: identical pitch-output stream = True; identical audio bytes = True; counts 71/71.
- E04_restored: identical pitch-output stream = True; identical audio bytes = True; counts 13/13.

All collected PCM hashes equal the hash of a zero-filled buffer of the corresponding length. The identical ordinary audio therefore establishes only identical silence: audible DSP playback and audio-regression behavior are unverified. These are valid control-flow and pitch-calculation tests, not audible-playback certification.

## Limits and next step

This establishes functional execution from loader-derived state through playback under the PC model. It does not establish a corrected container-to-loader path: the original E04 flash source remains in use and the correction is applied after loader handoff. Physical instruction-cache coherence, timing, exclusive RAM ownership and the cause of the actual hardware freeze remain unverified. These runs do not expand sustain, cancellation or queued-note pattern-handoff coverage.

The next concrete step is a separately named PC-only packaged candidate and an actual loader run that verifies it reconstructs these exact corrected bytes, followed by the same startup checks. A restored-state workload that actually reaches the arp quantizer also remains necessary. The five invalid encodings are corrected here, but a successful emulator run does not prove they were the only hardware problem. Keep the device on working stock 1.44.

Evidence: `Digitone-E04-PC-ISA-loader-startup.json`, `Digitone-E04-PC-ISA-loader-playback.json`, and `Digitone-E04-PC-ISA-loader-playback-summary.json`.

Restored-state limitation: the final source-pattern fixture produces 13 pitch outputs but zero quantizer calls in each run. Context captures match their expected words and payload/ready state survive, but scale-lock behavior in this state is unverified. The intermediate fixture applied after selection likewise produced ordinary notes without quantizer coverage; its evidence is preserved in `Digitone-E04-PC-ISA-late-pattern-fixture-controls.json`. No exception, halt or strict instruction violation was observed. The next workload should establish arp eligibility through the guest configuration path rather than adding more raw event fixtures.
