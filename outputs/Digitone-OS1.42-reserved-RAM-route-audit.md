# Digitone OS 1.42: reserved RAM route audit

## Result

Follow-up: [version pinning, stock DDR geometry and shared-alias tests](Digitone-OS1.42-reserved-RAM-follow-up.md) now establish the 128 MiB configuration and rerun the bounded suites with aliases sharing memory. The earlier statement below that alias operation was not emulated describes the initial pass only.

The Elekloader-style route is a viable **PC-tested replacement for the custom heap-backed code/context allocation**. It passes 52 startup/storage assertions and 5,475 relocated arp-integration assertions on OS 1.42 instructions. It removes the tested need to enlarge the stock allocation or publish that allocation before application startup.

It is not yet a certified OS 1.42 Elekloader port or a hardware-ready modification. Complete ownership of the region, computed accesses, DMA, real cache behavior, and all live/queued producer paths remain unproven.

## Address evidence

Elekloader's [Digitone profile](https://github.com/irpina/elekloader/blob/main/elekloader/devices/digitone_mk1.py) reserves `47be0000..47c00000` for mods and describes its OS 1.43 memory observations. Its [core boot code](https://github.com/irpina/elekloader/blob/main/mods/core/core.s) copies mod code and zeroes mod data before stock clearing and cache activation. Those measurements are useful evidence for the design, but are not automatically OS 1.42 measurements.

The following anchors were checked directly in our unchanged 1.42 image:

| Item | OS 1.42 evidence | Relation to proposed region |
|---|---|---|
| Early call at `40000538` | `4eb940001df4` | Exact match for the core's displaced call |
| Entry stack instruction at `400004f2` | `movea.l #48000000,a7` | Region ends 4 MB below entry stack top |
| Stock startup clear | `40242000..431dc690` | Entire proposed region lies above it |
| Previously executed stock heap | `419a38c0..429a38c0` | Entire proposed region lies above it |
| Reserved code/data budget | `47be0000..47c00000` | 128 KB |
| Candidate uncached mirror | `4fbe0000..4fc00000` | Included in reference screening; alias operation itself not emulated |

The rooted recursive disassembly screen starts from application/thread entries, all 119 constructor callbacks, initializer, and arp sites. It reaches 55,354 instructions and finds no direct operands into either candidate interval. It leaves 4,200 indirect edges and two unknown decode boundaries unresolved. This is a useful screen, not exhaustive control flow or a global computed-pointer/bulk-write ownership proof.

An even-aligned raw four-byte scan finds five cached-range and six candidate-mirror values. None appears as a region operand in the rooted screen. Their surrounding bytes have table or payload characteristics, but this audit does not certify every occurrence's data owner; arbitrary data matches should neither be called proven pointers nor silently discarded as proof of safety.

## PC placement and initialization

| Fixture component | Placement/size |
|---|---|
| Relocated helper code, initializer wrapper, trampoline | `47be0000`, 1,712 bytes |
| Private metadata pointer | `47be1000`, 4 bytes |
| Context header and records | `47be1004`, 2,928 bytes |
| Occupied end, exclusive | `47be1b74` |
| Total span including alignment gap | 7,028 bytes |
| Appended-source boot fixture | `4024f4b0`, 92-byte boot routine; `.run` source begins at `+100` hex |

The fixture uses the core's copy-before-clear ordering and adds initialization of our context header/private pointer. It is a translated test routine, not a compiled or installed Elekloader core. It does not reproduce the core's timer setup.

Existing helpers retain their metadata-offset convention through a **private mod pointer** whose value is `metadata_base - 14100`. Their accesses to the stock pointer location are redirected to this separate pointer. The real stock owner at `4199d590` remains under stock control. The private compatibility value is not an actual heap allocation.

Absolute helper relocations include internal return labels as well as function entries. The allocation-invalidation wrapper exposed one such internal reference during integration testing; the relocation was corrected before the passing run. No original firmware bytes were changed.

The startup test uses the entry stack top at `48000000`, executes the boot copy, replays the original vector-base call, and executes the original stock clear. The existing clear-loop summary is retained. Copied bytes and destination guards survive; metadata starts unready with zero contexts; stock cache-control instructions execute after copying. Source bytes are supplied as an already-decoded RAM extension, so this test does not establish a newly extended container's complete loader path.

The wrapper then calls the full stock initializer through its normal caller at `4009bcb8`, with the actual `9e` argument. It executes 35,007 instructions to the caller-return boundary, leaves all 64 stock records linked at their original `504` stride, and publishes context readiness only after stock initialization returns. Reentry clears stale snapshots while preserving both pointers and executable bytes.

This demonstrates placement outside the tested clear/heap operations. Four MB of separation from the initial stack top is not, by itself, a proof of every later stack's maximum extent.

## Arp integration

The existing instruction-level integration cases were rerun using the relocated bodies and separate reserved metadata. The suite passes:

- 5,256 stock-membership quantizer comparisons against the independent nearest-note oracle.
- Four track pipelines from the supplied producer-finalization boundary through stock acceptance, selection, scheduling, and the pitch insertion wrapper.
- Context guard rejection, accepted-snapshot stability, destination-track precedence on remapping, negative selection bypasses, and ordinary-note equivalence to stock.
- Actual fixed-event recycling and exhausted-pool return behavior.
- Preservation of the separate stock owner pointer in the four pipeline states.

The integration suite supplies an initialized context header; boot/initializer behavior is tested separately. Producer entry is a recovered finalization boundary, with other input fields and writer gates supplied. It does not establish complete held/live/queued capture or copy coverage, full asynchronous ordering, or real audio deadlines.

## Decision and next step

Use this route for further PC development. The custom early heap allocation, enlarged stock allocation, and allocation-survival audit can be retired as requirements of this **alternative design**. Existing arp-context and event-ownership rules still apply.

Before building anything flashable, pin the Elekloader source revision, complete a 1.42 device/core profile or deliberately select a supported firmware target, and validate the reserved area in a complete OS 1.42 runtime model, including stack and candidate uncached accesses. Package helpers as relocatable `.run`/`.bss` sections so Elekloader can place them alongside other mods; the fixed addresses here are PC fixtures, not a proposed SDK manifest. Then connect the remaining input producers and retest cold boot through actual playback.

Evidence: [startup/storage results](Digitone-reserved-RAM-route-results.json), [arp integration results](Digitone-reserved-RAM-arp-integration-results.json), and [reference screen](Digitone-reserved-RAM-reference-screen.json).

Original SysEx and main-section hashes remain unchanged. No firmware was repacked, no flashable output was produced, and no device I/O occurred.
