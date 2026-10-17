# E04 restore-versus-default decision

9 October 2026. PC-only. Stock 1.44 remains installed on the physical instrument. E04 SYX and the original emulator cards remain unchanged.

## Result

The decision is now traced, and the actual saved-mirror restore branch has been exercised. Stock and E04 both restore the retained enabled-scale project through cold startup and clear the logo. E04 also rejects a checksum-damaged first mirror and restores from the valid second mirror.

This closes the specific PC coverage gap: these runs restore persisted mirror bytes during boot rather than resume an after-boot snapshot. The mirror content is a disclosed fixture derived from the user's saved emulator RAM, not a physical storage dump. The physical freeze remains unreproduced.

## Restore decision

The stock startup function at `400a8360` performs these checks:

1. Read a header from sector `7a000`, byte offset `0f400000`, then call the validator at `4008525a` / `4008521e`.
2. If valid, select bank index 0. Otherwise read and validate sector `7c000`, byte offset `0f800000`, and select index 1 if valid.
3. If neither is valid, call recovery at `400a821a`. It scans the three flash offsets in the table at `401c2dd4`: `400000`, `800000`, `c00000`, looking for `COKI`. If none qualifies, it returns -1.
4. Recovery failure reaches `400a8402`, calls default initialization `40085162`, sets global boot/state bit `4`, and publishes selected-bank index -1 at `402369e4`.
5. A valid header reaches `400a83b0`. Header flags at `40555ef8` can request reset behavior: the recovered code propagates bit 1 as mask `92`, or bit 0 as mask `2`. At `400a83da`, nonzero global low bits (`flags & 3`) skip the full mirror read. Those requested-reset branches were inspected statically, not executed in the new controls.
6. With a valid header and no reset request, read the full `2a7514` bytes from the selected bank into the serialized project area beginning `40555ee4`, then publish its bank index. Stock conversion subsequently fills the runtime pattern used by producer capture.

The header validator requires magic `434f4b49` (`COKI`), declared length no greater than `f0`, and the checksum returned by stock routine `40085138` to equal the word at header offset +4. The checksum is an indexed additive/XOR calculation over header words. This validates the header contract; it is not a whole-project cryptographic integrity check.

## Test-state construction

The retained stock GUI RAM snapshot contains a complete serialized mirror at `40555ee4..407fd3f8`, length 2,782,484 bytes. Its header already has `COKI`, version 5, length `58`, checksum `e444252a`, and reset flags zero. An isolated execution of the actual stock validator returns 1 for this unaltered header. No checksum was invented or recomputed.

Two disposable card fixtures are prepared from copies of the saved stock emulator drive:

- **Valid first bank:** copy that complete retained serialized mirror into `0f400000`.
- **Bad first, valid second:** flip one bit of the checksum byte at offset +4 in the first bank, and put the unaltered retained mirror in `0f800000`.

The rest of the copied card is retained. The corruption is intentional PC test data. Neither card is an installable firmware image or a physical backup. Original card hashes were checked again after the tests and match.

## Executed controls

All four runs start at MAIN reset, supply the established loader-matching entry flags, execute native modeled DTIM1 completion without host semaphore kicks, and continue the cold state through actual intro exit with general semaphore unblocking disabled.

| Run | Header decisions | Result | Early captures | First-track root / raw scale |
|---|---|---|---:|---|
| E04, original blank mirror banks | Both invalid; flash recovery fails | Defaults; UI up | 8 | 67 / `ff` disabled |
| Stock, valid first bank fixture | First valid, index 0 | Full mirror restored; UI up | 4 | 60 / `00` enabled |
| E04, same valid first bank fixture | First valid, index 0 | Full mirror restored; UI up | 4 | 60 / `00` enabled |
| E04, bad first / valid second fixture | First invalid, second valid, index 1 | Full second mirror restored; UI up | 4 | 60 / `00` enabled |

Every run executes three native DTIM1 interrupts, observes one intro exit and reaches 138 main-loop entries. Full card-read coverage includes the complete selected mirror before normalization/capture. First-bank restoration reads in 32 KiB chunks after the header probe; the second-bank case follows the same path from its different offset.

The stock and E04 first-bank cases have matching captured source addresses, event addresses, track indices and all four tracks' root/scale bytes. Root/scale conversion is observed before capture. In the E04 restored runs, the cold snapshot retains candidate context word `800000bc` for track 0: valid bit, root 60 and enabled-scale index 1 (raw scale 0 plus one). The blank-bank control retains `80000043`, the disabled-scale startup context. This is evidence of actual context capture after restoration; it is not a playback or physical cache test.

## Correction to the earlier storage interpretation

The previous review called `0fc00000` the working-project restore area and inferred restoration behavior from writes there before its first read. The recovered stock address selector at `400f6b36` identifies sector `7e000` / byte offset `0fc00000` as **special project index 128**. Ordinary project indices use a different formula; the two startup restore mirrors are the banks at `0f400000` and `0f800000`.

The earlier read/write ordering observation remains correct, but it did not identify the restore gate. The newly executed header checks establish why the old cold tests selected defaults: both mirror headers were blank and the modeled flash recovery copies were blank. The original GUI RAM session had enabled-scale content despite those missing persisted mirrors. A saved RAM resume and a cold restore were therefore materially different inputs.

## Remaining limits and next focused check

Saved-project restoration no longer has to be assumed for this PC fixture. It still does not prove that the physical device's selected bank, header flags, project content, interrupts or memory/cache state match. The successful second-bank test covers the intended checksum rejection; full recovery from a valid SPI copy, short/failed storage reads and requested-reset paths are not certified by these tests.

The next bounded check is to inspect the four restored-project capture calls with the same complete memory/register tracing and producer-bypass control used for the earlier eight default-state calls. This tests the newly reached enabled-scale inputs directly. E04 is not ready for another hardware trial; the physical logo freeze remains unexplained.

## Evidence

- `Digitone-E04-PC-saved-mirror-fixtures.json`: retained payload identity, unchanged header and actual validator return.
- `Digitone-E04-restore-decision-checks.json`: branch events, selected bank, header bytes, full mirror reads, normalization, capture inputs and intro results for all four controls.
- `Digitone-E04-restore-decision-summary.json`: passing assertions, retained context words and preservation checks.
- `work/prepare-PC-saved-project-mirror.py`, `work/trace-E04-restore-decision.py`, `work/summarize-E04-restore-decision.py`.

E04 SYX SHA-256 remains `76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c`. No firmware was rebuilt or transmitted.
