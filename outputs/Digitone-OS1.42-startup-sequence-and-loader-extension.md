# Digitone OS 1.42: startup sequence and loader extension tests
**Subsequent mapping correction:** the descriptor and copied SPI reader are now recovered from section 2 under its SRAM linkage. The previously unresolved routine/provenance statements below are superseded by Digitone-OS1.42-section-descriptor-and-storage-limits.md. Earlier instruction tests used the container-address view; the new report supplies the runtime addresses.


**The proposed source-preservation/allocation/copy/erase sequence passed its PC tests. The recovered main-depack caller also accepts a valid synthetic decoded payload 4,096 bytes larger than stock. Complete updater/flash acceptance remains unverified.** These are separate results; neither constitutes an installed or hardware-tested mod.

## Executed proposed startup sequence

The PC driver executes two clear-routine clones whose instructions match the stock clear routine except for their start/end constants. Their ranges are **40242000..4024f4b0** and **402504b0..431dc690**. The temporary source **4024f4b0..402504b0** contains 4 KB of synthetic bytes.

After the two clears, the driver calls the complete stock allocator at **400dab8c**, requests **15c80**, clears that explicit allocation through stock memset, and copies the source to **owner+14c80** through stock memcpy. It then erases the temporary source through stock memset. Success returned owner **419a38c0**, destination **419b8540**.

The sparse RAM fixture initially includes dirty BSS samples at every 4 KB boundary and specific endpoints, lock/current-thread state, and source boundaries. The clear summaries remove every represented byte in their ranges and represent all other BSS bytes as zero. After both clears, only source contents remain nonzero in BSS. After copying and source erasure, the temporary BSS interval is zero and all other state is unchanged from immediately before erasure. Newly allocated heap bookkeeping and copied code are intentional post-clear writes, so this does not claim that the entire BSS remains zero after allocation.

The large repetitive clear loops are **summarized**, not individually stepped through millions of instructions. The summary checks the exact MOVEM/LEA/SUBQ/BNE bytes and zero registers, then reproduces the memory, register, flag, and iteration effects. It was compared against **17 fully executed stock-body iterations**, with identical resulting memory, registers, and SR. This limitation is recorded explicitly.

A pressure case allocates the entire heap through stock code after clearing, then attempts the enlarged request. The actual null return bypasses copying; the source is still erased and owner publication remains disabled. This checks local cleanup, not a verified return into ordinary device startup after an installation failure.

**18 startup-sequence checks passed.** Execution stops before ordinary cache/hardware setup. No owner pointer or executable readiness is published: relocation, destination validation, dispatcher installation, and the final continuation remain outstanding. The temporary clear clones exist only in PC instruction fixtures at synthetic addresses; they are not installed firmware hooks.

## Executed stock main-depack caller

Executed section-2 entry **02000a58**, including the actual depacker **02000878..020009da** and surrounding cache/control writes. This caller uses compressed source **40200000** and destination **40000400**. Tests keep them in the same physical address model: overlapping source and output accesses share bytes, rather than giving the decoder artificially independent input/output buffers.

| Synthetic decoded payload | Result |
|---|---|
| 4,096 bytes | Full instruction execution passed; compared against summarized execution |
| 8,192 bytes with a literal prefix | Full execution passed; literal-summary result matched |
| 2,420,912 bytes, matching stock decoded size | Passed |
| **2,425,008 bytes, stock plus 4,096** | **Passed** |

The large fixtures use a sufficient literal prefix to move the compressed-input cursor beyond the output overlap before the long backreference. A highly compressed tiny stream can overwrite its own unread input in this staging arrangement; testing size with independent buffers would miss that issue. The tested fixtures respect it. They contain repeated synthetic data, not Digitone instructions or a repacked main firmware section.

Long backreference loops and the large literal prefix are summarized after comparisons against full smaller executions. Output bytes, exact total write count, boundary contents, registers/SR in the comparison cases, and the stock control sequence were checked. **39 loader-probe checks passed.**

The depacker returns the decoded byte count. The caller then overwrites D0 while resetting cache controls and returns **0008c000**; it does not reject or compare the depacked size in this executed path. This closes the specific question of an original-main-size limit in the recovered main-depack caller. It does not prove every earlier loader stage accepts an extended image.

## Remaining acceptance boundaries

* The tested entry assumes compressed bytes are already staged at 40200000. The descriptor-provider call at **80005a88**, used elsewhere in section 2, and the earlier storage-read path have not been executed with a changed section descriptor.
* Actual extended-main compression and its read/write overlap trace remain untested. A synthetic stream proves size tolerance in this path, not the overlap safety of a future compressed mod.
* Device updater checks, container handling, storage limits, and flash layout have not been verified for an extension. Host tooling support is not evidence of device acceptance.
* The bootloader's resident dependencies are not all recovered from the supplied update. A direct mapping of the raw section-4 bytes did not yield a coherent descriptor-provider entry at 80005a88, so it is not treated as that routine. Its provenance/mapping needs establishment before interpreting it.

## Next bounded targets

Establish the section-descriptor provider and storage-reader mapping, then trace how the main compressed length is loaded and bounded. Separately, fit the proposed bootstrap and dispatcher into the justified resident interval, relocate helpers into the returned allocation, and execute their behavior there before any executable publication. A real startup continuation, allocation-failure behavior, and cache handoff must be tested at their actual insertion boundary.

Original SysEx and decoded-image SHA-256 values remain unchanged. No modified, repacked, or flashable firmware file was generated, and no device I/O occurred.

Evidence: `Digitone-proposed-startup-sequence-results.json` and `Digitone-loader-extension-probe-results.json` in this output directory.
