# Digitone OS 1.42: Ableton stock-output recording

This is a physical baseline capture using the unchanged OS. No modified firmware is required. A recording can establish observed audio behavior, note timing, sustain and completed pattern changes. It cannot expose the processor clock, instruction-cache misses, render-completion time or the execution cost of code that has not run on the device.

## Recording setup

Use an empty Live Set. Record the Digitone stereo output to an audio track, with no processing on that track or the master. Use your analog interface input pair or the appropriate Overbridge output, depending on the connection. Record WAV at the existing interface sample rate; 48 kHz/24-bit is a useful common choice if supported. Note the sample rate, buffer size, audio driver and connection route.

If you monitor directly through the interface or Digitone, set the recording track's Monitor to Off. Ableton documents that monitoring settings can alter recorded placement; preserve the same settings for every take. [Ableton recording guidance](https://help.ableton.com/hc/en-us/articles/7938193554460-Recording-Audio), [monitoring and offsets](https://help.ableton.com/hc/en-us/articles/360006569179-Monitoring-in-Ableton-Live-FAQ).

Disable Warp on the captured clips before evaluating timing, and keep the original recorded WAV files. Do not normalize, denoise, time-stretch or trim the originals. [Ableton Warp reference](https://www.ableton.com/en/live-manual/11/audio-clips-tempo-and-warping/).

## Three stock takes

Use test copies of your patterns. Record their bank/pattern identifiers, tempo, sounds, arp settings, root/scale, active tracks and effects. Leave these settings consistent between repetitions. Let the Digitone run its own sequencer for this baseline; record whether MIDI clock synchronization is enabled rather than changing clock routes between takes.

1. **Steady playback, 60 seconds.** Record a normal arp pattern without switching patterns. Include a few seconds of silence before starting and after stopping. Repeat once without changing settings. These captures establish the normal output and repeatability of the recording chain.
2. **Held-note pattern changes, 60 seconds.** Hold the initiating note, request the receiving pattern, and continue holding for several seconds after the Digitone actually displays/plays the new pattern. Release afterward. Repeat the same transition three times. Write down the approximate transition and release times, and distinguish request time from completed replacement.
3. **Sustain transition, if your input setup supports CC64.** Send sustain on, note on, note off while sustain remains on, then request the receiving pattern. After replacement, send sustain off. Repeat three times. Keep the MIDI clip or input event log if available. Without a CC64 source, label the test as held-note coverage rather than MIDI sustain coverage.

For heavier playback, make an additional 60-second take using your actual dense voice/effect workload and identify its settings. Eight pressed keys alone do not demonstrate every worst-case synthesis workload.

## Return for analysis

Provide the original WAV files, the MIDI clip/log if available, and a short note containing:

- Digitone OS version and recording route: analog/interface or USB/Overbridge.
- Live version, driver, sample rate and buffer size; any track offset or monitoring-latency setting.
- Pattern identifiers, tempo, arp/root/scale settings and active effects.
- Approximate start, completed transition, note-release and sustain-release times.
- Any observed Live CPU overloads or audio-interface dropouts.

Audio analysis can identify candidate discontinuities, silence, missing notes and timing changes. A click may also come from a sound/envelope or the recording chain, so it is not automatically evidence of a firmware DMA underrun. These stock captures cannot certify the proposed scale-lock behavior or the modified hook's physical timing. They provide a measured baseline for the next comparison.
