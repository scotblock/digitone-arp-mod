# Post-copy cold permit: boundary review

Two loader-derived PC startup traces pass: default and restored-project state. Three separate actual-helper/stock-initializer controls and two stock normal/diagnostic branch controls also pass. Firmware, prior raw candidate and prior guard overlay hashes are unchanged.

## Establishment candidate

`4029c518`, the existing copier's final jump, is after all 14,008 payload bytes and pointer/header setup, immediately before the displaced vector routine `40001df4`. Both runs reach it once with stack return `4000053e` and SR `2500` (interrupt level 5). A future permit update therefore must save/restore SR and raise its own interrupt mask; copying does not establish level 7 protection.

A host-supplied COLD marker here survives the actual subsequent SRAM copying, DDR clearing, cache configuration and application startup through the note initializer. The only observed native overlapping write to candidate `47be2840` is the original copier's zero store at `4029c4c2`. The marker is fixture data, not a native seed or integrated bootstrap. Cold execution is continuous through the initializer; later UI startup still uses the existing snapshot handoff/model shortcuts.

The sole recovered executable literal call to the copier is startup `40000538`. Literal `4029c4b0` at `4000049a` is the stock SRAM-copy endpoint comparison, not a call. No recognized relative call to copier/tail was recovered. This supports the cold-route candidate but cannot exclude arbitrary computed entry or a replay of early startup.

## Consumption candidate

Use normal startup's `4008d318` call boundary before `4009d0d8`, rather than waiting inside shared note-initializer wrapper `4009c5a0`. Both traced setups return to `4008d31e`; their later initializer call returns to `4009c5aa` with argument 158. Consuming before the normal setup call can precede its flag changes and all later note-pool mutation. The shared wrapper is also used by warm setup and diagnostic queue construction, so its return address alone is insufficient cold provenance.

Three isolated PC controls execute the actual copier, supply the declared cold fixture seed, run the native single-use claim helper and then execute stock wrapper `4009c5a0` through the fallback/initializer. INITIALIZING is present before mutation and survives valid, unready and bad-metadata cases; another claim is denied. Calls are deliberately separate controls. They do not implement a startup hook or a whole-operation refusal path.

## Alternate startup and replay requirements

Stock `4008d308..4008d310` tests boot flags bit `40`. Normal state calls `400f4cba` then setup at `4008d318`; bit 40 takes `4008d326`, bypassing that setup and entering the diagnostic path. Two actual mask/branch controls verify this selection, stopping before either setup. A seeded permit must be invalidated before this alternate path can execute; otherwise it could remain unused COLD. Full diagnostic cold startup is not tested here.

Seeding at the shared initializer, enabling it from READY, or trusting just a caller return address would not meet the admission policy. Replaying the early copier zeros this storage; a seed keyed only to zero would regrant permission. Unique trusted boot control flow and exclusion of warm replay remain requirements, not results of the literal-reference scan.

## Next implementation boundary

The observed addresses support a separate PC startup overlay that seeds after copying, consumes before the normal setup call, invalidates on alternate mode, and reaches explicit failure continuations before mutation. Its completion-to-LIVE decision must wait for verified full normal setup, not just a successful note initializer. No such bootstrap has been installed in this pass. Native refusal/cleanup, fresh-boot provenance, global/physical RAM ownership and hardware cache/timing remain unresolved.
