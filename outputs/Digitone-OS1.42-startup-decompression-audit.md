# Digitone OS 1.42: decompression and startup continuation

## Result

The selected startup asset now reaches the stock decompressor's terminator. Stock instruction execution, with a separately checked backreference-copy loop summary, produces exactly the same 2,738,180 output bytes as an independent bounded decoder. The proposed owner pointer and entire allocation remain unchanged through decompression and the subsequently executed startup interval.

The initializer has **not** been reached. After another 7,245,181 instructions, the PC interpreter stops at `4012c350` on an unmapped read at `00000045`. The cleanup routine has loaded pointer `00000041` into `a2` and is attempting to read its field at `+4`. This is a new model boundary requiring provenance analysis, not evidence of a physical device failure or of an overwrite of the proposed context storage.

## Embedded asset structure

Startup selects source `401c40a0` or `401cef90` according to the flag tested at `4008c9f8`. Both copies contain the same compressed stream and decode identically.

| Field | Value | Evidence |
|---|---|---|
| First big-endian word | `0000aee8` = 44,776 | Exact compressed bytes consumed through the terminator |
| Second big-endian word | `003ff538` = 4,191,544 | Equals the additive sum of those compressed bytes |
| Payload | Begins at header `+8` | Stock code explicitly advances its input pointer by eight |
| Decoded length | `0029c804` = 2,738,180 | Stock return calculation and independent decoding agree |
| Destination | `40508eac` through `407a56af` inclusive | Actual output pointers and byte comparison |
| End pointer | `407a56b0` | `aa00` bytes below the next caller-supplied buffer at `407b00b0` |

The second header word therefore has evidence for a compressed-byte checksum interpretation; it is **not** the decoded output length. The stock decompressor skips both header words. This audit does not establish that the caller validates that checksum or supplies an enforced output bound.

The decoded output starts with `beefbace` and includes `NEW PROJECT`. Its SHA-256 is:

`da9da2b7cf6280ee09290ccbbd5d00121b53767e8a13655bf87ea808db2d111a`

## Validation method

The independent decoder follows the recovered literal, bit-prefix, repeated-offset, length, and overlapping-backreference rules. It uses 32-bit wrapping for the offset calculation, which is necessary to recognize the terminal marker correctly. It enforces its own compressed-input and 8 MB output bounds; those guards belong to the analysis tool, not the recovered firmware.

The stock execution retains all bit and offset decoding and branch decisions. Only the byte-copy sequence at `400ee404` through `400ee40a` is summarized. Five comparisons against unsummarized stock execution cover lengths 2, 7, and 100 and distances 1, 3, 20, and 31. They compare registers, status flags, and surrounding memory, including overlapping copies. The summary copies in forward order and finishes with the same zero loop counter and flags.

From the first match to the return-size calculation, the run executes 2,170,835 interpreter instructions and summarizes 10,883 match copies. It checks the entire output against the independent decoder, the returned size, the exact input cursor, and preservation of the proposed allocation. Instruction decoding is cached for speed without changing decoded instruction semantics.

The independent checks also reject a truncated header, a truncated stream, and an insufficient PC output limit. These are analysis safeguards rather than claims about stock failure handling.

## Remaining startup boundary

After the decoder's stock epilogue, execution proceeds into the asset-consumer and cleanup path. At the failing boundary:

- PC: `4012c350`, instruction `move.l 4(a2),d0`.
- `a2`: `00000041`, loaded by `4012c34a` from the cleanup argument's first word.
- `a0`: `30001f73`; `a7`: `30001f42`.
- Interpreter failure: unmapped four-byte read at `00000045`.

The cleanup routine at `4012c344` treats that first word as a pointer, then decrements reference counts and conditionally dispatches destruction through virtual function pointers. We have not established why the modeled argument contains `41`, whether an earlier modeled instruction or fixture supplied it incorrectly, or whether missing state changes the selected consumer path. Supplying an arbitrary replacement pointer or skipping cleanup would invalidate the continuation, so neither was done.

The next focused task is to trace writes to this cleanup argument and its containing stack object, identify its initializer and actual caller, and compare the relevant interpreter semantics and fixture preconditions. Once that pointer is validly explained, resume the same path to `400f0504` and execute the wrapped initializer with its actual argument.

## Scope and evidence

[Startup execution results](Digitone-startup-decompression-results.json) record 17 passing assertions and the remaining boundary. [Independent decoding results](Digitone-independent-decompression-results.json) record eight checks, both asset copies, and checksum evidence.

The SPI/UART responses, initial scheduler boundary, timer delivery before blocking, and hardware window remain explicit PC fixtures. Interrupt entry/return, asynchronous scheduling, physical cache coherence, and global executable-space ownership remain unverified. Output bounds are established for this decoded asset, not for every malformed input or every startup configuration.

Both original firmware hashes remain unchanged. No firmware file was modified or repacked, no flashable artifact was produced, and no hardware I/O was performed.
