# Digitone OS 1.42: update-entry initialization and integrated PC installation policy

**53 checks across 17 recorded cases passed.** The recovered bootstrap OS UPGRADE menu dispatch reaches the tested SysEx entry. Its local setup does not initialize the staging buffer in the executed fixture. A proposed PC policy now combines the actual receiver, checksum, and padding helpers with simulated flash operations; it requires a fresh receive session and prevents handoff after every tested failure. This is not an installed updater change.

## Target entry and initialization

The target for this PC investigation is the recovered bootstrap **OS UPGRADE** SysEx route, matching the supplied official file's framing. We have not certified which route Elektron Transfer chooses on the user's device.

At **80000cac**, the recovered startup path calls menu **8000203e**. Its dispatcher loads **80004052** into `a4` at **800021f4**, then calls it at **80002258** for the fourth menu option. Actual dispatch instructions were executed with a supplied scanner event: type 0, key value 29, press 1. This reached **80004052**. Physical buttons, earlier complete startup, and the full key scanner were not executed.

Entry **80004052** clears completion **800089a4**, error flag **800088a0**, and another UART control field, then calls **80003ac6**. That initializer resets receive/control machinery and installs command handlers before branching into **800031b8**, which installs interrupt handler **800038f8** at vector **800002d4** and configures MIDI UART registers. The recovered staging pointer **800070e4** is **40000000**. Payload decoding starts there and advances by 101 bytes per packet.

The actual entry and setup instructions were executed to their first wait at **800040d6**, including **80001242 / 8000107a**, whose writes go to control UART registers. Screen-rendering helpers were explicit skipped boundaries. All 4,096 checked staging bytes retained their initial `a5` sentinel. No clear of the staging buffer occurs in the recovered setup instructions. Earlier full startup and the skipped display helpers have not been certified as a source of staging initialization; this result is local to the executed path and boundaries.

Receive counters/state at **80007712..80007720** are initialized by the begin marker, not all reset by this entry. A hypothetical reentry fixture retained prior end-wait state and counters; supplying its old end marker could republish completion locally. The actual device's ability to reenter from that state is unproven. The PC policy therefore requires an accepted fresh begin marker for the current entry instead of treating a completion flag alone as sufficient ownership evidence.

## Integrated PC policy

Each test enters through actual **80004052**, feeds in-memory synthetic SysEx frames through actual **800036f4**, and executes the actual content-checksum loop at **80003bfa**. The policy rejects invalid receive completion, an error flag, absence of a fresh begin marker, and invalid length/alignment/extent before any simulated erase.

After integrity succeeds, actual stock memset **400ec284** initializes precisely the final tail to the next 512-byte boundary. All valid payload bytes are preserved. This helper is called as an isolated test component; it is not linked into the bootstrap entry in firmware.

The Python policy then performs simulated 256 KB erase units and 512-byte programming, checks every operation's status, and compares every written block against readback. It stops immediately on failure and sets hypothetical handoff eligibility only after all blocks verify. The fixture allocates 8 KB of staging and a 2 MB mock flash array; these are explicit test choices, not measurements of device RAM or flash capacity.

| Scenario | Observed result |
|---|---|
| Valid payloads: 64, 512, 516, 1,024, 4,096, 4,160 bytes | Payload preserved; full final padding zero; written blocks verified; handoff eligible |
| Interrupted upload | No flash operations; no handoff |
| Bad packet checksum | No flash operations; no handoff |
| Bad container checksum | No flash operations; no handoff |
| Prior end marker without a fresh begin | No flash operations; no handoff |
| Erase error | No programming; no handoff |
| Second program call reports failure | No third program call; no handoff |
| Second program silently does nothing | Readback catches it; no third program call; no handoff |
| Readback mismatch | Stops; no handoff |
| Simulated bounded busy timeout | Stops; no handoff |

Valid fixtures also preserve bytes outside the erased footprint. The original SysEx remains unchanged and matches SHA-256 **0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda**. Synthetic frames and mock flash contents remain in process memory; no firmware package or flashable output was created.

## What this establishes, and what remains

The integrated policy no longer relies on inherited staging-tail contents, or on stock outer loops detecting wrapper failures. Its fresh-session, explicit-padding, status-checking, and readback behavior passes the tested sequences. The earlier 232-byte padding gap is addressed in these controlled fixtures by deliberate initialization, not by an assumption about cold RAM.

Actual menu dispatch, local entry setup, packet reception, content checksum, and memset ran as recovered instructions. Flash erase/program/readback and timeout behavior are mock-backend operations. Validation/result gates are Python orchestration. Full interrupt scheduling, entire device startup, hardware behavior, platform/version acceptance, the complete stock-sized receive stream, and executable handoff are not covered by this integrated fixture. A failure after erase can leave a partial image; the model does not promise rollback or atomic installation.

No proposal to modify the bootstrap has been implemented. These tests do not establish that the protections can be deployed through the intended host updater without additional work.

The next concrete task is to connect the proposed extension's staged source and startup-copy/cache handoff to this PC installation fixture, checking that exactly the verified bytes remain available when allocation and copying run, and that failure leaves stock execution selected. The installation transport and any producer-stop conditions need to remain explicit boundaries until verified.

Evidence: `Digitone-integrated-update-policy-results.json` contains all cases and outcomes; `Digitone-integrated-update-entry-instructions.txt` records entry/dispatcher/setup instruction windows.
