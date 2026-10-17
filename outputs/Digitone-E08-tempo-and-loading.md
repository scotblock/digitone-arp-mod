# E08 M1 — native tempo settings and loading layout

E07 remains unchanged. This phase produced native helpers and decompressed PC MAIN/payload images, not an installable E08 firmware.

## Tempo and settings

The retained native clock writer at 0x40095566 publishes the sequencer position, and its next position is advanced by 900,000 units. The relevant clock follows stock tempo in the observed UI controls. The arp scheduler continues to use that clock; no second millisecond clock was added.

Native configuration now supports 1/4, 1/8, 1/16, 1/32, 1/48, 1/96, 1/8 triplet and 1/16 triplet rates, with gate percentages 1–99. A guarded pending request is applied by the native MIDI consumer. Invalid requests preserve the previous configuration. A COLD admission guard prevents the M1 scheduler capturing or generating before LIVE. The public UI and persistence are not implemented.

The slowest table rate has 21,600,000 interval units. Native gate storage is half the desired duration because the stock timed-note retirement path doubles that field. Configuration arithmetic is bounded to avoid multiplication overflow. All 40 rate/gate combinations in the chosen controls passed native execution.

## Playback evidence

- initial_tempo_1_16: mean step 123.60 ms; native clock rate 43200000 units/s.
- LEVEL_plus400_1_16: mean step 126.40 ms; native clock rate 43199999 units/s.
- LEVEL_minus800_1_16: mean step 128.97 ms; native clock rate 41394543 units/s.
- same_tempo_1_8_gate25: mean step 261.43 ms; native clock rate 41399999 units/s.

The clock slowed from about 43.2 to 41.4 million units/s, and the measured arp interval increased accordingly. At the slower tempo, changing 1/16 to 1/8 doubled the step interval. Changing gate 50% to 25% at the same time retained the same absolute gate units. All 64 notes had matching endings and the final scheduler, held set and descriptor arena were inactive. Bulk encoder input did not establish exact preset BPM targets; results use measured stock clock rates. Native polling jitter remains.

## Loading and initialization layout

The proposed copied payload grows from 18,436 to 20,244 bytes, an extension of 1,808 bytes. The copier's longword count becomes 5,061. Existing E07 helpers retain their addresses; added routines are packed after the old payload and their absolute references relocated. Data/state guard gaps are explicit.

- Copy source: 0x4029c5b0 through 0x402a14c4 (exclusive end).
- Copy destination ends at 0x47be4f14.
- M1 state: 0x47be4d40, 336 bytes.
- Owned descriptor arena: 0x47be4ea0, 64 bytes.
- Cold-success initialization thunk: 0x47be4ee0.

The existing cold seed first checks its inherited caller/admission/context conditions. Only its successful continuation invokes the native M1 initializer. M1 defaults OFF, and its rate/gate defaults are created by the native configuration helper. The thunk then returns to the existing stock cache-handoff entry. A wrong caller reaches the inherited failure stop without calling the M1 initializer.

17 relocated native contract groups passed, including request publication and COLD refusal. Isolated cold copier execution verified exact code/table copying, initialization defaults, a zeroed descriptor arena and no writes beyond the destination. The final playback run verified code preservation at the relocated addresses.

## Limits and next step

The copier test stops at the stock cache-handoff entry. Playback starts from a settled E07 snapshot with disclosed overlay loading. These are separate tests: full loader-to-copier-to-application-to-M1 continuity is not established. No packed container was produced during this phase. The added RAM range has no exclusive ownership or physical cache-coherence certification. Warm copier replay remains an inherited hazard; the extension does not make it safe.

Next: join actual startup and playback using a PC-only packed image, then connect usable MIDI-track controls and settle pattern persistence. Hardware trials require a separate readiness review.

## Evidence

- [Digitone-E08-tempo-and-loading-results.json](./outputs/Digitone-E08-tempo-and-loading-results.json)
- [Digitone-E08-M1-tempo-playback.json](./outputs/Digitone-E08-M1-tempo-playback.json)
- [Digitone-E08-M1-relocated-tempo-contracts.json](./outputs/Digitone-E08-M1-relocated-tempo-contracts.json)
- [Digitone-E08-PC-copier-initialization.json](./outputs/Digitone-E08-PC-copier-initialization.json)
