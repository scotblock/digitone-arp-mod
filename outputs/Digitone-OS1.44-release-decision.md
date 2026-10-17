# OS 1.44 delayed-note release decision

The specific release is explained by an executed stock cancellation path. It is not evidence of a damaged event or an allocator failure. The same stock-produced delayed event reaches acceptance and pitch output when the pattern is kept unchanged. No custom context hooks were connected, and both source firmware hashes were checked unchanged.

## Captured chain

The event is `0x419ebebc`, allocation generation 68, type 0, track 3. It is published at 1291.737031 emulated ms with `+0x0C = 1` and a non-null descriptor at `+0x38`. Only its queue timestamp is delayed by the disclosed PC fixture.

1. Stock writes the receiving pattern pointer at 3220.455328 ms: `0x40813531` becomes `0x407fd414`.
2. At 3248.402625 ms, the preparation path compares the alternate pattern pointer at `0x4138f21c` with active pointer `0x4138f214`. They differ. Its byte guard through A4 is zero, so the executed path reaches `0x40095ba2`, calling the future-queue visitor `0x40100118` with callback `0x4009363c` and a track index.
3. The visitor calls that callback for tracks 0 through 7. The callback accepts event types 0 or 3, compares event `+0x08` with its track argument, and writes `-1` into `+0x0C` at `0x40093656` when they match. The observed target is type 0, track 3: calls for tracks 0–2 leave it unchanged, track 3 invalidates it, and later calls observe the invalid value. This scan is supervisor interrupt-masked in its stock implementation.
4. At 4417.333359 ms, the render consumer reaches the note dispatch at `0x4009d760`. It reads `+0x0C`, compares it with `0xFFFFFFFF` at `0x4009d76a`, and takes the equality branch at `0x4009d76c` to `0x4009d7d8`. That path calls release at `0x4009d7de`, returning to `0x4009d7e4`. It bypasses the acceptance and pitch sites.

The invalidation changes only `+0x0C` before release; the recorded descriptor, flags and other event fields retain their published values. The event is not silently reused before this decision. Memory-watch records from later allocation clearing are excluded from this event's lifetime: the generation probe runs after those clear stores, so its counter alone must not attribute them to the still-live old note.

## Unchanged-pattern control

The control suppresses the playing pattern-change request while preserving the stopped pattern-2 setup, delayed timestamp and MIDI sustain scenario. Its published event fixture is exactly identical: same address, allocation generation, publication time, timestamp, original fields and source pattern backing.

Without replacement, the target receives no invalidation callback or `+0x0C` invalidation write. It retains `+0x0C = 1`, reaches stock acceptance and pitch output at 4352.000000 ms, and produces coarse pitch 59. Its later release is normal cleanup after processing, not the rejection observed with replacement. Subsequent scheduling phases differ; these times are functional emulator observations, not physical timing measurements.

Sustain is independent evidence: the retained MIDI sustain-list object is a different object from this queued event. Pedal state/list persistence does not mean the cancelled arp event should be played.

## Consequence for V1

The proposed context handling must preserve stock cancellation. A saved root/scale must never reactivate a note that stock has marked `-1`. Our producer/context and pitch hooks should retain the original consumer's eligibility gate and release behavior.

This closes the cause of this particular failed replay. It does **not** prove that every queued note is cancelled on every pattern change, or that an eligible old-pattern note can retain custom scale context across a replacement. The callback's other types, other guards and alternate producer/copy routes still need their own coverage.

Next, adapt the 1.44 helper contracts in isolated PC tests while preserving this gate. Separately find an uncancelled eligible queue path before claiming old-scale retention across replacement. Physical timing, cache coherence and complete reserved-memory ownership remain unverified.

Evidence: `Digitone-OS1.44-release-guards.json`, `Digitone-OS1.44-release-no-handoff.json`, and `Digitone-OS1.44-release-decision-summary.json` beside this report. Traces and helpers are PC-only; neither stock firmware file was modified and no flashable image was produced.
