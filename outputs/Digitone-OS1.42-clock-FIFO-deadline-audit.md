# Digitone OS 1.42: core/timer clock reconciliation and FIFO deadlines

This is a PC-only timing audit. The original SysEx and decoded firmware are unchanged. The modified execution uses temporary RAM overlays and an explicit retained-context fixture; it does not establish natural capture for every producer or hardware readiness.

## Clock accounting

The execution loop previously advanced timers using only the cycles returned by a CPU step. Interrupt delivery after that step could add exception-entry and pending basic-block tail costs to the core clock without advancing timers. The isolated emulator now reconciles after every asynchronous source, each timer source, and the final boundary callback. Later sources receive the updated timestamp; repeated run calls retain the epoch and charges. This changes only the cycle-stepper path. The global clock epoch now also covers guest execution performed by simulated button input outside the regular loop. The longer comparison identified this final residual (147 cycles); a separate native check exercises the final correction.

A second mismatch paired a 250 MHz modeled core with the timer module's fixed 132 MHz bus. The clock module requires the peripheral bus to be half the core rate ([NXP reference manual, page 198](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=198)). Cycle-mode PIT and DMA timers now use fsys/2: 125 MHz for the selected 250 MHz core. Timer period caches include both rates; outstanding snapshot deadlines retain their remaining phase when their units change. The actual board clock is still unverified. The earlier stock UART-divider analysis uses a 132 MHz calibration, supporting an intended 264 MHz core; it is not a board measurement. The present playback comparison retains 250 MHz to compare with earlier runs, now paired consistently with a 125 MHz bus. A focused check also covers the conditional 264/132 MHz pair.

Twelve focused clock checks cover boundary costs, ordered sources, combined timers, split runs, legacy accounting, rate conversion, and cache invalidation. CPU callbacks inside a block can still observe a timer checkpoint behind the core; reconciliation is guaranteed at serviced outer boundaries, not at every guest instruction. DMA-timer counter reads retain the existing boundary sampling limitation.

## Stock FIFO evidence

A bounded execution of the unmodified MAIN startup captured these SSI1 writes:

| Register | Final value | Interpretation |
|---|---:|---|
| CR, fc0c8010 | 37 | synchronous I2S master; transmitter and receiver enabled; FIFO1/two-channel selection off |
| IER, fc0c8018 | 500000 | transmit and receive DMA enabled |
| TCR, fc0c801c | e8 | transmit FIFO0 enabled; internal bit/frame clocks |
| RCR, fc0c8020 | 488 | receive FIFO0 enabled; sign extension |
| CCR, fc0c8024 | 16101 | 24 valid bits; two slots per frame |
| SFCSR, fc0c802c | 22 | receive threshold 2 words; transmit threshold 2 empty slots |

The stock code at 4000117c writes 14 zero words to TX0 before enabling transmission. The controller's observed minor loop transfers eight bytes, hence two four-byte FIFO accesses.

The hardware manual describes 15-word FIFOs, overflow discard behavior, and watermark-triggered DMA ([SSI chapter, pages 1056 and 1063](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=1056)). These statements supersede a guessed 16-word FIFO. The trace begins directly at MAIN with supplied startup flags and documented DMA reset seeds; it does not reproduce physical serial boot or prove inherited hardware state.

## Occupancy model

The PC model uses a serial word event every half frame, exact fractional phase, TX consumption, RX arrival, and the actual DMA payload beats. It submits TX when occupancy is at most 13, and RX when at least two words are available. Requests remain asserted while service is needed; a busy channel does not count another frame pulse as a dropped request. After completion, the level is evaluated again. Serial events precede DMA beats on timestamp ties, a conservative convention.

FIFO underflow, overflow, and reads from an empty receive FIFO are the deadline criteria. The inherited next-frame counter is diagnostic only. At an assumed 48 kHz stereo frame rate, serial words are 10.4167 microseconds apart; FIFO buffering therefore differs substantially from the earlier 20.8333-microsecond per-frame proxy. Shift-register and status-flag phase are not reproduced.

Thirty-four FIFO checks pass, including threshold transitions, separate payload beats, fractional phase, sustained service, 18 starting-occupancy/phase combinations, and deliberate controller blockage that produces both TX underruns and RX overflows. The previous 15 audio/interrupt checks also pass.

## Playback comparison

The pattern-2 comparison executed 100 ms of active playback plus preparation and stop, about 280.052 ms per variant. Both completed 419 renders and observed 26,885 serial-word ticks. TX occupancy never fell below 13 words; RX never rose above two. There were no FIFO faults, late renders, dropped level requests, unresolved output captures, or stale output words. Decoder mismatches were zero.

| Longer comparison | Stock | Full arp overlays |
|---|---:|---:|
| Worst render | 580.444 us | 599.244 us |
| Nominal render margin | 86.224 us | 67.424 us |
| Post-warmup output captures | 12,483 | 12,483 |
| Minimum observed output-buffer freshness margin | 157.084 us | 137.808 us |
| FIFO faults | 0 | 0 |

These are modeled values at 250 MHz with the selected memory costs. Output-buffer freshness margin, render margin, and FIFO occupancy measure different things. The target track produced note 56 from stock note 57, matching the scale oracle; the two other observed tracks matched stock. The explicit context fixture remains necessary.

The longer comparison loaded the revision before the final out-of-loop input correction. It retained a 147-cycle end discrepancy, rather than the previous accumulating interrupt-entry drift. After that discrepancy was traced to simulated button input and corrected, a separate native run of the final revision exercised press/release of PLAY and STOP in both stock and overlay variants. All eight immediate input checks and both final totals had zero discrepancy. Each ran about 25.031 ms and completed 36 renders, with no FIFO faults, late renders, or stale output reads. This shorter final check did not repeat pattern-2 selection or prove the same worst render margin for the final revision.

The SysEx SHA-256 before and after both comparisons is `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`. Decoded MAIN also retains its recorded hash.

Evidence files:

- `Digitone-SSI-main-startup-config-trace.json`: recovered configuration and 14 priming writes.
- `Digitone-clock-reconciliation-checks.json`: 12 focused accounting/rate checks.
- `Digitone-FIFO-deadline-checks.json`: 34 occupancy checks.
- `Digitone-FIFO-audio-comparison.json`: longer comparison before the input-epoch correction.
- `Digitone-native-clock-FIFO-check.json`: final revision native checks.
- `Digitone-clock-FIFO-summary.json`: combined results and final implementation hashes.


## Remaining limits and next step

The 250 MHz core, 48 kHz audio rate, cache fill/writeback and DDR costs remain assumptions. The snapshot FIFO occupancy is supplied using the stock startup priming value, not measured on the device; phase sensitivity checks do not certify physical startup. Unknown external receive data is preserved. Cache contents, serial shift-register phase, status-flag timing, hardware arbitration overhead and other peripheral DMA paths are incomplete. RAM ownership and the natural cached-context producer remain separate unresolved issues.

The next useful check is to derive the SSI1 clock-source/divider chain from stock boot configuration, then test status-flag/shift-register phase and broader playback workloads under the resulting clock candidates. Passing this model is not sufficient evidence to flash a device.
