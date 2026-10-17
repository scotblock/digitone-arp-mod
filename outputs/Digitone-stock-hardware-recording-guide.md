# First physical timing recording: stock Digitone 1.44

Leave the physical Digitone on its current stock 1.44 firmware. This recording measures external timing and audio continuity. It does not directly measure CPU cycles, internal DMA deadlines or E04's cache behaviour.

## 1. Connect the cables

You need two 6.35 mm audio leads (TRS preferred; TS also works) and one standard five-pin MIDI cable.

| From | To |
|---|---|
| Digitone main OUTPUT L | Rubix22 front INPUT 1L, using its jack connection |
| Digitone main OUTPUT R | Rubix22 front INPUT 2R, using its jack connection |
| Digitone MIDI OUT | Rubix22 rear MIDI IN |
| Rubix22 USB | Computer |

Temporarily disconnect the Digitone's USB cable for this recording. Rubix MIDI OUT is not needed. Connect your headphones/speakers to the Rubix. Set Rubix +48V off and input 1 Hi-Z off; start with low input sensitivity and raise it while watching levels. DIRECT MONITOR can be STEREO if you want to hear the inputs without software monitoring. See the [Roland reference manual](https://static.roland.com/assets/media/pdf/Rubix_reference_eng01_W.pdf).

## 2. Set the Digitone

- Set tempo to **120.0 BPM**.
- In **SETTINGS → MIDI CONFIG → SYNC**: CLOCK SEND on, TRANSPORT SEND on, CLOCK RECEIVE off, TRANSPORT RECEIVE off.
- In **MIDI CONFIG → PORT CONFIG**: OUT PORT FUNC = MIDI; OUTPUT TO = MIDI. Use MIDI, not DIN24/DIN48.
- Choose an already empty pattern for the first take; leave existing patterns intact.
- Press **FUNC + PTN** to open the metronome menu: ACTIVE on, TIME SIG 4/4, and a clearly audible click volume.

These controls are documented in the original [Digitone manual](https://www.elektron.se/wp-content/uploads/2024/09/Digitone_User_Manual_ENG_OS1.41_231108.pdf). The cited edition is 1.41; the target instrument remains on 1.44. The first take needs only the metronome, so there is no sound/arp programming to reproduce.

## 3. Set Ableton

1. Select **ASIO → Roland Rubix** as the audio driver. Use **48,000 Hz**, a **256-sample buffer**, and **24-bit recording**.
2. Enable stereo input **1/2**. Create one audio track with **Audio From: Ext. In → 1/2**, **Monitor: Off**, and arm it.
3. Use an empty Arrangement with no track/master effects. Turn Live's metronome off and leave **EXT off**. Live should record continuously on its own clock.
4. In MIDI preferences, turn **Track, Sync and Remote off for Rubix MIDI input/output**. The logger owns MIDI input; Live records audio only.
5. Check the Digitone click reaches both channels. Adjust input sensitivity for peaks around **−12 to −6 dBFS**, avoiding overload.

Live's [routing manual](https://www.ableton.com/en/manual/routing-and-i-o/) describes the audio input and MIDI-port controls. If names differ in your Live version, use their corresponding settings. Direct monitoring through the Rubix lets you listen with Live's track monitoring off.

## 4. Start the receive-only clock logger

Keep these two files in the **same folder**:

- `Digitone-stock-clock-logger.py`
- `Start Digitone stock clock logger.cmd`

Double-click the CMD launcher. Select the numbered **Rubix22 MIDI INPUT** port when listed; the number may change. Enter take name **stock-click-120**. The logger sends no MIDI or firmware data. It writes a CSV and a companion JSON in `stock-hardware-measurements` beside the scripts.

The logger has been checked for message decoding and MIDI-port enumeration on this PC; it found Rubix22. Capturing its actual messages still needs this test. If Windows says the port is already allocated, disable that port in Live/other MIDI applications, close them, start the logger first, then reopen Live with its MIDI switches off. The Digitone clock should reach the logger through the physical MIDI cable.

## 5. Record the first take

1. Start Arrangement audio recording in Live.
2. Wait about **5 seconds**.
3. Press **PLAY on the Digitone**. Record **60 seconds** of metronome clicks without adjusting settings.
4. Press **STOP on the Digitone**.
5. Wait another **5 seconds**, then stop Live recording.
6. Press **Enter in the logger window** to finish and save. It should report clock messages and transport start/stop messages. Zero clock messages means the MIDI part failed; keep the WAV and check the port, cable and send settings.

Save the Live set and use its original recorded WAV from the project's `Samples/Recorded` folder. Keep the silence before/after the take. Do not warp, normalize or trim it. Alternatively export that complete interval as stereo WAV at 48 kHz/24-bit, with Normalize off and no effects. Label it **stock-click-120.wav**.

## 6. What to provide

Provide the WAV and the matching logger CSV/JSON, plus the actual recording sample rate and any reported audio-driver errors. I will compare click spacing in samples, MIDI-clock intervals and long-term drift. At 120 BPM the intended quarter-note interval is 0.5 seconds and MIDI clock averages 48 messages/second.

Audio and MIDI are recorded through different timing paths. MIDI callback times include interface/USB/driver/Windows delays; driver times have millisecond units. They cannot establish sub-millisecond wire jitter or precise audio-to-MIDI absolute latency. A clean stock take also cannot prove E04's cache coherence.

After that baseline, the useful second take is your existing busy/arp pattern at the same tempo and recording settings, with the metronome off. Name it **stock-arp-120**, keep the pattern unchanged during its 60-second take, and provide its pattern number, active tracks and arp settings. We can arrange this after confirming the first take records correctly.
