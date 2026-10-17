# E04 startup delay: actual producer and copy/cache interaction

8 October 2026. PC-only diagnosis after the physical E04 startup failure. The device remains on working stock 1.44. Both SysEx images are unchanged.

## Finding

The early completion is a **one-shot DTIM1 timer delay**, not evidence that an external transaction or coprocessor acknowledged a request. The emulator's old completion shortcut bypassed this delay. New matched runs disable that shortcut, deliver modeled vector 97, execute the native interrupt and native semaphore-post/wake code, and reach the interface in both stock and E04.

This closes a specific missing producer path in the PC evidence. It does not reproduce or explain the physical E04-only startup stall.

## Producer chain

Stock function `400fbc88` initializes completion semaphore `419eaeec` and serialization object `419eaef4`. It installs handler `400fbc58` at vector-table address `40000184` (vector 97), sets interrupt source 33's priority/control at `fc048061` to 2, and unmasks source 33 through `fc04801d`.

The function writes the requested reference count to `fc074004`, arms mode `841b` at `fc074000`, and calls the native blocking wait `4000185e` at `400fbd14`. The native wait links the current task if the completion has not been posted; it is not an unconditional return.

NXP identifies these as DTIM1 reference/mode registers and INTC0 source 33 as DTIM1. Mode `841b` selects prescaler 132 (divide by 133), bus-clock input, reference interrupt, restart and enabled state. Event bit REF is acknowledged by writing one. [MCF5441x reference manual, chapters 17 and 39](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf).

The interrupt at `400fbc58`:

1. Saves D0/D1/A0/A1.
2. Writes 2 to `fc074003` to acknowledge REF.
3. Writes zero to `fc074000` to stop the timer.
4. Calls `400019a0` with semaphore `419eaeec`.
5. Restores registers and executes RTE at `400fbc86`.

The post wrapper invokes actual RTOS code at `40001632`. In the new runs, guest instruction `4000163a` writes the completion value, and the subsequent wake path clears it while releasing the waiting task. No host write supplies a successful completion.

The timer/setup/ISR range `400fbc58..400fbd30` and reviewed native wait/post wrappers are byte-identical in stock and E04. Raw literal-reference scans support the recovered direct paths; they are not a universal proof against computed writers.

## Native-path execution

Each image uses the same direct MAIN reset configuration, explicit loader-matching `00140000` entry flags, and a fresh copy of the initialized emulator drive. Cold `patch_sem` is disabled. DTIM1 is attached from reset with stale-state repair disabled. Expiry is modeled; firmware executes exception entry, ISR, semaphore post and scheduler wake. The emulator's flash-read shortcut and scoped ISA emulation remain.

| Observation | Stock | E04 |
|---|---|---|
| Host completion kicks | 0 | 0 |
| DTIM1 interrupts / actual handler entries | 3 / 3 | 3 / 3 |
| Programmed reference counts | 100, 1000, 1000 | 100, 1000, 1000 |
| Native completion writes at `4000163a` | 3 | 3 |
| Delay callers' return addresses | `4008d038`, `400f5266`, `4008d724` | Same |
| Cold terminal PC | `4008d3ec` | Same |
| Cold task-create sites recorded | 10 | 10 |
| Intro general forced satisfactions | 0 | 0 |
| Intro completion stand-in calls | 0 | 0 |
| Intro exit / main-loop entries | 1 / 138 | 1 / 138 |
| Live interface | Yes | Yes |

The RTOS write trace includes actual waiter linkage and post/wake writes. General semaphore unblocking is disabled in the intro continuation. Both cold runs use a native basic-block estimate and an assumed timer clock; they are not cycle-exact or measured hardware delay durations. A test assertion initially indexed the timer's fired counter by vector 97 rather than channel 1; it was corrected and the complete final tests were rerun.

## Interaction with E04 startup changes

E04 executes its early copier at `4029c4b0` with IPL7. It copies 623 longwords from `4029c5b0` to `47be0000..47be09bc`, clears metadata/context at `47be1000..47be1b74`, seeds its header and pointer, then tail-jumps to the original routine `40001df4`.

Stock cache setup at `4000055a` is reached with IPL7 before the first DTIM1 wait in both runs. The cache setup instructions themselves are unchanged. E04's payload remains exact. Timer setup/waits then execute at IPL0 and the delivered timer ISR at IPL2. The timer code, vector word, completion semaphore and controller registers are outside the copier's destination spans. No direct overlap or stuck IPL7 is observed on this path.

The first two timer delays occur before E04's initializer/fallback. The third occurs after that initializer, and completes natively as well. Consequently, this test does not support either a permanently interrupt-masked initializer exit or a missing native timer post as the failure in the tested state. Low condition-code bits differ in the third ISR trace; the interrupt level remains 2 and the native wake succeeds. This is not a claim all CPU state is identical.

Cache-control ordering alone does not prove physical code visibility. Inherited physical cache state, copy/write completion, RAM ownership on the real device and actual interrupts during startup remain outside the model. Intro still uses the deliberate timer policy and a restored snapshot; physical storage is not the emulator's initialized drive.

## Decision and next target

The missing early producer is now identified and executed, with no observed stock/E04 difference preventing startup. Do not keep treating this semaphore as an unexplained external completion or reinstall E04 because the timer test passes.

Next compare the changed early copier and initializer separately using PC-only controls, and audit the copier's assumptions about inherited cache/memory attributes against the full loader path. This is a focused investigation of the changed startup mechanisms; it is not a new flashable candidate or authorization for another device trial. The physical cause remains unknown.

## Evidence

- `Digitone-E04-completion-code-audit.json`: decoded code and byte comparisons.
- `Digitone-E04-native-startup-delay-checks.json`: completed matched native-producer runs.
- `work/audit-E04-completion-code.py`, `work/test-E04-native-startup-delay.py`.
- Unchanged E04 SHA-256: `76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c`.
