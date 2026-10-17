# Startup continuation design and 1.44 RAM reservation

## Result

A 280-byte scratch machine-code startup prototype passes 33 controlled cases. Instead of the current failure loop, it disables the mod's context pointer and executes the recovered stock initializer. It has not been placed in the helper image, copied at startup, or integrated into E03. The reservation remains unproven; this report adds a version-specific bounded map, not exclusive ownership certification.

## Continuation contract

- Save registers and incoming status. Validate the known initializer argument and exact fixed-layout compatibility pointer `47bccf04` before any metadata dereference. Invalid/null/misaligned/out-of-region pointer values cannot choose an arbitrary metadata address.
- Validate magic, version and size at the fixed metadata base `47be1004`. For valid state, clear readiness before clearing the context records. For invalid state, write zero to private pointer `47be1000`, leave metadata untouched, and continue stock initialization.
- Restore the incoming interrupt level before invoking the stock initializer through existing displaced-prologue trampoline `47be0642` → `400ffeda`. Keep the original argument and returned D0. This does not hold IPL7 throughout the stock initialization as the present wrapper does.
- After stock returns, mask bookkeeping briefly and revalidate the expected pointer/header before publishing readiness. If pointer/header changed, disable the pointer instead. Restore saved registers/status and return.

Zero pointer is the existing runtime helper's unavailable-context condition. The prototype relies on that contract, already isolated-tested; it does not prove full playback after startup fallback. All validation addresses are fixed under the current layout. Exact-pointer validation does not prove that the fixed region is physically owned, accessible or undamaged.

## Passing test matrix

Eleven modes × incoming IPL 0, 3 and 7:

1. Valid metadata.
2. Initially unready metadata.
3. Bad magic.
4. Bad version.
5. Bad size.
6. Null pointer.
7. Out-of-region pointer `ffffffff`.
8. Misaligned pointer.
9. Unexpected argument 157.
10. Pointer changes during stock initialization.
11. Header changes during stock initialization.

Each reaches the original caller return, restores stack position, preserves D1-D7/A0-A6, passes the incoming IPL into stock initialization and restores it on exit. Stock event-pool writes and return value match a direct call to the recovered stock trampoline on the same capture. Valid/unready modes clear contexts and publish ready; all other modes end with pointer zero. Early-invalid modes leave metadata unchanged. The unexpected-argument test covers 157 only; it does not certify arbitrary counts or make stock initialization safe for arbitrary input.

Timers, IRQ/DMA producers and real exception unwind do not run in these isolated calls. The deliberately injected pointer/header mutation is a code hook, not natural concurrency proof. Exceptions/bus faults, a corrupted executable/copier, invalid stack or a stock initializer that never returns remain outside the continuation's recovery contract.

The prototype runs at scratch address `47f40000`. Its 280 bytes exceed the old reset-wrapper span (`47be055c..47be0642`, 230 bytes) by 50 bytes. The current helper image ends at `47be08a4`, below private pointer `47be1000`; there is 1,884 bytes of intervening space. Placement/relocation and copier length must be designed and tested before integrating anything. Existing images and helper bytes are unchanged.

## Reservation checks against actual 1.44

| Item | Evidence and implication |
|---|---|
| Startup clear | Stock instructions `400004ba..400004dc` clear `4028f000..4322ae60`; they do not reach `47be0000`. These differ from the profile's originally measured 1.43 numbers. |
| Entry stack | Stock `400004f2` sets A7 to `48000000`. The reservation ends at `47c00000`, leaving a 4-MiB gap; this is separation, not a stack high-water proof. |
| Current occupied region | `47be0000..47be1b74`, 7,028-byte span, within the 128-KiB candidate reservation. |
| Heap observation | Stopped 1.44 capture has globals `4024005c=419f20a0`, `40240064=429f20a0`, `40240068=14`, `4024006c=100000`. The base/end and 16-byte-unit count are consistent with a 16-MiB heap extent well below the reservation. These are observed configuration values; initialization/writers and every allocator path still require verification before treating them as an enforced bound. |
| Constructor inventory | Sixteen literal `JSR 4000170c` sites are recorded with preceding instructions. Dynamic/wrapper/relative task construction is not covered. Full task stack ranges and maximum interrupt nesting remain pending. |
| Alias word screen | Seventy-one aligned raw words fold into the candidate under the screening alias rule. Examples include short-branch encodings spanning adjacent instructions, so these are not 71 recovered writes/pointers. No ownership conclusion follows from raw matching. Computed pointers and DMA are not covered by this inventory. |
| Elekloader profile | The pinned profile supports 1.44, but its ownership rationale explicitly starts from measurements on 1.43 plus unchanged-address/no-mapped-page observations. Useful corroboration, not an independent 1.44 stack/DMA guarantee. |

The next bounded map task is to recover the 1.44 heap initialization bounds, actual task constructor stack ranges and DMA destination windows. Then target reset/project-load writers against that map. Do not return to an unbounded global alias investigation based solely on the raw-word screen.

## Next integration work

First verify fallback through continuous application startup and stock pitch behaviour with context unavailable; test whether any path unintentionally re-enables the pointer. Decide placement in the existing code/table gap and account for copied-code length/cache handoff. Only after those checks and the reservation map are reviewed should a new PC-only candidate be built. The startup-menu DIN route remains the chosen installation investigation; application USB freeze remains outside V1's critical path.

## Artifacts and preservation

- `work/test-os144-startup-fallback-design.py`
- `outputs/Digitone-OS1.44-startup-fallback-design-checks.json`
- `work/audit-os144-reservation-map.py`
- `outputs/Digitone-OS1.44-reservation-map-checks.json`

E03 remains unchanged and PC-only. No firmware build or device I/O occurred.
