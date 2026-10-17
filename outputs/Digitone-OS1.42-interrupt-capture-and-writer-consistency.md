# Digitone OS 1.42: interrupt capture and writer consistency

**Follow-up:** [Six-pass transaction and handoff audit](Digitone-OS1.42-six-pass-transaction-and-handoff-audit.md) classifies historical-format offset matches, identifies additional current-backing writers, and tests whole-pattern consistency separately from individual root/scale pairs. Outer transaction protection remains unresolved.

**The recovered input-task and audio-interrupt setup supports capture preempting a multi-store pattern update.** The input task starts with CPU interrupt mask 0; the audio service is a forced level-5 interrupt. No writer transaction guard was found on the previously recovered restore/reset route. Reader-only masking remains insufficient, and the proposed snapshot design must account for partial writes.

This is a static execution-path finding, not an observed hardware race or a certification that every runtime configuration permits capture. No firmware was edited, rebuilt, repacked or transmitted.

## Input task creation and interrupt state

The missing reference to input entry `40016d56` was PC-relative, rather than an absolute pointer:

| Address | Recovered instruction/effect |
|---|---|
| `400169b0` | `pea 40016d56(pc)` passes the input task entry |
| `400169b4` | Passes task object `404de544` |
| `400169ba` | Calls task initializer `4000170c` |
| `4000173a..40001740` | Installs initial exception-frame word `407c2000` |
| `40001744` | Installs the supplied entry PC in the next frame word |
| `400169ca` | Starts/enqueues the task through `40001758` |

The initializer also installs return trampoline `40001788`. The context-switch routine at `40000410` restores the selected task's saved registers/stack and executes `RTE` at `40000458`.

The initial frame's saved SR is `2000`: supervisor state, CPU interrupt mask 0. The exception frame stores format/vector and SR in its first longword, followed by PC; SR bits 10..8 are the interrupt mask. These interpretations follow the [NXP MCF5441x reference manual, sections 3.2.9 and 3.3.3.1](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=94).

Input execution subsequently reaches the event loop at `400171e2`, queue pop `40001d6c`, and the already traced UI dispatch/writer chain. The queue pop restores its incoming SR at `40001dbe`; it does not retain its temporary mask across dispatch. No explicit lasting mask was found in the recovered event-loop branch or local writer chain. Initial SR is now established; later inherited state is not globally proved for every possible call history.

## Audio interrupt source and priority

At `4009bd4c..4009bd52`, firmware installs `4009c838` into vector slot `400002fc`. At `4009bd58..4009bd5a`, it writes `5` to `fc04c07f`.

With the recovered vector base `40000000`, slot `2fc/4` is vector 191. The matching register map identifies `fc04c07f` as INTC1 source 63's control register; its low three bits assign level 5. INTC1 vector numbering is `128 + source`, matching 191. A level-5 interrupt is admitted when CPU mask is below 5. See [NXP manual, chapter 17 and SR field definitions](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=344).

The producer ISR `4009ba1c` unconditionally sets bit 31 of `fc04c010` at `4009ba5c..4009ba62` after its preceding bookkeeping. Audio entry clears that forced bit at `4009c840..4009c846`. The audio handler ends with `RTE` at `4009dc5c`.

This is a software-forced source-63 request. The manual states that force-register requests bypass the ordinary interrupt-source mask; CPU interrupt priority masking still applies. Consequently, ordinary source masking alone cannot be assumed sufficient for this request. See [NXP manual, section 17.2.3](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=339).

## Queue capture conditions and suppression

Audio processing calls the descriptor handler at `4009cae4 -> 400efcb8`. The branch at `4009ca12` enters descriptor processing when the mode read through `40007224` is not `6`. That getter reads `404dc2fc`. Descriptor availability/timing checks can defer an item or provide no item; a forced audio interrupt therefore does not imply a new snapshot on every invocation.

The `41345e64` branch near audio entry changes the work performed before the paths rejoin. Clearing this flag is not evidence that the descriptor handler is excluded for an entire pattern update.

An actual vector-suppression mechanism exists:

| Routine | Effect |
|---|---|
| `400eef48` | Saves the installed audio vector in `4199cd20` and substitutes `400eef30`, under a short SR guard |
| `400eef30` | Clears the forced request and returns with `RTE`, without descriptor processing |
| `400eef72` | Restores the saved vector, under a short SR guard, then clears the saved slot |

No direct/raw or recovered PC-relative call to these routines was found in the discovery inventory, and none occurs in the recovered restore/reset dispatch route. This does not prove they are unreachable through every indirect path. Their presence cannot be treated as an active writer guard. Their saved-slot scheme is also not evidence of nested ownership or a suitable per-edit policy.

## Consequence for the proposed snapshot

In the traced canonical-bank relationship, the writer and receiving capture can address the same track fields. With the input task unmasked and the audio request at level 5, the following sequence is architecturally possible:

1. Restore stores the new scale.
2. Forced audio service interrupts before the new root store.
3. Descriptor handling captures the partial pair.
4. `RTE` returns to the paused writer, which completes afterward.

A reader critical section, repeated identical reads or a valid CRC cannot establish that the writer committed its full metadata group. The remaining uncertainty about unrelated global gates is not a safe basis for implementation.

The preferred PC-only design to investigate is a short writer commit: prepare metadata and resolve one backing pointer first; save SR, mask the known interrupt, perform bounded stores without allocation/callbacks, restore SR, and notify afterward. The five-byte group `+3cb..+3cf` is a useful modeled unit for these restore/reset operations. This is not a firmware change or a universal solution: other writer/copy paths and multi-track transactions need the same ownership analysis. Do not simply mask an entire high-level restore function containing allocation and virtual calls.

## Verification and next target

Ten specification scenarios pass: all eight CPU masks, forced-request/source-mask distinction, queue-pop scope, actual-installed-stub distinction, mode/descriptor conditions, partial-pair capture, and a proposed five-byte masked commit with requests at all six store boundaries. Twenty-three byte anchors were checked against the decoded image. The PC model does not emulate the CPU, controller global level masks, interrupts, timing or firmware execution.

Next, classify the remaining conversion/default and whole-pattern-copy writers and determine their transaction boundaries. Test a common writer-commit rule against those paths before choosing any patch insertion. Queue-byte global alias coverage, event-context destination ownership and stack/register requirements remain separate implementation gates.

Original SysEx SHA-256 remains `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`; section-3 SHA-256 remains `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.
