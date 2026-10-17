# PC release and warm-reset protection

A separate host-loaded overlay at `47fa0900` adds 594 bytes of code. It does not modify E04, the stock recovery file or any earlier code artifact. It is not packaged firmware.

## Implemented policy

The recovered note-off entry `400eae0c`, sustain setter `400f049a`, and retained-release entry `400f0580` require exact LIVE before their original prologues execute. Denial preserves incoming registers/SR and leaves retained notes intact. Returning to LIVE does not automatically drain retained notes; a subsequent stock pedal-release event performs cleanup. Automatic replay/discard of closed-phase input is not implemented.

Normal setup entry `4009d0d8`, setup body `4009c5ae`, pool wrapper `4009c5a0` and pool initializer `400ffed0` accept only INITIALIZING with their recovered cold call-chain return addresses. LIVE cannot enter these recovered reset boundaries. The wrapper reproduces the native initializer return address instead of relocating its JSR into a different caller contract.

Test-exit entry `4009d0ea` refuses before its flags clear. Parsed diagnostic-exit command `4008b88a` refuses before its diagnostic flag clear, prints existing `?ERROR`, and enters the stock common response cleanup/worker loop. These are no-op refusals, not support for safe live reinitialization.

## Tests

- 29 denial controls: closed release/sustain and disallowed setup entries preserve monitored pool, context, sustain state, config, flags and CPU/SR. INITIALIZING with an unrecognized return is denied.
- One paired full cold pool-wrapper call: guarded/native initializer, cleanup, CPU and state match the prior implementation.
- Four paced receiver sessions: observed LIVE handler/state parity against displaced stock entries; closed CC64 no longer changes the tested sustain flags; held notes remain retained during closure and clear through stock release after a declared fixture LIVE resume. All MIDI bytes delivered; no emulator halt.
- Three parsed-command controls: LIVE, INITIALIZING and FAILED refuse with native error printing, a balanced stack and return to worker loop. The diagnostic flag, queue, pool, full tested context/sidecar bytes and setup flags remain intact.
- Three cold startup runs: default, restored project and feature-disabled fallback reach modeled UI and normal LIVE with all guards installed. Existing cold/intro/device/storage shortcuts remain; no physical timing claim.
- Static ColdFire ISA/MOVE checks cover the custom instructions.

## Limits and next scope

Retained-note resume uses an explicit host phase change as a negative-control fixture. This does not demonstrate a naturally scheduled warm transition. Cold phase plus recovered return addresses is bounded call-chain checking, not unforgeable fresh-boot provenance.

The prior UI ownership/refusal hooks are not installed by this overlay. An outer caller can continue after a no-op setup refusal; command cleanup is tested, but page retained-reference transfer and every unknown computed/interior caller remain separate work. Panel-note production was not positively observed in the earlier attempts. Guards on these recovered release paths are not certification of every event cancellation/queue consumer.

Physical RAM ownership, executable placement/copy/cache handoff and timing remain unverified. No hardware trial is justified by these PC results.

Evidence: `Digitone-E04-PC-release-reset-controls.json`, `Digitone-E04-PC-release-reset-sustain.json`, `Digitone-E04-PC-release-reset-command.json`, and `Digitone-E04-PC-release-reset-startup-startup.json`.
