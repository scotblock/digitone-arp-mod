# OS 1.42: first code-analysis milestone

All work remains offline. No firmware was modified or rebuilt.

## Disassembly now available

Installed Capstone 6.0.0a11 only in the workspace's analysis dependency directory. Its ColdFire mode decodes coherent startup and UI code. This is an alpha disassembler and supports the combined ColdFire instruction set; its output does not identify the exact CPU variant. Selected byte encodings and absolute references were checked directly against the extracted image. Arbitrary window starts can produce incorrect instructions, so the meaningful arp window was restarted at an apparent function prologue.

Primary tool references: [Capstone releases](https://github.com/capstone-engine/capstone/releases) and [ColdFire mode definitions](https://github.com/capstone-engine/capstone/blob/next/include/capstone/capstone.h). Ghidra also provides a [ColdFire language definition](https://github.com/NationalSecurityAgency/ghidra/blob/master/Ghidra/Processors/68000/data/languages/68000.ldefs).

## Main-image completeness and load address

The main image's initial big-endian word is `0x400004e8`. At that address, assuming base `0x40000400`, code sets up a stack at `0x48000000`, writes peripheral registers, calls initialization functions, and eventually calls `0x4012b344`. This is strong evidence that the initial word is an entry pointer and the proposed load base is correct.

Startup calls a data-initialization routine at `0x4000045c`. It copies:

- image range `0x40242000..0x402478f0` to RAM starting `0x80000000`, then clears through `0x80008000`;
- image range `0x402478f0..0x4024f4b0` to RAM starting `0x80008000`, then clears through `0x80010000`.

The exclusive source endpoint `0x4024f4b0` minus image base `0x40000400` equals **2,420,912 bytes**, exactly the decoded main-image size. This substantially reduces the earlier concern that input-exhaustion decoding had cut off the main image. It is evidence from the image itself, not a formal proof of every compressed-stream boundary or updater acceptance rule.

These RAM copies matter for later cross-reference work: some initialized objects use their runtime RAM addresses rather than their stored file addresses.

## Arpeggiator UI entry located

An apparent constructor begins at **0x4004ef38**, main-image file offset **0x4eb38**:

- saves registers and receives an object pointer;
- pushes the `ArpSetupMenuView` string;
- calls shared routines also used by `ScaleMenuView`;
- installs several pointers into the object, including `0x40179d34` at offset zero;
- initializes buffers and registers callback objects.

This strongly suggests the arp setup-view constructor. Pointer `0x40179d34` is a candidate virtual-method table, requiring table inspection before naming individual methods.

One callback pair installed by this constructor is **0x4004e428 / 0x4004e448**. Those addresses are concrete next targets for following the view's actions into arp settings. They are not yet identified as pitch generation or note emission.

The musical-scale name pointer table and `ScaleMenuView` anchors from the previous report remain useful, but the timing/length scale view must not be confused with pitch-scale handling.

## Current assessment

The original OS is sufficiently readable to proceed with structured reverse engineering. We now have a supported load-base hypothesis, coherent ColdFire code, evidence for main-image completeness, and a concrete arp UI function. We still have **no validated arp pitch-generation function, musical-scale quantizer, or patch location**.

Next analysis should inspect the candidate arp virtual table and registered callbacks, trace settings into storage, and trace musical-scale table references into pitch mapping. A full Ghidra project would make this substantially easier through function recovery and decompilation; the current workspace disassembler can continue supplying targeted evidence without rebuilding firmware.
