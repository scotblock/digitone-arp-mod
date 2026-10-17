# Digitone OS 1.42: 1,024-byte candidate investigation

The zero run at `401fbf8c..401fc38c` cannot currently be used as a 1,024-byte code interval. Recovered stock readers can reach its final 512 bytes through signed indexing. Its first 512 bytes remain unverified; even granting those bytes, the current layout would still need 302 additional bytes.

## Concrete stock readers

Function `40098fd4` receives a parameter structure. Its stock caller at `40096a30` passes `a2+542`, then calls it at `40096a40`.

* At `40098fe4`, `MVS.B +4(a0),d0` sign-extends the parameter. `40098fe8` loads table base `401fc48c`; `40098ff6` reads `table + 4*d0`. Parameters -128 through -65 address `401fc28c..401fc38c` exclusive, i.e. the final 256 bytes of the zero run. There is no bounds clamp in this recovered slice.
* At `40099022`, `MVS.B +2(a0),d2` sign-extends another parameter. The value is saved at stack offsets +2c and +30, with a second signed-word extension. At `4009907a` the table base is `401fc38c`. The comparison at `4009908a` rejects only values greater than 63; negative values take the indexed read at `40099092`. Parameters -128 through -1 read `401fc18c..401fc38c` exclusive: the final 512 bytes of the zero run.

The arithmetic and exact addresses are recorded in the JSON evidence.

These bytes are integer lookup data consumed by MAC-heavy signal-processing code. The earlier description of the neighboring data as floating-point was an unsupported interpretation of raw bytes; it should not be used as an ownership claim.

## PC verification and limits

Executed the unchanged recovered reader slices for all 256 parameter-byte values in each path: 512 cases. Verified signed conversion, exact table addresses, returned stock values, and the constant fallback for values 64..127 in the second reader. The union of candidate reads is exactly `401fc18c..401fc38c`, 128 four-byte entries / 512 bytes.

The parameter bytes were supplied by the fixture. Full upstream parameter writers and normal-device eligibility of negative values have not been established. These tests establish a concrete potential stock read overlap; they do not establish that a particular negative setting occurs during normal playback. Excluding those values would require an upstream proof. The first half is also not certified free merely because these two readers do not reach it.

## Consequence and next investigation

Current code needs 1,678 bytes; the earlier bounded resident interval provides 864, leaving 814. The best possible contribution from this candidate after preserving these reader ranges is 512 bytes, leaving 302. Therefore this candidate alone cannot solve placement even under favorable assumptions.

The next useful placement target is the earlier 2,064-byte zero run at `401fd47c..401fdc8c`: trace the indexed readers based at `401fcc8c`, the explicit read at `401fdc88`, and their input limits to determine whether any subinterval is usable. A read at one endpoint does not establish ownership of the whole run, but it prevents using it wholesale. If no adequately bounded resident interval emerges, evaluate an allocated-RAM installation route, including executable permissions/cache behavior and initialization lifetime, before implementing it.

Original SysEx and decoded-image hashes still match their recorded values. No firmware was modified, repacked, or sent to a device.

Evidence: `Digitone-zero-table-candidate-audit.json` and `Digitone-zero-table-reader-instructions.txt` in this output directory.
