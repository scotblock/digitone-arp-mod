# Digitone OS 1.42: persistent context design decision

PC-only design, 3 October 2026. Firmware, startup hooks, allocation requests and event fields remain unchanged. This settles the preferred design for further audit; it does not certify an implementable patch.


Follow-up: the integration audit corrected the PC copy adapter to read accepted-source snapshots when copying retained templates into scheduled events. Generic copies into retained destinations cannot establish acceptance and require a dedicated identity commit. See `Digitone-OS1.42-persistent-context-integration-audit.md`.

## Decision

Use an explicitly reserved, persistent context table appended to the existing payload-pool allocation. Store root/scale values independently for each candidate event, cached template and delayed queue node. Store accepted context separately for each playback track, with its accepted arp identity.

Do not associate snapshots with parameter-payload addresses or reference counts. Do not clear the whole table during ordinary playback reset or setup reentry. This removes the proposed feature's requirement to discard all outstanding snapshots before those transitions. It does not establish that arbitrary stock pool reconstruction is safe, or remove the need to protect individual metadata operations.

This replaces the earlier 16-byte guard-only trailer proposal with a larger layout. Both proposals remain unimplemented.

## Why this option

| Option | Benefit | Remaining cost / reason for decision |
|---|---|---|
| Event bytes +20..+27 and queue note padding | Existing raw copies carry values automatically | Global byte ownership is still unproved; do not use these fields in this design |
| Context indexed by payload +38 | Few storage entries | Cache replay can retain addresses across record recycling in controlled execution; context must not depend on that ownership history |
| Read current pattern at pitch time | Minimal metadata | Changes the agreed snapshot semantics for queued and retained notes |
| Persistent explicit table | Owns extra memory without borrowing stock event bytes; metadata survives independently | Requires explicit propagation at every relevant producer/copy; selected for the next audit |

This decision trades uncertain ownership of existing bytes for a larger, explicit list of integration obligations. It is not proof that table propagation is easier or already complete.

## Concrete allocation and layout

Let P be the existing persistent pool owner at `*(4199d590)`. Keep all 64 stock records and their 0x504 stride unchanged. Explicitly request an additional 2,928 bytes after the 0x14100-byte record area.

| Trailer-relative offset | Entries | Bytes | Purpose |
|---|---:|---:|---|
| 0x000 | Header | 32 | Layout/version/readiness, pattern-writer depth and capture fault; reserved remainder |
| 0x020 | 128 | 512 | Pooled playback event candidate snapshots |
| 0x220 | 512 | 2,048 | Four tracks × 128 held-note template candidates |
| 0xa20 | 4 | 16 | Synth sequencer cache candidates |
| 0xa30 | 64 | 256 | Delayed queue-node candidates |
| 0xb30 | 4 | 64 | Accepted per-track records, 16 bytes each |
| 0xb70 | End | 2,928 total | Exclusive end |

Proposed request: `0x14100 + 0xb70 = 0x14c70` (85,104 bytes). The earlier recovered buddy-order arithmetic rounds this and stock 0x14100 to 0x20000. This is arithmetic, not an actual allocator execution or a promise of unchanged runtime memory usage.

Header and entry addresses derive from P, never from an event's +38 payload pointer. Normal record links and counts exclude the trailer. The allocator request must explicitly include it; undocumented rounding slack is not the ownership contract.

The held-note and cache counts are bounded design assumptions supported by the mapped layouts. The new address resolver checks exact aligned records only. Exhaustive firmware validation of those address classes is still required. Synth cache mapping includes tracks 0..3; MIDI or unknown temporary storage has no context entry and falls back.

## Value format

One aligned 32-bit candidate word:

- Bit 31: valid.
- Bits 0..6: captured root, 0..127.
- Bits 7..12: raw scale plus one, 0..35 (-1/chromatic becomes zero).
- Bits 13..14: original capture track, 0..3.
- Remaining bits: zero.

Zero means no context. All 18,432 supported root/scale/track combinations are unique and nonzero in the specification. Root 0..127 is an encoding capacity, not a change to the firmware setter's narrower normal range.

The immutable capture track is independent of the stock source-track field, which remapping can overwrite. No pattern pointer survives capture. Equal root/scale values need no separate pattern number for quantization.

