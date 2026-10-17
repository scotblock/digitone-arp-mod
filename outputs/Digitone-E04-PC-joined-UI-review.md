# Joined UI refusal and actual panel routes — PC only

The existing persistent retained-defer and explicit-refuse UI hooks are now installed alongside the cold startup, input/LIVE and release/reset guards. A joined layout records 18 distinct patch sites. All code remains host-loaded at fixture addresses; no firmware container or earlier binary was modified.

Three native cold startup cases (default, restored project and feature disabled) reach modeled UI and LIVE. Saved executable pages were checked for all 17 persistent hooks. The early copier-tail site is no longer present in settled UI memory; its execution is covered by the startup trace, not a final-snapshot byte assertion. Twelve LIVE route controls cover audio refusal/defer and ordinary/null pass-through using both explicit and retained selection and two mutex/ownership forms. Two lifecycle runs complete three close/re-entry cycles each, including native registry removal, list unlink, reference cleanup and final destructors/free. Protected audio callbacks and pool rebuild are not reached. Constructor and retained-reference state remain declared native test fixtures.

## Panel execution now positively observed

A longer sequence — KEYBOARD, T1, key 1, T2, then key 5 — reaches the actual panel path. Earlier short presses were insufficient to establish that workload. With scheduler forced-unblock disabled, UART8 interrupt `40002342` and receiver `400e9076` consume all supplied bytes. In the LIVE case, target press reaches guarded producer `400eae5c`, queue publication `40100252` and pitch `4009e882`. The observed T2 note count rises from 0 to 1. Release returns it to 0 through internal release `400eabb4`, sustain-release `400f0580`, and publication. This is a functional panel route, not a physical timing measurement. The symbolic `ui_key_dispatch` hook did not resolve; no missing dispatch address was guessed.

## Closed-phase controls and their limit

Supplying INITIALIZING before target press makes the producer guard refuse it; there is no target note publication or active count. A note pressed in LIVE and then released after a declared host phase change remains retained with count 1, with no release publication. The internal release is outside the MIDI packet wrapper but its call to the guarded sustain-release helper stops the tested path.

The return contract matters: internal release sets D0 to 127 before calling the helper and checks its low byte afterward. The guard preserves 127 on refusal, which the actual caller interprets as handled and skips further release work. That is evidence for this recovered caller; it does not certify arbitrary callers entering the helper with D0=0. No automatic replay of a panel release dropped during closure is implemented. Reopening LIVE alone does not demonstrate cleanup of that retained panel note, so seamless close/resume behavior is not certified.

An exploratory forced-unblock comparison was rejected by checkpoint manifest validation before execution; it supplies no panel evidence. The successful three panel sessions all preserve the saved unforced scheduler configuration.

## Remaining work

Audit refusal return contracts of other recovered release callers and define deferred panel-release cleanup if any reachable transition is allowed to close and reopen admission. The current warm-reset policy refuses recovered live resets, so the tested LIVE-to-INITIALIZING panel transition is a negative-control fixture, not a proved stock transition. Unknown computed/interior UI routes, fresh-boot provenance, physical RAM ownership, executable/cache handoff and hardware timing remain unproven.

Evidence: `Digitone-E04-PC-joined-UI-summary.json`, `Digitone-E04-PC-joined-UI-startup-startup.json`, `Digitone-E04-PC-joined-UI-routes.json`, `Digitone-E04-PC-joined-UI-lifecycle.json`, and `Digitone-E04-PC-joined-UI-panel-tests.json`.

