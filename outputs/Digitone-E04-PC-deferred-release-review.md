# Deferred panel-release cleanup and refusal contracts — PC prototype

Firmware and all earlier code artifacts remain unchanged. A separate 750-byte host-loaded overlay at `47fa0c00` adds bounded deferred release handling. It uses a 400-byte fixture queue at `47fa2000` with 32 entries; tests explicitly zero this storage. Physical ownership and packaged/native cold initialization are not established.

## Behavior implemented

The internal release entry `400eabb4` now records track, pitch and source arguments when admission is INITIALIZING, before its stock prologue mutates note storage. Other closed phases deny without recording. Track and note bounds are checked. Entries retain scalar arguments rather than pointers into caller/page objects.

The queue uses the stock per-track/pitch reference count at `419952a8` to cap pending releases for a pitch. Multiple legitimate same-pitch releases remain separate; excess duplicates do not consume capacity. Zero references permit one normal stock cleanup attempt. This is bounded use of the recovered stock counter, not a new global lifetime proof.

The sustain-release predicate `400f0580` returns explicit handled value 1 on refusal, regardless of incoming D0. Other saved scratch registers and full SR are restored. During replay, closed-phase stock processing is admitted only with the drain flag, the recovered `400eabdc` return and IPL7. The original internal release body and stock initializer/reset guards remain in place.

Native completion success at `47fa0044` now dispatches to deferred draining. Under IPL7 it replays accepted records through the stock release routine, clears pending count/drain, and only then publishes LIVE. Completion failure retains its prior FAILED behavior. Overflow or a detected error prevents LIVE. A replay fault can have partial stock effects; it remains closed/latched rather than attempting an unsafe automatic retry or rollback.

## Tested evidence

- 16 refusal controls span four closed states and incoming D0 values including 0. Refusal returns 1 with other registers/SR and monitored original note state intact.
- Isolated controls cover exact duplicates, 32-entry capacity, overflow blocking completion, empty completion, and original failure completion.
- Native panel sessions cover LIVE, blocked new press, a note held before closure, and two distinct held notes. Closed phase is an explicit host fixture; resumption runs the actual patched completion helper. One/two retained counts become zero before LIVE and fresh panel notes then execute normally.
- An isolated same-pitch multiplicity fixture starts with stock count 2: three identical requests record two releases, and native replay clears both reference counters. Two naturally simultaneous same-pitch producers remain to test.
- A native publication control observes the sole LIVE store after count/drain are zero, under IPL7, and verifies full incoming SR restoration.
- A deliberately injected error during replay keeps admission closed and prevents automatic retry. Actual exception cleanup/recovery is not proven.
- Three cold startup cases (default, restored and optional-feature-disabled) reach modeled UI/LIVE with the final overlay. Saved executable pages contain the final code and persistent hooks. Queue initialization is disclosed host setup.
- Static ColdFire ISA/MOVE checks pass. Earlier firmware/recovery hashes remain unchanged.

## Caller audit and limits

The absolute-JSR scan finds the recovered `400eabd6` call to the sustain predicate, followed by a low-byte handled test. Four absolute-JSR candidates call internal release (`4003b2ea`, `400464ba`, `400b5f34`, `400ee35a`); caller fragments clean stack or load other state instead of directly consuming the release result. Internal release also appears as a function-pointer target. These are candidate direct call-site observations, not exhaustive disassembly or proof excluding computed/interior entries.

Returning explicit handled removes the former dependence on incoming D0=127 for the known predicate contract. It does not certify every unknown indirect caller. The scalar queue avoids retaining a page-pointer owner; it still needs initialization, lifetime/epoch, RAM ownership and live-reset policy integration before packaging.

The tested panel gap is resolved in the PC prototype. This is not blanket MIDI/CC64 replay coverage: blocked pedal changes and every input/reset overlap are separate behavior. The current live warm resets remain refused; the closed/resume sessions do not prove a naturally scheduled warm transition. Physical interrupt latency during masked replay, cache coherence and hardware timing remain unvalidated. No hardware-ready build was produced.

Evidence files: `Digitone-E04-PC-deferred-release-controls.json`, `Digitone-E04-PC-deferred-release-panel.json`, `Digitone-E04-PC-deferred-release-multiplicity.json`, `Digitone-E04-PC-deferred-release-failure.json`, `Digitone-E04-PC-deferred-release-publication.json`, `Digitone-E04-PC-deferred-release-startup-startup.json`, and `Digitone-E04-PC-deferred-release-summary.json`.
