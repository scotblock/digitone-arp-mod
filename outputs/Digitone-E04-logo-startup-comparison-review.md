# Stock versus E04: logo transition and emulator shortcuts

8 October 2026. PC-only investigation after E04 failed physical startup and the user successfully restored stock 1.44. No firmware was changed or transmitted.

## Result

The physical E04-only stall has **not been reproduced**. Both stock and E04 reach a live interface in the matched PC comparison, with or without the later general semaphore-unblocking shortcut. Disabling the earlier hardware-completion stand-in stops both images before the initializer. That identifies a real model dependency, but does not establish the cause of the E04-only device failure.

## Matched comparison

Each cold run starts from direct MAIN entry with the same reset register setup and an explicit `00140000` boot-flags word at SP+4, matching the previously captured loader's flags. The loader itself is not executed in these runs. Each run gets a fresh byte-identical copy of the initialized emulator drive. Images are the verified stock recovery file and unchanged exact E04. E04's resident ISA instructions receive the same scoped emulator support as earlier tests; code bytes are not overlaid.

Native block estimates bound execution; they are not physical instruction cycles. Snapshot replays carry guest state into fresh engines with device models reattached. An early draft's missing entry flags and stock private-memory observation were corrected before the completed comparisons below; that draft is not evidence about firmware failure.

| Image | Cold completion stand-in | General unblock during intro | Result |
|---|---|---|---|
| Stock | Enabled, three kicks | Enabled | Logo exit once; 138 main-loop entries; live UI |
| Stock | Enabled, three kicks | Disabled | Same acceptance result |
| E04 | Enabled, three kicks | Enabled | Same acceptance result |
| E04 | Enabled, three kicks | Disabled | Same acceptance result |
| Stock | Disabled | Intro not run | Parks at `4008cdf0`; two startup tasks recorded; initializer not reached |
| E04 | Disabled | Intro not run | Same stop, tasks and initializer non-entry |

Completion-enabled cold runs park at `4008d3ec` after about 130 million estimated instructions. Intro reaches acceptance after 80 million additional estimated instructions in all four continuations. Completion-disabled runs park after about 30 million estimates. Equal chunk outcomes are not equal physical timing.

## Actual boundaries observed

The cold stock initializer site is `400ffed0`. E04 reaches the same site, then fallback `47be08a4` and stock trampoline `47be0642`. At entry the stack is `41378688` and SR `2004` for both images. E04's trampoline sees SP `41378640`, SR `2000`, as expected from its wrapper frame.

A second replay with general unblock disabled traces the actual intro-exit instruction at `40091b0c`. Both images reach it at SP `413808d8`, SR `2000`, D0 zero. E04 then has pointer `47bccf04` and header `[534c4332, 2, b70, 1]`: private context is ready after initialization. The ready flag is written by the wrapper only after its stock initializer call returns. There is no evidence of an initializer hang in this modeled state.

Both replays report zero general semaphore satisfactions. Their recorded intro stand-ins contain 516 idle reschedules each; there are no intro-stage completion or flash-read stand-in calls in these two traces. This narrows the earlier suggestion: general forced semaphore waits are **not needed to clear the logo in this workload**, though cold hardware-completion kicks remain necessary to reach it.

The stock animation loop compares its counter against `b4` (180) at `40091af8`, returns to `40091978` until complete, then executes the exit sequence. This is actual stock instruction flow, not a host jump to a settled UI. It does not establish how far physical E04 progressed within that loop.

## Remaining model substitutions

- **Cold hardware completion:** at `400fbd14`, the emulator sets semaphore `419eaeec` to one before the native wait. Stock code writes `fc074004` and `fc074000` immediately before the wait. Real hardware must deliver the relevant completion; the comparison does not execute or validate that physical mechanism. Both images share three supplied completions.
- **Flash access:** the cold flash-read hook copies requested data from the packaged image and returns success. Physical transfer latency, errors and device status are bypassed. No flash-read shortcut was hit in the separately traced intro interval.
- **Timer policy:** cold boot supplies scheduler events at idle spins without pacing the logo. Intro enables PIT3, holds PIT0/PIT2 and DMA timers until exit begins, then releases the broader set. This is an explicit emulator policy, not a measured device power-on interrupt schedule.
- **Peripheral and storage state:** ready/status registers, SD continuity, storage and DSP exchange use emulator models. The initialized synthetic drive is not a dump of the user's physical projects or storage state.
- **Cache and RAM:** cache-control writes are represented, but physical instruction/data visibility, cache tags, memory latency and all RAM writers are not reproduced. A modeled successful copy cannot exclude a physical visibility/placement fault.
- **Execution engines:** scoped ISA handling, softfloat/bitmap acceleration and snapshot reconstruction remain. Disabling general unblock does not make this a full silicon simulation. Cold depack clamp counters are recorded separately; no blanket decompression equivalence claim follows from the boot result.

## What is and is not narrowed

The modeled logo transition is actual guest execution, and E04's ready initializer completes before it. A general unblock helper artificially completing the logo is not the explanation in this tested state. The earlier completion mechanism, real interrupt ordering, cache/RAM visibility and physical storage state remain concrete gaps; none has been identified as the device cause. The screen's H remains uninterpreted.

The next bounded target is the hardware-completion routine and its actual completion writer/interrupt, followed by whether E04's early copy/cache handoff can affect that path. Compare the changed startup sites against stock and trace the real completion producer instead of immediately assuming success. Keep stock on the instrument. Do not construct or install another candidate solely because these PC runs pass.

## Evidence

- `Digitone-E04-logo-startup-comparison.json`: four cold runs and four intro continuations.
- `Digitone-E04-intro-boundary-trace.json`: two further intro replays, with general unblock disabled.
- `Digitone-E04-hardware-startup-incident.md`: physical observation and user-reported stock recovery.
- Scripts: `work/compare-E04-logo-startup.py`, `work/trace-E04-intro-boundaries.py`.
