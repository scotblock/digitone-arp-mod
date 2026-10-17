# Digitone OS 1.42: cached queued-note context fix

**The previously failing queued-arp case now passes in the PC prototype without acceptance-time metadata injection.** The device firmware is unchanged; physical timing and startup copying of the revised overlay remain unverified.

The stock cached-note constructor uses explicit pattern `a3` and track `d4`. In the observed source-pattern selection, it builds track 2 at `0x419a30dc` from pattern backing `0x407c61e9`, root 61/raw scale 0. The earlier pool-only candidate store rejected that cache address. The revised exact-slot resolver admits precisely four 72-byte sequencer-cache slots and stores their captured context in the existing four-word sidecar at offset 2592.

At `0x40093892`, the actual raw copy moves those 72 event bytes into the private allocated event. A machine-code wrapper carries the cache context alongside it before the stock timed publisher. The other raw-copy site at `0x4009344e` is also wrapped, including its displaced stack cleanup. Unknown sources resolve to zero rather than reading a later pattern.

| Case | Context | Actual pitch | Result |
|---|---|---:|---|
| Previous natural crossing | 0 | 57 | Fails original scale |
| Fixed natural crossing | `0x800040bd` | 56 | Original scale retained |
| Fixed no-delay control | `0x800040bd` | 56 | Same capture before replacement |
| Separate fresh-pattern setting control | `0x8000433b` | Matches new-scale oracle | Different settings captured |

The delayed event `0x4199dadc`, generation 1, is published at 248.667 ms, crosses completed native replacement at 251.165 ms and reaches eligibility/acceptance at 3168.667 ms. The same-generation context is present at publication, acceptance and native quantization. No event eligibility, identity or acceptance metadata is forged.

In a separate control, actual native selection constructs the track-2 cache from root 59/raw scale 5. 11 native arp outputs carry that different word and match its scale oracle. Repeated-slot refresh is separately tested by executing the actual producer hook first with root 61/raw 0, then root 59/raw 5, on each track. An attempted second panel handoff did not complete and is not counted as a refresh witness; fresh eligible receiving-pattern notes in one uninterrupted transition remain a coverage target.

The isolated checks pass 291 cache-address boundary/alignment cases, four cache read/store/clear cases, five invalid-header cases, eight valid producer refresh cases and sixteen producer invalid-capture cases (bad root, bad scale, writer busy and capture fault across four tracks). Eight differential copy cases compare all data/address registers, status register, stack position and 72 event bytes against stock at both call sites. The three counted functional runs complete with helper/guard bytes intact and no unexpected guest writes to the reserved region.

The new RAM overlay is 2,564 bytes, 240 bytes larger than the previous image, and fits below the owner pointer at offset 4096. It uses existing sidecar storage. The test deliberately installs the revision in PC RAM after the inherited startup snapshot. Passing it does not establish loader/copier continuity for this new revision, exhaustive cache mutation coverage, interrupt atomicity or physical deadlines.

## Next step

Connect this revised overlay and the two copy hooks to the PC bootstrap, repeat startup through playback, then repeat the cycle-aware timing controls with the added copy cost. Keep hardware flashing deferred until those checks and the remaining integration limits are addressed.