An accepted record contains a 32-bit identity, candidate word, playback binding and valid/commit state. These fields must be committed/read together under an audited bounded protection protocol. Merely aligning a word does not prove hardware or interrupt atomicity.

## Required lifecycle contract

1. **Cold setup:** allocate the explicit extent, initialize everything locally, and publish readiness only after completion. Null allocation must take a verified failure continuation. Neither the continuation nor the machine-code hook is approved yet.
2. **Capture:** read a coherent source root/scale pair at its established source boundary. For streamed delayed notes, capture the receiving pattern when the descriptor is handled, not at USB arrival or eventual emission. Busy or failed pattern updates prevent new capture; they do not erase older valid snapshots.
3. **Construct/recycle:** every candidate producer explicitly writes a fresh word or zero before publication. Pooled-event allocation invalidates its entry, and reclaim invalidates it while still owning the slot. Queue allocation/rejection/emission/reclaim follows the same rule. This does not invent a queue flush.
4. **Copy:** copy the candidate word alongside the event, including common copies, every relevant raw copy, cache emission and remap. Missing or unrecognized source metadata explicitly clears the destination. Publish neither half of a byte/metadata copy early.
5. **Acceptance:** commit only when an actual new arp identity is accepted. Additive input and rejection preserve the current record. A contextless new identity replaces old context with invalid state.
6. **Pitch:** after proven successful arp selection, use the playback track's accepted context with active-list, type, identity and playback-binding checks. A continuing remapped tick uses its destination's accepted context. Preserve raw allocation/release note identity.
7. **Sustain/release:** keep accepted context through deferred release; an empty active list makes it unusable. Later acceptance commits a new record before output can use it.
8. **Ordinary reset:** reclaim only metadata for actually reclaimed events/nodes. Preserve surviving caches and retained accepted snapshots. Active-list and identity checks control usability; a blanket context clear is unnecessary.
9. **Setup reentry:** preserve the existing layout, guard depth, fault state and snapshots. Do not mark a busy writer complete or reinitialize the trailer because payload free lists were rebuilt. A valid existing owner/layout is reused. Unexpected header/layout state disables context rather than clearing live state speculatively.

No runtime generation counter is claimed to solve missed lifecycle hooks. If an allocator/reuse producer is missed, pointer-indexed metadata can become stale. Complete hook coverage and protected ordering are mandatory. Arp identity wrap and stale ticks remain separate integration questions; an identity match alone does not provide timeless freshness.

## What the PC checks establish

The specification passed 26 checks: nonoverlapping layout; arithmetic extent/rounding; exact resolver mapping and rejection of interior/unknown addresses; independent snapshots across cache refresh and queue reuse; explicit event invalidation; busy/fault capture fallback; additive/rejected and contextless replacement handling; destination context for remapped ticks; reset/reentry preservation; sustain/empty-list gating; missing-source fallback; and all 18,432 candidate values.

The reset/reentry operations are proposed metadata behavior, not execution of the stock transition or proof it preserves every firmware invariant. The model receives coherent capture inputs and accepted identity outcomes; it does not prove writer coverage, real arp setup, concurrency, allocator behavior, instruction hooks or hardware behavior. The two previously decoded firmware images were not changed.

Machine-readable results: `Digitone-persistent-sidecar-design-results.json`.

## Step 2: focused integration audit

Audit the exact event-copy and construction graph against this table: pool allocation/free, held builder and all three selected-cache copy sites, synth sequencer construction/cache emission, queue enqueue/emit/reclaim, remap clone, retained acceptance and scheduled ticks. For each edge, establish the source/destination address class, last context write and publication boundary. Any unknown storage class must produce explicit stock-pitch fallback until supported.

In parallel within that audit, retain the separate coherent-capture obligation: writer-depth entry/exit coverage and fail-closed behavior around complete pattern updates. Persistent snapshots remove the blanket-reset requirement; they do not make partially updated pattern fields safe to capture.

Only after this graph and cold initialization/failure integration are established should we consider a PC prototype combining real firmware control flow with the proposed metadata operations. No flashable build is warranted by step 1.
