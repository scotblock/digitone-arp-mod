from pathlib import Path
p=Path('outputs/Digitone-OS1.42-held-note-arp-context.md')
s=p.read_text()
s=s.replace('Complete external MIDI port/channel/Auto Channel routing has not yet been established, and live hardware behavior has not been tested.', 'Incoming MIDI Note On/Off convergence is now established in the follow-up below. Exact transport labels, configuration names, and all controller behavior still require confirmation; live hardware behavior has not been tested.')
s=s.replace('However, the mapped-input route has not been proven to represent every external MIDI Note On path. It must not be labeled a complete USB/DIN/Auto Channel trace. Identification of those incoming routes remains a discrete follow-up.', 'The configurable mapped-input route is not the sole incoming MIDI path. The explicit MIDI status dispatch and direct channel-routing path are established in the follow-up below.')
s=s.replace('Trace actual incoming USB/DIN MIDI Note On/Off and channel resolution into these builders, including Auto Channel and sustain. Then build a PC-only context model', 'Identify the configuration setters for the special selected-track channel and the two incoming transport queues, and finish sustain/controller routing. Then build a PC-only context model')
s += '''

## Follow-up: actual incoming MIDI convergence

Receive task `0x400db15a` registers input queues with low-level helper `0x400d9b68`, then handles two input queues at `0x400db1fa..0x400db2ae`. It reads the status byte, shifts it right four bits, and dispatches through the 16-entry function table at `0x401aade0`. The exact USB versus DIN labels for these two queues are not yet established.

The table proves these protocol identities:

| Status nibble | Handler |
|---|---|
| 8, MIDI Note Off | `0x400dc3e2` |
| 9, MIDI Note On | `0x400dc8c4` |
| B, Control Change | `0x400db68a` |

`0x400dc8c4` extracts channel from the status low nibble, note from byte 1, and velocity from byte 2. If velocity is zero, it branches to the Note Off handler. Otherwise it calls `0x400dc758(channel, note, velocity, source_flags)`.

Channel resolver `0x400dc758` compares the input channel to:

- `0x4131b9e4`, a special channel routed to selected track `0x4131b998`;
- each entry in the eight-track channel table at `0x4131b9e8`;
- `0x4131ba10`, another special channel routed through configurable mapping function `0x400df87a`.

The first behavior is consistent with Auto Channel, but that UI name is not confirmed by the traced setters. A matching ordinary channel can set multiple track bits when channels are shared. This means the receiving MIDI channel number must not be used directly as the track index.

For each resolved track, it selects canonical pattern bank B using current pattern index k, reads track fields +0x3cb root, +0x3ce scale, and +0x3cd, then calls related-note constructor `0x40106c30` at `0x400dc852`. It iterates up to four constructed notes, with -1 terminating the sequence, and calls held-note builder `0x400dc432` indirectly through a5 at `0x400dc898`. This closes the external MIDI-to-held-arp path that the earlier direct-call scan missed.

The source flags distinguish the two input paths and special-channel matches (8/16 on one queue, 2/4 on the other). Their interpretation as transport/source flags follows their construction, but the hardware transport labels remain to be verified.

Note Off handler `0x400dc3e2` calls `0x400dc2f6(channel, note, source_flags)`. That resolver uses track/channel state and retained generated-note bytes at `0x41945f50` to emit releases through `0x400dc18a`. On the special selected-track channel, it also consults the note-to-track map at `0x41946f70`, which allows a release to target its stored owner rather than blindly use the currently selected track. The configurable mapping channel has its own release route through `0x400df202`.

This gives V1 a stronger constraint: preserve original input-note and release mappings. Quantizing the arp's generated output is separate from changing the keys held in its note list. A release must continue to remove the corresponding stored input/generated note even if the sounding arp pitch was snapped elsewhere.

The known current/previous pattern switching and arp priority rules still apply. The mapped incoming Note On path uses the canonical bank selected at note reception; the active arp identity can outlive that reception context. Store V1 metadata only for an accepted new arp identity, rather than overwrite it for every arriving MIDI note.
'''
p.write_text(s)
