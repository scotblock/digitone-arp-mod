# Digitone OS 1.42: hook layout and initialization plan

Read-only planning and isolated machine-code fixture tests, 3 October 2026. Firmware is unchanged. Synthetic executable addresses beginning at 50000000 belong only to the PC harness; they are not available or reserved Digitone code space.

## Outcome

There is now a concrete calling-convention layout for setup gating and accepted-context commit, plus a cold initialization sequence that prepares owned storage before the stock initializer mutates its pools.

- **25 machine-code fixture checks** passed: actual setup wrapped by synthetic before/after stubs, register/SR preservation, original argument offsets and displaced-instruction replay.
- **14 initialization checks** passed: proposed preallocation combined with actual stock clear/linking, preserved table on existing-owner reentry, null preflight rejection and a synthetic non-returning failure endpoint.

The fixture helpers are deliberate register/SR clobber stubs; metadata effects and preallocation decisions are Python observer operations. This is not execution of completed firmware hook helpers. Final executable placement and the full initialization helper remain unimplemented.

## Accepted record layout

Keep each 16-byte accepted record at trailer +b30 +16*track:

| Record offset | Proposed field |
|---|---|
| +00 | Accepted 32-bit arp identity |
| +04 | Packed root/scale/source snapshot, zero for no context |
| +08 | Per-track setup/commit depth or unavailable state |
| +0c | Publication validity, fault flags and playback binding |

The reader requires published validity, zero depth, supported binding, matching active stock/retained identities and the earlier synth/selection gates. Missing context preserves ordinary coarse pitch. Overflow handling remains the separately chosen policy.

Use short protected metadata updates that restore the caller's prior SR. Do not clear a busy state speculatively on reentry or failure. Nested same-track setup/commit must remain unavailable until balanced; unsupported nesting or overflow should latch unavailability. Detailed nested hook behavior is not implemented by the fixtures.

## Machine-code boundaries

| Boundary | Existing bytes/instructions | Proposed shape | Continuation |
|---|---|---|---|
| Setup call, 4009dda6 | Six-byte absolute JSR 4009719e | Replace call target with a gating wrapper | Original return at 4009ddac |
| Accepted commit, 4009de46 | Four-byte track load followed by six-byte absolute LEA | Ten-byte displaced window; jump to commit wrapper, preserve/replay both instructions | 4009de50 |
| Common initializer entry, 400f0504 | Push d3, push d2, absolute LEA: ten bytes | Preflight trampoline before first stock pool mutation; replay all ten displaced bytes | 400f050e |
| Initializer completion, 400f05d0 | Pop d2, pop d3, RTS: six bytes | Completion wrapper publishes cold readiness, then replays original epilogue | Original caller return |

These are proposed instruction windows, not edited bytes. Entry/exit placement requires final branch-target coverage, relocation and executable storage validation. The common initializer entry covers recovered wrapper calls and avoids placing the guard after the first pool mutation at 400f051a.

### Setup wrapper: avoid an extra argument displacement

A naive wrapper that calls setup with an extra JSR shifts the arguments by four bytes. The tested layout instead:

1. Saves registers and SR in a private scratch frame.
2. Runs the before-setup metadata operation and restores the entry state.
3. Replaces the existing stack return address with the after-setup stub address.
4. Jumps to actual setup without adding a return frame.
5. Actual setup returns to the after stub with its real result in d0.
6. The after stub preserves that result while closing the gate for zero return or retaining unavailability for new acceptance, then jumps to 4009ddac.

The continuation is specific to the chosen caller. A generic wrapper cannot substitute this fixed continuation for arbitrary callers. Applying a gate at the common setup entry would require a separately designed return-continuation contract.

The fixture uses a 64-byte scratch frame: 60 bytes for d0–d7/a0–a6 and a saved SR word at +60. Before-setup helper entry sees the original track at helper SP+72; after-setup helper entry sees it at SP+68 because the actual setup return has consumed its return address. Those offsets were exercised with actual setup.

SR restoration uses a data register followed by MOVEM restoration. No unsupported memory-to-SR form is assumed. The helper deliberately clobbers d0/d1/a0/a1 and SR; the wrapper restores the tested state.

This frame is a fixture design, not a certified hardware stack budget. Helper nesting, interrupt frames and final stack bounds still require accounting.

