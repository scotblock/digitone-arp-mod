# Digitone OS 1.42: persistent context integration audit

Read-only investigation, 3 October 2026. No firmware bytes, allocation requests, startup hooks or hardware state were changed. This report audits the persistent-table design from step 1 against recovered stock lifecycle paths.

## Outcome

The recovered paths provide concrete places to initialize, propagate and invalidate separate metadata before publication or reuse. Bounded execution now exercises the actual held-cache builder and all three selected-cache copy sites, common event copying, remap cloning, event allocation/recycling, the notes-only delayed queue handler and timed scheduler publication.

The step-1 model needed a correction: scheduled ticks copy from the retained template, whose context is in the accepted-record table, rather than the ordinary candidate dictionary. The corrected adapter reads that accepted snapshot. A generic copy into a retained template must not invent acceptance; the actual accepted-identity caller needs a dedicated commit.

This closes the listed helper/order checks under controlled inputs. **Complete firmware hook coverage, coherent pattern capture and protected accepted-context commit remain unproved.** The audit does not certify the design for a flashable build.

## Execution evidence

An external metadata observer follows execution of unchanged stock instructions. It applies proposed metadata rules in Python; no hook instructions are injected or timed. Consequently these are actual stock-control-flow tests with hypothetical metadata operations, not execution of a modified firmware.

- 72 assertions passed across 13 cases, executing 9,174 stock instruction steps.
- All three held raw-copy completion boundaries were visited: 400efbe2, 400efc0a and 400efc30.
- 45 listed instruction anchors match the decoded image bytes.
- The corrected step-1 specification still passes its 26 checks.

Cases include press–consume–press–consume–release under last/low/high selection; held-cache construction despite event exhaustion; subsequent departure invalidation; common retained copying; remap cloning; raw sequencer-cache copying; immediate event reuse; queue note-on/release, MIDI and invalid-track inputs; future queue emission after a supplied receiving-pattern change; queue event/node exhaustion; and timed head/middle/same-time publication.

Capture values and accepted identities are explicit observer inputs. Real root/scale reads, full sequencer construction, successful arp setup and interrupt interleavings are not executed in these new cases. The queue handler executes complete notes-only descriptor paths (tag ec, flag 10); other command flags are outside this execution coverage. The sequencer cache test executes the raw copying helper with a constructed cache, not the whole sequencer producer.

## Integration ledger

Addresses name existing instructions. They identify logical boundaries to audit for hook placement, not relocation-ready patch sites.

| Route | Context source → destination | Required action / publication boundary | Evidence |
|---|---|---|---|
| Event allocation, 400f0626 | Old pool entry → invalid | Clear metadata for nonnull private slot by return at 400f0658; null must not index the table | Actual allocation and exhaustion |
| Event free, 400f065c | Owned pool entry → invalid | Invalidate inside or before masked recycle, before free-head store 400f0684 | Actual free and immediate reuse |
| Held builder, 400efa20 | Explicit upstream capture → held candidate | Invalidate/refresh before first event mutation at 400efa5a; releases carry no candidate | Actual builder, supplied capture |
| Held selection copy 1 | Held candidate → pooled event | Transfer after raw copy at 400efbe0 and before publication call 400efbe4 | Executed |
| Held selection copy 2 | Held candidate → pooled event | Transfer after raw copy at 400efc08 and before publication tail 400efc3e | Executed |
| Held selection copy 3 | Held candidate → pooled event | Transfer after raw copy at 400efc2a and before the same tail | Executed |
| Fresh/cached sequencer constructor, 40093c26 | Explicit pattern a3 / track d4 → pooled or cache candidate | Refresh at successful construction; zero/failed refresh invalidates the affected cache before it can be reused as new input | Arguments and success boundary statically mapped; complete producer not executed |
| Sequencer cache emission | Cache candidate → pooled event | Cover raw calls 4009344e and 40093892 before timed scheduling | Static callers; raw helper execution |
| Common copy, 400f0690 | Known event/cache candidate → ordinary destination | Propagate with byte copy, ready at 400f06ca; missing source clears destination | Executed helper |
| Accepted retention | Incoming candidate → accepted playback record | Dedicated commit at accepted caller 4009de40 / completion 4009de46; generic copy cannot authorize it | Static accepted caller; identity outcome supplied in new model |
| Scheduled tick | Accepted retained snapshot → pooled event | Specialized accepted-source lookup around 4009ce3c; complete before first link store 4009ce68 | Static caller; actual common helper with constructed retained source |
| Remap clone, 4009bd8a | Incoming candidate → clone candidate | Preserve immutable capture source separately from overwritten stock +3c; finish before first link store 4009bdd2 | Complete clone executed |
| Delayed queue enqueue | Receiving descriptor snapshot → node candidate | Initialize each popped node; capture valid synth note-on before first pending link at 400efede | Complete notes-only handler; supplied snapshot |
| Delayed queue emit | Node candidate → new event | Transfer while node still owned, before publisher call 400efffa | Complete handler executed, including delayed emission |
| Queue reject/reclaim | Node candidate → invalid | Clear before rejection free-head store 400efecc or normal free-head store 400f0024; failed event allocation takes reclamation too | Invalid track and allocation failure executed |
| Scheduler publish | Completed event and candidate → visible queue | Metadata must precede live chain/head stores and timed chain/head stores | Actual live and timed helpers |
| Drain/ordinary retirement | Owned event → recycled slot | Shared free invalidation covers actual 400f065c route; preserve separate retained/cache records | Drain free route statically confirmed; individual free executed |

