# E11 — synth-style M1 arp programming

18 October 2026. Separate experimental candidate; E10 remains unchanged.
M1 remains the only extended MIDI track.

Left/Right select a step, E edits its scale-degree offset, F edits sequence
length, Up enables the step and Down makes it a rest. Repeated Up/Down are
idempotent. Cursor and length limits clamp correctly. The entry remains
FUNC + SYN2 then D clockwise. A/B retain root/scale, D counterclockwise
returns to main controls and H enables the step sequence. C is unused on
the step page; G retains the old rest-encoder alias. Main OFF/UP, rate and
gate are unchanged. Other synth sorting modes/range and pixel-identical
artwork are not added. The strip uses + enabled, - rest, X selected enabled,
* selected rest and . outside length.

Native panel checks program 0/1/2/3 with the third step resting, validate the
record checksum and retained mirror, recall the pattern and preserve the
other patterns/M2 bank. Existing E10 ownership/publication/persistence APIs
handle edits. There is no new persistent state or record format.

Three RAM UI handler entries change. UI code/strings/fallback clones are
appended; MAIN changes only its copy count and appended payload. Copy size
increases from 90,320 to 98,112 bytes, still below 0x47c00000. That address
bound does not prove physical exclusive ownership of the added interval.

The exact stock loader reaches MAIN, and native copier/init/logo/UI verifies
the added code/strings and restores 128 records. Final keyboard/sequencer
playback uses startup-copied UI code without a host overlay and produces
25 matching DIN/USB note pairs with release/Stop cleanup. A separate overlay
test also passes. These are serialized engine stages with inherited MIDI,
USB, peripheral and timing fixtures, not continuous physical execution.

Four exact-container startup-DIN controls pass. Valid input programs within
the slot; bad checksums or missing end cause no programming. Data packets
enter the recovered callback; first/end use UART IRQ. Flash operations are
fixtures, not hardware writes or full serial-pacing validation.

A local experimental candidate and stock-dependent patch ZIP are prepared.
No public release or device update occurred. Physical code placement/cache/
timing/UI behavior and a new full E11 save/reboot/copy/reset suite remain
pending. E10 persistence code and format are retained; the editor's native
bank/mirror/recall checks pass.

[Verification](Digitone-E11-PC-verification.json).
[Control guide](Digitone-E11-control-guide.md).
[Official synth workflow, page 31](https://www.elektron.se/wp-content/uploads/2024/09/Digitone_User_Manual_ENG_OS1.41_231108.pdf#page=31).
