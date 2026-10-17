# Digitone OS 1.42: event ownership, memory, scales, and later pitch

Read-only investigation, 2 October 2026. Firmware remains unchanged. This report supersedes the unresolved scale-index and later-pitch details in the preceding audit.

## Findings and their limits

- Raw track scale values are resolved: **-1 is chromatic; 0..34 directly index the membership rows.** Only the name-table lookup adds one.
- The later integer pitch adjustment is the sound's **octave offset** through its normal setter. The later fractional contribution is **MIDI pitch bend scaled by bend depth**.
- The 72-byte event format is a **tagged union**. `+20..+27` is unused in the traced synth-note paths, but holds real pointers in pattern-context events. It is not universally free space.
- Event-pool, retained-template, audio-frame, heap, and startup-clear boundaries are now mapped. There is still **no proven unowned RAM reservation** for new globals.
- A type-specific context field inside existing synth-note events is now a more concrete candidate than expanding records or assuming a free static RAM gap. It still requires a complete lifetime and ownership proof before firmware changes.

The scale conversion and the identified later pitch contributions are resolved through code and table evidence. Event/memory mapping is complete for the listed structures and traced paths; a global proof that no indirect caller or other producer uses candidate bytes remains outstanding. This is not a patch-readiness claim.

## 1. Ownership of event bytes +20..+27

### Synth-note event: type zero

`40093c26` constructs sequencer synth events. It collects at most eight notes (`40093d54–40093d58`) and writes them to `+18..+1f` (`40093f08–40093f10`). The held-note builder `400efa20` creates type-zero per-note templates, with one note at `+18`, count at `+14`, and clears type at `400efab8`. The traced release producer at `400eff9c` also constructs a one-note event from an allocated type-zero slot.

No read or write of `+20..+27` was found in the examined type-zero construction, arp setup/output, held-template selection, or voice-allocation argument preparation. The known synth fields resume at flags `+28`. That makes this eight-byte region a **type-zero-specific candidate**, rather than a confirmed extension field.

### Pattern-context event: type two

At `40095982–40095984`, the producer assigns type two. The loop at `400959bc–400959dc` stores eight track-transpose pointers beginning at `event+18`, using `+18 + 4*index`. Thus `+20` and `+24` are the pointers for indices two and three.

The type-two consumer `4009cba0–4009cc38` follows these pointers: its loop at `4009cc1c` reads the first four entries and installs the signed track transpose values. Consequently, blanket use or clearing of these fields in already-built events would corrupt pattern-context behavior.

### Two misleading references resolved

- `400942d8` writes `+20` through **a5**, but `4009422c–40094234` establishes a5 as a separate MIDI backing object, attached to the allocated outer type-three event through `+10`. This is not a write to synth-event `+20`.
- In the type-three consumer, `4009cc8e` loads that backing object from `event+10`, and `4009cc94` writes its `+24` timestamp. This is also not a synth-event field.

These distinctions remove two apparent collisions from the previous audit, while the type-two pointer array establishes a real union owner.

### Copy and reuse implications

All previously identified `memcpy(0x48)` paths preserve the candidate region automatically, including the direct copies that bypass `400f0690`. A field carried *inside* a type-zero event therefore avoids separate metadata propagation at those particular copy sites.

However, `400f0626` does not clear `+20/+24`. A recycled slot may contain old note metadata or type-two pointers. Every relevant type-zero producer and persistent held template must initialize proposed context explicitly. The context interpretation must be gated on event type, a valid context encoding, synth-track bounds, active arp list, and matching arp identity. A plausible-looking leftover byte or pointer cannot establish validity.

The absolute-reference search found the allocator in scheduler/control producers, synth/MIDI builders, remapping, arp scheduling, held selection, and release production. It also found allocator pointers used for indirect calls. This is useful coverage, but absolute references alone cannot prove that every event producer or consumer has been found. No candidate bytes were written during this investigation.

## 2. RAM and object boundaries

Ranges below use exclusive end addresses.

