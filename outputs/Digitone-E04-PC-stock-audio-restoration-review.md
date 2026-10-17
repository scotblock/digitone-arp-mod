# Restoration with a stock-constructed AudioTestMenuView

Both native PC restoration controls complete through rendering, the actual registered audio-test entry callback and caller cleanup, using uncontended and recursive manager locks. The earlier synthetic-renderer gap is resolved for this path. Firmware containers and the current raw PC candidate are unchanged (hash checked); no guard or boot latch is installed.

## What executes

The control first uses the initialized stock application state for allocation and construction, before substituting the test parent/manager fixture:

1. Stock allocator `400e96c0` allocates the real 0x248-byte audio object, at `419f20a0` in these runs.
2. Full constructor **400b2b5e** completes. Root/page vtables are `401c467c`/`401c4714`, name is the actual "AudioTestMenuView" string, renderer/menu state and entry/exit callback records come from the constructor. No replacement renderer, callback record or allocator result is supplied.
3. Stock settings-style wrapper **400e43fc** creates its real owning control block and registers clear closure **400e4848** on this actual child. This matches the wrapper used by the settings constructor; the control block is not a fabricated shared-reference structure.
4. The test chooses initial selected ownership through actual assignment `401774c0`. This initial choice is a host-supplied condition, not a recovered user selection request.
5. Stock parent close **400e4ec2** saves the selected reference to retained +8c and requests child/parent close. The saved reference is thus guest-produced.
6. The control invokes **the actual constructor/wrapper-registered clear target using its real callable record**, clearing selected +84. It does not run the rest of the diagnostic exit callback list, which includes setup/reinitialization. Full page removal/exit dispatch remains outside this test.
7. Full parent restoration **400e4e1e** transfers retained +8c to selected +84, invokes the actual page manager directly, executes selection/list publication and rendering, reaches registered entry **400b25bc -> 400e7e7e**, then completes all local cleanup and returns.

Constructor/helper calls explicitly check return PC and stack; restoration checks saved registers, stack and incoming interrupt control. The child and heap/control/callback state are native-produced. The outer parent, manager/list, current-task identity and initial selection are constructed PC conditions. Parent entry callbacks are empty in this fixture; this does not certify the complete actual settings-parent transition.

## Observed result

In both manager-lock states:

- Retained +8c is consumed and selected +84 points to the restored actual audio page.
- A real manager node is allocated/published, and the child is bound to the manager.
- The shared selection helper **400e47e6 is never entered**. Restoration bypasses it as predicted.
- The actual audio-entry body runs once and changes audio vector **400002fc from 4009d120 to 400e7b32**.
- Watched receive/note gates, diagnostic flag, queued notes, pending/descriptor state and tested pool/context hashes remain unchanged through restoration/entry.
- Temporary reference accounting balances to the wrapper owner, selected owner and manager-node owner (strong count 3). Normal mutex ownership is released; an existing recursive owner and recursion state are restored.

The entry callback address appears twice in raw trace because the test pauses at that boundary and resumes from the same instruction. A separate entry-body hook verifies one execution. Raw allocator-entry observations can include lazy-map retries; they are not asserted as an exact allocation count or timing measurement.

## What this closes

The earlier probe's fault at `400e4fcc` came from incomplete synthetic menu/renderer state. Using the actual constructor allows the same restore route to complete without a rendering substitute. We now have a concrete conditional native path from retained child ownership to the real audio-test handler change.

This strengthens the protection requirement: a guard only in shared explicit-selection helper 400e47e6 would miss this route. A refusal only after the parent has transferred retained ownership also leaves the parent changed, as shown by the preceding negative controls.

## Limits and next step

This does not identify the first actual input or application request that selects the audio-test page. It does not execute complete page exit/reinitialization dispatch, normal settings-parent construction/entry callbacks, interrupt interleavings or on-device startup. The test neither certifies RAM ownership/physical timing/cache coherence nor establishes hardware readiness.

Next, test refusal of retained audio restoration **before reference transfer**, using this stock-constructed child, and establish how that refusal interacts with the actual parent entry callbacks. Treat it as a consistent deferred-child transaction or find an earlier whole-parent admission boundary; do not assume the void entry handler can propagate false to its outer caller. Native enforcement remains unimplemented.

Evidence: `Digitone-E04-PC-stock-audio-restoration.json`, `Digitone-E04-PC-stock-audio-restoration-summary.json`.
Reproduce: `work/test-PC-stock-audio-restoration.py`.
