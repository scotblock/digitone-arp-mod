# Arpeggiator virtual-table inspection

Read-only analysis of the extracted OS 1.42 main image. Runtime addresses below use the supported base `0x40000400`. Firmware is unchanged; no flashable output was produced.

## Class identity and table boundaries

The candidate at **0x40179d34** is strongly established as the primary virtual-function address point for **ArpSetupMenuView**:

- word at 0x40179d2c: zero, consistent with the primary table's offset-to-top;
- word at 0x40179d30: pointer 0x40179d04, consistent with type information;
- type-information word at 0x40179d08 points to the string `16ArpSetupMenuView` at 0x401b7f83;
- the constructor writes 0x40179d34 into the object's first word;
- 19 consecutive code pointers occupy 0x40179d34 through 0x40179d7c;
- the next pair is `-4` and the same type-information pointer, beginning a secondary table rather than additional primary methods.

The negative-offset/type-information pattern repeats for object offsets 4, 8, 12, 16, 0x4c, and 0x68. Those match pointers installed by the constructor. Destructor thunks explicitly subtract corresponding offsets before forwarding, adding independent evidence for multiple base-class/subobject tables.

## Primary entries

Names below are provisional behavioural classifications, not recovered source symbols.

| Slot | Table address | Target | Interpretation |
|---:|---|---|---|
| 0 | 0x40179d34 | 0x40140b36 | Destructor candidate: resets table pointers, destroys members, forwards to base cleanup |
| 1 | 0x40179d38 | 0x40140bee | Deleting destructor candidate: calls slot-0 target, then apparent deallocation |
| 2 | 0x40179d3c | 0x4004f4ca | Arp-specific method; precise role unresolved |
| 3 | 0x40179d40 | 0x400d6938 | Shared getter for object field +0x28 |
| 4 | 0x40179d44 | 0x4004e59c | Display/render candidate: formats text and calls drawing-like helpers |
| 5 | 0x40179d48 | 0x400d6d46 | Shared view-framework method |
| 6 | 0x40179d4c | 0x400d6944 | Shared forwarding method |
| 7 | 0x40179d50 | 0x400d6db6 | Shared view-framework method |
| 8 | 0x40179d54 | 0x400d6950 | Shared setter for object byte +0x16 |
| 9 | 0x40179d58 | 0x400d695c | Shared method; exact role unresolved |
| 10 | 0x40179d5c | 0x400d6b5e | Shared method; exact role unresolved |
| 11 | 0x40179d60 | 0x4004f644 | UI update/timer candidate: decrements counters and refreshes `T%d ARPEGGIATOR` text |
| 12 | 0x40179d64 | 0x4004f218 | Arp-specific action; allocates an object after a condition/helper call |
| 13 | 0x40179d68 | 0x4004f31a | Arp-specific method; precise role unresolved |
| 14 | 0x40179d6c | 0x4004f3f4 | Arp-specific method; precise role unresolved |
| 15 | 0x40179d70 | 0x400d6ee4 | Shared forwarding method |
| 16 | 0x40179d74 | 0x400d6ef0 | Shared forwarding method |
| 17 | 0x40179d78 | 0x4004eb34 | Input/edit-dispatch candidate: nine-way jump table and settings helper calls |
| 18 | 0x40179d7c | 0x4004f10c | Context/action candidate; reads a setting and branches on global flags |

Slot numbering is zero-based from the primary address point, not a claim about a documented class interface. Several short functions use tail jumps; these were separated from following functions. The edit-dispatch function embeds a jump table, which must be treated as data rather than sequential instructions. The saved exploratory disassembly has bounded windows and is not a complete control-flow recovery.

## Correction to callback interpretation

The constructor's previously identified pair **0x4004e428 / 0x4004e448** is consistent with a captured C++ lambda callback and its manager:

- 0x4004e428 dereferences the captured object pointer and tail-calls shared routine 0x400d6aba;
- 0x4004e448 switches on operation values 0–3, returns type information, copies captured storage, allocates a copy, or frees storage;
- its type-information references lead to `ArpSetupMenuView` constructor lambda names.

Thus the manager is not a pitch-processing function. The callback might request a UI update; that particular meaning remains to be confirmed through the shared target.

## Concrete settings-storage leads

The rendering and editing candidates call three helpers that use an object's virtual slot at byte offset **0x28** to obtain a storage pointer, test it for null, and read adjacent bytes:

| Helper | Byte read from returned storage |
|---|---:|
| 0x4002ecea | +0x10f |
| 0x4002ee82 | +0x110 |
| 0x4002ef20 | +0x111 |

These are offsets within the returned storage, **not** offsets within ArpSetupMenuView itself. Exact parameter names remain unproven. The +0x111 value is rendered after adding one, suggesting a zero-based displayed parameter. The +0x10f and +0x110 values select display entries. All three helpers also have references near **0x40091500**, outside this arp UI region; that region is a promising next inspection target, although shared use alone does not establish sequencing or pitch generation.

## Next milestone

Inspect the nine-way edit dispatch with its jump-table targets, identify the setter paired with each storage getter, and examine the shared callers around 0x40091500. This should reveal what these arp fields represent and provide a route from screen settings into operating behaviour. No quantizer or arp note-emission function has yet been validated.
