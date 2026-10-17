# E08 two-pattern handoff, copy and reset checks

The checks found a settings-ordering issue in the packaged E08C prototype.
Storage isolation, copy/paste/undo and the tested reset refusals pass. The
running handoff is **not certified correct**, because the automatic UI-binding
observer advances the arp settings before the receiving MIDI context arrives.
No hardware-ready firmware is released; E07 and the E08C package are unchanged.

## Distinct patterns and native operations

A01 was configured through the panel as UP / 1/32 / 80%; A02 as UP / 1/8 / 20%.
Native stopped pattern selection returned to each pattern's own MIDI data and
settings, and returning to A01 restored its original values. No settings words
or event metadata were injected from Python.

During uninterrupted playback, a held C–E–G chord crossed A01→A02. The native
receiving MIDI context reached the actual consumer, and its settings were
applied. Release emptied the held-note set and descriptor arena. A02→A01 then
completed, followed by fresh-note playback and release. The baseline output
has 40 matched note-on/off pairs; the separate control
has 41. Both have no hanging notes, including the observed
native output-channel change from channel 1 to channel 6 and back.

These are held-note and fresh-note observations. They do not demonstrate an
eligible old note remaining queued until after replacement. The earlier
`transition_done` probe label is misleading: that address runs periodically.
Actual context consumption plus changed backing/MIDI-data pointers are the
handoff witnesses used here. Future tests rename the periodic probe.

## Settings-ordering finding

| Observation at A01→A02 | Packaged E08C | Separate PC control |
|---|---:|---:|
| First settings application before receiving MIDI context | 124.67 ms | 0.00 ms |
| First publisher | UI-binding observer, 0x47be6f1e | MIDI-context consumer, 0x47be6844 |

In E08C the UI bank has already rebound to the receiving pattern when the
observer publishes its settings. The consumer applies those settings about
125 ms before the receiving stock MIDI-context descriptor is consumed. This
changes output: relative to the receiving context, the baseline's final old
note is at about −124 ms and its next note at +123 ms. In the control an
additional old-pattern note occurs at about −62 ms, followed by a receiving
note near +1 ms. This is an observed scheduling difference, not just a pointer
or display difference.

The PC-only control changes one observer: it suppresses automatic binding
publication while transport is running, allowing the native MIDI context to
drive this handoff. The context consumer and explicit panel-edit path are
unchanged. This eliminates the observed lead in the test, but it is a
host-loaded experimental overlay, not a packaged or complete fix. Live panel
edits still need an ownership rule so an edit to an incoming bank cannot
prematurely change the currently playing MIDI context. The native active MIDI
parameter binding is the next concrete ownership target.

The times above use modeled instruction pacing. They are not physical latency
measurements. No claim is made that every queued-note or sustain sequence is
covered by this control.

## Copy, clear and reset

- Native pattern copy/paste carries the added settings: A02 changes from
  UP / 1/8 / 20% to A01's UP / 1/32 / 80%.
- Native undo-paste restores A02's original settings. Pasting again restores
  A01's values, while A01 itself remains unchanged.
- The native UI reports sequence clear and undo pattern clear. The complete
  164-byte MIDI record, including the extension, remains unchanged across
  these operations. This clear route preserves MIDI parameters; it does not
  reset the arp settings to OFF.
- Nine native diagnostic/setup/pool/reset-entry controls return with balanced
  exits and unchanged D0. No guest write reaches the monitored payload,
  complete M1 state, arena or inherited pool spans. Diagnostic entry remains
  deliberately disabled; warm setup/reset entries refuse before mutation.
  These calls use explicit admission fixtures from a stopped state, and are
  not proof of concurrent UI/input shutdown or unknown computed bypasses.

The prior cold-initializer test separately demonstrates clearing the new
pending/binding fields. This does not make warm copier replay safe. Physical
RAM ownership, cache coherence and real-time behavior remain unverified.

## Next bounded step

Establish which native MIDI parameter binding owns playback during the
look-ahead interval, then use it to govern automatic binding updates and live
panel publication. Repeat this handoff control and project-save/reload after
the rule is implemented. Keep the result PC-only until separately reviewed.

Evidence: `Digitone-E08C-pattern-copy-reset-results.json`,
`Digitone-E08C-pattern-settings.json`,
`Digitone-E08C-running-pattern-handoff.json`,
`Digitone-E08C-order-control-handoff.json`,
`Digitone-E08C-native-copy-clear.json`, and
`Digitone-E08C-reset-refusal.json`.

Unchanged E08C internal package SHA-256:
`081c592e16bb8cb32b0b4c0ede6f0f10bc8dec95c783a50a7ee259d8d4ee6da6`.
