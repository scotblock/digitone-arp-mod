# Digitone OS 1.42: resident installation route and connected metadata helpers

3 October 2026. PC-only execution fixtures. Original firmware and decoded main image remain unchanged; no modified, repacked or flashable image was produced.

## Outcome

A concrete **resident placement route** now fits the tested initialization and accepted-context integration into the existing main image. It avoids runtime code copying: selected instructions would occupy a bounded padding candidate already loaded with the main section, while the separately owned allocation stores only metadata.

The PC harness connects actual metadata instructions to the stock setup and retained-copy caller. **301 assertions passed across 45 cases**, including all four synth tracks, cold initialization followed by the caller, initialization reentry, and controlled failure paths. The recovered startup table reader also executed **119 callback dispatches in 957 instructions**, with callback bodies supplied as immediate returns.

This establishes the route in the PC fixtures. It does not certify physical instruction fetch or exclude every computed alias into the selected gap. Those limits remain explicit; no hardware claim follows from these results.

## Why this particular placement is defensible

The stock image contains a counted startup function-pointer table:

| Item | Address/value |
|---|---|
| Count word | `40241ab4`, value 119 |
| First entry | `40241ab8` |
| Exclusive table end | `40241c94` |
| Zero padding end | `40242000` |
| Selected fixture start | `40241ca0` |
| Available selected interval | 864 bytes |

The reader at `4008c7d4` loads the base and count, dispatches one pointer per iteration, and stops after 119 entries. Actual traversal with stubbed callback bodies leaves its pointer at `40241c94`; it does not read the padding. Twelve zero bytes after the table are retained before the selected interval.

The startup initialized-data sources begin at `40242000`, and the subsequent clear also begins there. Consequently, the selected interval lies inside the original loaded main section and outside both the startup data-copy source ranges and the clear range. This avoids the previously rejected append-at-image-end route.

An all-byte-alignment literal scan found four apparent addresses into the gap. Each was an odd-alignment overlap across instruction bytes, rather than a decoded address operand; the evidence file records their surrounding instructions. This scan cannot exclude computed pointers or indexed accesses. The placement is supported by recovered boundaries and local consumers, not a universal ownership proof.

The startup writes cache/control registers before entering the application. The resident route adds no runtime code writes or new load destination and keeps the stock startup cache setup. Its actual MMU/cache behavior is not simulated here. In particular, Capstone's name for control selector `0004` is not used as verified target-specific register semantics.

## Resident fixture layout

| Body | Address | Bytes |
|---|---|---:|
| Begin gate | `40241ca0` | 46 |
| Cancel gate | `40241cce` | 40 |
| Commit accepted tuple | `40241cf6` | 154 |
| Read accepted tuple | `40241d90` | 74 |
| Resolve owner/header/track | `40241dda` | 94 |
| Read known event candidate | `40241e38` | 60 |
| Before-setup wrapper | `40241e74` | 66 |
| After-setup wrapper | `40241eb6` | 68 |
| Retained-copy commit wrapper | `40241efa` | 94 |
| Initialization preflight and local failure endpoint | `40241f58` | 120 |
| Initialization readiness completion | `40241fd0` | 28 |
| **Total / exclusive end** | **`40241fec`** | **844** |

Twenty bytes remain before `40242000`. The separate copy/invalidate helpers from the previous six-helper tests are not included in this selected resident layout. This is enough for the tested accepted-context path, not the complete V1 mod with every producer/copy hook and scale-constrained pitch implementation. Further code needs another justified interval or layout compaction.

## Initialization now executes instructions

The fixture redirects the stock common initializer entry at `400f0504` before its first pool mutation:

1. Replay the original d3/d2 saves and require geometry argument 158.
2. For a zero owner, request **`14c70` bytes** from stock allocator entry `400dab8c`.
3. Reject a null result before stock fixed-pool or owner mutation.
4. Execute the stock memset over the explicit extended allocation.
5. Write magic `534c4332`, version 2 and metadata extent `b70`; readiness remains zero.
6. Publish the allocated owner, replay the original LEA of `4199dad8`, and resume at `400f050e`.
7. Execute stock pool linking. At `400f05d0`, the completion wrapper publishes readiness and replays the stock pops/return, restoring the incoming condition flags around its readiness store.

