# Receive-buffer protection during OS update

## Finding

The recovered stock 1.44 local-update path does not establish an explicit receive-buffer freeze across checksum validation and programming. The bounded PC model now demonstrates changed receive bytes being used by the simulated programmer if new input is scheduled in that interval. Disabling the stock receive gate prevents the modeled change. This is evidence against assuming that the already-tested route protects the buffer; it is not proof of a physically reachable device defect.

Firmware files and the device remain unchanged. No new flashable image was created.

## What protects what

The main receiver `400e9fcc` checks gate `419950a4` before parsing any packet. The normal view enables it through `400ed8dc` on entry and disables it through `400ed8ea` on exit. Literal-reference tracing finds initialization plus setter `400eb524`, not a programming-time gate clear. This scan is not a proof about every computed/global alias. The tested completion/work/programming route leaves the gate enabled. The busy view flag at `+95` suppresses UI handling, not packet decoding or receive-buffer writes.

The queued action retains a view/context reference, not an immutable image. Accessor `400eab94` returns the shared completed buffer. `400c9536` validates it and invokes updater `40100440`; the updater validates again, caches its length, then reads successive pages from that same RAM. It does not revalidate every page or require receive phase 3 during the programming loop.

Erase `400fcb2a` and page programmer `400fc832` acquire flash mutex `419eaf08` and the peripheral/bus mutex reached through `400f9b8c` (`419cf750`). Those protect flash/peripheral operations. The receiver and recovered DIN input-consumer path do not acquire them. The mutex routines mask interrupts temporarily for ownership bookkeeping and restore the incoming status. An isolated stock mutex test, entered with interrupt mask zero, returns with interrupt mask zero while the worker still owns the mutex. The updater's explicit `SR=2700` at `40100528` occurs after programming and the completion delay, not before buffer reads.

Task setup `4000170c` writes the initial exception frame `407c2000`. The input task is constructed at priority 7 in `400eb3e6`; the dialog/work task at priority 2 in `400a8950`/`400a84ac`. Actual stock task/ready-list routines and dispatcher `40000410` select the modeled ready input task ahead of the worker. This test stops before the selected task register restoration/RTE; actual interrupt arrival/preemption was not reproduced. Project-save wrapper `400a0248` leads to `400a8182`, which selects/saves project state and returns; the current continuous harness still stubs project-save work. Its deeper callees and complete application preconditions remain outside this proof.

## PC evidence

1. **Baseline with worker entered at SR 2000:** unchanged input produces the exact advertised image in simulated flash.
2. **New input after final validation, before erase:** stock receiver changes the buffer; one different byte is subsequently programmed.
3. **New input before first page programming:** same observed mismatch.
4. **New input after 50 pages:** a later unread buffer byte changes and is subsequently programmed.
5. **Gate-disabled control:** the same incoming frames change neither the receive buffer nor simulated flash.
6. **Actual DIN consumer:** a separate run feeds bytes through `400e7eca`, actual input enqueue/wakeup, dequeue and the DIN consumer branch `400e9bfa..400e9c72`, then SysEx dispatch and reception while the programmer is parked. Gate enabled changes one simulated programmed byte; gate disabled changes none. No direct receiver call replaces this interfering input path.
7. **Stock scheduling/mutex check:** ready input priority wins over worker priority, and holding the flash mutex does not retain an interrupt mask of 7.

The new traffic has valid packet framing/checksums. It makes the previously completed whole-image checksum stale; the programmer continues after its prior validation in these scheduled cases. Corruption is confined to the simulated flash array, with no hardware transfer or generated firmware artifact.

## Limits and next action

These use persistent PC machines with explicit task interleavings. UART hardware, USB ingress, interrupt arrival/pacing, full application state and kernel scheduling are not modeled end to end. Flash operations, registry/heap, display, project-save and some locks/thread operations remain fixtures. The real DIN consumer and stock scheduler selector narrow the former direct-callback gap, but do not certify physical timing. The observed executable interval is unchanged; source firmware file hashes also match their records.

The safest next step is a PC-only receive-freeze design: close the existing gate before obtaining/validating the completed buffer, prove that already queued input cannot write through another path, retain the freeze until programming/reset, and establish the proper gate restoration on rejected updates. Do not add a firmware hook until all success/failure exits and queued producers have been audited. A gate clear after validation would leave an earlier race window; a UI busy flag or flash mutex alone is insufficient in the tested model.

Startup failure continuation, exclusive reserved-RAM ownership, physical cache/timing and actual flash failure/reset behavior remain separate blockers. The firmware is still not hardware-ready.

## Files

- `work/validate-E03-input-scheduler-protection.py`
- `work/validate-E03-receive-buffer-interleavings.py`
- `work/validate-E03-DIN-buffer-interleavings.py`
- `work/buffer-protection-refs.py`
- `outputs/Digitone-OS1.44E03-input-scheduler-protection-check.json`
- `outputs/Digitone-OS1.44E03-receive-buffer-interleaving-checks.json`
- `outputs/Digitone-OS1.44E03-DIN-buffer-interleaving-checks.json`
- `outputs/Digitone-OS1.44E03-receive-buffer-protection-audit.json`
