# Digitone OS 1.42: actual identity and accepted-context commit audit

Read-only execution and PC observer checks, 3 October 2026. No firmware patch, allocation extension, startup hook or flashable image was produced.

## Concrete gaps narrowed

Actual arp setup and its retained-copy caller now execute in the bounded ColdFire interpreter. The outcomes are no longer supplied by the behavior model for these cases. The new suite passes **53 checks across 14 cases, executing 3,136 stock instructions**.

Two findings materially change the prior discussion:

1. **The actual counter skips zero on wrap: ffffffff → 1.** The earlier PC prototype's conservative zero-context wrap handling was not an accurate stock identity model. It has been corrected.
2. **Ordinary arp reset does not reset these counters.** All four counters survive executed reset 4009713c, and the next accepted setup advances the existing value. Repetition after every ordinary reset is not supported by this route.

New accepted setup, additive input, lower-priority rejection, settings replacement, disabled mode, ordinary reset and per-track independence have actual instruction-execution evidence under the stated inputs. A protected metadata commit remains a proposed addition; the observer does not execute hook machine code.

## Actual identity behavior

The setup routine creates an identity only after an empty note list is seeded. At 400972f0..400972fa, it records that a list was newly populated. The test at 400973c8 selects the state initialization and identity increment.

At 40097414..40097422:

- Load the previous 32-bit identity.
- Increment it.
- If the increment is nonzero, store it.
- If it would be zero, add two to the previous value and store one.

The returned identity is then loaded from the track state. Controlled execution verifies 0 → 1, 1 → 2, fffffffe → ffffffff and ffffffff → 1.

Each track has its own state at `41344530 + 40*track`; the identity is +18. All four independent first acceptances return one. This normal cross-track coincidence is why a remapped tick can select another track's accepted arp and must use the destination context.

Additive setup returns zero, preserves the accepted identity/settings/priority and adds its note. Lower-priority rejection returns zero without adding the rejected note. A settings-pointer replacement clears prior notes and creates the next identity.

Executed reset 4009713c clears lists and bitmaps but preserves all four identities. A subsequent setup advances rather than restarting at one. These results establish this reset route, not every possible indirect writer or full startup transition. Cold whole-RAM initialization is a separate lifetime.

## Freshness decision

The evidence no longer justifies treating ordinary resets as an immediate identity-reuse problem. A single track's nonzero sequence repeats after 4,294,967,295 accepted new identities. Additive notes and rejected setup do not advance it.

A stale tick surviving that complete sequence could still coincide; the PC negative control continues to demonstrate that identity alone cannot distinguish it. No evidence here shows a queued tick survives such a cycle on hardware, and no complete queue-age bound has been established. We therefore keep this as an explicit bounded-lifetime assumption for the experimental design, rather than claiming mathematical freshness or adding an unverified generation scheme now.

This is a scope decision, not proof that every reset preserves identity or that counter reuse is impossible. If a different reachable writer resets a live counter, or a queue can retain ticks across its reset lifetime, the decision must be revisited. The new execution results narrow the concern substantially.

## Actual retained-copy caller

The tested caller starts at 4009dd80, calls real setup at 4009dda6, and follows the actual branch after its return.

| Setup case | Actual result | Retained-copy behavior |
|---|---|---|
| Empty list, enabled arp | Nonzero new identity | Writes incoming +40, sets arp flag and calls 400f0690 at 4009de40 |
| Same settings/priority, additive note | Zero | Skips retained copy |
| Active higher priority rejects input | Zero | Skips retained copy |
| Changed settings | Next nonzero identity | Replaces retained template through the common helper |
| Arp disabled | Zero | Skips retained copy |

For accepted cases, execution reaches 4009de46 after the real 72-byte retained copy. The copied template and incoming event both contain the returned identity. At that exact mid-function boundary, the two copy arguments are still on the stack: SP is eight bytes below its entry value. A hook must account for them; this is not a function return boundary.

Additive/rejected/disabled cases are followed to 4009df0a. They do not enter the common retained-copy helper and have no reason to overwrite accepted context.

The tests supply an empty voice-stop mask, mode one and a single note without duration scheduling. They do not execute the full note consumer/audio interrupt or all setup modes.

## Concrete commit protocol

The accepted context already has a 16-byte record in the proposed trailer. Its final status/binding word can encode both playback binding and an unavailable/busy bit; no extra global reservation is needed for this proposal.

1. Enter a per-track unavailable state before actual setup begins at 4009719e. Use a short protected state-word update and preserve the caller's prior interrupt state. This begins before note-list, settings and identity mutations.
2. Keep existing accepted identity/context bytes intact while unavailable. A pitch reader declines quantization during this interval; it does not wait or acquire a different pattern's context.
3. When setup returns zero, restore availability for the prior record after setup finishes. The normal active-list and identity guards still apply. Additive/rejected/disabled input does not invent a new commit.
4. When setup returns nonzero, keep unavailable state through the caller's retained-template copy. At 4009de46, update accepted identity, snapshot word and playback binding, then publish availability last. A missing candidate commits invalid context rather than inheriting an old scale.
5. Never treat a generic copy to a retained address as acceptance. The dedicated accepted caller authorizes this operation; scheduled retained-to-event copies only propagate the existing snapshot.

The per-track gate is distinct from the pattern-writer depth that controls coherent **new capture**. An unrelated busy pattern update should not erase a completed accepted record.

The external observer offers a read at each executed instruction between setup entry and retained-copy completion. With the proposed unavailable gate, no intermediate accepted context is exposed. Separate specification checks interrupt between the proposed identity, snapshot and binding stores; the gate remains unavailable until the final publication.

Those checks validate protocol ordering only. The busy-bit update, save/restore instructions, branch relocation and scratch-register/stack use have not been implemented or executed. Normal setup returns are verified; actual abnormal-exit cleanup is not. An interrupted or failed commit must remain unavailable rather than expose a partial record.

## Prototype correction

The combined PC prototype now mirrors the actual zero-skipping identity increment. Its wrap test expects identity one with the newly accepted snapshot. The synthetic repeated-identity test still intentionally demonstrates the unresolved historical alias; it does not claim ordinary reset creates that alias.

All existing combined checks pass again: 20 scenarios, 75 assertions, 18,432 encoding cases, 55,296 combined pitch comparisons and 3,000 mixed sequences. The downloadable prototype ZIP has been refreshed with the corrected code and report.

## Remaining concrete implementation work

The accepted-return/copy boundary is now supported by actual execution. The next engineering work is to turn this protocol into a reviewable hook layout and close cold storage initialization/failure handling:

- Fit per-track unavailable/binding flags into the accepted record and audit the exact reader/writer operations.
- Specify preserved registers, pending stack arguments and all normal exits at each chosen hook.
- Establish how the enlarged explicit allocation is initialized and becomes ready, while existing-owner reentry preserves the table. Do not merely return zero on allocation failure: recovered callers currently continue into audio setup without checking it.
- Complete known producer/copy hook coverage and coherent capture guards before creating a working firmware patch.

These are implementation obligations with named boundaries. This audit is not a requirement to prove every conceivable hardware behavior before an eventual controlled test.

Evidence: `Digitone-actual-identity-and-accepted-commit-results.json`. Decoded image SHA-256 remains `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.