The cache resolver intentionally supports synth cache tracks 0..3. The existing sequencer cache region also contains MIDI tracks, which receive stock-pitch fallback. It must not interpret adjacent structures as extra synth records.

## Publication and concurrency

The event allocator removes a slot under its existing short mask, then restores SR before clearing stock fields. The removed event is private to its caller under the recovered pool contract. A metadata clear before its return does not need to occur after publication, but its exact register preservation and ownership during interrupts still require implementation review.

Event recycling publishes the address at 400f0684 under a mask. Clearing metadata after that store would permit another allocator to reuse the address first. Clear before publication under the same protection. This ordering is necessary even though allocation independently invalidates metadata.

Raw copies to newly allocated private events can finish metadata before publishing the destination. The live publisher does not itself establish capture provenance: invalid metadata is a legitimate fallback, not something it can replace with a current-pattern read. Timed scheduler publication is a second visibility mechanism and must be covered alongside 400f0886.

The queue's first pending link store is 400efede, not the final node link initialization at 400efee8. A hook placed only after the last store is too late for a concurrent reader. The recovered notes-only execution orders enqueue before due conversion in the same invocation; this does not exclude other readers or higher-priority writers globally.

For cache or retained destinations already visible elsewhere, byte-copy completion plus a separate word store is not automatically a transaction. The new observer executes sequentially. Protect the metadata/data association under audited existing ownership or an explicit bounded protocol before treating concurrent reads as safe.

## Accepted identity is a separate operation

In the ordinary caller, successful new setup reaches nonzero identity test 4009de12, writes incoming +40 at 4009de1c and copies to the retained template at 4009de40. Additive or rejected setup must preserve the previously accepted context. An accepted new identity with no candidate must replace it with invalid metadata.

The generic common helper also serves retained-to-event copying; its destination address alone cannot establish acceptance. Keep two explicit operations:

1. Candidate propagation for ordinary copies, including accepted-source lookup for scheduled ticks.
2. Accepted-record commit only from a proven accepted setup path.

The new negative control shows that a generic retained copy does not acquire valid accepted context. The scheduled-copy test shows that a separately committed accepted snapshot can be propagated by the actual common helper. Full setup success and the protected interval spanning its identity/state update and retained commit remain the next concrete execution target.

Output still requires successful arp selection, active-list state, event and retained identity agreement, supported type/track, playback binding and valid accepted context. Continuing remapped ticks read the destination's accepted record, rather than requiring incoming source binding to match it. Identity wrap remains unresolved; merely comparing a 32-bit value cannot distinguish every historical tick.

## Storage lifetime and fallback

Metadata is independent of +38 and parameter-record reference counts. The controlled cache replay tests therefore preserve original A context even after a new input carries B context. They do not change or certify stock payload ownership.

Unknown source storage clears a recognized destination's candidate. However, fallback is safe only if every relevant overwrite/reuse of that destination is observed. An unhooked raw overwrite can leave a valid-looking old table entry. No tag, checksum or pointer resolver compensates for missed producer coverage.

Ordinary resets need not blanket-clear this persistent table. Actual event reclamation clears those event entries; surviving held/retained metadata follows its own owner. Setup reentry must preserve table/header state, including busy depth. Cold allocation success/failure and publication ordering are still pending integration proofs. This report does not establish that stock pool reinitialization with live owners is safe.

## Coherent pattern capture is still separate

Persisting snapshots solves their subsequent lifetime, not the consistency of the initial read. Earlier analysis found separated root/scale writes and recovered complete pattern replacements. A reader-only interrupt mask cannot repair a writer already paused between stores.

The proposed header can hold writer depth and capture-failure state without borrowing a stock global. Every participating writer must enter before its first mutation and exit after its complete data commit. Observer/destructor callbacks should stay outside the narrower data-only guard scopes where previously recovered. Those scopes and whole-pattern data call graphs are documented, but complete writer coverage, actual abnormal exits and injected guard preservation remain uncertified.

During busy/fault state, new capture declines and the note keeps stock pitch behavior. Older accepted snapshots remain usable subject to ordinary arp lifetime checks. Do not wait, acquire a later pattern's scale, or clear surviving snapshots as a substitute for coherence.

## Next concrete work

The known helper edges now have a reviewable propagation ledger. Before progressing to a combined pitch prototype, execute successful/additive/rejected arp setup through the retained-copy caller and test the dedicated accepted-record commit at those real outcomes. Pair this with the coherent-capture guard at the recovered data-only pattern-writer scopes. Keep cold initialization/failure handling and exhaustive producer/copy coverage explicitly open.

Evidence files: `Digitone-persistent-context-integration-execution.json`, `Digitone-persistent-context-integration-anchors.json`, and the corrected `Digitone-persistent-sidecar-design-results.json`.

Decoded section-3 SHA-256 remains `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.
