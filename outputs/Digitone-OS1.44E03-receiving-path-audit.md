# OS 1.44 E03 ordinary receiving-path audit

PC-only evidence. Firmware files are unchanged. This does not establish hardware readiness.

## What now executes

The complete E03 transport contains 1,604,128 bytes, comprising 12,532 data packets and two markers. The stock byte parser at `400e7eca` processes every byte and emits the exact complete frames. Its ring wraps during this run. Collected queue messages are delivered synchronously to the stock manufacturer/device dispatcher at `400eaac8`, whose existing tables select receiver `400e9fcc`. The receiver produces the exact transport-decoded bytes, phase 3, and one completion notification (`12`). Tested wrong manufacturer/device IDs do not reach this receiver.

The main receiver's packet decoder/counters run unchanged. Tests reject packet checksum, sequence, truncation/terminator, seed and missing-packet/end errors without completion publication. A new start after an interrupted session resets the receive counters. Gate-disabled input is ignored.

Completed-buffer accessor `400eab94` returns `40325f00` only after completion. Stock whole-image checksum `400eb76c` returns 1 for the valid stream. A modified payload with recalculated packet checksums reaches transport completion but fails this whole-image check.

Delivering the completion notification directly to view handler `400c9cca`, using the actual stock local-provider constructor/vtable, reaches completion UI builder `400c98da`. A set view busy flag at `+95` suppresses this path. The UI builder statically installs received-image action `400c9536` at `400c99b0`. That action executes the completed-buffer accessor and stock compatibility check and then calls updater `40100440` at `400c960e`.

Executing that action with the same buffer produced by the full receiver reaches the stock programming-complete boundary `40100504`. Under the supplied JEDEC ef/4018, 256-byte page, 64-KiB erase geometry, it issues 20 erase requests and 4,944 programming requests. Programming ends at flash offset `1b5000`. All source reads remain within the advertised container, including explicit final padding; simulated programmed bytes match it exactly. A guard at stock data offset `380000` survives. These are results of the supplied geometry and simulated flash, not measurements of a physical Digitone.

The same action rejects the packet-valid/content-invalid stream with result 3 before modeled hardware queries or flash calls.

## Boundaries of this evidence

These are joined, bounded instruction tests, not one uninterrupted peripheral-to-reboot execution. Queue enqueue/wakeup are collected and frames delivered synchronously. The byte parser receives a test stream through a PC-only runner; UART interrupts, USB endpoint ingress, USB-MIDI framing, overrun behavior and real transport pacing remain unexecuted. The update view's allocation/layout is supplied, and its completion notification is delivered directly. The completion UI builder and confirmation dialog/function-object lifetime have not been executed together. Received-image action execution stubs display/string/function-object helpers and project-save operations; its buffer accessor, checksum/compatibility branch and updater loop run as stock instructions. Flash identity/geometry/factory state are explicit fixtures; erase/program are simulated. Physical write errors, power interruption, reset completion and cache coherence are not established here.

## Remaining release blockers and next checks

1. Execute the real queue consumer and confirmation callback lifetime, then join the tested byte route and received-image action in one continuous PC run. Trace/test actual USB-MIDI ingress separately from the common SysEx routing.
2. Resolve startup failure behavior: the present header/argument failure path masks interrupts and stops rather than continuing with stock operation; a non-null owner pointer has no established address-bound validation.
3. Establish ownership of the reserved RAM across computed writes, DMA, reset and worst-case stack use for OS 1.44. Passing observed traces is not exclusive-ownership proof.
4. Validate physical cache handoff and timing/audio deadlines. Emulator memory costs and clock candidates remain assumptions.

No hardware transfer or flash was performed. No firmware image was rebuilt in this audit. Original 1.44 and E02/E03 hashes match their recorded values.

## Reproducible evidence

- `Digitone-OS1.44E03-application-receive-checks.json`
- `Digitone-OS1.44E03-ordinary-receive-updater-checks.json`
- `Digitone-OS1.44E03-byte-parser-routing-checks.json`
- `Digitone-OS1.44E03-completion-view-routing-checks.json`
- `Digitone-OS1.44E03-receive-action-updater-checks.json`
- `Digitone-OS1.44E03-receiving-path-audit.json`

Test scripts are in `work/validate-E03-*.py`. The stock-producing receive stream is saved as `work/os144/E03-actual-received-stream.bin` for PC analysis only.
