# OS 1.44 helper contracts: isolated PC tests

The compact context/pitch helpers have been adapted to 1.44 and pass the isolated checks below. The PC helper remains 2212 bytes; 17 instruction-contained absolute operands were changed. Its internal helper layout, metadata format and 420-byte pitch lookup table are unchanged. The original firmware, 1.42 main program and original packed helper image retain their hashes.

The new derived helper SHA-256 is `0c5d58bf72828102b6f1fe19277e633ef97503fdcb727fd2a5f728ded2a8e299`. It exists only as an isolated PC test image. No stock-session or startup installation was performed and no flashable firmware was produced.

## Version-specific contracts

- Event pool: `0x419ebe2c`, 72-byte event stride. Physical cache candidates: `0x419f182c`; this cache relocation is different from the pool's relocation. The actual cache-base operand is at `0x40094c38` in stock 1.44.
- Selected identity records: `0x413915f4`; acceptance cache: `0x41392fcc`; selection gates: `0x413926e4`; commit neighborhood global: `0x41392fbc`.
- Producer continuation: `0x400947f4`; selector entry/return continuation: `0x40097a94` / `0x4009e694`; caller-commit continuation: `0x4009e738`; pitch continuation: `0x4009e88a`.
- Stock memcpy/memset: `0x400fbad8` / `0x400fbb20`. Allocator displaced-prologue continuation: `0x400ffff8`. Stock pool initializer continuation: `0x400ffeda`.

Exact PC hook sites and expected stock bytes are recorded in the companion summary JSON. Address correspondence does not establish broader storage ownership.

## Passing checks

| Check | Cases | Result |
| --- | ---: | --- |
| Context/helper differential checks | 13,514 | Registers, materialized status, metadata and event/cache outputs agree between the two ported reference layouts |
| Cache bounds | 291 | Exact alignment/range checks |
| Cache read/store/clear and invalid headers | 4 + 5 | Valid operations and fail-closed storage behavior |
| Cache producer refresh / invalid captures | 8 + 16 | New captures replace stale candidates; invalid root/scale, busy and fault cases clear them |
| Stock raw-copy interfaces | 8 | Registers, status and copied bytes match stock 1.44; metadata follows the copy |
| Stock producer/pitch interfaces | 4 tracks | Displaced instructions, registers/status, event preservation and fixed-point output checked |
| Commit / allocator return / before-after continuation | 40 / 8 / 20 | Stack, storage and return interfaces match the reference contracts |
| Direct reset | 7 | Ready/not-ready cases initialize; invalid header, null pointer and argument cases stop at the existing failure loop without context mutation |
| Stock cancelled-note consumer gate | 4 tracks | `+0x0C = -1` reaches release before any custom helper, even with valid-looking retained metadata |
| Quantizer against extracted 1.44 scale rows | 13,824 | All 36 scale selections, every note 0–127 and roots 0, 60, 127 agree with an independent nearest-note oracle |

The 35 non-chromatic 13-byte scale rows occupy a unique byte-identical 455-byte table at `0x401d5238` in 1.44, with two operand references. The chromatic sentinel remains raw scale -1. The quantizer oracle uses these extracted 1.44 rows rather than assuming the old mapping.

## Cancellation and limits

The stock consumer's cancellation gate remains upstream of the helper insertion points. Isolated tests temporarily attach downstream hooks and execute the real rejection branch; no helper is entered. The pitch helper is not an independent cancellation checker and must never be called as a way to reactivate a cancelled event.

These tests use explicit event, cache, selection and ready-header fixtures. The before/after tests stop at selector entry and the return continuation; they do not yet execute the changed stock selector together with the helpers. Direct reset tests are not a startup installation, setup-failure recovery or producer-shutdown proof. No assertion of hardware timing, cache coherence, complete storage ownership or eligible old-scale retention across pattern replacement follows from these results.

## Next step

Run the actual 1.44 selector and caller with the ported helpers in a PC stock session, validating entry/return state before attempting controlled playback integration. Keep startup installation separate until that integration passes.

Detailed evidence beside this report: `Digitone-OS1.44-helper-contract-summary.json`, `Digitone-OS1.44-helper-differential.json`, `Digitone-OS1.44-helper-copy.json`, `Digitone-OS1.44-native-helper-ABI.json`, `Digitone-OS1.44-outer-helper-ABI.json`, `Digitone-OS1.44-helper-reset-cancellation.json`, and `Digitone-OS1.44-scale-contract.json`.
