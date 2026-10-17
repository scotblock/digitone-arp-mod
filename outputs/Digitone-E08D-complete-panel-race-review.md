# Complete incoming-pattern panel race: PC verification

15 October 2026. **The previously missing complete panel race was reproduced and passed in the PC engine.** No candidate firmware bytes were changed and no device update was performed.

The successful run used the existing E08D package and its loader-derived startup state. UART panel input drove the actual native UI handlers, MIDI settings accessor, stock dirty notification, guarded publisher and MIDI context consumer. No helper, settings word, return value or program counter was replaced to force success.

The earlier test incorrectly tried reopening an arp page that was still active. Its original 30 ms encoder observation was also too short: the successful incoming encoder event took about 52 ms to reach its handler. Leaving the existing page open and observing for 80 ms resolved the test gap without changing the firmware.

| Native event | Modeled time | Result |
|---|---:|---|
| Incoming A02 panel edit reaches MIDI accessor | 2119.426 ms | Gate changes from 20% to 50%; its saved in-memory word changes `0xac94` → `0xacb2`. |
| Stock dirty notification returns | 2119.426 ms | The normal stock notification runs and invalidates the track cache. Playback ownership remains A01. |
| Guarded panel publication returns | 2119.426 ms | Refused (`D0=0`): A02 is the edited record, but A01 still owns playback. No pending settings word is published. |
| Actual A02 context is consumed | 2202.105 ms | Reads the edited `0xacb2` word and establishes A02 ownership. |
| Configuration applies the edited settings | 2202.105 ms | UP / 1/8 / 50%; no premature configuration call occurred in the intervening 82.679 ms. |

Throughout that interval A01 continued at UP / 1/32 / 50%. A later A02 panel edit, after it became the active owner, successfully changed its gate to 80%. Returning to each pattern preserved the separate edited in-memory values. Independent serial parsing found **35 note-ons, 35 matched note-offs and no hanging notes**.

This verifies one complete native execution of the previously missing race, including the stock cache invalidation caused by editing the incoming record. It does not prove every possible interrupt interleaving, same-address record reuse, disk save/reload, physical memory ownership or hardware cache/timing behavior. E08 remains PC-only.

Candidate SHA-256 remains `c6e2b327af09c46858ab3b902e0a35a0dce5bf355258952c0915983aabfc5099`. E07 and E08C hashes were checked and remain unchanged.

Reproduction: `work/test-E08D-complete-panel-race.py`, followed by `work/verify-E08D-complete-panel-race.py`. Raw trace: `outputs/Digitone-E08D-complete-panel-race-handoff.json`. Independently checked results: `outputs/Digitone-E08D-complete-panel-race-results.json`.
