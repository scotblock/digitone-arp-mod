# Digitone OS 1.42: SSI1 clock source and serial-phase audit

PC-only work: the original firmware is unchanged, and no flashable file was produced.

## Clock chain recovered

Stock MAIN loads the signed mask `ffffffcf` at `40000f66`, executes its own buffer-clear call, then reads MISCCR, applies that mask and writes it at `40000f96`. This clears both SSI source-selection bits. The bootstrap contains the corresponding sequence at `80004ee0..80004eea`. Six native execution checks run the actual MAIN instructions: four different initial MISCCR values all have the source bits cleared, and both board-flag branches produce the recovered CCR values.

Bounded MAIN startup with the normal supplied boot flags ends at MISCCR `0800`. The alternate supplied flags also end at `0800`. No CDRH write was observed in these runs. Its simulated zero readback is an unseeded model value, not a hardware reset observation; it is bypassed for the selected source.

NXP identifies MISCCR bit 5 clear as external SSI_CLKIN selection, and defines the I2S master frame as 64 serial bits. Its worked example pairs PM=1, DIV2=0 and PSR=0 with 12.288 MHz input and 48 kHz audio. [NXP SSI and CCM reference](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=1107).

| Stock branch | CCR | Input-to-bit-clock divisor | Input required for 48 kHz | Bit clock |
|---|---:|---:|---:|---:|
| Board flag 80000 clear; current PC snapshot | 16101 | 4 | 12.288 MHz | 3.072 MHz |
| Board flag 80000 set | 56103 | 16 | 49.152 MHz | 3.072 MHz |