| Structure/range | Ownership established |
|---|---|
| `40242000..431dc690` | Startup clear range, routine `400004b2`; includes large static buffers and the managed heap |
| `80000000..80008000` | First initialized-data RAM bank; copy from `40242000..402478f0`, then clear remaining bank |
| `80008000..80010000` | Second bank; copy from `402478f0..4024f4b0`, then clear remaining bank |
| `41344530..413445d0` | Four fully occupied 40-byte arp-state records |
| `413445d0..41344610` | Four 16-byte arp-note bitmaps; directly adjacent to the records |
| `41345f08..41346028` | Four retained 72-byte arp templates |
| `41346028` onward | Another live message ring, indexed at `4009d154–4009d172`; retained templates cannot grow into it |
| `4199d594..4199da94` | 64 scheduler nodes, 20-byte stride |
| `4199da94..4199fe94` | **128 playback events**, 72-byte stride |
| `4199fe94/98/9c/a0` | Scheduler head, payload free list, scheduler-node free list, event free list |
| `41925eb8..41945eb8` | Heap allocation bitmap: 1,048,576 allocation units / eight bits per byte |
| `419a38c0..429a38c0` | **16 MB managed heap**, 16-byte allocation units |
| `80001fa4..800034c4` | Two alternating audio frames, each `0x0a90` bytes |
| `48000000` | Startup stack pointer; this alone does not establish all stack reservations |

### Pool initialization

`400f0504` links the fixed event pool via each event's `+44` field. The loop starts at the first link address `4199dad8` and stops at `4199fe90`, the final link. It installs the first event address `4199da94` into free-list head `4199fea0`. The difference between pool start and end is `0x2400`, exactly `128 * 0x48`.

The preceding scheduler-node pool uses the same pattern with `0x14` stride (`400f053a–400f0564`). Neither pool is spare RAM. The reference-counted payload pool is allocated separately through `400dab8c` during `400f0504` initialization.

### Heap evidence

Initialized words at `401fe594`, `401fe598`, and `401fe59c` contain heap base `419a38c0`, bitmap base `41925eb8`, and heap end `429a38c0`. Words at `401fe5a0/+a4` contain maximum order 20 and `0x100000` allocation units.

Allocator `400dab8c` accesses these structures. Address translation `400da9e0` multiplies a unit index by 16 and adds the base. Free routine `400dad92` checks against base plus `0x00fffff0`, checks 16-byte alignment, and reads the allocation bitmap. This corroborates the 16 MB ownership rather than merely relying on recognizable constants.

The startup clear includes this heap; **cleared does not mean available to a patch**. A runtime allocation during initialization might provide owned storage, but it still needs a place to retain its pointer, failure handling, initialization ordering, and task/interrupt lifetime verification. No arbitrary address beyond the static clear endpoint or between mapped structures has been certified free.

## 3. Scale conversion verified

Track getter `40032816` reads `storage+3ce` signed and returns -1 for absent storage. Setter `40032846` clamps values to **-1..34**, then stores the byte at `40032882`.

The live note path at `400dc4aa–400dc4b8` passes that signed byte directly to `40106b6c`, alongside root `storage+3cb` and the note. There is **no index offset** before membership testing.

The name renderer at `4005f018–4005f020` adds one before calling the long-name accessor `40106db2`. The short-name renderer does the same at `4005f110–4005f118`. A second UI path uses `raw+1` at `400b6186`.

| Raw track scale | Name-table index | Meaning |
|---:|---:|---|
| -1 | 0 | CHROMATIC; any valid MIDI note is allowed |
| 0 | 1 | IONIAN (MAJ) |
| 5 | 6 | AEOLIAN (MIN) |
| 34 | 35 | LOCRIAN BB3 BB7 |

All 35 non-chromatic rows were extracted from `401b107c`, each 13 bytes long. The thirteenth byte represents the octave endpoint; its membership agrees with pitch class zero for every row. The complete mapping, names, degree bytes, and pitch classes are saved in `Digitone-OS1.42-scale-map.json`.

A PC check reproduced the membership routine's relative-note reduction and compared it with pitch-class membership for 128 MIDI notes, twelve root pitch classes, and all 36 settings: **55,296 cases passed**. This validates the extracted static mapping, not hardware execution. The related-note/chord routine's seven-interval table is a different representation and is not substituted for membership.

## 4. Later pitch adjustments traced to source

The audio interrupt selects alternating frame bases `80001fa4 + 0x0a90 * slot` at `4009c8fc–4009c926`. The per-voice parameter area begins at frame `+50`.

