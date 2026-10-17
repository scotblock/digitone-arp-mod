# E10 modeled automatic shutdown and interrupted-write recovery

17 October 2026. The E10 MAIN/payload and E09A container remain unchanged. No installable firmware is produced.

## Outcome

The PC engine now exercises the native board-input interrupt, stock callback dispatch, stock shutdown writer and a fresh cold startup. With the modeled write allowed to complete, all 128 records match, including a further unsaved A01 edit from +3 to +4. No writer call frame is supplied in this path.

A separate interrupted-write control exposes a stock protocol limitation. With bank 1 containing the prior valid working copy and bank 0 being replaced, completing only the first 32 KB command gives bank 0 a valid header before its complete payload exists. The actual stock cold selector chooses bank 0 despite bank 1 remaining intact. The two programmed E10 records are absent in the selected partial image; only the other 126 already-empty slots match. Thus completed-write recovery passes, but arbitrary mid-write recovery is not safe in this tested case. This is a PC counterexample, not a physical brownout result or a newly introduced E10 writer change.

## Native path recovered

- Stock setup at 0x400a841c registers shutdown callback 0x400a7b8e through 0x40002106; the pointer lives at 0x40528598.
- The stock enable-sense poll at 0x4008cdf2 reads GPIO 0xec09401e bit 3. Its accepted branch invokes 0x400a8448, which sets the shutdown cache-ready byte at 0x4139420c. Earlier PC snapshots left this input low and the byte unset; directly invoking the ordinary writer concealed that missing prerequisite. The physical board wiring and electrical thresholds have not been measured, so “power good” is a fixture name inferred from this use.
- The external GPIO input fixture drives C2 low and injects external vector 66 at its stock programmed level 7. Native handler 0x40001e54 sets INTC2 force bit 30. Native vector 222 handler 0x40001e2a acknowledges it and calls the registered callback. No firmware guard, callback pointer, ready byte, bank selector, payload or executable code is host-written.
- The callback checks the cache-ready byte and pending bank, then uses 0x400a7a6c to write fixed 32-KB transfers. There are 85 data commands for the retained image (the final transfer includes native padding), followed by one 32-KB old-header invalidation command. This differs from the ordinary writer tested earlier.
- The test stops after the native cache loop finishes, before the post-cache reset tail. The resulting card is then used for fresh direct-MAIN cold startup and native E10 bank capture. All 128 records are recovered, without Save Project.

## Required PC model changes and limits

The synthetic idle-loop scheduler interrupt is disabled for this test. It would otherwise inject a scheduler trap into the stock shutdown parking loop after the handler has intentionally reset its stack. The existing generic forced-interrupt model is attached to INTC2 source 30, using the stock ICR level. These changes affect only the dedicated test session.

The controller model lacked the acknowledgement semantics used by the polled shutdown driver. A narrow CC/TC adapter now retains one completion flag when the firmware acknowledges the other. It does not manufacture completion events: those still come from the existing controller/DMA command model. Native guest-store/read controls cover CC-first, TC-first, zero writes and later TC arrival. NXP defines IRQSTAT acknowledgements as write-one-to-clear in [MCF5441x Reference Manual, section 25.3.10 and Table 25-14](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=638). The adapter is scoped to CC/TC; it is not a complete controller error, SDIO interrupt or timing implementation.

The eMMC model copies a command payload and reports completion immediately. Physical busy time, write durability, bus contention, capacitor hold-up, supply thresholds, cache coherence and the post-cache reset/board power behavior remain unmeasured. Passing this path cannot certify physical power-loss recovery.

## Interrupted-write controls

Private cards are reconstructed from the untouched pre-shutdown card and actual command payload bytes from the successful run. These are disclosed synthetic cut fixtures, not staged firmware writes:

| Completed new-image bytes | Actual stock reader result |
| --- | --- |
| 0 | Selects bank 1 and restores all previous E10 records |
| 32,768 (one command) | Selects bank 0, although it is incomplete; neither the new nor the previous two programmed records is recovered |
| 2,785,280 (all 85 new-image commands, before old-bank invalidation) | Selects bank 0 and restores all new E10 records |

The actual 0x400a8360 cold selector/full-image reader executes through the native eSDHC path in a stopped-entry fixture. Only the successful automatic-write case receives a full cold reboot. The cut tests do not model torn sectors, partial eMMC internal programming, all cut positions, concurrent input or the opposite bank direction.

Byte comparisons confirm that the external dispatch, enable-sense logic, shutdown writer, selector and header checksum code are identical to stock 1.44. The selector validates the header; that validation does not prove the rest of the image was written. The stock protocol therefore depends on shutdown completing before power disappears. Whether the real unit provides enough hold-up time remains an open hardware question.

## Evidence and next step

`Digitone-E10-PC-powerfail-verification.json` records both the successful automatic modeled path and `mid_write_recovery_safe: false`; it must not be interpreted as an overall hardware-safety pass. Related reports contain the interrupt trace, 86 controller transfers, 128-record cold restore, and three cut controls. The earlier E10 lifecycle report remains the record of explicit-writer tests.

The next useful check is the shutdown write/hold-up budget on stock hardware, or a separately reviewed PC-only commit-order design. Do not infer a safe abrupt power-cut trial from these results. No new installation or storage protocol change has been made.

## Later closed-unit clarification

The [hold-up assessment](Digitone-E10-PC-hold-up-assessment.md) corrects the earlier “power latch” label: 0xec090000 bit 7 requests a CPU software reset. It also records the nonmaskable level-7 interrupt caveat. The external input arriving during custom retained-image updates was not covered by the successful completed-write test. Physical hold-up remains unknown, and no internal measurements are planned with the current equipment.
