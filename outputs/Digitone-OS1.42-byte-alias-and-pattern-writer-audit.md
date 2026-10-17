# Digitone OS 1.42: queue-byte aliases and pattern writers

**Follow-up:** [Active writer ownership and protection](Digitone-OS1.42-active-writer-ownership-and-protection.md) resolves the track backing getter and canonical-bank binding. The restore/reset writers can overlap receiving storage in the recovered canonical install path. The queue-pop interrupt mask ends before writer dispatch; inherited interrupt state and global callback gating remain unresolved.

The queue-byte candidate remains compatible in the traced producer, consumer and recycling paths. **The writer consistency gate is not closed:** group restore/reset paths contain separate scale and root stores, and protection across those stores has not been established. A reader interrupt mask alone cannot provide that protection. No firmware was modified, repacked or flashed.

## Queue-byte audit result

An even-offset literal scan across decoded section 3 found 25 references with values in `431dbfb8..431dc4c4`, covering the 64-node pool and adjacent queue heads. All reconcile with the known initializer, descriptor handler, or held-reset boundary. The held reset ends at the pool start; it does not supply another payload reader.

Within the recovered queue path:

| Operation | Evidence | Effect on proposed bytes |
|---|---|---|
| Enqueue | `400efe8e` zero-extends note; `400efe94` writes the entire word at node `+04` | Every accepted input overwrites `+04..+07` |
| Emit | `400effca` reads only node `+07` into event note `+18` | No upper-note-byte read found |
| Link/reclaim | Free/pending operations use node `+00` | Upper note bytes survive until overwrite |
| Downstream handoff | `400f0886` receives the separately allocated event | Queue payload pointer is not handed off in this path |
| Initialization | Links pool and sentinels; startup precedes callback installation | Payload clearing is not a live-reset guarantee |

The handler's node pointer remains locally owned through conversion and reclamation; allocator calls preserve the saved address register. No node copy, alternate note-word consumer, or escaping node pointer was found in this chain. Sentinel records lie outside the pool and must never be decoded as ordinary nodes.

**Bounded conclusion:** no conflicting owner of `+04..+06` was found in these paths. This is not a universal alias proof. The literal inventory cannot expose every computed address, arbitrary memory copy, indirect consumer or unaligned data pointer. The linear disassembly scan is a discovery aid, not exhaustive control-flow recovery. Event `+20..+27`, proposed as the later context destination, remains separately uncertified.

## Pattern writer findings

The field scan was expanded beyond the normal setters. The following stores were checked against their actual instruction bytes:

| Recovered function | Scale store | Root store | Observed operation |
|---|---|---|---|
| `40034a8c` | `40034bb4` | `40034bca` | Restore saved metadata through the object's storage getter |
| `40034c78` | `40034d00` | `40034d16` | Another saved-metadata restore path |
| `40035268` | `40035356` = `-1` | `40035368` = `60` | Group default/reset path, after preserving prior metadata |

These functions obtain backing storage through virtual slot `+28`, also used by the normal track-field accessors. They store multiple metadata fields and notify afterward. They do not commit root and scale with one atomic store; storage-getter calls occur between the two stores in the restore paths.

Direct UI callers include `400b6db6 -> 40034c78`, `400b6e16 -> 40035268`, `400b6e9e -> 40034c78`, and `400b6efe -> 40034a8c`. Their containing functions start at `400b6d92` and `400b6e7a`. No explicit status-register interrupt-mask operation was found spanning the writes in these recovered functions or direct callers. Caller setup uses `4012f97a` and `400237b0`: the former returns a lazily initialized manager; the latter selects a per-track object using index/stride arithmetic and accessors. These observations do not establish an interrupt lock.

**Limits:** virtual-call behavior, outer dispatcher protection, callback priorities, and whether each selected backing can equal the receiving active pointer `*(41342150)` remain unresolved. Consequently, this is a concrete consistency requirement, not proof that an actual hardware race occurs.

Normal independent edits remain distinct: root setter `40032580` stores at `400325c4`, while scale setter `40032846` stores at `40032882`. A root edit alone may legitimately leave scale unchanged. The concern here is a multi-field operation intended to restore/reset a pair.

Other discovered candidates include byte/word writes near `40008ac8/40008b18`, `40008c5a/40008c90`, `4000ae8e/4000ae9e`, `4000b034/4000b046`, `4000b19e/4000b1b0`, and defaults at `40013348/40013358`. Their backing layout, active/inactive ownership and surrounding transaction boundaries need classification. A matching field displacement alone is insufficient to label them active-pattern writers. Whole-pattern copies may use generic memory routines without these displacements.

## Why the previous capture guard is insufficient

For a hypothetical group update `(root=60, scale=0) -> (62, 5)`:

1. Writer stores scale `5`.
2. Audio capture preempts the writer before it stores root `62`.
3. Capture masks interrupts and reads the same backing: `(60, 5)`.
4. Encoding produces a valid marker and CRC for that partial state.

A second identical read can still return `(60, 5)`, because the writer is paused. Holding the backing pointer stable also cannot solve this. CRC validates stored bytes, not the transaction that produced them. An interrupt callback must not spin waiting for a paused lower-priority writer to finish.

This corrects the preceding capture report's protection proposal. The eight-byte reader critical section may still be part of a design, but it does not certify capture by itself.

## PC verification and safest next target

Eight specification scenarios passed, including both store orders at all three capture boundaries, stable-pointer and repeated-read counterexamples, CRC acceptance of mixed fields, and hypothetical writer-guard/version-rejection alternatives. Eight firmware instruction anchors were checked against the decoded image. These tests model assumptions; they do not execute firmware or establish its scheduling.

Next, resolve the storage getter for the restore/reset callers and compare its backing identity with the active receiving backing. For any writer that can overlap capture, trace the outer dispatcher and actual interrupt exclusion across the **entire update**. Classify the additional conversion/default and generic-copy paths under the same ownership rule. If protection is absent, develop a PC-only writer-transaction design: protected commit, or a published consistent snapshot/version with bounded rejection rather than interrupt-side spinning. Neither alternative is implemented or certified here.

Keep the compact queue encoding as a candidate. Do not progress to firmware insertion until writer consistency, event destination ownership and stack/register requirements are established.

Original SysEx SHA-256 remains `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`; section-3 SHA-256 remains `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.
