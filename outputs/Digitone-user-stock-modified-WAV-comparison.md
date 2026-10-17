# User recordings: stock versus modified Digiemu

The stock recording does not show the modified recording's concentration of sharp jumps at 32-frame audio boundaries. Both are 48 kHz, 16-bit stereo WAV files of about four seconds, with no full-scale samples.

| Measurement | Modified | Stock |
| --- | ---: | ---: |
| Duration | 3.988 s | 3.959 s |
| Peak | -23.09 dBFS | -25.68 dBFS |
| Sample-to-sample jumps above 0.02 full scale | 162 | 0 |
| Mean boundary jump / mean interior jump | 4.45 | 1.01 |
| Largest sample jump | 0.079865 | 0.002045 |
| Largest 100 jumps on the strongest 32-frame phase | 100 | 7 |

The modified file's 162 jumps above the chosen threshold all occur on 32-frame boundaries. Its largest jump is about 39 times the stock file's largest jump. The peak-level difference is only about 2.6 dB; increasing the stock file by that amount would still leave its largest jump well below the threshold. Full-scale output clipping does not explain this difference.

These results support treating the modified playback/export behavior as a suspected regression. They do not isolate the root cause. The recordings do not include verified pattern, sound, effects, scale and scheduling state; the modified channels are exactly identical whereas the stock channels differ, so exact matching cannot be established from the WAVs alone.

Next: run stock and E02 against explicitly matching sound/pattern input state, trace parameter transfer and audio buffer consumption, and isolate startup/reset changes from the seven arp hooks. Earlier instruction-paced controls already found differing DSP parameter-packet consumption order; this recording supplies evidence to investigate whether buffer continuity is also affected. Do not attribute these discontinuities to a particular hook or extrapolate to hardware without that comparison.

Details: `Digitone-user-stock-modified-WAV-comparison.json`. Source files remain unchanged. This analysis makes no claim to have listened to the recordings.
