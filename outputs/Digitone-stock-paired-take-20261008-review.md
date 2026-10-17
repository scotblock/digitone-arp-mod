# Digitone stock audio and MIDI reference — 8 October 2026

This capture establishes a usable external stock reference. It does not validate E04 on hardware. The physical instrument is user-reported stock OS 1.44, following the requested sequence/arp recording procedure. Exact pattern, sound, voice count and arp settings were not recorded, so workload identity must not be inferred from the WAV alone.

## Sources

- Audio: `inputs/recordings/3-Audio 0016 [2026-10-08 193839].wav`
- MIDI CSV: `stock-hardware-measurements/stock-click-120-20261008-194030.csv`
- Logger metadata: matching JSON.
- Numerical results: `Digitone-stock-paired-take-20261008-analysis.json`.

The user supplied these as the repeat paired take. Their timestamps and filenames alone do not prove synchronization. MIDI callback time zero and audio time zero are independent; exact transport-to-audio latency has not been established.

## Audio

Stereo, 48 kHz, 24-bit PCM; duration 72.197 seconds. Peak -17.008 dBFS; zero clipped samples. Channel RMS is -28.403 and -28.519 dBFS including the recording's leading/trailing quiet sections.

The first 10 ms block exceeding -60 dBFS peak occurs at 1.96 seconds. There are no blocks forming at least 100 ms below -60 dBFS RMS between 1.96 and 68.55 seconds. Quiet intervals occur near the recording's end. There are no runs of exactly zero stereo samples lasting at least 1 ms anywhere in the file.

The largest adjacent-sample change is 0.0035003 full scale. These level/continuity checks do not establish an absence of every click, crackle, repeated buffer or subtle dropout. Analog noise can hide digital silence, and quiet intervals or waveform transients can be intentional musical content. No listening-based claim or internal DMA deadline measurement is made.

## MIDI

4,012 messages: 4,010 clocks, one START and one STOP. CSV counts agree with the logger metadata. No driver error or callback exception was reported.

START-to-STOP duration is 63.2676 seconds using callback timestamps (63.268 seconds using millisecond driver timestamps). There are 3,037 clock pulses between START and STOP.

Linear regression of clock timestamp against pulse ordinal, using 24 clocks per quarter note, gives 119.99714 BPM on both callback and driver time bases. Mean callback clock interval is 20.833864 ms. Observed callback intervals span 20.3709–21.6503 ms; driver intervals span 20–22 ms. No playback interval exceeds 31.25 ms, falls below 10.4167 ms, or is nonpositive. These thresholds screen for gross lost/doubled arrivals, not every possible transmission error.

The capture shows no clock gap suggestive of a missed pulse during playback. Interface buffering, driver quantization and host scheduling are part of these measurements. They are not direct MIDI-wire jitter measurements or Digitone CPU/cache measurements. Clock messages outside START/STOP are retained in the source but excluded from playback rate calculations.

## Next step

No further stock metronome recording is necessary for this baseline. Preserve the physical Digitone pattern and sound settings used for this recording, so any later comparison uses the same workload. Next consolidate a bounded E04 hardware-trial readiness and stock-recovery plan using the chosen startup-menu DIN MIDI route. Do not install or transmit E04 as part of this analysis.

Physical E04 cache coherence, RAM ownership under unobserved workloads and worst-case render deadlines remain unmeasured. Stock audio/MIDI timing cannot resolve those issues by itself.
