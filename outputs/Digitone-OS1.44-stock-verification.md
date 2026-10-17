# Stock Digitone OS 1.44: PC behavior verification

The stock 1.44 engine boots to a settled interface and executes queue handling, MIDI sustain and an actual playing pattern change. These observed functional scenarios pass. Firmware files and the 1.42 main-program reference remain unchanged; no custom arp code was installed.

## Verified execution

The new baseline starts from the supplied 1.44 main program with a fresh emulated drive and snapshot, not a 1.42 snapshot. First boot settled at the engine's estimated 1,400M instruction mark. This uses the engine's direct main-image entry rather than the full firmware loader.

In the combined run, lasting 3.584 emulated seconds:

- 1,170 events reached the actual queue publisher. 10 observed acceptance calls matched an earlier publication by address and allocation generation. 11 published slots were reused. Real producer calls were observed for all four track indices.
- MIDI CC64 set the sustain flag. Note-off left a retained note-list entry. That same flag and list entry persisted through actual replacement, then pedal release cleared both.
- The active pattern backing switched from `0x40813531` (pattern 2) to `0x407fd414` (pattern 1), at 3220.466516 ms, written by stock code at `0x4009621e`. The receiving pattern's data hash differs. Six pending publications were observed at that boundary; this alone does not establish that a queued note survives it.
- A fresh MIDI note after replacement reached stock pitch output with pitch 62. The parser handled all injected MIDI bytes, and the engine did not halt.

The input-enable setting is a disclosed PC RAM fixture so the real DIN MIDI parser accepts the test bytes. Note handling, queue publication/consumption, pattern replacement and pedal handling execute stock instructions.

## Delayed queued note

A second run delays one actual stock-produced type-0 note by 96,000,000 queue timer ticks, changing only the publisher's timestamp argument in PC RAM. The event's fields and eligibility are not manufactured. It is `0x419ebebc`, generation 68, track 3, and has a non-null `+0x38` descriptor (`0x41a120a0`).

The event remains identifiable across replacement, but is released at 4417.333359 ms without reaching the instrumented acceptance or pitch point for that generation. This is **not** a successful old-note pitch replay. The exact release decision still needs tracing; do not infer its cause from the final release alone. The unmodified combined run also contains no matched publication/acceptance pair crossing pattern backings.

## Controls and limits

Earlier multi-input runs did not complete their playing pattern requests. Those negative traces are retained separately and excluded as handoff proof. A minimal stock panel sequence established a real playing transition; repeating it with MIDI sustain also succeeded. The recurring probe previously labeled `transition_done` is a sequencer callback and is not used as completion evidence. The pointer write and changed receiving data establish the observed replacement.

These are finite functional observations. Allocation failures, all copying/remap branches, naturally eligible delayed arp playback across replacement, and custom retained root/scale context are not exhaustively verified. Instruction pacing and engine float/bitmap, storage, device and ISA stand-ins remain in use. Physical cycle timing, DMA/cache coherence and reserved RAM ownership are not established by this run.

## Next step

Trace why the delayed stock note is released and check the changed selector's eligibility/list handling. Use that result to adapt the 1.44 PC hook contracts, then replay these successful scenarios with overlays. Keep custom hooks unconnected until those contracts are checked.

Evidence files beside this report: `Digitone-OS1.44-stock-startup.json`, `Digitone-OS1.44-stock-pattern-isolation.json`, `Digitone-OS1.44-stock-sustain-transition.json`, `Digitone-OS1.44-stock-delayed-queue.json`, and `Digitone-OS1.44-stock-verification-summary.json`.
