# E02 audio isolation using the saved user session

The uploaded crackling symptom was reproduced using background DSP rendering, the mode used by Digiemu's live GUI. The same saved modified session, notes and sound are clean with synchronous DSP rendering. Neither source firmware nor the user's installed app/session files were modified by these tests; their files were copied into the workspace.

Matched simple track-1 and factory arp workloads produce byte-identical stock/E02 audio, including controls that restore the seven runtime hooks after E02 startup and install those hooks after stock startup. A nonchromatic factory arp test changes pitches as intended without the dense boundary discontinuities.

## Actual saved modified session

| Execution | Large sample jumps | At strongest 32-frame boundary |
| --- | ---: | ---: |
| E02, synchronous DSP | 0 | 0 |
| E02, background DSP | 256 | 256 |
| Seven arp hooks disabled, background DSP | 250 | 250 |
| All nine modified sites restored to stock, background DSP | 249 | 249 |
| E02, background DSP plus voice-read barrier | 0 | 0 |

Counts use the same 0.02 full-scale jump threshold as the initial WAV analysis. The workload is 2.8 emulated seconds including STOP/PLAY controls. Host-thread scheduling makes the unsynchronized counts nondeterministic.

The main render starts DMA channel 47 at 0x4009d1ac to read the DSP voice buffer at 0x100003a0. A test-only host wait at that instruction ensures the background DSP render completes before copying its output. This restores **byte-identical PCM** to the clean synchronous E02 run, not merely fewer detected jumps. Stock retains the same pitches and has no large discontinuities with the barrier, but its PCM differs from the synchronous stock control. That remaining scheduling difference needs validation before packaging an emulator fix.

This localizes the observed discontinuity to threaded DSP handoff behavior in this engine/workload. Disabling the nine sites after loading does not erase earlier startup history, so it is not a universal startup proof. The user stock session has different note/effect settings from the modified session; its direct WAV comparison is not a matched control. The same-snapshot thread/barrier and hook-restoration tests establish the stronger result.

## Scale-locking confirmation

From the user's saved pattern, actual arp pitch outputs with the seven hooks disabled are MIDI notes 60,61,64,66,60. E02 produces 60,60,64,65,60: C,Csharp,E,Fsharp,C becomes C,C,E,F,C. The clean audio exports keep the same pattern and sound and differ in hook configuration, making them suitable for the intended Ableton pitch comparison.

Clean files: `Digitone-user-scale-locked-clean.wav` and `Digitone-user-same-pattern-stock-pitch-clean.wav`. The second is a same-session stock-pitch control with the seven runtime hooks restored, not a fresh stock firmware boot.

## Remaining work

The voice-read barrier is currently a PC test harness change only. A separately packaged emulator/launcher fix still needs implementation and validation for live use. This result does not change E02 firmware, certify hardware timing or authorize physical flashing. Detailed cases and hashes are in `Digitone-E02-audio-isolation-summary.json`.
