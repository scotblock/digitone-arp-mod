# Digitone OS 1.42: completed PC prototype

3 October 2026. This is a runnable PC specification of the proposed V1 behavior. It does not load, modify, rebuild, transmit or flash firmware, and produces no audio or flashable binary.

## Result

Context handling and coarse pitch quantization are now combined in one prototype. The suite passes:

- 20 end-to-end specification scenarios, with 75 explicit assertions.
- 18,432 root/scale/source encoding round trips.
- 55,296 combined pitch-path comparisons against an independent exhaustive nearest-note oracle: 12 root pitch classes × 36 scale settings × 128 MIDI notes.
- 3,000 deterministic mixed sequences involving pattern changes, capture-busy state, setup priorities, accepted replacement and event recycling.

The prototype is complete for the bounded behavior contract below. It is not a complete Digitone emulator or certification for a binary patch. Its tests include a passing negative control that demonstrates unresolved identity reuse; passing that test records the limitation rather than resolving it.

## Musical behavior

Each supported note captures root/scale values at its defined source boundary. Streamed delayed notes use the receiving pattern when the descriptor is handled. The PC enqueue call represents that boundary, not USB arrival or the original sender's pattern.

When setup accepts a new arp identity, the playback track retains that note's snapshot. Additive notes and rejected lower-priority input preserve the accepted snapshot. A contextless replacement explicitly removes scale locking for the new identity.

For proven successful arp selection, the pitch path:

1. Handles negative sentinel results without producing a note.
2. Applies the selected overflow policy before byte narrowing.
3. Adds the global and track transpose contributions and performs the MIDI-range check.
4. Uses the playback track's validated accepted snapshot to choose the nearest permitted MIDI note; equal-distance ties choose the lower note.
5. Preserves the generated allocation-note identity independently of the snapped sounding pitch.
6. Applies the later octave offset and expressive bend to the result.

The scale lock therefore applies to coarse note selection. Bend can move the sounding pitch between scale notes, and later octave adjustment can exceed the earlier 0..127 range. No final DSP clamp, glide behavior or smoothing is claimed.

### Concrete example outputs

| Sequence | Generated allocation note | Coarse result | Later pitch |
|---|---:|---:|---:|
| C-major note queued; receiving pattern changes to D major before emission | 61 | 60, using captured C major | 60 |
| C-source continuing tick remapped to a track with accepted D major and matching identity | 61 | 61, using destination accepted context | 61 |
| C-major output with two +1 transpose contributions, then +12 octave and +0.5 bend | 61 | 63 → 62 | 74.5 |

The allocation note is never replaced by the snapped pitch. Physical input-note release uses its original key in the single-source lifetime model.

## Persistent table and lifecycle

The prototype uses separate metadata entries and immutable snapshots, following the step-1 persistent-table proposal. It does not write proposed context into stock event bytes or derive context from +38 payload ownership.

It covers independent held caches, finite 128-event/64-node pools, queue-to-event transfer before modeled publication, copying/remapping, explicit recycling invalidation, dedicated accepted-context commit, accepted-source copying for scheduled ticks, deferred pedal release, reset and missing-context fallback.

Host event handles carry a generation solely to catch test misuse. That generation is not a proposed firmware field and does not establish firmware freshness. The Python table is a logical representation of the proposed allocation layout, not a byte-accurate heap or ColdFire RAM implementation.

A busy/nested writer or capture fault prevents new capture while preserving already accepted snapshots. Ordinary modeled queue drain reclaims event metadata; surviving caches and accepted records remain. Empty arp state prevents using a physically retained context. Setup reentry preserves feature metadata and guard state; stock pool reconstruction is not simulated by that operation.

## Coverage

The 20 scenarios include:

