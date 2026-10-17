# Digitone / Digitone Keys OS 1.42 — computed pointers and bulk writes

Read-only investigation, 3 October 2026. Candidate marker: **`4199d510 .. 4199d517`**. Firmware and decoded section 3 retain their original hashes; nothing has been patched, rebuilt or sent to hardware.

**Result:** the recovered queue aliases, several nearby computed writers and specific bulk destinations are now bounded. Startup clearing definitely overwrites the candidate. No additional marker overlap was established in the bounded runtime paths. Global ownership remains uncertified because other indirect destinations, wrapper callers and global index ownership have not been completely proved.

## 1. Follow the actual end-record pointer

The constructor establishes `S = 4199d50c` and writes it to global end pointer `431dc4c0` at `400efc7a`. The proposed marker begins at `S+4`.

All six recovered literal uses of that global are accounted for:

| Instruction | Pointer flow and effect |
|---|---|
| `400efc7a` | Store fixed `S` into end-pointer global |
| `400efed6` | Load `S` into `a3`, then load its last-node link; append writes that node's `+0` link at `400efede` |
| `400efee0` | Reload `S`; store the new last-node link to `S+0` at `400efee6` |
| `400efee8` | Copy `S` into the new ordinary node's `+0` link |
| `400eff72` | Compare next node with `S`; exit before payload reads when equal |
| `400f0006` | Load `S` into `a0`; reclamation can update only `S+0` at `400f0012` |

Thus the visible pointer-copy chain does not pass `S` as a copy/clear destination or compute `S+4`. Putting `S` into an ordinary node's link is not itself a payload write: the consumer's sentinel test is what prevents subsequent payload access.

This is a recovered-path result. It does not prove that an unrelated computed write cannot alter the global, the fixed record, or a queue link.

## 2. Startup contains a real bulk overlap

The boot path calls the RAM-clear routine at **`40000542 → 400004b2`**. That routine writes 16-byte groups using `movem` at `400004d2`, advances by 16 at `400004d6`, and covers:

`40242000 .. 431dc690` — exclusive end.

The marker is inside this range. This is a demonstrated write to the candidate bytes, not an inferred possibility. It occurs in the recovered boot initialization path. Any future readiness initialization must follow this clearing and precede use; preserving marker state across a restart cannot be assumed. No additional runtime entry to this clear routine was established by the encoded direct-transfer search.

## 3. Nearby work-buffer destinations are bounded

The copy at **`400ef7fe`** has literal arguments:

`copy(destination=4199cd24, source=4199d024, length=0x200)`.

Its destination ends at `4199cf24`; its source ends at `4199d224`. Neither includes the marker.

For **`400ef514`**, the destination is computed rather than literal. The recovered loop establishes fixed base `4199d024` at `400ef43a`, saves it at `400ef446`, processes eight outer iterations, and advances the saved base by `0x40` at `400ef7ce`. Two inner iterations select its two `0x20`-byte lanes; the second shifts `a2` back by `0x20` at `400ef7b4`.

All **16 copy destinations** are therefore inside `4199d024 .. 4199d224`. This closes the destination bound at this particular bulk site under the recovered loop and ordinary calling convention. It does not certify every called helper or every write in the surrounding function.

## 4. The nearby indexed ring has an explicit proof dependency

Routine `400f021c` loads an index from `4199d4f4`, uses base `4199d224`, and accesses two banks through indices `head` and `head+90`. Its internal stores are at `400f025e` and `400f0270`. After both accesses, it increments and wraps the index at `400f0274 .. 400f027a`. The outer loop runs 32 iterations.

For an entry index in **0..89**, every internal four-byte store lies in:

`4199d224 .. 4199d4f4` — exclusive end, 28 bytes below marker start.

The address checks exhaust all 90 entry indices and 32 iterations: **5,760 word stores**. Every returned index remains in 0..89. Startup initializes the index to zero; the recovered direct index store at `400f0286` stores the normalized loop result.

However, wrapping occurs **after** the stores. As a concrete dependency check, an entry index of 97 would make the second-bank store at `400f0270` address `4199d510`, overwriting the first marker word. **No legitimate producer of that value was established.** This counterexample shows why global ownership of the index must be proved; the presence of a wrap instruction alone does not establish safety.

