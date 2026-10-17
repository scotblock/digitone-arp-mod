# Digitone OS 1.42: section descriptor and storage-reader limits

**Both routines are recovered from the supplied section 2, and the executed path forwards a larger main-section stored length without a stock-size clamp.** The storage reader transmits a 24-bit address. Complete updater/write acceptance and actual flash capacity remain unverified.

## Corrected code mapping and provenance

Section 2's decoded bytes contain a four-byte length prefix **7056**, followed by a coherent SRAM-linked image and four trailing bytes. The decoded total is **705e**. Mapping the image after that prefix at **80000400** means raw offset zero corresponds to **800003fc**. This mapping aligns the absolute descriptor call, descriptor routine, copy helper, hardware setup calls, and storage-code copy loop. The trailing word **79fa185a** has not been identified as a particular integrity algorithm.

The former **02000800** view followed the container destination/storage address. Its relative-only depack instruction tests still describe those bytes, but it was not the correct SRAM address view for linking absolute calls. In the corrected view, the former main descriptor/read routine at 020009dc is **800005d8**, and the former direct main-depack caller at 02000a58 is **80000654**. This is an address-mapping correction, not a firmware modification.

At **80000efc..80000f10**, provided code copies longwords from **80007300** to **8000f000**, stopping once the source reaches/passes **80007456**. The loop's rounded copy is 344 bytes. The copied block contains a 16-byte descriptor scratch area followed by the SPI read routine at **8000f010**, and a section-4 read/entry routine at **8000f100**. These byte and linkage anchors establish the routine's source. The preceding complete boot/SRAM installation path is not yet executed.

## Descriptor routine: 80005a88

On its first use, helper **80005a50** reads **32 bytes from storage offset 80000** into **80007a34**, then sets its cache flag at **80007a30**. The cached count is the header word at +1c, address **80007a50**. The descriptor routine scans 16-byte records from storage offset **80020**, in order, and stops at that count.

Each record is:

| Offset | Meaning in recovered use |
|---|---|
| +0 | Section ID |
| +4 | Section offset relative to storage/container base |
| +8 | Stored/compressed byte count |
| +c | Load destination |

On a matching ID, it optionally copies the complete record to the caller and returns 1. Missing IDs return 0 and leave the caller's output buffer unchanged. The header and records match the inspected ELE3 container layout. This scan does not independently validate a maximum count, length, destination, magic, or checksum; those may be validated in other paths.

PC cases executed the real descriptor and its copy helper for the original main stored length **925,444**, that length plus **4,096**, **200000**, **7fffffff**, and **80000000**. All matching records were returned without a size rejection. The descriptor tests supply a finite simulated storage table. They do not assert those large lengths are valid for the device.

## Main-section read caller: 800005d8

The caller requests ID 3 and takes its offset and stored length directly from the local descriptor. At **80000616** it adds **80000** to the offset, then calls **8000f010** with that address, the stored length, and fixed destination **40200000**. It subsequently passes the descriptor's destination to the depacker. There is no local stock-length comparison, staging-buffer limit, offset-addition overflow check, or descriptor-success check between lookup and read.

Executed stock and enlarged stored-length cases to the actual SPI routine's entry. The original descriptor produces address **83e40**, length **925444 decimal**, destination **40200000**. The enlarged descriptor forwards **929540 decimal** unchanged. These cases stop at the payload-read entry instead of pretending that actual modified compressed bytes were supplied.

A boundary fixture with offset **fff90000** wrapped the addition to **10000** without local rejection. A missing-main fixture reached the payload-read entry after the descriptor returned 0; its initially zero local descriptor yielded offset 80000 and length 0. Real stack contents need not be zero. This confirms the caller itself does not implement that failure guard; it does not establish a normal-device failure.

## Copied SPI reader: 8000f010

The code emits command byte **03**, then exactly three address bytes: bits 23..16, 15..8, and 7..0. Higher address bits are discarded. It drains four initial receive words, reads the requested payload bytes into the supplied destination, sends the final transfer command, and polls completion. The data loop compares the length as a signed longword; **80000000** skips payload reads rather than transferring 2 GB.

Executed the actual reader for lengths **0, 1, 17, 4,096, and 80000000**, plus an address above the 24-bit range. The MMIO model supplies ready/completed status and deterministic storage data; it does not stub out the read function. Verified the command bytes, receive count, exact copied bytes, and destination guards. Address **01880000** transmits the same address bytes as **00880000**.

There is no local destination-buffer bounds check, flash-partition check, or polling timeout in this routine. The effective practical bound still depends on flash capacity/partitioning, valid container descriptors, and available staging RAM. Simulated ready/completed hardware cannot establish device timing or error behavior.

## Result and remaining question

**43 checks passed across 15 recorded cases**, with an additional missing-ID scan check. The descriptor and read-code limits no longer depend on an unidentified external routine. Their local behavior does not reject a modest stored-length increase; that is meaningful support for the RAM-code route.

This does **not** certify updater acceptance of a firmware extension. Next: trace the update/write path that creates the storage container and establish flash slot/partition capacity and its length checks. Then test an actual extended-main compressed stream's overlapping read/write layout in the PC fixture before connecting relocated code to startup.

Original SysEx and main-image SHA-256 hashes remain unchanged. No firmware was patched, repacked, or sent to a device.

Evidence: `Digitone-section-descriptor-storage-results.json` and `Digitone-section-descriptor-storage-instructions.txt` in this output directory.
