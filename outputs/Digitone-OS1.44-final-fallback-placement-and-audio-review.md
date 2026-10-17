# Digitone 1.44: fallback placement, copying and audio diagnosis

The tested fallback now occupies its planned location in a PC-only startup overlay. The real guest copier installs it before caching is enabled. Startup and playback succeed in valid and failed-metadata cases. The matched-pitch audio difference is explained, for this tested workload, by parameter-packet consumption timing: replaying stock packets at the corresponding DSP render restores stock PCM exactly with all fallback hooks still active.

E03 remains byte-for-byte unchanged, SHA-256 `8775320f161cb02efa8f51b2671034baf73eeec95f4bb66ffc20a29e9b0a2a3d`. No new SysEx image was produced and no device was accessed. The fallback is not present in E03 itself.

## Placement and copying

| Item | Result |
|---|---|
| Existing helper/table extent | `47be0000..47be08a4`, unchanged 2,212 bytes |
| New fallback | `47be08a4..47be09bc`, 280 bytes |
| Combined payload | 2,492 bytes / 623 longword stores |
| Space before owner pointer `47be1000` | 1,604 bytes |
| Startup initializer redirect | `400ffed0` jumps to `47be08a4` |
| Copier | Existing guest code at `4029c4b0`, word-count immediate changed from 553 to 623 |

The continuation has relative internal branches and fixed stock/helper/data references; changing its entry address does not require changing those operands. Its 33 isolated initializer cases pass at the new address, including invalid metadata/pointers, changed state during stock initialization and incoming interrupt levels 0, 3 and 7.

Three continuous application runs start from direct MAIN reset using separate initialized PC-drive copies. Valid, bad-magic and bad-pointer runs copy the complete payload through guest instructions, pass through stock cache setup, reach the interface and play pattern 2. Destination RAM starts poisoned; host-side code installation does not populate the destination payload. Exact payload checks run after copying, after cache setup and at the initializer entry. Each run records exactly 623 copier stores. The valid pointer remains available; both failures retain pointer zero through playback. Pitches and PCM match the corresponding earlier scratch-placement run, so placement alone did not change the observed behavior.

Direct reset starts with modeled CACR zero. A separate test retains the actual stock E03 loader-derived state, with CACR `0008c000`, then overlays the new source/count/redirect before application startup. Copying occurs with both cache-enable bits clear. At `4000053e` the destination matches the full source, with metadata ready still zero. Stock startup subsequently writes CACR `a50ce100` and ACR0 `4007e020`; at `40000568` the copied bytes still match. This verifies code/data preservation and cache-control ordering in the model. It does not simulate physical cache tags or coherence.

The loader test loads unchanged E03 first and supplies the extension afterward in PC memory. It does **not** prove that a newly packaged extended container loads successfully. Repackaging and checking that new container remain future work.

## Audio difference

All controls start from the same final-placement bad-pointer UI snapshot, with private context disabled. They receive the same panel input, source-pattern root/scale fixture and 1.5-second playback period. The trace records generated parameter packets before the stock transfer instruction, packets consumed by each DSP render, resulting voice-block hashes, pitches and PCM. Instrumentation reproduces the previous stock and fallback PCM hashes.

Stock and full fallback both generate and transfer the same **4,049 complete parameter packets**, byte for byte, and produce the same 12 fixed-point note pitches. Their DSP consumes 4,050 packets, but some renders select a different age of packet.

The first consumed-packet difference is render 49, before the first reported note at about 802 ms. Stock consumes transfer 48 again, while fallback has already transferred packet 49. Word `+290` is `267d1800` versus `26aa1800`. The ordered trace shows stock rendering before transfer 49 and fallback transferring before that render; both then converge on packet 50.

The first voice-output difference is render 1,424. Stock repeats packet 1,423; fallback consumes the next packet. PCM first differs at stereo frame 45,677. Across this recording, 2.36% of frames differ, with maximum absolute sample difference 93 on the 16-bit scale. These measurements describe this deterministic offline recording, not live GUI crackling or physical timing.

| PC control | PCM matches stock? | Interpretation |
|---|---|---|
| All hook sites restored to stock | Yes | Reference |
| Full fallback hooks, pointer zero | No | Original discrepancy reproduced |
| Context hooks retained, pitch hook restored | Yes | Earlier packet-age differences alone do not guarantee an audible difference |
| Pitch hook alone, pointer zero | Yes | Pitch hook alone does not reproduce the discrepancy here |
| 32 NOPs at the stock pitch path | Yes | Small delay control |
| 32 NOPs at stock allocation entry | No | Extra execution alone can change audio in this model; its cost is not matched to the full helpers |
| Full fallback, stock packets replayed by render ordinal | **Yes, byte for byte** | Controlling consumed packet age restores both every voice-block hash and the complete PCM |

The replay explicitly writes each recorded stock input packet into shared RAM before pending DSP service. It is a disclosed PC causality fixture, not an implementation proposal. Full fallback hooks remain active, context remains disabled and pitches stay unchanged. Together with identical generated packets, this isolates the complete observed audio discrepancy to the consumed packet stream for this workload. It does not establish that every future workload or physical-device difference has the same cause.

## Remaining work

The planned fallback location and guest copying path are now tested. The audio difference has a bounded explanation; adding synchronization to physical firmware solely to reproduce this emulator's packet age would be unjustified. Physical render timing, DMA arbitration and cache behavior remain hardware-validation questions.

A next PC-only candidate can integrate the tested payload extent, copier count and initializer redirect, then validate its packed-container loader path and startup. Keep E03 PC-only: its original startup failure behavior has not been changed by these overlays.

Machine-readable summary: `Digitone-OS1.44-final-fallback-audio-summary.json`. Tests: `work/test-os144-final-fallback.py`, `work/test-os144-final-loader-cache.py`, `work/test-os144-final-fallback-contracts.py`, `work/investigate-os144-fallback-audio.py`, and `work/summarize-os144-final-fallback-audio.py`. The raw PC payload is `work/os144/fallback-final-payload.bin`; it is not a flashable firmware container.