These input frequencies are derived requirements, not oscillator measurements. The original Digitone specification supports 48 kHz converter operation. [Elektron manual, technical information](https://www.elektron.se/wp-content/uploads/2024/09/Digitone_User_Manual_ENG_OS1.41_231108.pdf#page=88).

The alternate branch also configures SSI0 (`CCR 56700`, enabled `CR 3b`) and additional DMA output. It is not covered by the current SSI1-only playback route. The supplied flag does not establish which physical product or revision uses that branch. Both startup traces begin directly at MAIN with supplied flags and documented DMA reset seeds; they do not reproduce hardware serial boot or certify every computed writer.

This resolves an important relationship: audio uses an external clock, so it cannot establish the core frequency. The broader tests use the previous 250 MHz sensitivity candidate and the 264 MHz candidate supported by stock UART calibration, each with its required half-rate timer bus. Both use the documented 48 kHz audio rate and the current snapshot branch. The real core clock remains unmeasured.

## Status and shift phase

The previous FIFO model combined word consumption, receive arrival, and request assertion at one instant. The new isolated model separates FIFO-to-TXSR loading, completion of the preceding shifted word, and delayed status assertion. NXP says SSI flags update after the first bit of the next word; its error bits support write-one-to-clear acknowledgement. [NXP status register](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=1069).

With the tested I2S format, words are 32 serial bits apart; the first-bit checkpoint is one thirty-second of the word period later. Fractional scheduling retains that phase. An empty TX FIFO invalidates the active shifted word even if a DMA refill arrives later. Receive arrival and transmit consumption are processed before a payload beat on ties. Status assertions schedule watermark-driven DMA; requests are acknowledged at minor acceptance and guarded by the real modeled occupancy when re-evaluated. Payload transfers deassert the modeled watermark bits as thresholds clear.

The model supplies TFE0, RFF0, TUE0 and ROE0 on guest ISR reads, and FIFO0 counters on guest SFCSR reads. Native guest instructions verify those reads and selective error acknowledgement. Other ISR bits are preserved rather than claimed as fully implemented. The longer raw comparison retains the inherited `next_frame_deadline_misses` counter. That counter is invalid in the loaded revision because it uses the old fixed frame phase; it must not be interpreted as an audio fault. The final revision corrects this diagnostic to use each request timestamp and is checked separately. This change affects the diagnostic only, not payload scheduling or the criteria reported here: actual modeled FIFO occupancy, shifted-word validity, output freshness, and render completion.

The shift model tracks word validity and timing, not the actual codec bitstream or TXSR data value. Request acknowledge/deassert edge behavior remains a modeled policy.

Sixty-seven focused checks pass: native MMIO reads/W1C, fractional first-bit timing, FIFO/shift separation, blocked-DMA errors, and phase variations at both core candidates. Immediate word-edge assertion is retained as a comparison policy. The 44.1 kHz cases are additional phase sensitivity only, not recovered board configurations.

## Broader execution results

Each stock/overlay pair ran the same sequence at 250/125 MHz and 264/132 MHz core/bus candidates, with 48 kHz SSI1 audio. The workload selects pattern 2 before playback, holds panel trig buttons 1 and 5, releases them separately, requests pattern 3 and pattern 2 during playback, then stops. Each run lasts about 285 ms, including selection and stop; this is broader input coverage rather than prolonged stress testing. The brief pattern requests are queued-operation coverage, not proof of completed pattern replacement.

| Core candidate | Variant | Completed renders | Worst render (us) | Nominal margin (us) | FIFO faults | Stale output captures |
|---|---|---:|---:|---:|---:|---:|
| 250 MHz | stock | 426 | 573.332 | 93.336 | 0 | 0 |
| 250 MHz | all | 426 | 593.304 | 73.364 | 0 | 0 |
| 264 MHz | stock | 426 | 550.777 | 115.890 | 0 | 0 |
| 264 MHz | all | 426 | 570.871 | 95.795 | 0 | 0 |

All four runs ended with zero core/timer discrepancy and zero decoder mismatches. There were no invalid completed shifted words, modeled SSI error flags, late/unresolved output captures or dropped FIFO level requests. TX occupancy stayed at or above 13 words and RX at or below two. The extra panel presses produced note events on tracks 0 and 1. Both core candidates produced the expected target-track changes 57 to 56 and 69 to 68; the four other observed note outputs matched stock.

No guest SSI1 configuration/status writes or ISR/FCSR reads occurred in these playback intervals. Therefore the native fixtures, rather than these playback runs, exercise MMIO status read and acknowledgement behavior. No claim is made that the hardware deasserts requests on exactly the modeled edge, or that every possible clock writer was excluded.

A separate short native stock/overlay check exercises the final diagnostic-counter correction: both runs have zero frame-window proxy misses, FIFO faults, stale output reads and final core/timer discrepancy. This reporting correction does not change DMA event scheduling. The loaded and final phase-code hashes are preserved in the summary.

The raw runner was corrected after loading to place descriptive clock-source metadata outside the overlay-only branch. It has no scheduling effect; both stock runs retain their per-run core frequency and CCM snapshot evidence. The saved raw comparison reflects the loaded revision; the final runner hash reflects this metadata-only correction.

Evidence: `Digitone-SSI1-clock-chain.json`, `Digitone-SSI1-clock-main-trace.json`, `Digitone-SSI1-alternate-board-clock-trace.json`, `Digitone-SSI1-clock-aligned-disassembly.txt`, `Digitone-SSI1-native-source-divider-checks.json`, `Digitone-SSI1-serial-phase-checks.json`, `Digitone-SSI1-phase-workloads.json`, `Digitone-SSI1-final-native-phase-check.json`, and `Digitone-SSI1-clock-phase-summary.json`. Original SysEx and decoded MAIN hashes remain unchanged.


## What remains unverified

This does not establish physical clock readout, cache contents/coherence, calibrated DDR/DMA arbitration costs, all SSI status flags, a bitwise codec waveform, alternate-branch SSI0 playback, global computed clock writers, or complete RAM ownership. The retained-context fixture remains explicit; cached-producer capture is not certified by these tests. Passing this PC model is insufficient evidence to flash a device.

The next useful test is a confirmed pattern handoff with queued/sustained notes through the actual transition, followed by longer voice-heavy playback under the 264/132 MHz candidate and memory-cost sensitivity. That would extend observed coverage without treating queued panel requests as proof of completed pattern replacement.
