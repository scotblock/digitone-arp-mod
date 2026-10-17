# E08 MIDI arp: playback ownership and settings guards

15 October 2026. E08D is an **internal PC-only candidate**, not a hardware release. E07 and the E08C baseline are unchanged.

**Later readiness finding:** E08D continued generating a held live arp after Stop and left retained membership when MODE was turned OFF. It is superseded for trial review by the corrected E08E candidate. See `Digitone-E08E-readiness-review.md` for the actual task-command trace, correction and final-package checks. Earlier passing release-after-Stop tests did not cover held Stop.

The tested playback owner now follows the parameter record selected by the actual MIDI consumer. Merely displaying another pattern no longer changes the running arp's settings. Current-owner panel edits still apply during playback.

## Stock ownership findings

Stock distinguishes three bindings:

| Binding | Recovered use |
|---|---|
| UI root's M1 MidiPreset | The pattern currently shown/edited; can rebind before playback does. |
| `0x419c5b10` | Consumed KitActive pointer. Kind-2 descriptors bind their `+4` kit here. |
| `0x419c5b14 + track*4` | Per-track cached parameter source. It can be invalidated independently; it is not the universal pattern owner. |

For an eligible note-on, stock uses the descriptor's explicit parameter pointer at `+0x28`, otherwise the track cache, otherwise the consumed kit's MIDI record (`kit+0x5ce` for M1). `0x400f3750` binds/copies track parameters; `0x400f40ba` and related code apply the queued kit binding and clear the four caches. The captured M1 extension lies at record `+0x9e`, equivalent to raw kit `+0x66c`.

Static code and the unmodified E08C ownership trace agree: the UI can show the receiving record while the stock MIDI consumer still uses the old kit/cache. These are findings for the recovered paths and observed workload, not a lifetime proof for every possible parameter pointer.

## Native guard implementation

- Consuming a valid pattern context establishes its M1 owner. An eligible M1 note-on can establish the explicit/cached/default source that stock actually selects. Releases, other tracks and rejected notes do not take ownership.
- The automatic UI observer publishes only with transport stopped and the held set, active arp and event arena quiescent.
- A panel edit continues through the MIDI-specific accessor and normal stock dirty/save notification. During playback it may publish new settings only if its record matches the captured playback owner. Editing another record can save that record without replacing the running configuration.
- Publication rechecks the current UI handle, data pointer and normalized saved word inside its short interrupt-masked section. Requests carry their owner identity, and the consumer rejects requests from a different owner. A newly consumed context/source supersedes earlier requests.
- Null contexts revoke generation/ownership and clear the held set without prematurely freeing a descriptor still marked busy. Closed admission refuses the new metadata changes.

The two owner identities occupy eight additional bytes in the existing state area: `0x47be4e90` and `0x47be4e94`. Native initialization clears them. State grows from 336 to 344 bytes; the event arena stays at `0x47be4ea0`, with eight alignment bytes remaining before it. The copied payload remains 32,256 bytes. Retained identities are compared, not later dereferenced by the publisher.

## PC execution results

The package was accepted by the modeled stock loader, copied through the actual startup route and run through the restored-project UI. Continuous playback used the packaged helper bytes; helper code/settings were not host-loaded or injected. Peripheral behavior and ISA compatibility still use the disclosed emulator models/adapters.

| Check | Result |
|---|---|
| Strict ColdFire encoding, region overlap and 12 isolated native contract groups | Pass |
| Loader, cold copier, initializer poison/clear and startup-to-UI | Pass |
| A01 → A02 → A01 with a held chord, release and fresh notes | Pass; 41 note-ons and 41 matched note-offs |
| Live gate edits on the active owner before and after handoff | Pass; 35 note-ons and 35 matched note-offs |
| Complete incoming-pattern panel edit before context consumption | Pass in the follow-up native run: edit saved in memory, early publication refused, edited value consumed at handoff; 35 matched note pairs |
| Returning to each pattern after editing | Separate edited values preserved in the in-memory pattern records |
| Native copy/paste/undo and clear/undo | Pass; stock clear preserves MIDI settings rather than resetting them |
| Nine diagnostic/reset refusal entry cases | Pass in stopped native calls with explicit admission fixtures |

During A01 → A02, the UI exposed the receiving record about **124.93 ms** before context consumption. Settings stayed with A01 throughout that interval. A02's first configuration call occurred at **4803.104 ms**, the same modeled time as its context consumption: **zero premature lead**. The return handoff showed the same ordering across a roughly 125.60 ms UI lead. E08C had applied settings about 125 ms early.

Native panel edits changed A01 from UP / 1/32 / 80% to 50%, and subsequently changed the active A02 from UP / 1/8 / 20% to 50%. Switching back preserved each value. Serial output used the actually observed channels 1 and 6, with no unmatched or hanging notes in either test stream.

## Explicit limits and next target

The initially unsuccessful incoming-panel attempt has now been resolved. The custom arp page remained active; reopening it disturbed the route, and the earlier 30 ms observation was shorter than native encoder delivery. Leaving the page open and observing for 80 ms produced the complete native path. At 2119.426 ms the MIDI accessor wrote A02's edited gate value and the stock dirty notification returned. The owner-checked publisher then returned refusal while A01 continued at its existing rate/gate. At 2202.105 ms the actual receiving context read the edited A02 record and applied it, **82.679 ms after the edit**, with no earlier configuration call. A subsequent edit after ownership transferred was accepted. All 35 output notes received matching note-offs. This closes the specific missing PC execution witness; it is not certification of all interleavings or hardware timing. See `Digitone-E08D-complete-panel-race-results.json` and `Digitone-E08D-complete-panel-race-review.md`.

Pointer identity is not a global proof against a record being overwritten/reused at the same address. The next ownership checks should cover same-address pattern replacement and full project save/reload under these new guards, plus an eligible queued old note crossing replacement. M2–M4 are not implemented by this change. Reset-entry refusal tests do not establish arbitrary asynchronous reset or exception cleanup.

Physical RAM/DMA ownership, cache coherence and timing remain unverified for E08. This work does not make the candidate hardware-ready or change the installed firmware.

Evidence: `Digitone-E08D-owner-guard-results.json`, `Digitone-E08D-owner-guard-contracts.json`, `Digitone-E08D-running-pattern-handoff.json`, `Digitone-E08D-live-edit-handoff.json`, `Digitone-E08D-native-copy-clear.json`, and `Digitone-E08D-reset-refusal.json` in this folder. The stock trace is `Digitone-E08D-owner-trace-handoff.json` (that trace ran the unchanged E08C package). Implementation and reproducible drivers are under `work/build-E08D-owner-guards.py`, `work/integrate-E08D-owner-PC.py`, and the `work/test-E08D-*` files.
