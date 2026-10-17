# Digitone OS 1.42: eligible queued-arp verification

**The current PC overlay fails the old-scale requirement on this natural queued producer route.** Physical timing remains unverified. The original firmware is unchanged.

The test starts from the existing arp-enabled pattern 2, with root 61/raw scale 0, then requests pattern 1 with root 59/raw scale 5. A real type-1/state-1/track-2 event is delayed in PC RAM. The firmware performs the actual replacement, accepts the same event generation and executes the native arp quantizer. Neither the event eligibility fields nor the pattern pointer is forged.

| Control | Publication ms | Replacement ms | Acceptance ms | Quantizer context | Output | Old-scale expected |
|---|---:|---:|---:|---|---:|---:|
| natural | 248.667 | 2669.858 | 3168.667 | 0x0 | 57 | 56 |
| no-delay | 248.667 | 2669.821 | 250.000 | 0x0 | 57 | 56 |
| forced-context | 248.667 | 2669.858 | 3168.667 | 0x800040bd | 56 | 56 |

In the natural crossing, event 0x4199dadc/generation 1 remains pending at the replacement and is accepted afterward without recycling. Its context is already zero when published, remains zero at acceptance and is zero at the native quantizer. The helper therefore falls back to note 57. Its initiating pattern would constrain that note to 56. The receiving scale also allows 57, so the zero word and helper trace—not output alone—identify missing context.

The no-delay control produces the same zero-context fallback before any replacement. This rules out pattern replacement as a necessary cause of this failure. A separate diagnostic supplies 0x800040bd at commit; the actual retained commit/read and quantizer then output 56 after replacement. This control verifies that supplying the original context closes this particular downstream failure, while leaving natural producer capture unimplemented.

The natural publisher returns to 0x40093900. At the corresponding cached-emission branch, 0x40093892 calls the raw 72-byte copy routine 0x400ec23c, and 0x400938fe invokes the queue publisher. This differs from the producer-capture hook at 0x40093ef4. A 72-byte event copy does not itself copy the separate private context array. The exact source-cache ownership and a correct metadata capture/copy hook still need auditing before implementation.

All three runs complete without a halt or unexpected reserved-region writes; helper bytes and guards stay intact. Zero context is a fallback to unchanged pitch, rather than a proven scale lock.

## Physical timing and Ableton

No hardware recording or internal timing measurement has been received. The user can record the unchanged Digitone output in Ableton. That supports a stock output baseline, observed sustain/pattern behavior and investigation of candidate audio discontinuities. It does not measure processor/cache timing or prove modified-code deadlines, because the proposed hooks have not executed on the device.

Use [the stock recording protocol](Digitone-Ableton-stock-recording-protocol.md) to collect original WAV files and recording settings. Stock audio observations and modeled margins must remain separate from measured modified-device timing.

## Next step

Audit and connect natural context capture/copy for the producer whose publisher returns to 0x40093900, then repeat the natural queued-arp crossing without injected metadata. Physical output analysis can proceed when the Ableton recordings are supplied. No installable firmware was produced.
