# E04 instruction correction: PC-only overlay and startup results

9 October 2026. All five unsupported stores are corrected in separate raw PC overlay files. Original E04 SYX, MAIN, payload, user emulator cards and saved-mirror source remain unchanged. No packaged firmware was built or transmitted; the physical Digitone remains on working stock 1.44.

## Result

The corrected overlay passes the documented MOVE-combination check and existing ISA_C decoder checks throughout the audited custom code. With those checks enforced during actual custom-code execution, both default and restored-project startup clear the logo. Two injected context failures also complete startup with the mod disabled.

All 33 isolated fallback contract cases pass using the corrected code, including full incoming SR/condition-flag restoration, register and stack preservation, stock initializer return/pool equivalence and invalid-context handling. This establishes a tested PC correction for the five definite instruction defects. It does not confirm the physical freeze's fault PC or establish hardware readiness.

## Concrete changes

The copier's four immediate-to-absolute stores now load each constant into D1 and store D1 to the same absolute destination. After the four writes it restores D1 to zero, its known value after the clear loop, and tests the length word to reproduce the original final condition flags. A paired isolated execution compares all D0–D7, A0–A7, SR and continuation PC against the old copier; all match. Private metadata also matches, and the corrected resident payload is copied exactly.

The copier grows from 94 to 110 bytes. Its end moves from `4029c50e` to `4029c51e`, within the original 256-byte staging interval. The source payload still begins at `4029c5b0`, leaving 146 padding bytes. The initial loops and their branches are unchanged; only the final tail-jump moves, still targeting `40001df4`.

The fallback ready store at `47be0998` becomes:

```text
MOVEQ #1,D0
MOVE.L D0,47be1010
NOP
```

Bytes: `700123c047be10104e71`. These occupy the same ten bytes. D0 is scratch within the fallback's saved frame; the stock initializer's return value is restored from that frame before return. No fallback branches or helper entries move.

Payload length remains 2,492 bytes, copied as 623 longwords. The fallback remains 280 bytes and ends at `47be09bc`. Existing source/copy spans and stock cache-handoff locations are unchanged. That layout preservation is not physical cache validation.

## Isolated fallback contracts

The actual corrected final fallback runs against the prior stock-captured machine state and actual stock initializer/trampoline. Eleven situations are tested at incoming SR `201f`, `231f`, and `271f`, exercising IPL 0, 3 and 7 with condition flags set:

- Valid context and initially unready context.
- Wrong magic, version or size.
- Null, outside-region or misaligned pointer.
- Wrong initializer argument.
- Pointer or header changed during the stock initializer call.

Every case returns with balanced stack and preserved D1–D7/A0–A6. Full returned SR equals incoming SR. Stock initializer D0 return and event-pool contents match the stock control. Valid cases clear contexts and publish ready; invalid cases disable the owner pointer and use the stock continuation. The stock initializer runs exactly once with the incoming IPL restored.

These are metadata/failure-continuation tests, not bus-exception recovery or a guarantee of recovery from a non-returning stock initializer.

## Full cold/intro tests

Each case starts from direct MAIN entry with the established loader-matching flags and a fresh disposable card copy. The source image is the corrected raw MAIN overlay; the emulator's flash data still comes from unchanged E04 SYX. The firmware's copier supplies the resident payload: it is not host-seeded into executable RAM.

The strict instruction watcher covers the new copier extent, helper code and fallback. It rejects the documented bad MOVE combinations, decoder illegal/FPU/line-F flags and privileged instructions without supervisor mode.

| Case | UI reached | Strict custom-instruction checks | Context result |
|---|---|---:|---|
| Default initialized drive | Yes | 5,320 | Ready; 8 captures; candidate `80000043` |
| Restored enabled-scale mirror | Yes | 4,704 | Ready; 4 captures; candidate `800000bc` |
| Bad owner pointer at fallback entry | Yes | 4,532 | Owner disabled; ready 0; candidate zero |
| Header magic changed at stock initializer entry, restored project | Yes | 4,347 | Post-call validation disables owner; ready 0; candidate zero |

Every case has zero strict violations, three native modeled DTIM1 interrupts, zero host delay-semaphore kicks, zero general intro semaphore satisfactions, one intro exit and 138 main-loop entries. Each invokes the actual stock initializer once with argument 158.

The restored cases observe first-mirror validation and full payload-read return, with no default-initialization branch. All four restored capture inputs are root 60/raw scale 0. Failure injections change private metadata only; they are intentional PC controls, not modified device settings.

## Files and evidence

Raw emulator overlays, explicitly not packaged updates:

- `work/os144/PC_ONLY-E04-ISA-corrected-main.bin`
- `work/os144/PC_ONLY-E04-ISA-corrected-payload.bin`

Evidence:

- `Digitone-E04-PC-ISA-correction-layout.json`: exact replacements, strict static audit, layout and old/corrected copier-state comparison.
- `Digitone-E04-PC-ISA-fallback-contracts.json`: 33 passing failure/success cases and full-SR checks.
- `Digitone-E04-PC-ISA-startup-checks.json`: four complete cold/intro runs with strict checks and fault injections.
- `Digitone-E04-PC-ISA-correction-summary.json`: passing combined assertions and unchanged-original hashes.
- Scripts: `work/build-PC-E04-ISA-correction.py`, `work/test-PC-ISA-fallback-contracts.py`, `work/test-PC-ISA-corrected-startup.py`, `work/summarize-PC-ISA-correction.py`.

E04 SYX SHA-256 remains `76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c`. Original MAIN remains `686dc4675e5af33f2e3b313e9101f92b914c0a848d0a858424b2d335d85b186c`; original payload remains `eb908e6ae5ac26490bf4fea0216ba8fcfbff258a8f8ea0f7159342a00e14d2e7`. Original cards and the saved-mirror source payload were reverified unchanged.

## Remaining step

Next carry the corrected overlay through loader-derived startup state and into playback, checking source copying/cache handoff and behavior/timing regressions. These runs use direct MAIN entry and the old container's flash contents, so they are not a newly packaged loader-to-corrected-image test. Physical cache coherence, RAM ownership and timing remain unverified. Do not reinstall original E04 or treat these raw overlays as a device update.
