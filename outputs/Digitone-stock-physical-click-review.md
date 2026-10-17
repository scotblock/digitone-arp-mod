# Physical stock Digitone 1.44: first recording

The analog metronome recording provides a useful, stable stock-hardware timing baseline. The MIDI files contain no messages, so no MIDI-clock measurement or audio/MIDI alignment is available from this submission. E04 physical cache behaviour and internal render/DMA timing remain unmeasured.

Input: `inputs/recordings/3-Audio 0013 [2026-10-07 205444].wav`. The recording is stereo 24-bit PCM at 48,000 Hz and lasts 76.864 seconds. Windows read access was granted; closing Ableton released its file lock before analysis.

## Audio findings

- 132 metronome clicks detected, from approximately 6.36 to 71.85 seconds.
- No missing/extra click gap detected within the approximately half-second sequence.
- Peak level −6.07 dBFS, with zero full-scale/clipped samples.
- Four-phase waveform-matched fit: 23,995.908 recorded samples per beat, or **120.02046 BPM relative to the Rubix recording sample clock**.
- Equivalent mean beat period: 499.91476 ms. The rate is about 170 ppm faster than an exact 120-BPM reference measured at the nominal recording sample rate. The audio alone cannot assign this difference to a particular clock or software mechanism.
- Matching click phases four beats apart span 1,999.64583–1,999.66667 ms, a one-sample range in the recording. Fixed waveform-phase offsets are fitted separately; residual references span about 0.97 samples. This describes waveform-alignment repeatability, not a direct measurement of internal CPU jitter.

The detector first groups threshold crossings on a 1-ms envelope, then aligns 2,048-sample templates by normalized correlation. Each four-beat phase uses its own template to avoid confusing accent/shape differences with timing. Correlation quality is at least 0.995. The fixed phase-reference offsets must not be interpreted as actual adjacent-beat jitter. Silent intervals between metronome clicks do not provide continuous audio coverage, so this is not an exhaustive dropout/crackle test under synth load.

## MIDI findings

`stock-click-120-20261007-205913.csv` contains only its header. Its companion JSON reports zero short messages, zero clocks, zero starts/stops, and no callback/driver errors. The capture therefore provides no MIDI timing evidence. This does not by itself identify a logger, routing, configuration or cable fault.

The WAV filename and logger filename also suggest different capture start times. No shared start/stop event exists in the empty CSV to align them; simultaneous capture cannot be assumed.

## Next small check

The logger now prints live clock/all-message counts every five seconds. With Ableton closed, run it on Rubix22 input, press Digitone PLAY for approximately ten seconds, then STOP and finish the logger. Check Digitone MIDI OUT → Rubix MIDI IN, OUT PORT FUNC=MIDI, OUTPUT TO=MIDI, CLOCK SEND=ON and TRANSPORT SEND=ON. Growing counts confirm that the physical MIDI path reaches Windows. Only after this works is another simultaneous audio/clock take needed.

No firmware was installed or changed. Machine-readable measurements and limitations are in `Digitone-stock-physical-click-analysis.json`; the analysis script is `work/analyze-stock-click-recording.py`.
