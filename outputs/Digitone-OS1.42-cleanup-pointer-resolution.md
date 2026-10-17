# Digitone OS 1.42: cleanup pointer origin and model correction

## Finding

The `00000041` pointer was caused by incorrect stack addressing in the PC interpreter. It was not a pointer captured from the Digitone, and the trace does not implicate the proposed context allocation.

The interpreter applied a classic 68000 exception: byte predecrement/postincrement on `a7` adjusted by two bytes. ColdFire instead adjusts every address register, including `a7`, by the operand size: one byte for a byte operation. This is specified in sections 2.2.4 and 2.2.5 of [NXP's ColdFire programmer's reference](https://www.nxp.com/docs/en/reference-manual/CFPRM.pdf).

The shared interpreter's four read/write predecrement/postincrement cases are now corrected. Firmware files remain unchanged.

## Exact provenance

The consumer at `4000f9b4` constructs temporary objects on its stack. Two relevant call sequences contain:

```text
4000fa26  clr.b -(a7)
4000fa28  subq.l #3,a7
...
4000fada  clr.b -(a7)
4000fadc  subq.l #3,a7
```

Each sequence reserves four bytes on ColdFire: one byte plus three bytes of padding. The old interpreter reserved five, shifting subsequent stack locations and allowing a later stored pointer to overlap an earlier local object.

The recorded faulty trace shows:

| Stock instruction | Modeled destination | Value |
|---|---|---|
| `4000fa60`, clearing a temporary pointer | `30001f73..30001f76` | `00000000` |
| `4000faf0`, storing a returned pointer | `30001f76..30001f79` | `41da38d0` |
| `4000fb0c`, clearing the next temporary | `30001f72..30001f75` | `00000000` |

The bytes at `30001f73..30001f76` therefore become `00 00 00 41`. Cleanup at `4000fb50` passes `30001f73`; `4012c34a` loads its first word into `a2`, producing `00000041`. The next field read at `4012c350` attempts address `00000045` and stops the interpreter.

With correct byte adjustment, the recorded writes become:

| Instruction | Corrected destination | Value |
|---|---|---|
| `4000fa60` | `30001f74..30001f77` | `00000000` |
| `4000faf0` | `30001f78..30001f7b` | `41da38d0` |
| `4000fb0c` | `30001f74..30001f77` | `00000000` |

Cleanup now receives `30001f74`, whose pointer field remains zero. It returns normally; the trace records execution of `4000fb54` and `4000fb58`, beyond the formerly failing call. No arbitrary pointer replacement, cleanup bypass, or new firmware patch was used.

## Verification

- Twelve direct addressing checks cover predecrement writes and postincrement reads for `a0` and `a7`, each at byte, word, and longword widths.
- The corrected continuation runs 10,000,000 instructions from the saved, byte-validated post-decompression state. It passes the old cleanup boundary and preserves the owner pointer and entire proposed allocation.
- The shared interpreter's existing payload-lifecycle suite passes all 50 checks.
- The machine bootstrap suite passes all 74 checks.
- The placed bootstrap/initializer suite passes all 54 checks.

The continuation currently ends at its execution budget in the stock allocator scan at `400dadd2`, called from the next parsing stage. That is an execution bound, not a recovered firmware timeout, and it does not establish a device hang.

## Limits and next step

This closes the specific `41` pointer provenance and stack-adjustment defect. It does not complete application-startup certification. The corrected continuation resumes a checkpoint whose earlier constructor execution preceded the correction; the full prefix must also be rerun with the corrected shared interpreter before claiming an end-to-end result.

Next, check and accelerate the bounded stock allocator scan if needed, then rerun the complete startup prefix with correct ColdFire stack semantics and continue to the initializer. Peripheral fixtures, initial thread selection, physical interrupts, and cache coherence retain their earlier limitations.

Evidence: [faulty writer trace](Digitone-cleanup-pointer-trace.json) and [corrected continuation results](Digitone-corrected-stack-pointer-results.json).

Both original firmware files retain their recorded hashes. No repacking, flashable output, or hardware I/O occurred.
