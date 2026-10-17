# Modified-firmware WAV: initial crackle analysis

Input: `inputs/recordings/digitone-20261006-184404.wav`.

The file is 3.987583 seconds of 48 kHz, 16-bit stereo PCM. Both channels are identical. The output peak is -23.09 dBFS, with no full-scale or near-full-scale samples. There is no evidence of full-scale output clipping in this recording.

The waveform has abrupt sample jumps aligned with 32-frame boundaries. The twenty largest jumps all occur on those boundaries, including -1494 to +1123 at 1.514 seconds and the same jump at 3.514 seconds. These discontinuities are present in the saved PCM, independently of Windows live output buffering. They are consistent with an audio-block continuity problem, but the recording alone does not establish whether stock Digiemu, this modified build, the sound settings, or their interaction causes it.

There are two short exact-zero runs near the beginning and no later exact-zero gaps exceeding one millisecond. No adjacent active 32-frame blocks are exact duplicates. Those negative checks do not exclude stale reads or reordering of other buffers.

Next comparison: save a stock OS1.44 WAV with the same sound, notes, arp, tempo, effects and volume, preferably using the same exported pattern/project settings. Compare block-boundary behavior and note output. Do not change firmware based solely on this one recording. Hardware testing remains outside this result.

Numerical details are recorded in `Digitone-user-WAV-analysis.json`. No listening judgment or definitive audible-cause attribution is claimed by these measurements.