`4009b69e`, called at `4009d2ae`, copies `0x4a0` bytes from parameter source `800034c4+5a0` into the selected frame's parameter area `+5a0`. Consequently, frame fields `+5f7/+5f8` come from source offsets `+5a7/+5a8`, respectively.

The sound-to-voice loader `4009b99e` copies sound settings `+b2..` into `80003a64 + 0x94*voice` (`4009b9e8–4009ba02`). Since `80003a64 = 800034c4 + 5a0`, the resulting ownership is:

| Pitch field | Sound field | Established behavior |
|---|---|---|
| `frame+5f7+94*voice` | `settings+b9` | Bend depth; getter `4002f5f4`, setter `4002f624` clamps to 0..60 |
| `frame+5f8+94*voice` | `settings+ba` | Octave offset; getter `4002f690`, setter `4002f6c0` truncates to multiples of 12 and clamps to -60..60 |

The octave UI divides the stored value by 12 at `4007c1fc–4007c202`, and multiplies edited octave values by 12 before the setter at `4007c2a8–4007c2c2`. This establishes octave units, rather than an arbitrary semitone transpose.

At `4009d550–4009d568`, this octave offset is added to the snapped/coarse baseline before stateful pitch routine `400f02b4`. For values produced through the normal setter, adding an octave preserves pitch class. Sound deserialization at `400083d2` copies the stored byte directly, so the multiple-of-12 invariant is verified for the normal setter, not every conceivable serialized byte.

### MIDI bend chain

The MIDI status dispatch table's E entry points to `400db8ce`. This handler combines the two seven-bit data bytes, centers/scales the value, resolves its track, and calls `4009c51a` through a3 (`400db946`, `400db97e–400db982`). That writes signed controller data to `80004648` through bounded helper `4009b968`.

Descriptor `4018b388` connects `80004648` to smoothed output `800046a0`. The audio smoothing loop `4009d4d8–4009d530` updates that output. The pitch loop reads the track-indexed smoothed value at `4009d57c`, multiplies it by the sound's bend depth, and adds it after `400f02b4` at `4009d580–4009d594`.

This confirms that the later fractional contribution is pitch bend. A coarse scale lock that leaves this chain intact allows expressive bend between scale notes. It cannot promise that every instantaneous sounding pitch is a scale tone. Octave changes can also move the pitch beyond the earlier MIDI range check; the eventual synth limit behavior has not been established here.

## 5. Integration decision

Keep the coarse quantization candidate at `4009df9a`. The octave contribution preserves pitch class under its normal setter, and bend can remain expressive. This is a more precise V1 promise: **arp note selection follows the captured scale; octave and pitch bend continue to operate afterward**. Stateful glide/rounding remains a separate downstream behavior, not a reason to quantize the original held keys.

The most economical storage design to investigate next is a **type-zero event context encoding in +20..+27**, initialized at source creation and copied with the existing event. Accepted setup already copies its event into the per-track retained template at `4009de40`; an accepted context could therefore live in that template alongside the existing identity at `+40`, without adding a new global table. Additive/rejected setup must not overwrite the retained context. That is a design candidate, not an implemented change.

Before using it, complete the remaining proof: every type-zero producer and persistent held template initializes or invalidates context; raw copies/remaps retain the intended source track; no type-zero consumer reads those bytes; reused union events cannot pass validity accidentally; resets and stale identities reject context. Also retain the previously identified full-width overflow guard before both arp-result byte stores.

The next concrete deliverable can be a PC-only model of this tagged event encoding, pool reuse, template copying, and accepted-context lifetime. Its tests should include recycling a type-two pointer event into a type-zero note, a held-template replacement after a pattern change, and source-track remapping. No binary patch or hardware test is justified until the ownership proof closes.

## Verification

The earlier behavioral model was rerun: ten scenarios and 4,608 quantization cases passed. The new extracted scale mapping passed 55,296 membership comparisons. Original SysEx and decoded main-image hashes match the prior inspection. No firmware was repacked or modified.

Disassembly remains targeted static analysis. Raw reference scans can include data; arbitrary-window and skip-data output was used for discovery only. Conclusions above use mapped object relationships and coherent instruction sequences, not an assertion that scanning references recovered every possible indirect path.
