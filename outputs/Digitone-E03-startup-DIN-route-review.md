# E03 startup-menu MIDI route: bounded PC validation

## Result and scope decision

The distinct startup-menu route is now identified and exercised in bounded PC tests. A FUNC-held stock-bootstrap run reaches the startup menu without entering MAIN or writing flash. Its actual menu dispatcher, supplied a decoded TRIG4 event, reaches the SRAM OS-upgrade entry. Separate receive/program tests accept exact E03 bytes and reject three failure controls without flash calls.

This is sufficient to move the next development work back to startup handling and RAM placement, rather than implementing an application USB receive freeze. It is not full hardware route certification or permission to install E03. Physical Rubix22 SysEx transfer and stock recovery have not been tested.

## Which code handles this route

The original 1.44 bootstrap section 2 executes from SRAM at `80000400`. FUNC is modeled as group 0 bit 2. The key bitmap at `80008052` contains `04` when the bootstrap reaches menu entry `80002162`. MAIN is not entered.

The stock menu dispatcher selects OS UPGRADE for decoded key code 29 (TRIG4), calling `800041a6`. Only that decoded panel event is supplied; the branch/table and surrounding menu code execute. This continuation stops at upgrade entry. The diagnostic `halt_vec=-2/-3` values are intentional observation boundaries, not recovered firmware exceptions; the engine's stop wording should not be read as a device fault. Its instruction counter at the terminal selection stop does not measure the whole menu continuation.

Upgrade entry calls receiver setup `80003bf2`. Setup installs UART9 receive interrupt `80003a24`, using `ec074000` and the recovered vector entry. That IRQ accumulates SysEx bytes, checks manufacturer/device framing and dispatches Digitone command `7e/7f` to `80003820`. The receiver writes the staged transport stream to DDR at `40000000`, independently of the application receiver buffer `40325f00` and its USB work queues.

The upgrade loop observes receive state `80008b7e` and eventually calls `80003d26`, which recomputes the whole-image checksum and performs identity/compatibility and flash programming decisions. Before erase/program, the recovered code writes interrupt-controller masks at `8000408c..80004098`; subsequent flash-interrupt setup is retained. These explicit instructions are evidence of different programming-phase input handling, not a simulation of every hardware masking/acknowledgment effect.

## Executed controls

| Case | Result |
|---|---|
| FUNC boot/menu plus supplied TRIG4 event | Actual menu and upgrade entry reached; no MAIN entry or flash writes. |
| Exact E03 receive/program | Phase 3 and complete state 2; received transport stream exact. Five simulated 256-KiB erases and 2,472 512-byte program calls write the exact advertised container, ending at `1b5000`. Stock-data guard at `380000` survives. |
| Bad whole-image checksum after reception | Stock checksum failure reaches its error loop before any modeled flash action. |
| Missing end marker | No completed phase; no programming invoked. |
| Bad packet checksum | Error flag set, no completed phase; no programming invoked. |

All 12,532 data packets execute the native bootstrap receiver, including checksum/sequence/unpack logic. Start/end marker frames execute byte by byte through the actual UART9 interrupt and exception return; data frames enter its recovered frame callback directly. Display and flash ID/geometry/erase/program calls are simulated. This does not test full UART baud pacing, overruns, physical MIDI interface behaviour, post-update reboot, actual flash errors or power loss.

The menu/entry probe and receiver/program tests are separate machines. There is not yet one continuous power-on → all serial bytes → flash → reboot run. Earlier E03 loader/decompression tests provide separate boot evidence. No application USB shutdown guard is installed or required by the code exercised here.

An initial test assertion compared programmed bytes to transport padding as well as the advertised container. It was corrected to the receiver's advertised logical length; all four final controls pass. This was a test expectation error, not a firmware modification.

## Unchanged recovery components

Compared directly against the user's original 1.44 SysEx, stored sections 2, 4 and 8 are byte-identical in E03. Section 2 contains this startup bootstrap; no mod is applied to its receiver/program code. Equal sections do not guarantee recovery after every physical failure.

Stored-section SHA-256:

- 2: `ff8b24e006803ce39eb253f2f5f7ee210c58d292b2c578bb823c01c9a87aee39`
- 4: `6fef191122b48a32875d252b655e3501284ba0d0edec1c9d00e728e55342d151`
- 8: `764f169834ac9ebcdbc1fd883e9f941be1eb43c2d57e4ff02e04685550838b06`

## Returning to startup and RAM placement

The next software change to design, still PC-only, is a stock-compatible continuation when context metadata is unavailable. Current reset entry `47be055c` can stop indefinitely at `47be0640` with interrupts masked. Runtime pitch fallback is not a startup fallback. The private pointer at `47be1000` is intended to hold `47bccf04` (`47be1004 - 14100`); bounds or an exact expected-value check must precede its use if retaining this fixed layout. No such new check/fallback was implemented here.

Keep the RAM question bounded: map known 1.44 task/interrupt stacks, heap bounds and DMA destinations against occupied span `47be0000..47be1b74`, then cover reset/project-load writers with focused traces. The candidate interval remains `47be0000..47c00000`, profile-backed but not yet sufficiently justified for hardware. Do not resume whole-USB certification unless this chosen route's remaining work establishes an actual need for it.

Before a hardware trial, the actual interface/cable/stock recovery path still needs a backup-first stock baseline. That is separate from this PC audit and has not occurred. Candidate startup/cache/RAM and physical audio-timing risks remain unresolved.

## Artifacts

- `work/probe-E03-startup-menu.py` and `outputs/Digitone-E03-startup-menu-probe.json`
- `work/test-E03-startup-DIN-route.py` and `outputs/Digitone-E03-startup-DIN-checks.json`
- Research-only extracted SRAM images: `work/os144/startup-bootstrap-image.bin`, `work/os144/startup-updater-image.bin`

No firmware was rebuilt or transmitted. E03 remains SHA-256 `8775320f161cb02efa8f51b2671034baf73eeec95f4bb66ffc20a29e9b0a2a3d` and PC-only.
