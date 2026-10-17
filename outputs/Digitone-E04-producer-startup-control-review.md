# E04 early producer-capture control

8 October 2026. PC-only. The physical Digitone remains restored to working stock 1.44. E04's SYX is unchanged; no installable diagnostic image was created or transmitted.

## Result

Bypassing producer capture alone does not change startup success in the tested PC state. Both unchanged E04 and the bypass control reach the live UI, observe one intro exit and 138 main-loop entries, and execute three native DTIM1 interrupts. Neither uses host delay-completion kicks or general intro semaphore completion.

All eight calls have matching input registers between the controls, and identical output registers, including the stock condition-code changes. Complete isolated replays of the actual captured calls find no unexpected data access or unmapped access. This closes the specific input/access check for this modeled workload. It neither reproduces nor diagnoses the physical logo freeze.

## Control and tracing method

The control restores the eight original bytes `254400082544003c` at `400947ec..400947f4` in an otherwise identical raw E04 MAIN image. Those instructions write D4 to event offsets +8 and +3c. The appended copier, initializer, payload and all other hooks are retained. A byte comparison confirms no change outside this interval.

`work/os144/PC_ONLY-E04-producer-bypass-main.bin` is a raw emulator overlay, not a packaged update. The emulator still reads E04's SYX for flash data. No SYX was rebuilt.

The continuous cold run watches the original hook site, records registers and stack words before the branch, then records registers at the original continuation. Cold state is saved and continued through intro with the existing engine. Both cases use identical initialized synthetic drives and matched boot flags.

An initial dynamically installed memory watcher missed accesses from already translated code. Its partial lists remain in the evidence as `memory`; **use `isolated_replay.memory` for the complete access lists**. Each call is replayed separately with its actual CPU context and source, private RAM, event, code and stack pages copied from that continuous run. Read/write and invalid-access watchers are installed before execution. There is no unexpected-access auto-mapping in the isolated engine. All eight baseline replay outputs match the corresponding continuous execution; all eight bypass replays also match.

An initial assertion incorrectly required SR to remain unchanged. The original stock MOVE instructions deliberately update condition flags. The final checks compare against the bypass's exact flags and registers; no register discrepancy remains.

## Eight calls and their inputs

Calls alternate track indices 0 and 3, four times each. These correspond to tracks 1 and 4 in a one-based UI. A3, the supplied source object base, is `407fd414` for every call. A2 is the event descriptor; D4 is the track index.

| Calls | D4 | Event A2 | Root read | Scale read | Extra context write |
|---|---:|---|---|---|---|
| 1, 3, 5, 7 | 0 | `419f182c` | `407fd7df`: `43` (67) | `407fd7e2`: `ff` | `47be1a24` = `80000043` |
| 2, 4, 6, 8 | 3 | `419f1904` | `407fe34f`: `3c` (60) | `407fe352`: `ff` | `47be1a30` = `8000603c` |

The addresses exactly match `A3 + D4*3d0 + 3cb` for root and `A3 + D4*3d0 + 3ce` for scale. The signed scale read interprets `ff` as -1; adding one encodes disabled scale as index zero. The stored words contain the valid bit, track and root, with scale index zero. These startup calls are not capturing an enabled scale in this workload.

Before the reads, the resolver checks private pointer `47bccf04`, magic `534c4332`, version 2, length `b70`, and ready 1. Two additional private state words at `47be1014` and `47be1018` are zero. Candidate-store resolves the header again and validates the event slot before writing.

## Complete access and register results

Each baseline replay performs 75 data accesses; the bypass performs the two original event writes. Baseline accesses are confined to:

- The two source bytes above.
- The private pointer/header and state fields.
- One candidate word at `47be1a24` or `47be1a30`, within the occupied reservation ending at `47be1b74`.
- The original event writes at A2+8 and A2+3c, with values 0 or 3 respectively.
- The caller's stack, extending at most 92 bytes below entry SP.

No other read/write address is present in these complete replay traces. There are no peripheral, DMA, unrelated pattern or out-of-range context accesses. The observed stack extent is a local measurement for this call; it is not a worst-case interrupt/whole-task stack bound.

The baseline saves/restores D0–D7 and A0–A6 and balances A7. SR is `2004` at entry. At continuation it remains `2004` for D4=0 and becomes `2000` for D4=3, exactly matching the bypass. No interrupt-mask leak is observed at continuation.

## What remains

The PC workload supplies valid, initialized source fields and a ready private context. It does not establish that the physical device encounters these same input objects, saved project or initialization order. The replay also does not measure the added memory traffic, cache misses or interrupt timing on hardware. Its 75 accesses versus two stock accesses are an access count, not a cycle estimate.

The physical failure remains unexplained. A focused next investigation is tracing when this source object becomes initialized and how its selection differs when restoring a saved project, rather than assuming the synthetic PC startup state represents the device. Separately, source-pointer validation checks only non-null after private context validation; these successful calls do not certify arbitrary non-null pointers. Keep E04 off the instrument while investigating these differences.

## Evidence

- `Digitone-E04-producer-startup-control-checks.json`: continuous results, all eight register snapshots, complete isolated replay accesses and cross-control assertions.
- `work/test-E04-producer-startup-control.py`: two startup controls and exact-state replays.
- `work/summarize-E04-producer-startup-control.py`: allowed-access bounds, encoding and register comparisons.

Reverified E04 SYX SHA-256: `76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c`.
