# Digitone OS 1.42 — expanded storage ownership audit

Read-only analysis, 3 October 2026. Candidate: `4199d510..4199d518` (end excluded), the first eight payload bytes of queue end record `4199d50c`.

**Exclusive ownership is still unproved.** This pass closes two specific gaps: the recovered direct task-stack reservations do not overlap the candidate, and neither nearby compiler word-offset jump table supplies an entry into the unresolved ring routine. It also extends literal searches to every container section. None of these results establishes a complete global points-to proof. No legitimate runtime overwrite of the candidate has been demonstrated, either.

## Expanded container coverage

All six container sections were examined: decoded sections 2 and 3, and stored bytes of sections 4, 5, 6 and 7. The scan checks every byte offset for a big-endian 32-bit value inside the candidate range or ring routine `400f021c..400f0296`, and for the two queue sentinels and three queue-head/end globals.

Only section 3 contains matches: 21 occurrences of the previously known sentinel and queue-global addresses. There are no exact stored values inside the candidate range or ring routine, including interior ring addresses. The other sections have no matches for these searched values.

This closes an omission in the earlier literal inventory. Stored-byte searches do not decode additional sections' relocation schemes or synthesized addresses, and are not proof of their runtime memory destinations.

## Relative dispatch into the ring

An even-offset opcode search across the complete decoded section 3 finds 84 candidates for the compiler expression `move.w table(pc,index),dN; ext.l dN; jmp table(pc,dN.l)`.

Only two corresponding table bases lie within signed-word reach of the ring. Both were checked against their actual unsigned selector rejection and all permitted entries:

| Table | Permitted selectors | Actual target range | Ring target |
|---|---:|---|---|
| `400ee4a0` | 0–64, 65 entries | `400ee522..400ee65a` | None |
| `400f0c2e` | 0–221, 222 entries | `400f0dea..400f31de` | None |

At `400ee490..400ee492`, the comparison rejects unsigned values greater than 64. At `400f0c18..400f0c20`, zero extension and unsigned rejection limit the selector to 221. Every allowed signed-word target excludes the complete ring interval.

The other 82 standard-expression candidates are too far away for any signed 16-bit table value to target that interval. Candidate discovery is not a validated code map for those 82 sites. Other indexed instruction candidates are retained separately in the results; the search does not establish that all computed control transfers use this expression.

Together with the earlier direct transfer and absolute pointer searches, this removes the standard local switch-table mechanism as a recovered caller. **It does not prove the ring unreachable.** Synthesized pointers, RAM-loaded dispatch and control-flow coverage remain unresolved. The routine's input/output buffer ownership therefore remains unresolved, including the earlier hypothetical output alias to the index and candidate.

## Task-stack reservations

All 16 recovered absolute calls to task initializer `4000170c` have a contiguous, exactly parsed five-argument constant push sequence. The initializer computes the initial saved stack pointer as:

`stack base + (size & ~3) - 12`

The final 12 bytes hold the initial exception frame. `407c2000` is frame content, not the stack address. Every recovered reservation is disjoint from the candidate.

| Initialization call | Stack start | End excluded |
|---|---|---|
| `4000158c` | `404d9f8c` | `404daf8c` |
| `4000304a` | `404db6ac` | `404dbeac` |
| `400169ba` | `404dedb8` | `40506db8` |
| `4008c37e` | `402d3eec` | `402d7eec` |
| `4008c50e` | `413275ec` | `4132b5ec` |
| `4008cb34` | `41323598` | `41327598` |
| `4008cf34` | `4132b5f0` | `4132f5f0` |
| `40090502` | `4132f888` | `41333888` |
| `400a7970` | `41348dac` | `4134cdac` |
| `400dcaa6` | `419493cc` | `419513cc` |
| `400dce4c` | `41952088` | `4195a088` |
| `400e55b0` | `419780b4` | `4197c0b4` |
| `400e9476` | `4197cbf8` | `41980bf8` |
| `400eaffc` | `41993ad4` | `4199bad4` |
| `400eb084` | `4198aad4` | `41992ad4` |
| `400eb118` | `41981ad4` | `41989ad4` |

The closest recovered stack ends at `4199bad4`, `0x1a3c` bytes below the candidate. This establishes intended reservation boundaries for these constructors. It strengthens the earlier frame-relative descriptor-copy evidence under normal stack operation; it does not establish every runtime saved-SP writer, every computed initializer caller or all interrupt/startup stack bounds.

## Why the global proof cannot yet be signed off

The established queue lifetime proof remains valid within recovered paths: ordinary nodes exclude the fixed tail, emission rejects it before reading payload, and append/removal write links rather than tail payload. Startup clearing is an intentional whole-region writer before any proposed marker initialization.

The missing global requirement is stronger: every reachable non-startup memory operation must either have a destination disjoint from these eight bytes or be an intentional owner. The current evidence does not establish that requirement:

1. The ring's caller-supplied buffers are still unknown. Its local valid-index proof does not restrict those buffers.
2. Generic copies, clears, inline stores and RAM-loaded pointers do not have a complete caller-to-destination map. The earlier provisional bulk inventory contains 836 calls whose destination was unresolved by that scanner. This is a historical discovery count, **not** 836 confirmed reachable unsafe writers or an updated count after manual owner tracing. Branches can also conceal additional indirect calls, as the previous audit demonstrated.
3. Local pool and stack bounds depend on their pointer and range invariants. Those invariants have not been established for every global alias and producer.

Repeating absence-of-literal searches or adding PC behavior tests cannot close these obligations. A complete proof would require a validated reachable-code map plus propagation of pointer bounds across calls and joins, with explicit treatment of indirect dispatch and external memory writers. The present scripts deliberately do not implement that whole-program proof.

**Decision:** keep this candidate unapproved for new firmware state. No evidence currently supports claiming its exclusive ownership, and the audit has not shown a legitimate clobber that definitively rejects it. Further work must resolve these global dependencies or establish a different storage design with a narrower ownership contract; changing the storage address alone would not supply that contract.

## Verification

This pass verifies 19 exact instruction anchors, the five-argument encodings at 16 direct task initializer calls, all 287 permitted targets in the two nearby tables, and the candidate's separation from all 16 reservations. Machine-readable evidence is in `Digitone-storage-ownership-expanded-results.json`.

No behavior model changes, model-suite reruns, firmware execution, hardware operations or flashable output were performed. Source firmware and decoded section 3 hashes remain:

- SysEx: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`
- Section 3: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`
