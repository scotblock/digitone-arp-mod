# Digitone / Digitone Keys OS 1.42 — data commit closure and remaining storage proof

Read-only audit, 3 October 2026. Original firmware and decoded executable are unchanged. No guard has been inserted, no firmware has been rebuilt, and no device has been contacted.

**Full certification remains incomplete. This pass closes a bounded application-call graph and identifies narrower commit scopes that avoid the unresolved observer/destructor paths. It does not establish actual firmware exception cleanup or global RAM exclusivity.**

## 1. Whole-pattern updates have a closed data-only call graph

Instruction-level branch traversal covers **13 routines, 752 reachable instructions, 17 call sites and one external tail transfer**. Every recovered call resolves to another routine in this set. There are no unresolved calls in this bounded graph, allocator calls, observer calls, or decoded explicit exception/trap instructions.

| Routine | Address | Dependencies |
|---|---|---|
| Pattern import | `40008de0` | Header conversion/defaults, track conversion/defaults, step defaults, parameter conversion/clear |
| Pattern defaults | `400134e4` | Header defaults, track defaults, step defaults; tail to parameter clear |
| Header conversion | `4000879c` | Bounded string copy |
| Header defaults | `4001341c` | Bounded string copy |
| Parameter conversion | `40008ca4` | Memory clear, parameter table lookup |
| Step defaults | `40013370` | Memory clear |
| Parameter clear | `40013478` | Memory clear |
| Track conversion | `400089fa` | None |
| Track defaults | `4001330c` | None |
| Memory copy | `400ec23c` | None |
| Memory clear | `400ec284` | None |
| Bounded string copy | `40128448` | None |
| Parameter table lookup | `40007e3e` | None |

The full string-copy routine extends through `40128506`, with return at `40128502`; the earlier shorter window did not cover its complete branch graph. Its alignment, byte-copy and zero-padding paths now all belong to the verified call-free leaf. The parameter lookup reads fixed executable tables at `4016fc04` / `4016fdd4`; it is not being identified as the musical scale quantizer.

The initializer's `40013556 → 40013478` tail remains part of the complete update. An outer data scope must close after that continuation returns. Per-track completion cannot authorize capture while other tracks or parameter areas are still changing.

**What this proves:** under the recovered concrete targets and calling convention, these routines have no call path into application allocation, notifications or exception helpers. Preparing arguments first and protecting this data-only call can avoid those application-exception hazards.

**What this does not prove:** argument validity, mapped writable memory, CPU fault handling, asynchronous unwinding, inserted-hook correctness, complete writer coverage, or any actual guard cleanup in stock firmware. No exception landing-pad map has been certified. Normal calls are still modeled as returning normally.

## 2. Five narrower commit windows end before notification

| Writer | Proposed data-only interval, end excluded | Calls within interval |
|---|---|---|
| Metadata restore | `40034bb4 .. 40034c10` | Four concrete backing getters |
| Metadata record restore | `40034d00 .. 40034d5c` | Four concrete backing getters |
| Metadata reset | `40035356 .. 400353a6` | Four concrete backing getters |
| Record replacement: pattern backing | `400256dc .. 400256ee` | One memory copy |
| Whole-pattern copy candidate | `400225c2 .. 400225d2` | One memory copy |

All five intervals are straight-line data sequences in the decoded control flow. The metadata getter is track-vtable `401764c8`, slot `+28`, resolving to call-free `4013a33a`: load the argument, load object `+10`, return. This is a concrete-type result, not a claim that every runtime object sharing a slot number has the same behavior.

The metadata intervals include the last field store at `40034c0c`, `40034d58` and `400353a2` respectively. Their following slot `+10` notification calls are outside the proposed interval. Record replacement copies the complete `0x1611d`-byte pattern backing at `400256ec`; the next indirect operation begins at `400256ee`. Its separate `0x988`-byte associated-data update is outside this narrower scope. This proposal therefore protects the complete pattern backing, not an atomic pattern-and-associated-data operation.

The whole-pattern copy candidate finishes its copy before the indirect notification tail at `400225ea`. Runtime reachability of that candidate remains unproved.

These boundaries are analysis findings, not replacement instructions. Saving live registers and flags, preserving arguments/results, placing entry before the first write, and closing before notification all need a later integration audit. In particular, metadata entry occurs with prepared store operands live in registers.

## 3. The broad notification path remains uncertified

Track slot `+10` leads through `4003514a → 4013b2d4 → 4013b25c`. The observer loop invokes a registered function pointer at **`4013b2aa`**, loaded from its callback record via the stack. Its target depends on runtime registration. Pattern notification `40021086` also invokes per-track notifications.

Slot `+44` notification preparation includes allocation and scheduler/event submission through `400a7cb2`. Several locally created record cleanup targets resolve to simple destruction/free paths, but that local result does not resolve all externally fetched objects or all observer callbacks.

There is no evidence here that a particular callback throws. There is also no validated evidence that every callback returns normally or that an exception unwinding across a proposed outer guard would balance it. A broad guard spanning these paths would still need actual exceptional cleanup certification.

The narrower design closes the data scope before notification. A callback failure after a completed commit then cannot strand that already-closed scope. A callback that performs a further pattern write needs its own correctly covered data scope; a partial failure in that later update must still latch invalidity.

## 4. Global marker storage is still provisional

The proposed marker remains `4199d510 .. 4199d517`, inside the fixed queue end-record payload. The prior audit established exclusion from ordinary node allocation/traversal/reclamation. It did not establish ownership against every subsystem.

An unaligned raw four-byte search of both decoded sections finds:

| Search | Section 2 | Section 3 |
|---|---:|---:|
| Nearby addresses `4199d000 .. 4199da93` | 0 | 79 |
| Literal addresses inside the proposed eight bytes | 0 | 0 |
| Bases from which a signed 16-bit displacement could reach a marker byte | 0 | 4,625 occurrences, 649 distinct values |

The wider search is a candidate inventory, not 4,625 decoded aliases. It includes code/data and possibly coincidental byte sequences. Sampled nearby globals have real separate consumers, including synchronization helpers using `4199ccb0`; adjacency cannot establish marker ownership.

Absence of a direct literal reference does not rule out a pointer loaded from RAM, an indexed address, arithmetic from a distant base, or a generic bulk operation. The known startup RAM clearing also covers the marker. A ready state must therefore still require explicit quiescent initialization after startup; zeroed bytes cannot authorize capture.

**`global_storage_certified` remains false.** There is no defensible basis yet to promote these eight bytes to certified reserved storage. The next storage task is to classify the candidate references into code/data, track address provenance through RAM loads and argument passing, and bound generic copy/clear destinations that can overlap the record. If those bounds cannot be established, this storage choice must be rejected or replaced with storage whose reservation can be demonstrated.

## 5. PC checks and decision

All **13 PC specification suites pass: 121 scenarios**. Six new checks cover preparation failure before entry, callback failure after completion, mixed-track capture blocking, initializer tail completion, a later callback's partial update, and the failure mode of keeping a callback inside a broad scope. These are specification tests, not execution of the firmware or proof of installed cleanup.

The accompanying `Digitone-data-only-closure-results.json` contains function/interval hashes, call edges, provenance byte anchors, literal inventories, model results and unchanged input hashes:

- Original SysEx: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`
- Decoded section 3: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`

**Proceed with the data-only scope design for further static analysis. Do not implement a firmware patch yet.** The broad exception-cleanup assumption can be avoided for these recovered commit paths; global storage proof, complete writer coverage, asynchronous/fault behavior and instruction-level integration remain open. Actual firmware exception cleanup remains uncertified, and no guard has been implemented.