The routine also copies words to its output argument through `a1` at `400f0256` / `400f0268`. That argument's destination remains unresolved. No direct transfer or raw function-address reference to `400f021c` was recovered, so its runtime reachability is also unproved. The internal ring bound is not a certification of the entire routine.

## 5. Other recovered destination families exclude the marker

The fill/clear loops in `400f00ee` take a caller-provided buffer. Both recovered callers, at `4009d8de` and `4009da72`, pass **`8000f270`**. Their slot logic selects at most 32 frames of `0x30` bytes; the traced stores at `400f018e` / `400f01ea` stay within `8000f270 .. 8000f870`. All 384 possible word positions were checked. This closes those caller routes, not arbitrary indirect callers.

Previously mapped fixed pools are also disjoint:

| Destination family | Exclusive-end interval | Condition |
|---|---|---|
| Ordinary live queue nodes | `431dbfb8 .. 431dc4b8` | Valid pool nodes; 64 × `0x14` |
| Scheduler nodes | `4199d594 .. 4199da94` | Valid pool nodes; 64 × `0x14` |
| Events | `4199da94 .. 4199fe94` | Valid pool events; 128 × `0x48` |
| Managed heap | `419a38c0 .. 429a38c0` | Valid allocations using recovered allocator configuration |
| Heap bitmap | `41925eb8 .. 41945eb8` | Valid allocation-unit indices |

In particular, `400f0592` clears the pointer returned by allocator `400dab8c`, then retained in `4199d590`. A valid allocation belongs to the heap above the marker. Null/failure handling, invalid pointers and corrupted allocator/index state are not certified by that interval argument.

## 6. Expand bulk coverage beyond the original helpers

This pass identified and traced additional bulk paths:

- **`400ebc68`**: two-argument byte-zero routine, with 16-byte, four-byte and byte tails.
- **`400f0954`**: backward copy, including 16-byte block stores.
- **`400f09a4`**: overlap-safe copy, dispatching to backward copy or the existing forward copy.
- **`40102ae6`**: direct forwarding alias to `400ec23c`.
- Compiler/container wrappers near `40168692 .. 401687e6`, including one-byte inline writes and tail transfers to bulk routines.

A provisional instruction/constant scan across the examined executable area finds **1,098 bulk-call candidates** for six identified routines and one forwarding alias:

| Candidate classification | Count |
|---|---:|
| Locally recovered constant destination and length give a disjoint range | 259 |
| Destination remains unresolved | 836 |
| Destination constant, length unresolved by the candidate scan | 3 |

Manual inspection resolves those three length cases: `400986d0` clears `0x60` bytes at `413456bc`; `400d93fc` clears `0x100` bytes at `431a4044`; `400e64f8` copies at most `0x10000` bytes to `4be37280`. These ranges are disjoint. Their original candidate classifications remain preserved in the result file for provenance.

An independent aligned opcode search finds **697 direct call encodings and 17 direct tail-transfer encodings** to the searched targets. These counts overlap the candidate scan; they must not be added together or presented as validated reachable functions. Register calls, additional forwarding wrappers and inline loops require further coverage.

**These are discovery counts, not a global exclusion proof.** Linear decoding can include data or lose alignment. For example, the candidate scan missed the length push at known function entry `400986c4`; decoding from the confirmed entry resolved it. The scan deliberately forgets constants at branch boundaries and does not treat a pointer loaded from RAM as a proven address. Its unresolved cases therefore include both genuine provenance gaps and limitations of this conservative discovery method.

## 7. Verification and remaining work

The new verification checks **61 exact byte anchors**, the end-pointer literal uses, computed ring/work-buffer/scratch bounds, the invalid-index counterexample, allocator configuration and unchanged input hashes. Detailed results and candidate site lists are saved in `Digitone-marker-pointer-and-bulk-write-results.json`. The existing musical behavior models were not changed in this pass.

Global marker storage remains provisional. To close it, the next analysis needs an interprocedural destination/provenance map for the unresolved writes and wrappers, including RAM-loaded pointers and bounds at their producers. The ring's output argument and index ownership are explicit unresolved cases. Bus-master/DMA destinations and other inline writers also remain outside the completed bounds. No valid runtime producer reaching the marker was demonstrated, but absence of such a demonstration is insufficient to certify the storage.

Original SysEx SHA-256: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`.

Decoded section 3 SHA-256: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.
