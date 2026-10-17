# Separate PC-only UI defer/refusal overlay

A **150-byte native machine-code overlay** now implements two bounded guards: retained AudioTestMenuView deferral after normal parent entry, and explicit AudioTestMenuView refusal before selected-reference assignment. Sixteen execution controls and eight stock-parity comparisons pass. It is installed only into disposable PC test machines. No firmware container, existing raw MAIN or existing payload is changed.

## Overlay and hooks

Artifact: `work/os144/PC_ONLY-ui-defer-overlay.bin`; manifest: `work/os144/PC_ONLY-ui-defer-overlay.json`. Test address **47fa0000** is a disposable fixture address, not a hardware executable-placement claim. This is not a firmware package or a drop-in Digiemu firmware.

| Guard | Stock hook | Protected behavior | Stock pass-through |
|---|---|---|---|
| Retained child defer | `400e4e42`, 8 displaced bytes | After normal parent callbacks, keep retained +8c, leave selected +84 unchanged and follow native return tail `400e4eae` | Replay MOVE/ADDI and continue at `400e4e4a` |
| Explicit child refusal | `400e47f6`, 6 displaced bytes | Return false through native tail `400e483c` before selected-reference assignment | Replay argument pushes and continue at `400e47fc` |

The guard saves/restores scratch D0/A0. When enabled and supplied a non-null page, it matches both the known 1.44 AudioTestMenuView page vtable `401c4714` and underlying root vtable `401c467c` at page -38. It does not intercept a generic View or null request. These identity checks rely on the stock-owned, readable page/reference conditions in the fixtures; they do not prove arbitrary pointer validity or every runtime alias.

All custom instructions pass the local ColdFire ISA_C and documented MOVE source/destination restrictions. No SR masking, allocator or busy wait is added by the guard itself. Execution follows the guard's emitted conditional branches; the host does not rewrite PC or return values to choose refusal. Boundary observations and ordinary test call setup remain host operations.

## Admission is intentionally a PC test control

Each helper has a compiled MOVEQ live-control constant. The default test overlay uses 1 (protection active); disabled/cold comparisons set both constants to 0 before execution. **This is not an implemented lifecycle latch, a proven cold-start permit or runtime admission storage.** The disabled comparison only proves stock pass-through when the test selects it; it does not prove safe initialization on a device.

No new RAM state word is reserved or certified by this task. The prototype does not include startup installation, relocation/cache handoff, notification UI, diagnostic command rejection or common-initializer protection. It must not be described as persistent V1 enforcement.

## Execution results

Sixteen controls cover retained and explicit routes, each with:

- Active protection and a fully stock-constructed audio page.
- Disabled protection and that same class of page.
- Active protection and an unrelated page made with the actual generic View constructor.
- Empty/null reference behavior.

Every scenario runs with normal and already-recursive manager state. Audio and parent entry records are native-created; the parent uses the actual settings base-constructor prefix. Explicit-selection parents are first bound through their real entry dispatcher so the stock helper has a valid manager pointer.

With protection active, retained audio deferral completes normal parent publication/binding/registry entry, preserves retained ownership and selected state, and prevents the audio entry body. Explicit audio refusal returns false before parent-selected ownership changes. The queued-note state, audio handler, gates and tested pool/context hashes stay unchanged. Register, stack, interrupt-control, reference and mutex checks pass.

With protection disabled, stock audio entry runs and changes the audio handler as in the preceding successful restoration controls. Ordinary View selection/restoration passes through with active protection. Empty retained state follows the stock branch without entering the retained helper; an explicit null request follows the stock helper behavior.

Eight separate paired comparisons run stock and overlay on matching fresh fixture states. Disabled audio paths and active ordinary-page paths match **all compared CPU registers including CCR**, parent/child/control/node/manager state, queued-note/context state and registry. This is bounded parity, not every RAM byte, interrupt ordering, live playback or physical timing certification.

## Remaining before integration

The native local branch behavior is now tested. Remaining implementation requirements are persistent live/cold admission and storage provenance, certified code placement and startup copying/cache handoff, and lifecycle tests for close/re-entry/retained ownership and refusal reporting. Complete settings construction still has the earlier application-dependency gap; the first actual audio-test selection request is also unidentified. Full diagnostic command and common pool-initializer safeguards remain separate.

Next, test close and re-entry of the deferred parent/child using correct outer ownership and real callback dispatch. Then select/validate native admission storage and integrate only into a separately named PC candidate. This overlay provides no new hardware-ready or flashable firmware.

Evidence: `Digitone-E04-PC-ui-defer-overlay-tests.json`, `Digitone-E04-PC-ui-defer-stock-parity.json`, `Digitone-E04-PC-ui-defer-overlay-summary.json`.
Reproduce: `work/build-PC-ui-defer-overlay.py`, `work/test-PC-ui-defer-overlay.py`, `work/test-PC-ui-defer-stock-parity.py`.
