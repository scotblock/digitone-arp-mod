# Digitone OS 1.42: complete live Note On and mode-entry transition audit

Firmware remains unchanged. The proposed context trailer and startup/reset hook remain unimplemented.

## Finding

Complete **nonzero-velocity live Note On** execution is now verified for the tested synth-track route, rather than stopping at handler admission. The outer mode-entry routine is also executed through its return, including its mutex, list insertion, maintenance, virtual entry, both constructor-registered entry callbacks and unlock.

On the controlled PC state, the actual transition accepts a page while a scheduler event, counted template and cached payload pointer are live. It preserves those owners and both MIDI gates. The actual receive-task continuation subsequently runs the full accepted Note On path and publishes a new event. Thus this recovered transition path cannot itself be used as proof that input production and ownership have stopped.

This is a bounded firmware execution result, not an observed device transition or a stock-device fault report. The complete hardware preconditions remain uncertified.

## Two gaps closed

The previous receive check stopped at `400dc8c4`. The handler has a second gate at `400dc8d0`, reading `4131ba40`; a zero value returns without producing a note. The first receive queue separately tests bit 1 of `4131ba1c`. Both gates are now exercised. With either relevant gate disabled, the corresponding dispatch/production is bypassed. With both enabled, execution returns to the receive loop after publication.

The parent-adjustment thunk at `400d65d4` uses `MOVEQ #$c8`. MOVEQ sign-extends this byte: it is **-56**, so the thunk subtracts `0x38` from the page interface pointer. It does not add 200. Execution now follows the actual virtual chain:

`400d7a6e -> virtual +18 -> 400d6944 -> virtual +14 -> 400d65d4 -> 400d653a -> 400d6d46`.

Constructor inspection revealed another required callback. Base constructor `400d59dc` registers `400d5eca`; derived constructor `400ae9fa` then registers `400ae458`. Both are included, in that order. The base callback appends the page to a supplied existing UI object with available vector capacity; the mode callback installs the alternate audio/timer vectors. The base constructor also explicitly clears the optional child handle at parent `+8c`, supporting the no-child branch tested here. Later writes to that handle are not exhaustively certified.

## Complete handler execution

The accepted route executes stock instructions through:

- Channel routing and active-pattern lookup.
- Single-note expansion and note registry allocation/linking.
- Press counters and descriptor construction.
- Synth-track predicates and, for selected step zero, payload allocation and all 79 parameter entries.
- Actual cache construction, event allocation, event copying and scheduler publication.
- Timing metadata, input notification copying, kernel queue insertion and its semaphore signal with no waiting task.
- Normal handler return with stack, preserved registers and interrupt-mask restoration.

The tested packet is channel 0, note 60, velocity 100, assigned synth track 0, single-note expansion, receive flags 8. Its flags and arguments come from the actual first receive queue's dispatch instructions. The selected-step cases are -1 (no parameter payload) and 0 (allocated parameter payload). The complete Note On wrapper, router and producer execute; ownership helpers and notification helpers are not replaced by modeled outcomes.

An exhausted-event case uses all 128 actual event allocations before receiving the note. The full handler still returns and sends the input notification, while the actual builder retains a payload pointer in its cache and publishes no scheduler event. This is another reason queue emptiness alone cannot certify safe storage lifetime.

Not all handler branches are covered: velocity-zero Note Off, auto-channel held-note replacement, chord expansion, external tracks, different arp selectors, notification waiters and concurrent execution remain outside these new tests.

## Transition preconditions established locally

The tested outer entry uses an initialized empty page list, an unattached non-null page, empty dependency vector, both entry callbacks, no optional child page, available UI-vector capacity and an existing UI context taking the no-pending-work branch. Current-task state is supplied. Actual mutex instructions cover both uncontended and recursive ownership.

The actual routine rejects a null page or an already-attached page; both rejection paths return and restore the mutex/mask. On accepted paths, it inserts the page before invoking virtual entry and returns with the expected manager association. A preexisting counted template plus queued event retain two references through the entire accepted transition; a cached pointer and the scheduler queue also survive. Neither input gate is cleared.

Heap allocator results are supplied only at explicit UI boundaries: a 16-byte page-list node and one-byte callable copies. Callable destruction is handled at its corresponding heap boundary. These are not payload, event or scheduler-node allocation substitutes. All ownership-related pool and publication instructions are executed from the unchanged image.

## What is still unproven

This closes full execution of the selected handler and outer-entry branches. It does **not** prove that an actual device reaches them with our supplied gates, pattern pointers, owners, page list and UI context. There is no hardware RAM capture or interrupt/task interleaving in this audit. The higher application request path may impose additional conditions. Writers of the two input gates may use object offsets or computed addresses; exact literal reads do not certify their complete writer provenance.

Consequently, there is still no certified global shutdown barrier for rebuilding the proposed storage. Other pages, pending UI work, child pages, contended locks, interrupts, exception cleanup and DMA/peripherals are not generally proven quiescent.

The next focused target is the application path selecting this constructed mode page and the writer provenance of `4131ba1c` and `4131ba40`: determine whether it supplies an earlier input-stop/ownership barrier before calling the now-tested outer transition. Keep the trailer and startup/reset hook unimplemented until that contract is established.

## Validation and evidence

**89 checks passed:** 83 execution checks across 12 recorded cases (12,437 recorded stock instruction steps), plus six structural checks across 12 function graphs (755 instructions). Counts exclude setup instructions outside recorded case paths and supplied heap-boundary operations.

Detailed evidence:

- `Digitone-full-handler-transition-execution-results.json`
- `Digitone-outer-mode-entry-complete-results.json`
- `Digitone-receive-full-handler-results.json`
- `Digitone-full-handler-transition-graphs.json`

Original SysEx SHA256: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`.

Decoded section SHA256: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.

Both hashes were checked and remain unchanged. No firmware patch, trailer, startup hook, repackaged SysEx or flashable image was produced.
