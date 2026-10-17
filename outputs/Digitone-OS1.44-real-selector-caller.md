# OS 1.44 actual selector and caller with context helpers

The actual changed stock selector and caller pass the bounded PC replay checks with the 1.44 helpers. Fourteen paired cases (28 replays) cover eight stock-generated states, one non-chromatic context fixture and five invalid-context controls. The firmware and helper image hashes remain unchanged. No startup hook was installed.

## Stock-derived execution

Eight guest snapshots were captured at `0x4009e668` during a clean stock session with queued notes, MIDI sustain, a confirmed pattern change and fresh receiving notes. They cover tracks 0–3, event types 0 and 1, descriptor-backed queued states and live MIDI states before/after replacement. Registers, the existing caller stack and guest memory are captured; branch results are not supplied by the test.

Each snapshot is replayed twice from the same state: once with stock call sites, once with temporary PC hooks for before/after selection, caller commit and pitch. Both execute the actual selector at `0x40097a94` and stop at the common release boundary `0x4009d7d8`.

For all eight natural cases:

- Selector return at `0x4009e694`, commit continuation when reached at `0x4009e738`, pitch continuation at `0x4009e890` and the final boundary match in registers, status, 64 bytes of current caller stack and original event bytes.
- Selector entries and the original event's final bytes match. Actual selector return values include a successful result of 1 and seven results of 0; the successful state reaches context commit, retained-context read and quantization.
- Final hashes match for the complete 128-event pool, four physical-cache slots, selected-note records, acceptance cache, selection gates and caller globals.
- The helper code remains intact and neither replay records a newly unmapped access.

The natural context words are chromatic. These equal-output cases verify caller compatibility, not a musical pitch change.

## Positive context and fallback

The successful stock-generated state is replayed with sidecar word `0x800040bd`: track 2, root 61, raw scale 0 (Ionian). This explicitly changes metadata only; the stock event and selection fields remain unchanged. The actual selector and caller still execute.

Stock note 57 becomes 56 at the helper pitch boundary, matching the independently extracted 1.44 scale oracle and downward tie rule. Selector and commit boundaries are identical. At pitch output, all registers other than D6, status, stack and event bytes match. D6 holds the expected fixed-point note. Checked stock memory regions and final release-boundary registers also match. DSP/audio output is not compared here.

Invalid magic, version, size, ready flag and a null owner pointer each fall back to stock note 57. Their observed caller boundaries match stock and quantization is not entered.

## Scope and next step

This closes the specific gap left by the previous entry/return-only tests: the changed selector now runs with the helpers around its real caller. It is still a bounded guest-state replay. Host timer, DMA and scheduler components are not restored for the slice, and no asynchronous transition or physical timing claim follows.

The private header and candidate metadata are explicit fixtures. Producer capture, allocation clearing and raw-copy bookkeeping are not yet connected in a continuously running 1.44 session. No eligible old-pattern note retaining scale across replacement, full reserved-memory ownership, cache coherence or startup installation is established here.

Next, connect those producer/allocation/copy paths with the verified caller/pitch hooks in a PC-only session and repeat continuous stock/helper playback, sustain, cancellation and a confirmed handoff. Keep startup installation separate until those checks pass.

Evidence files beside this report: `Digitone-OS1.44-caller-state-capture.json`, `Digitone-OS1.44-real-selector-caller.json`, `Digitone-OS1.44-real-selector-context.json`, and `Digitone-OS1.44-real-caller-summary.json`.