### Commit wrapper and pending arguments

At 4009de46 the retained copy has completed, but its two arguments remain on the stack. The wrapper must preserve those eight bytes.

The tested commit fixture saves/restores the scratch frame, then replays:

```
move.l  8(a3), d0
lea     41345ef8, a0
```

It continues at 4009de50 with the same register and condition-code effects as those displaced instructions. Other registers and the pending arguments remain intact. The actual metadata commit helper is not part of this fixture.

Commit only if current stock identity and copied retained identity still agree with the new setup result. Write identity/snapshot/binding while unavailable; publish validity last. A failed consistency check must leave context unavailable rather than commit a mixed record.

## Cold initialization before mutation

The proposed wrapper handles the supported geometry (158 payload entries, stride 504, 64 records) before allowing the original initializer to run:

1. Validate supported geometry and ownership state before stock mutation.
2. If owner is zero, request **14c70 bytes**: stock record area 14100 plus explicitly reserved trailer b70.
3. Reject a null allocator return before any stock pool initialization or clear through that address.
4. Clear the complete extended block through stock memset, using the returned pointer locally.
5. Initialize trailer layout/version/extent with readiness zero.
6. Publish the prepared owner pointer.
7. Let actual stock initializer execute. Because the owner is nonzero, it skips its cold allocation and links the original record, event and scheduler-node pools.
8. At successful initializer completion, publish cold readiness. Later capture/playback hooks may then use the table.

The PC test supplies the allocator return, then executes actual full memset and stock linking. It verifies exactly 64 ordinary payload records, unchanged fixed event/node heads, initialized metadata and a preserved header. The allocator itself is not executed.

The original and extended requests have the same previously calculated 20000 buddy rounding. This is not justification to borrow slack: the larger extent must be explicitly requested.

The cold preflight has more stack/local requirements than the 64-byte gating fixture. It needs its own frame and calling-convention test; the exact implementation is not supplied by reusing the gating fixture unchanged.

## Existing owner / reentry

For an owner created by this firmware layout, validate the header and extent, preserve the complete trailer and let the stock initializer follow its existing-owner route. A busy pattern writer, accepted setup gate, fault latch or retained snapshot must not be cleared by that operation.

Actual existing-owner stock linking preserved all b70 trailer bytes in tests, including a nonzero depth and accepted snapshot. This establishes physical trailer preservation, not the safety of rebuilding stock pools with live owners.

An owner whose allocation provenance or header/layout is unknown cannot be assumed extended. Do not initialize beyond its established allocation or silently convert it. The preflight needs a deliberate rejection/feature-disable contract before mutation; merely recognizing a nonzero pointer is insufficient.

## Failure handling

Recovered setup callers do not test an initializer failure return. Returning zero would permit subsequent setup and audio-vector installation. It is therefore not the proposed failure path.

The reviewed local failure endpoint is:

```
move.w  #2700, sr
spin:   bra spin
```

The six-byte synthetic fixture was executed for a bounded run: it masks CPU interrupts and never returns, without pool stores. Null preflight rejected initialization before the stock initializer was called, leaving the owner and fixed pool state unchanged in the model.

This is a terminal startup failure, not graceful rollback or recovery. It does not establish DMA/peripheral shutdown, exceptional execution behavior, device recovery, or live-reentry safety. Final integration must restrict its use to the audited preflight scope and document how a user recovers from a failed boot. No halt instruction has been installed.

A graceful alternative would require auditing and modifying outer callers to propagate failure before later setup. That larger caller change remains an alternative, not something the current return convention already supports.

## What is concrete now, and what comes next

The callframe problem, commit displacement window and successful preallocated-linking sequence now have executable evidence. The next work is:

1. Establish an owned executable location; synthetic fixture addresses cannot be used in firmware.
2. Implement/test actual RAM helper operations in isolated fixtures, including per-track gate publication and cold preflight locals/failure paths.
3. Complete supported producer/copy and coherent pattern-capture hooks against the reference prototype.
4. Verify container integrity and an unchanged round trip before any eventual experimental image.

This plan keeps the original firmware unchanged while making the eventual patch layout reviewable. It is not a statement that an experimental image is ready to install.

Evidence: `Digitone-hook-frame-fixture-results.json` and `Digitone-preallocated-initialization-layout-results.json`.
