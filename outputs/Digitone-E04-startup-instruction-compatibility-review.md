# E04 startup instruction compatibility: five unsupported stores

9 October 2026. PC-only audit. E04 remains unchanged; no corrected firmware was built or transmitted. The physical instrument remains restored to working stock 1.44.

## Finding

There is a concrete instruction-compatibility defect in E04: **five custom `MOVE.L #immediate,absolute-long-memory` encodings use a source/destination combination excluded by the ColdFire instruction set.** Four occur in the early copier. The fifth sets the private context ready flag after the stock initializer returns.

The earliest is `4029c4e0`. Successful PC execution did not catch it because the emulator accepts the encoding. The local `cfisa` checker also recognizes it as MOVE without enforcing combined source/destination restrictions. Earlier compatibility confidence from that checker was therefore incomplete.

This is a plausible cause of the physical logo hang and a definite defect to correct before any further trial. The physical fault PC and exception state are unknown, so the cause of that observed hang is not confirmed.

## Documentation and target

The retained firmware target is MCF5441x, V4/ISA_C, as established in the prior bootstrap/DDR investigation; this turn did not read a physical chip identifier. NXP specifies ISA_C and its additions in [MCF5441x Reference Manual, section 3.3.2](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=97).

The [ColdFire Programmer's Reference Manual, page 4-48, PDF page 124](https://www.nxp.com/docs/en/reference-manual/CFPRM.pdf#page=124) excludes immediate-source MOVE to absolute memory. Its byte/word immediate-to-displacement exception does not permit these longword-to-absolute stores. Register-to-memory and immediate-to-register forms are allowed.

## Exact unsupported sites

| Custom site | Bytes | Intended operation |
|---|---|---|
| Copier `4029c4e0` | `23fc47bccf0447be1000` | Store owner pointer `47bccf04` at `47be1000` |
| Copier `4029c4ea` | `23fc534c433247be1004` | Store magic `534c4332` at `47be1004` |
| Copier `4029c4f4` | `23fc0000000247be1008` | Store version 2 at `47be1008` |
| Copier `4029c4fe` | `23fc00000b7047be100c` | Store length `b70` at `47be100c` |
| Startup fallback `47be0998` | `23fc0000000147be1010` | Set ready flag to 1 at `47be1010` |

Each has source mode 7/register field 4 (immediate) and destination mode 7/register field 1 (absolute long), and is ten bytes long. The incompatibility is the documented operand combination, not the constant or RAM address.

The real copier spans `4029c4b0..4029c50e`. Its trailing zero padding before source payload `4029c5b0` is data/padding, not executable instructions. It was excluded from the audit. Likewise, the pitch lookup table was excluded from instruction decoding.

## PC controls demonstrating the gap

An isolated execution of the unchanged actual copier copies all 2,492 payload bytes, clears metadata, executes all four unsupported stores and reaches stock continuation `40001df4` under the permissive V4e engine. Its header becomes `47bccf04 534c4332 00000002 00000b70`.

The same copier with a read-only instruction guard enforcing NXP's MOVE combination rule also copies the payload exactly, then stops **before executing `4029c4e0`**. The metadata header is still zero. This guard deliberately stops execution; it does not model a physical illegal-instruction exception or claim a device trace.

Five additional isolated instruction controls demonstrate that the engine accepts each offending encoding. Five paired examples use an immediate load into D0 followed by a register store; those pass the documented combination check and produce the intended word. These are scratch-register examples only. They were not inserted into the firmware and do not establish a drop-in register-preservation contract.

The distinction matters: the emulator's CPU-family selection alone is not strict enforcement of that family's operand restrictions. The checker must reject the disallowed combination even when the backend executes it.

## Remaining custom code audit

The script decodes the complete custom helper layout and all 280 bytes of the fallback, as well as the true copier extent. The combined-mode check identifies exactly the five sites above. No further FPU, unimplemented line-F or illegal flags are reported by the existing decoder in these code regions; that absence is supporting evidence, not a complete independent decoder certification.

The documented checks include longword MOVEM through indirect/displacement addressing, supervisor SR access, longword arithmetic/shifts, word division, and signed/zero-extending moves. No additional incompatibility was identified in these reviewed forms. Supervisor SR access still requires the appropriate runtime mode; the prior observed startup/capture SR values have the supervisor bit set. Instruction legality does not prove memory backing, cache coherence or timing.

The recorded execution addresses from all four restored-project producer replays were checked separately. None uses the forbidden MOVE combination. Thus the prior successful producer access controls are distinct from the earlier copier and later ready-flag store, whose permissive execution they did not certify.

## Safest next step

Correct the four copier stores and the fallback ready store **in a PC-only overlay**, using permitted register-mediated operations and preserving the caller's required registers/status. Recalculate code lengths, branch positions and copy/cache spans as necessary. Then repeat strict instruction checks and actual startup on both default and restored-project paths, including failure continuation.

Do not merely replace the opcode in a packaged image or assume the isolated D0 examples preserve the stock caller. No new hardware trial is appropriate until the complete correction has passed those PC checks and been reviewed. Physical cache/timing uncertainty remains even after these encodings are fixed.

## Evidence

- `Digitone-E04-startup-instruction-audit.json`: complete decoded regions, exact five failures, permissive/guarded copier controls, isolated store examples and recorded producer-address cross-check.
- `work/audit-E04-startup-ISA.py`: read-only firmware audit and isolated emulator controls; adds the documented MOVE-combination rule without changing the upstream decoder or firmware.

E04 SYX SHA-256 remains `76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c`. No firmware output was generated.
