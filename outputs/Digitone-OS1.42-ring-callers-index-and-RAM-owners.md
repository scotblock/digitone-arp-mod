# Digitone OS 1.42 — ring callers, index writers and RAM destination owners

Read-only follow-up, 3 October 2026. Candidate storage remains `4199d510 .. 4199d517`. Firmware and decoded executable hashes are unchanged; no patch or device operation was performed.

**The three requested investigations have produced bounded findings, not global certification.** Several nearby destinations now have concrete owners. The ring's caller remains unidentified, and its output pointer is a specific unresolved dependency of both marker safety and index ownership.

| Requested check | Result |
|---|---|
| Find the ring's output-pointer suppliers | No caller recovered after the expanded entry search; output/input arguments remain unresolved |
| Prove index writers retain 0–89 | Proven for startup and the sole recovered direct writer, conditional on no alias overwrite; global proof remains open |
| Trace nearby RAM-loaded bulk destinations to owners | Persistent heap pool, fixed event pool, retained templates and temporary descriptor frames identified in six route groups |

## 1. Ring entry and argument ownership

The search now covers the entire decoded section 3 for absolute transfers and byte-, word- and **long-relative** branches into `400f021c .. 400f0296`. It also checks raw function pointers in both decoded sections and candidate PC-relative references.

The only three encoded branches entering that interval originate inside the routine itself. No external direct entry, exact stored pointer to `400f021c`, or recovered PC-relative address-taking reference was found. The preceding instruction is a return, so ordinary sequential execution from the previous routine does not supply a caller.

This strengthens the possibility that the routine is unused, but **does not prove it unreachable**. Computed entries, additional relocation/relative-table schemes and control-flow provenance remain unproved. There is no defensible caller buffer to substitute for the missing evidence.

The recovered signature is concrete: after saving its registers, the routine takes its output pointer from stack `+10` into `a1`, and input pointer from `+14` into `a2`. Its loop accesses **256 bytes of each buffer**. It performs no local pointer-range rejection before its output writes at `400f0256` / `400f0268`.

The output must be shown disjoint from both the marker and the index word. A dependency check illustrates why: if an unproved caller supplied output address `4199d4f4`, the first word would overwrite the index and output offset `0x1c` would reach marker address `4199d510`. **No runtime caller supplying that address was demonstrated.** This is a counterexample to assuming the internal ring bounds alone certify the routine.

## 2. Direct index ownership and its limit

The index `4199d4f4` has two exact literal references in section 3 and none in section 2:

- `400f023c`: read it into `d0`.
- `400f0286`: store the normalized loop result.

The wider constant-store candidate trace finds the same sole direct store; no additional locally resolved constant destination overlaps the index word.

An instruction graph starting at the confirmed entry covers **33 reachable instructions**, has no application calls and ends at common return `400f0294`. A nonpositive work counter exits without changing the index. The active path performs 32 increments, wrapping values above 89 to zero before the final store. Exhausting every valid entry state establishes:

`inactive: head' = head`

`active: head' = (head + 32) mod 90`

Startup clearing supplies the initial zero. Thus the recovered direct updates preserve 0–89 inductively; repeated or interleaved normal completions still store an in-range value.

The internal ring stores also stop before the index word. **However, the caller-supplied output stores are potential aliases, not excluded writers.** Consequently this is not a proof that every possible writer of the index preserves its range. Step 2 depends on resolving Step 1, as well as excluding unrelated generic writes. The earlier invalid-entry example remains valid: entry index 97 would address the marker through the second ring bank before wrap correction.

## 3. Persistent payload-pool clear: owner and exact size

The initialization chain is now resolved:

`4009bcec → 4009bcb8 → 400f0504`

The wrapper pushes literal **`0x9e` (158)** at `4009bcb8`. The initializer calculates:

- Record stride: `8 × 158 + 0x14 = 0x504` bytes.
- Requested pool size: `64 × 0x504 = 0x14100` bytes, or 82,176 bytes.

It requests that storage from allocator `400dab8c` at `400f0580`, retains the returned pointer in **`4199d590`** at `400f058c`, and clears the requested extent at `400f0592`.

