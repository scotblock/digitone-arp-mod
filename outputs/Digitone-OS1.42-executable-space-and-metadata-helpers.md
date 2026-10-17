# Digitone OS 1.42: executable space and actual metadata helper tests

3 October 2026. PC-only analysis and synthetic instruction tests. No firmware bytes were edited, no repacked image was produced, and no device was contacted.

## Result

Six metadata helpers have now been implemented as ColdFire instruction fixtures and executed against mapped test RAM. **898 assertions passed across 42,937 executed instructions.** Their metadata writes come from the executed instructions, replacing the earlier Python observer for these operations.

**A verified executable home has not yet been established.** The search eliminated a tempting but incorrect placement and identified an explicit allocation approach whose execution and installation still need checking. The synthetic addresses `50001000` onward are only harness addresses.

## Space audit

The main section spans `40000400..4024f4b0` (exclusive end). Startup at `4000053e` calls `4000045c`, which copies these initialized-data sources:

| Source | Destination |
|---|---|
| `40242000..402478f0` | `80000000` onward |
| `402478f0..4024f4b0` | `80008000` onward |

The next call, at `40000542`, invokes `400004b2`. Its loop clears **`40242000..431dc690`** in 16-byte units. Consequently, merely appending instructions at the current main-section end would place them inside startup-cleared RAM. The current image tail is data used before that clear, not spare executable storage.

The scan found 104 runs of at least 64 identical zero or FF bytes before `40242000`. The largest zero run is 2,064 bytes at `401fd47c..401fdc8c`; the final zero run is 876 bytes at `40241c94..40242000`. These are inventory entries only. Blank bytes do not establish that an area is unused: resources, lookup tables and alignment can contain them. No such run is approved as a code cave by this audit.

An explicit allocation can request **`15c70` bytes**, comprising the original `14100` bytes, the proposed `b70`-byte metadata table, and a further `1000` bytes for instructions at owner +`14c70`. This avoids borrowing undocumented allocator slack. The prior buddy-size arithmetic would still round that request to `20000`, but the actual allocator with this request has not been executed here.

This establishes a proposed reservation layout, not executable ownership. Before using it, we need a surviving source for the instructions, a bootstrap that allocates/copies them before hooks can call them, and verification of instruction fetch and cache handling at the allocated addresses. Startup contains CACR/ITT0 writes at `4000055a`/`40000564`; this audit does not infer their complete execution policy. The initialization bootstrap cannot itself depend on helpers that have not yet been installed.

## Actual helpers

Each helper takes an explicitly validated, aligned RAM entry pointer; the accepted record remains identity +0, snapshot +4, depth +8, and publication/binding +c. Helpers save SR, mask interrupts to level seven for their bounded operation, and restore SR exactly before return. Scratch registers are d0/d1/a0/a1; callee-saved registers and the stack are preserved in the tests.

| Helper | Behavior |
|---|---|
| `begin(record)` | Increment gate depth; refuse wraparound and invalidate publication at overflow. |
| `cancel(record)` | Decrement an outstanding gate while preserving prior context; unmatched cancellation invalidates publication. |
| `commit(record,id,snapshot,binding)` | Require depth one, nonzero identity, binding 0..3 and a valid snapshot or zero. Write the tuple, clear depth, publish validity last. |
| `read(record,id,binding)` | Return the snapshot only when depth is zero and publication, identity and binding match; otherwise return zero. |
| `copy(dst,src)` | Copy one candidate word, including self-copy. |
| `invalidate(entry)` | Clear one candidate word. |

Malformed snapshot words are rejected: missing validity bit, nonzero reserved bits, or scale index beyond 35. Zero snapshot deliberately commits ordinary-pitch fallback. Source-track bits remain part of the snapshot while playback binding is separate.

A commit attempted at a depth other than one invalidates publication and leaves outstanding depth unchanged. It cannot expose a partially accepted context; subsequent balanced cancellations leave fallback until a later successful commit. This is a conservative nested-path behavior, not a claim that nested same-track setup is expected on hardware.

## Evidence and limits

Tests cover all four bindings and all 36 scale encodings at roots 0, 60 and 127 (432 successful commit/read combinations); wrong identity/binding; busy and nested gates; balanced cancellation preserving prior context; malformed words; zero context; depth overflow; unmatched cancellation; copy/self-copy/invalidation; guards around the records; and exact SR restoration across several interrupt masks.

An observer inspects RAM before each commit instruction. Any observable published tuple is the complete new identity/snapshot pair. The observer only reads RAM; the helper instructions perform all metadata mutation. This checks store ordering in the bounded harness, not asynchronous hardware behavior.

The helper contracts deliberately require validated pointers. Owner/header resolution, event-address classification, stock active-list/selection gates, retained-identity checks, and actual wrappers that supply these arguments remain to be integrated. The custom interpreter is not an independently validated CPU emulator. Interrupt masking does not establish DMA or other-processor exclusion. Exceptions and hardware cache effects were not exercised.

The decoded image SHA256 remains `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.

## Next concrete step

Audit one complete installation route: where helper source bytes can survive startup, how a bootstrap reserves and installs them, and whether the allocated area supports coherent instruction fetch. Then connect these tested helper bodies to the setup/commit wrappers and exercise the actual stock caller with metadata mutations performed by instructions. The proposed startup hook remains unimplemented until that installation route is established.

Machine-readable evidence: `Digitone-executable-space-screening.json` contains startup disassembly and the padding inventory; `Digitone-metadata-helper-instruction-tests.json` contains helper disassembly, sizes, assertions and limitations. Reproduction scripts remain in the workspace under `work/screen-executable-space.py` and `work/test-metadata-helper-instructions.py`.
