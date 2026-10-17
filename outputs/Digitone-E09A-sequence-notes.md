# E09A — M1 sequencer arp correction (PC candidate)

The native panel-entered sequence confirmed that E09 disables the arp when a note selects its parameter-lock list as if it were a full MIDI parameter record. Descriptor +0x28 and cached address 0x419c5b14 hold parameter-lock list pointers. Reading the custom +0x9e settings word from either list is incorrect. The current isolated ownership tests that called these pointers runtime records modeled the wrong contract.

E09A obtains M1 arp settings from the KitActive context already consumed by the MIDI task, at its M1 runtime record +0x5ce. It does not read the current UI selection to override a playing pattern. Only the existing 242-byte source-owner helper interval changes; the corrected helper is 220 bytes plus NOP padding. No RAM or startup copier growth is introduced. E09 remains unchanged.

The unchanged E09 control generated one raw note for the actual sequenced trig and disabled the arp. The corrected overlay and final startup-copied E09A generate repeated pulses with the arp enabled. The packaged check also sends a live C–E–G chord, checks its three keyboard arp pitches, compares DIN and USB messages, balances note-ons/offs and checks clean state after releases and Stop. The helper is not host-loaded in the final packaged run. A separate isolated consumer/dispatcher/retirement test produces C E G C E G from a sequenced chord fixture and checks OFF, Stop, live release and M2 bypass.

The real loader reaches MAIN, the native startup copier/initializer reaches the UI, and independent MAIN decompression matches. These are PC tests. Continuous native multi-note chord entry, physical port delivery/timing/cache behavior, saved-project persistence and exhaustive queued-note context ownership remain separate gaps. M2–M4 and the MIDI arp step editor are not added.

Try this as a separate Digiemu entry first. Use a trig length long enough for several arp steps: a very short trig can legitimately contain only one arp pulse. Configure M1 with FUNC + SYN2 from an ordinary MIDI parameter page, enable UP, choose RATE/GATE, and check note-offs when stopping. No device was updated by this work.

File: `Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx`. SHA-256: `68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c`.