The RAM-loaded pointer is then reused at `400f059e` to build 64 linked payload records. Free-list head **`4199fe98`** is installed at `400f05c0`; allocation `400f05d6` pops records through their `+10` link, while reference release `400f05f8` returns records to that list. The final record begins at allocation offset `0x13bfc`, and its extent ends exactly at `0x14100`.

The three exact references to persistent owner `4199d590` are the initialization test, assignment and reuse load. A valid allocation belongs to the previously traced heap `419a38c0 .. 429a38c0`, above the marker. The recovered constructor route therefore has a concrete owner and size. This does not certify allocation failure, corrupted allocator configuration, arbitrary pointer aliases or an undiscovered caller using a different record count.

## 4. Event copies: RAM free-list pointer to fixed pool

Three nearby copies have resolved destinations:

| Copy | Destination provenance |
|---|---|
| `400efbe0` | Allocation through `400f0626` at `400efbc2`; null rejected |
| `400efc08` | Second allocation at `400efbea`, retained in `d2`; null rejected |
| `400efc2a` | Allocation at `400efc16`; null rejected |

Each copies `0x48` bytes. Allocator `400f0626` reads free-list head **`4199fea0`**, advances it through event `+44`, and returns the allocated event pointer. Under the established free-list invariant, all 128 destinations lie inside **`4199da94 .. 4199fe94`**, disjoint from the marker.

The indirect copy at **`400efc08` was absent from the earlier straight-line candidate inventory** because that scan discarded a saved function-pointer fact at a branch. The confirmed path preserves `a5 = 400ec23c` and passes the second allocated event as destination. This is a concrete coverage improvement, and another reason not to treat the inventory count as exhaustive.

Common event copy `400f0690 → 400f06c4` has two recovered direct callers:

- `4009ce3c`: destination is a newly allocated event; the retained template is the source. The allocator pointer is explicitly loaded at `4009cd70` and retained through `d3`.
- `4009de40`: destination is `41345f08 + 0x48 × track`, a retained template; the event is the source. For valid synth tracks 0–3, the four template ranges exclude the marker.

These are owner bounds conditional on valid pool pointers and track inputs; they do not establish that every producer/free-list mutation throughout the firmware preserves those invariants.

## 5. Descriptor copies belong to temporary frames in recovered routes

Copies at `400eebc4`, `400eec42` and `400eecc2` each write a newly created **24-byte current-stack argument area**. Their source descriptors are also explicitly prepared in the caller's local frame. Their destinations are not the nearby song-state globals that appear earlier in the same routines.

The three default-descriptor copies at `400ee8b0`, `400ee992` and `400eeac6` take the caller's descriptor buffer through the custom `a0` argument convention. Their function pointers belong to policy table **`4020034c`**:

| Slot | Target |
|---|---|
| `+00` | `400ee7f8` |
| `+04` | `400ee96c` |
| `+08` | `400eea88` |
| `+0c` | `400ee7c0` |

Recovered policy dispatches load the selected table from RAM, then explicitly put a frame-relative descriptor buffer in `a0`. Examples include `400933c0`, `40093570`, `400956b4`, `40095888` and `40095f44`. This resolves how a RAM-loaded callback reaches these copy routines and who supplies their destination in those routes.

Relative frame ownership is established. Absolute reservations for every task stack, arbitrary computed policy callers and global separation of all stacks from the marker remain outside this proof. Generic overlap-safe/backward-copy helpers also retain caller-dependent destinations.

## 6. Verification and decision

Verification passed **62 exact byte anchors**, the ring's complete local instruction graph, all 90 valid index transitions, 64 payload-record extents, 128 event destinations, four retained-template ranges and the output-alias dependency check. Detailed results are in `Digitone-ring-index-and-RAM-owner-results.json`.

The new evidence removes several vague destination assumptions. It does not close global storage ownership. The ring is now a precise unresolved case: identify its computed caller and both buffers, or establish that no valid execution path can reach it. Its output pointer cannot be ignored when claiming index safety. Broader RAM aliases, stack separation and remaining generic bulk destinations still need coverage before reserving the marker bytes.

Original firmware SHA-256: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`.

Decoded section 3 SHA-256: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.