- Delayed receiving-pattern snapshot through acceptance and final pitch, followed by queue reuse.
- Additive/rejected input, settings replacement and stale identity rejection.
- Busy/nested writer state, failure latch, reentry preservation and contextless replacement.
- Sustain across a pattern change; overlapping CC64/CC66; selected-track pedal ownership.
- Initial fan-out and continuing remap with differing source/destination contexts.
- Cache refresh while accepted context persists; stale host handles.
- Event/node exhaustion, dropped queue emission and later cache replay.
- Drain versus active-list reset; raw release identity; MIDI and invalid tracks.
- Pitch after both transposes, octave/bend, sentinels, bounds and downward ties.
- Both synth event types, mode-off setup, invalid capture values and corrupted accepted records.
- Actual zero-skipping identity wrap and reuse limitations, all supported encodings, all scale settings and mixed-sequence stress.

The scale tables are the previously extracted OS 1.42 membership rows. The pitch oracle enumerates every permitted MIDI note and chooses the minimum distance independently of the prototype's sorted-neighbor implementation. Chromatic mode preserves each valid input.

## Overflow policy is explicit

The default `reject` policy suppresses a full nonnegative arp result above 127 before narrowing. This is an additional proposed behavior change, separate from scale quantization and missing-context fallback. It is exercised on both modeled initial and continuing outputs through their shared pitch function; this does not prove hooks exist at both actual firmware return sites.

The comparison option `stock_byte` narrows the generated result to an unsigned byte before later transpose/range handling. For 274, the comparison sees allocation note 18; C-major quantization then produces 17. This reproduces the previously traced narrowing arithmetic, not full stock firmware execution.

Missing context leaves the valid coarse note unchanged by quantization. It does not disable the separately selected overflow policy.

## What is assumed, and what remains unresolved

This new prototype executes Python behavior rules. The earlier step-2 audit separately executed 9,174 unchanged stock instructions in 13 controlled cases. Those results inform the lifecycle contract; they are not silently treated as execution of these new context or quantization operations.

Arp output values and successful-selection provenance are supplied inputs. The stock arp traversal algorithm, every arp mode, latch, detailed transport scheduling, duplicate input sources, voice allocation, stateful glide and DSP smoothing are outside this model. The queue's PC clock abstracts due-time emission; it does not reproduce every stock scheduling boundary.

Accepted setup is the earlier modeled priority/list behavior, not execution of the real successful setup plus an injected commit. Pattern changes do not automatically clear an arp in this specification; actual transition events must eventually supply the correct reset/additive/replacement behavior. Captures are guarded at the specification level, not proven coherent in actual firmware.

### Identity reuse negative control

The suite deliberately recreates an old event and a new accepted state sharing identity 1. The old event then selects the new accepted context because current guards cannot distinguish those histories. Follow-up actual setup execution shows that the firmware skips zero: ffffffff wraps to one. The prototype now mirrors this. Ordinary reset preserves the counter; it does not restart it. A full counter-cycle repetition remains unresolved. Host handle generations do not fix this firmware identity ambiguity.

The experimental design still needs an explicit freshness assumption or mechanism excluding stale events across full counter-cycle reuse; the actual ordinary-reset path does not itself cause that reuse. This is a remaining correctness obligation, not evidence that the stock instrument is faulty.

Other integration obligations remain: complete producer/copy coverage; protected data/context association and accepted commit; coherent pattern-writer coverage and abnormal exits; allocator and cold setup-failure continuation; register preservation, relocation and executable storage; and real device transition preconditions. None is certified by the PC suite.

## Run and inspect

Extract the accompanying ZIP into a folder and run:

```
python digitone_pc_prototype_checks.py
```

Only Python's standard library is required. The command prints the counts and example outputs, and writes `Digitone-PC-prototype-results.json` beside the script. Keep the behavior-model module and scale-map JSON in the same folder.

Files:

- `digitone_pc_prototype.py`: combined engine.
- `digitone_pc_prototype_checks.py`: scenarios, independent oracle and stress checks.
- `digitone_behavior_model.py`: reused bounded priority/pedal lifetime model.
- `Digitone-OS1.42-scale-map.json`: previously extracted membership data.
- `Digitone-PC-prototype-results.json`: recorded results.

## Next integration target

Before building modified firmware, close the protected accepted-record commit against actual successful/additive/rejected setup, and resolve identity reuse freshness. The PC prototype can now serve as the reference behavior for those checks. It does not require or authorize a hardware test.

Decoded section-3 SHA-256 remains `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.
