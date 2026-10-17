# Digitone OS 1.42: receive completion, integrity, padding, and write errors

**99 PC checks across 44 cases passed.** They confirm recovered receive-completion behavior and integrity checks, and expose two integration concerns: the stock SysEx does not supply every final-block byte, and the outer OS write loops ignore failed erase/program returns. No firmware was modified, repacked, or sent to hardware.

## Receiving paths and correction

The previous capacity report called the `001e0000` receiver the normal update receiver. More precisely, it is the **binary/service receiver** configured by **4008abc4 / 4008ac80**, using **400d9e26 / 400d9e3c**. A recovered registration at **4008caa2..4008cac2** is gated by application mode bit `0x20`. Its size limit has not been established for every ordinary SysEx or Elektron Transfer route. The complete mode-selection path and the host application's chosen transport were not executed here.

Separately, section 2's **SysEx marker/packet handler at 800036f4**, called by the SRAM interrupt parser, matches the supplied file's packet format. The relationship between these two paths remains unverified end to end.

## Receive completion

The actual SysEx handler tracks an initial marker, expected sequence, and total packet count, and decodes 101 bytes per packet through **800036a4**. A bad terminator is ignored; a wrong sequence invalidates receiving state and raises the error flag. A bad packet checksum also invalidates reception, but the handler still decodes that packet and advances its counter. A bad-checksum packet followed by an end marker did not publish successful completion.

The last expected valid packet moves reception into its end-wait state. A matching end marker must agree with seed, original sequence reference, and received count before publishing **800089a4 = 2** and terminal state **80007712 = 3**. Tests covered early end, bad seed/count, valid end, and an actual final-two-packets/end-marker chain. That chain starts with supplied prefix counters validated against the original file; all 10,912 packets were not instruction-executed as one session.

The actual binary/service function **400d9e3c** and its stock copying helper were run from clear fixtures with complete headers and payloads, in whole, split, and one-byte chunks. One notification occurred only after the declared payload was copied. Truncation withheld notification. Altered payload was still delivered: this function has **no local checksum check**. Integrity checks elsewhere in that transport remain possible and unverified. Bytes beyond the payload were untouched.

## Checksums

All **10,912 data-packet checksums** were independently recomputed from the original SysEx and matched. The complete container's stored and recomputed content checksum is **b77a7eee**.

The bootstrap loop **80003bfa..80003c4a** computes:

`sum((word_index + 1) XOR big_endian_word) modulo 2^32`

Its actual instructions and acceptance/rejection branch were run on small full fixtures, including a corrupted stored checksum. The loop covers `floor(length / 4)` words, excluding any odd tail byte. Stock length is divisible by four; a future extension should preserve alignment and recalculate the checksum over its declared length. The full stock checksum was recomputed in Python; its entire 1.1 MB machine-code loop was not executed.

## Final-block padding

Both recovered outer OS writers request a full **512 bytes** on their last program call.

| Current file property | Bytes |
|---|---:|
| Declared container | 1,102,032 |
| Rounded program footprint | 1,102,336 |
| Required bytes after container | 304 |
| Zero padding received from SysEx | 72 |
| Additional unreceived bytes | **232** |

Executing the final two stock SysEx packets left a sentinel in those 232 unreceived bytes. Executing **400edb42 -> 400ecf7a** for the final stock block transmitted 208 valid container bytes, 72 received zeros, and 232 existing sentinel bytes. This proves the recovered code's reads/emission in controlled RAM, not the actual contents of device RAM. Hardware was simulated.

Initialization of those 232 bytes has **not** been proven along the full update-entry path. The binary receiver also leaves its tail untouched. A controlled installation must deliberately initialize the complete rounded write footprint; readable padding alone is insufficient.

RAM-only tests used actual stock memset **400ec284** to zero exactly the necessary tail, preserving the payload for lengths 1, 511, 512, 513, stock, and stock +4 KB. The actual final-block program path then transmitted 304 zeros after the container. This preparation is tested but not integrated into an updater or firmware hook. Extra transport bytes are not automatically a solution for the binary receiver, which stops at its declared length.

## Write errors and cleanup

Actual main low-level program **400ecf7a** and erase **400ed272** ran with supplied hardware statuses. Their bus/mutex/scheduler helper internals were explicit boundaries; command emission, status branches, delay loops, and cleanup calls ran as recovered instructions.

- Busy clear: cleanup and success.
- Busy followed by clear: polling, cleanup, success.
- Busy plus error bits `0x60`, then clear: status-reset helper, recorded failure, cleanup, return **-1**.
- Error bits `0x60` with busy already clear: success locally, because this loop examines those bits only while busy. This does not establish that a fitted chip produces that status sequence.
- Persistent busy: a test-imposed third-poll boundary was reached without return or cleanup. No timeout counter appears in the recovered loop. Hardware or outer recovery remains unverified.

Main wrappers **400edb42 / 400edbbe** propagate low-level failure as **-1** and stop their remaining suboperations. Tests failed the first/second program subcalls and first erase subcall.

However, the **outer OS writers ignore wrapper results**. Main **4008ad76 / 4008ae3c** reached the same completion boundary **4008aec2** despite injected erase, program, or all-operation failures. Bootstrap **80003f6a** likewise reached **80003fd8** despite every supplied wrapper return being -1. These establish caller behavior, not power-loss behavior or identical physical error reporting by bootstrap helpers. No readback verification appears in the recovered outer loops.

## Consequence and next step

The extension still fits the tested erase footprint, but a controlled PC installation model needs **explicit final-block initialization and a failure gate preventing success/handoff after an erase/program error**. Neither is installed in machine code.

Next: establish the intended update entry/transport and its staging-buffer initialization, then connect zero-tail preparation and failure gating to that path in a PC-only integrated fixture, including interrupted receive and simulated flash failure. A flashable build is not justified by these checks alone.

Evidence: `Digitone-update-completion-results.json` records all cases and boundaries; `Digitone-update-completion-instructions.txt` contains instruction windows. Full mode entry, a complete uninterrupted hardware receive session, device RAM tail contents, and physical flash programming remain unverified. The original SysEx matches SHA-256 **0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda**.
