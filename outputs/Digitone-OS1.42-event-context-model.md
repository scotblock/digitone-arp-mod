# PC-only event context model: results

**Subsequent firmware-audit correction:** cached synth events use type 1 as well as type 0. The harness now admits both. Continuing remapped arp ticks bypass destination setup, so its strict incoming-event context guard loses coverage on those ticks. That guard remains in the harness to reproduce the gap; it is not a complete integration design. See `Digitone-OS1.42-producer-copy-remap-verification.md` for the corrected proposal and outstanding proofs.

The proposed eight-byte context encoding passed **15 lifecycle scenarios**, **92,160 encoding round trips**, and **64 single-bit corruption checks**. These are PC specification tests, not firmware execution or proof that the candidate event bytes are safe to modify.

The model deliberately demonstrates an unsafe reuse case: the stock-style allocator leaves a previous context tag intact. Explicit producer initialization fixes the modeled problem. A checksum cannot establish ownership or freshness.

## Encoding under test

The model stores proposed metadata in event bytes `+20..+27`; no firmware or binary output is written.

| Event offset | Proposed content |
|---|---|
| `+20..+22` | ASCII `SLC` marker |
| `+23` | Encoding version 1 |
| `+24` | Captured root, 0..127 |
| `+25` | Raw firmware scale plus one, 0..35; zero represents raw -1/chromatic |
| `+26` | Source track in bits 0..1; bound playback track in bits 2..3; accepted-context flag in bit 7; bits 4..6 reserved and zero |
| `+27` | CRC-8 over the preceding seven bytes, polynomial `0x07`, initial value zero |

Before acceptance, metadata contains the source track and no playback binding. When a new arp identity is accepted, the retained copy receives its destination-track binding. This distinction fits inside the same eight bytes.

The root and scale are values copied from the source, rather than pointers to mutable pattern storage. The encoding does not carry a pattern number: equal root/scale values have equal musical behavior, regardless of pattern identity. Pattern names in the earlier behavioral model remain diagnostic labels only.

All 128 roots, 36 scale values, four source tracks, and five binding states—unbound or bound to one of four tracks—round-trip correctly: `128 × 36 × 4 × 5 = 92,160`.

## Lifecycle rules tested

1. Every synth-note producer writes new context or explicitly invalidates it. Updating a persistent held-note template follows the same rule.
2. Type-two events retain their transpose-pointer interpretation. Context decoding is allowed only for synth events of type zero or one.
3. Event allocation invalidates old context in the proposed model; the producer independently initializes it. The stock-style allocation variant intentionally omits this additional invalidation to expose stale metadata.
4. Full 72-byte copies preserve context, both for the shared helper's byte-copy behavior and for direct copies. Copies own independent byte buffers.
5. Only accepted **new identities** update the retained context and binding. Additive notes and lower-priority rejection leave it unchanged.
6. A replacement with missing/invalid context cannot inherit the old scale. Output falls back to the stock coarse pitch calculation.
7. Pitch context requires the arp flag, type zero or one, supported playback track, valid encoding, source-field agreement, matching identity, matching retained context, active note list, and matching accepted playback binding.
8. Releasing the last note or resetting a track makes old context unusable. Freed/reused pool handles are rejected by the PC harness.

The host harness's generation counter is a test mechanism for identifying stale handles. It does not assume a generation field exists in the firmware event.

## Cases and findings

| Scenario | Result |
|---|---|
| All supported encodings and invalid input boundaries | Passed |
| Bit corruption, invalid decoded fields, unsupported version | Passed |
| Type-two pointer event recycled into a synth-note event | Passed |
| Cached type-one synth event and independent snapshot copy | Passed |
| Cached type-one synth event and independent snapshot copy | Passed |
| Old context surviving stock-style allocation | Unsafe case reproduced; explicit initialization fixes it |
| Union bytes resembling a valid context | Type gate rejects them; changing type without initialization remains unsafe |
| Shared-helper/direct-copy byte semantics and independent snapshots | Passed |
| Queued source retained across pattern change; additive/rejected setup | Passed |
| Replacement identity, stale ticks, missing replacement context | Passed |
| Held-template refresh, selection, and older copied events | Passed |
| Single track remap and nested source-field changes | Passed, with fallback for nested mismatch |
| Coinciding arp identities on different playback tracks | Rejected by explicit playback binding |
| Type, track, flags, source, identity, retained context, release/reset gates | Passed |
| Allocation-note preservation, transpose bounds, negative sentinels, full-width overflow | Passed |
| Pool exhaustion and reclamation | Passed |

### Two requirements exposed by testing

**Initialization cannot be replaced by a tag.** A recycled type-zero event may still contain an intact old tag and CRC. Even bytes occupied by another union variant can be made to resemble the encoding. The tag detects format errors, not provenance.

**Identity matching needs playback-track binding.** Arp identities are per track and can coincide. A copied arp event remapped to another track could otherwise match that track's identity and scale by coincidence. The proposed binding rejects a copied accepted context until destination setup creates and binds a new retained context.

### Remap policy

For a single observed-style remap, the event keeps its original captured source scale while playback targets the destination track. Destination settings control setup, and acceptance binds context to that destination.

A second observed-style remap rewrites `event+3c` with the intermediate playback track. If that no longer agrees with the captured source, this model deliberately disables scale locking for that event. It does not invent a new source scale or silently alter the traced remap behavior. Whether nested remaps actually occur in the relevant firmware routes remains to be traced.

## Pitch and scope

The model preserves the note byte used by stock voice allocation. Snapping changes only the calculated coarse output after transpose. Negative arp values remain sentinels, and a proposed guard rejects full-width results above 127 before byte narrowing, including 256 and 274. This guard is a proposed behavior change, not stock behavior.

Octave offset, expressive pitch bend, glide, payload reference counts, interrupt interleaving, actual queue scheduling, and firmware identity wrap are outside this new model. The prior sustain/behavior model remains separate and its ten scenarios and 4,608 quantization cases were rerun successfully. The new harness imports its musical snapping and setup/lifetime behavior; it does not emulate the ColdFire CPU.

## Files and reproduction

- `digitone_event_context_model.py`: new standalone PC harness; standard library only.
- `Digitone-event-context-model-results.json`: results of the successful run.
- `digitone_behavior_model.py`: earlier behavioral model, required alongside the new harness.
- `Digitone-OS1.42-scale-map.json`: extracted musical scale mapping, also required alongside it.

Run `python digitone_event_context_model.py` from any directory with Python 3.10 or newer; it locates the scale JSON beside itself and prints the results. It reads no firmware, communicates with no device, and produces no flashable file.

## Next step

Return to static tracing with these concrete requirements: prove that every relevant type-zero producer initializes context, that no type-zero consumer owns `+20..+27`, and that remap ordering allows playback binding only after accepted destination setup. Check pool-reset and persistent-template initialization routes, then analyze atomicity and identity wrap. This model provides a reviewable storage contract; it does not close those firmware ownership questions.

Original SysEx and decoded executable hashes remain unchanged.
