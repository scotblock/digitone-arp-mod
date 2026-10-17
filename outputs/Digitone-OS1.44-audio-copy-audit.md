# Digitone OS 1.44: ordinary audio and first-copy audit

Firmware remains unchanged. All hooks, the ready header and diagnostic inputs exist only in the PC engine; no startup installation or flashable image was created.

## Ordinary audio difference

The stock repeat has identical DSP input packets, voice buffers and PCM bytes. The full helper run has the same pitch-output sequence as stock, but first differs at DSP render index 5976: stock consumes its packet at 3984.667969 ms and helpers at 3985.073625 ms. The first different PCM frame is 191347, or 3986.395833 ms at 48 kHz. DSP input changes precede voice-buffer and SSI-output changes, so the first observed divergence is upstream of audio payload capture.

Allocator-only and pitch-only controls also preserve the pitch sequence and change audio. A timing-only allocator shim executes 64 NOPs followed by the displaced stock prologue and continuation; it performs no metadata operations. That control first differs at PCM frame 197772 (4120.25 ms). Added execution time alone is sufficient to create audio differences in this model. This shim is not matched to the exact full-helper cost.

The stock parameter transfer at 0x4009e050 starts DMA channel 47, copying 0x3a0 bytes from on-chip RAM at 0x80001c00 to DSP shared RAM at 0x10000000. Source-memory tracing and the ordered DSP/DMA trace are included in the audit JSON. The instrumented runs reproduce the original ordinary audio hashes. These results diagnose model scheduling and packet age; they do not certify physical DMA deadlines or promise audio equivalence on a device.

The ordered trace identifies the first divergence precisely. Stock DSP renders 5975 and 5976 both consume word8 `405e1c3f` and word32c `4de78fad`; only afterward does stock update word8 to `405f1c3f` and initiate DMA with word32c `4d0d677f`. Helpers render 5975 with the old words, then perform the same update and transfer before render 5976 consumes the new words. Assertions verify both runs generate the matching new words and that consumption/transfer order differs. Thus the first ordinary audio difference is a change in parameter-packet age caused by scheduling in this PC model, despite unchanged pitches. This does not prove all later differences have that same cause.

## First-copy coverage

Ordinary PLAY, a held panel note before PLAY, and pause/resume did not enter 0x40093c98. Static tracing found a caller at 0x400ff7a8 inside the stock transport-status handler. It selects this entry for incoming state 3 when the incoming state differs from the stored state. The outer routine also requires its enable flag and both values returned by the active descriptor to be nonzero.

A disclosed PC fixture supplies the 16-byte status packet `ec200000000000000000000000030000` to the actual stock render callback at 805.333359 ms. It does not inject note events, eligibility bits or sidecar context. The enable flag is already 1; the descriptor returns the active pattern and its associated data. Actual cache states are [0, 0, 1, 1]. The stock loop skips two inactive entries and allocates/copies both active entries.

The first-copy hook at 0x40093d46 executes twice. Each 72-byte destination equals its source exactly at the continuation; both nonzero context words propagate correctly. Sources 0x419f18bc and 0x419f1904 copy to 0x419ec0b4 and 0x419ec06c. Each destination subsequently publishes, is accepted, and reaches pitch output with the same allocation generation. The matched stock status-input control chooses the same destinations. Playback, MIDI sustain release, queue cancellation and a completed pattern handoff continue without a halt; code and storage guards remain intact.

This closes downstream first-copy execution coverage for the supplied status input. Normal hardware production of that status packet remains unverified. It is not evidence that ordinary panel PLAY exercises this route.

## Next step

Use the ordered packet-age result to create a tighter phase control, then repeat the comparison with the cycle-aware DMA model and 1.44 addresses. Separately trace the real producer of the state-3 status packet. Startup installation and physical testing remain outside this result.