The allocator's result is supplied at its boundary; its internals are not executed. Unlike the previous Python preallocation model, the request, memory clear, header stores, owner publication and readiness store are now driven by executed instructions.

Existing-owner reentry retains the table byte-for-byte and avoids allocation in the fixture. It still runs the stock pool rebuild; this is not evidence that rebuilding live stock pools is safe. The integration assumes a cold boot through this modified initializer establishes the extended owner before reentry. Adopting an unknown preexisting stock-sized owner is unsupported.

Wrong geometry and null allocation take a local interrupt-mask-and-spin endpoint. The tests establish non-return and absence of pool/table mutation, not graceful recovery, DMA shutdown or actual device recovery behavior.

## Connected stock caller

The setup call at `4009dda6` is redirected only in the harness fetch overlay. The before wrapper resolves the actual owner, checks header magic/version/extent/readiness and track 0..3, then runs the real begin helper. It replaces the existing return address and jumps into unchanged stock setup, keeping original arguments at their expected offsets.

The after wrapper reloads the saved setup result before deciding whether to cancel. A zero result closes the gate and preserves prior context. A nonzero result leaves the gate closed to readers until stock retained-copy completion.

At `4009de46`, the commit wrapper reads the candidate from the metadata slot corresponding to the actual fixed event-pool address. It supplies the actual event identity written by stock setup and the playback track to the real commit helper. Unknown event addresses or missing candidate words commit fallback. The wrapper then restores registers, replays both displaced instructions and resumes at `4009de50`.

The accepted-context reader is executed after commit, but it is **not yet connected to the live pitch insertion point**. Candidate words are supplied as test inputs; the actual root/scale capture producers are not yet instrumented with these instruction bodies.

## What the tests establish

All four synth tracks exercise new acceptance, additive input, lower-priority rejection, settings replacement, disabled arp, unknown event address, missing context, not-ready header, null owner and bad magic. A further case uses the allocation/header created by the instruction initializer and continues into the actual caller.

For every caller case, a parallel unmodified execution provides a baseline. At the chosen continuation, **all registers, exact SR and all 72 retained-event bytes match stock execution**. The extra metadata changes are separate. Tests also verify retained copy precedes commit, the busy gate hides intermediate stock mutation, the two pending copy arguments remain intact, zero-result paths preserve readable prior track binding, and the accepted reader returns the expected snapshot or fallback.

The observer only inspects RAM; metadata writes come from the executed helper/wrapper instructions. Stock setup, retained copy and the relevant caller branches run from unchanged decoded bytes. Fetch substitutions and resident bodies exist only in the PC harness.

The tests use controlled single-note mode-one inputs and an empty voice-stop mask. They stop at the selected caller continuation; they are not full audio/handler execution, a scheduler model, exception cleanup verification or an independently validated CPU emulator. Readiness and local interrupt masking do not establish global producer exclusion.

## Remaining work

The immediate integration gap is **actual producer capture and the pitch reader hook**: candidate snapshots are still supplied, and scale-constrained pitch output remains in the PC prototype. Integrate those instructions next, while accounting for the 20-byte remaining resident capacity. The stock allocation path, final placement aliases and device execution remain material uncertainties for any later experimental build.

Evidence files:

- `Digitone-resident-installation-route-audit.json`: 11 stock instruction anchors, startup table boundaries/traversal, startup interval checks and classified literal matches.
- `Digitone-resident-caller-helper-tests.json`: fixture layout/disassembly, 301 assertions and 45 cases.

Reproduction scripts remain under `work/test-resident-caller-helpers.py`, `work/audit-resident-installation-route.py` and `work/test-resident-startup-table.py`. The latter augments the installation audit after the audit script runs.

Original SysEx SHA256: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`.

Decoded main SHA256: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.
