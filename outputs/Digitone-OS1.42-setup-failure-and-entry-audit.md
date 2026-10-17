# Digitone OS 1.42: setup failure and initializer entry audit

Firmware remains unchanged. The proposed trailer and startup hook remain unimplemented.

## Outcome

A local terminal continuation is verified: `400f04d0` is an unconditional branch to itself. Stock scheduling-node allocation reaches it after setting SR to `2700`, on an empty free head. Under that interrupt-mask precondition, it prevents normal execution from continuing into pool consumers. It is a halt endpoint, not a graceful setup-failure return, diagnostic screen or verified hardware recovery procedure.

The common pre-mutation guard location is the entry of `400f0504`, before its first pool store at `400f051a`. Guards beside the owner check or allocation call are too late. A guard location has been identified; its live shutdown/quiescence conditions remain unproven.

## Recovered entry routes

| Route | Evidence | Earliest relevant guard boundary |
|---|---|---|
| Normal setup | `4009c7f0 -> 4009bcc6 -> 4009bcb8 -> 400f0504`; direct caller at `4008ca3a` | `4009c7f0` before its state stores, or common initializer entry for pool protection |
| Test-exit setup | `4008aff4 -> 4009c802 -> 4009bcc6`; command text is `#EXIT_TEST_MODE` | `4009c802` before its state clear, or common initializer entry |
| Constructed callback | `400ae45e` tail-calls `4009c802`; its address is loaded at `400aeae4`, stored at `a6-4`, near a call to `400d6ef0` | Same `4009c802` boundary; callback invocation/lifetime not executed |
| Additional test-like setup | `4009bde8 -> 4009bcb8`, followed by synthetic queue construction | Before initialization in `4009bde8`, or common initializer entry |
| Shared wrapper | Sole recovered direct initializer call is `4009bcbc`; wrapper has callers `4009bcec` and `4009bdec` | `4009bcb8` entry covers those recovered routes; `400f0504` entry also protects direct/computed calls entering there |

This inventory establishes concrete routes beyond a single startup call. The test-exit route is identified by actual command text; it is not evidence that an ordinary performance operation invokes setup. The constructed callback is a concrete address escape, not an executed callback dispatch.

The aligned transfer scan found no outside direct transfer into the interior of `400f0504..400f05d6`. This is discovery evidence, not a complete computed-caller proof. One apparent branch to `400ae45e` at `400ae3f6` was rejected: it lies inside the six-byte call instruction starting at `400ae3f2`. Confirmed-entry decoding prevents treating that operand as another caller.

## Why returning failure is currently insufficient

The normal setup caller proceeds from `4009bcec` directly to other initialization calls without testing a pool-setup result. It later installs the audio handler at `4009bd52`. The test-like caller likewise proceeds from `4009bdec` into event allocation and writes without a failure-result check.

Consequently, returning zero from a newly added allocation check is not a verified failure continuation. Both callers would need an audited propagation/abort contract before an ordinary return could be used. Returning early merely because the owner already exists is also unverified: outer setup still performs its other state resets and hardware initialization.

The initializer changes fixed-event links and clears queue state before its owner test at `400f0572`. On an allocation failure, some setup mutation has therefore already happened. A terminal fallback would prevent subsequent use; it would not roll those changes back. A live-reentry rejection must occur before any mutation.

## Terminal endpoint assessment

The confirmed stock node-allocator graph at `400f04c0` saves SR, raises the mask to level 7, loads the node free head and either proceeds or spins at `400f04d0`. A bounded execution with an empty head repeatedly visits the spin, retains SR's upper byte `27` and makes no pool writes. No scheduler calls, logging, allocation or pool accesses occur inside the terminal loop itself.

The assertion handler also reaches a self-loop at `400f09e2`. That loop does not itself disable interrupts, and reaching it through assertion formatting introduces unrelated output operations. It is not a standalone safe shutdown argument.

Thus `400f04d0` is a locally verified non-returning endpoint **only with an established interrupt-mask precondition**. Branching to it alone does not establish that precondition. Calling the entire node allocator is not a substitute: with an available node, that routine returns normally.

No jump to either endpoint has been installed. Interrupt masking does not prove that DMA, peripherals or exceptional execution have stopped. Recovery behavior after such a halt is not established by this audit.

## Remaining shutdown obligation

The normal setup body's recovered local graph contains no explicit SR protection before the initializer. Its conditional preparatory calls do not, from this local graph alone, establish complete shutdown. Their transitive effects and callers' execution context remain outside the proof.

The prior queue/reset execution showed surviving retained templates and cached payload pointers. Any permitted live pool reconstruction therefore requires a stronger lifecycle barrier: stop producers/consumers, resolve every retained owner, finish active pattern writers, disable context capture, reconstruct, then publish completed state. An empty queue or a nonzero owner pointer cannot replace that barrier.

For now, the verified decisions are to retain a common entry guard boundary, reject the assumption of cold-only setup, and avoid a failure return that callers do not check. A graceful failure continuation and a complete live shutdown are not yet verified, so storage/hook implementation remains deferred.

## Validation

21 checks passed. Eleven confirmed-entry local graphs cover 239 instructions. The existing terminal failure branch was executed for a bounded 12-step run. Source SysEx and decoded section 3 hashes remain unchanged.

The interpreter is not independently validated against ColdFire hardware. Full callback dispatch, computed callers, interrupt/task interleaving, transitive shutdown helpers and hardware recovery remain untested.

Next: trace the constructed callback's lifecycle and the test-exit caller's audio/task state, looking for an existing shutdown barrier before setup. In parallel, investigate whether the setup caller can propagate failure without reaching audio installation. The trailer and hook should remain unimplemented during those checks.

Machine-readable evidence: `Digitone-setup-failure-and-entry-audit-results.json`.
