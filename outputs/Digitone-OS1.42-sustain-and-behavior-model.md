# Sustain tracing and PC-only V1 behavior model

## Outcome

CC64 sustain and CC66 sostenuto now have concrete static traces through deferred release and into the held-note arp. A standalone Python behavior model was built and run successfully:

- **10 context/release scenarios passed.**
- **4,608 scale cases passed** (128 notes x 12 roots x major, minor, and unrestricted).
- Original firmware SHA-256 is unchanged: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`.
- No patched, rebuilt, or flashable firmware was produced.

The model is a specification combining observed firmware rules with proposed V1 behavior. It is not a ColdFire emulator and its passes are not hardware or binary-patch validation.

## Confirmed sustain and sostenuto paths

Incoming MIDI Control Change dispatches to `0x400db68a`. Track/channel resolution calls `0x400dee6e`, which normalizes its two boolean routing arguments and branches to controller handler `0x400dea02`.

That handler identifies controller number 0x40 (CC64) at `0x400dea7c..0x400dea82` and number 0x42 (CC66) at `0x400deaea..0x400deaf4`.

| Controller | Value threshold | Implementation target | Effect |
|---|---|---|---|
| CC64, sustain | 0..63 off; 64..127 on | `0x400e10d6` | Sets per-track sustain state; off flushes sustain-deferred releases |
| CC66, sostenuto | 0..63 off; 64..127 on | `0x400e1052` | Marks currently held entries; off clears those marks and flushes its deferred releases |

The threshold compares against 0x3f at `0x400ded98` and `0x400dedea`. This is not a velocity or note-length condition.

Track list/state storage:

| Address | Observed meaning |
|---|---|
| `0x41962008 + track` | Sustain on/off byte |
| `0x41962010 + 8*track` | Sustain-deferred list head/tail pair |
| `0x41962050 + 8*track` | Sostenuto-deferred list head/tail pair |
| `0x41962090 + 8*track` | Currently held input-note entries |

Held entries retain the note byte at +0x04, a sostenuto mark at +0x05, and the input/source identifier as a long at +0x00. The release helper matches both note and identifier. The Python model deliberately abstracts this to a single source with unique held pitches; duplicate-source collisions remain outside its coverage.

On Note On, helper `0x400e114a` removes matching stale entries from these deferred/held lists, then records the new held entry. This prevents a previous deferred release for the same source/key from lingering across a repress in the traced path.

On Note Off, helper `0x400e11bc`:

1. looks up the corresponding held note/source entry;
2. removes it from the held list;
3. if its sostenuto mark is set, moves it to the sostenuto-deferred list;
4. otherwise, if sustain is on, moves it to the sustain-deferred list;
5. otherwise frees it and allows normal release processing.

If there is no held entry but sustain is on, it can allocate a sustain-deferred entry. The normal matched-release cases are modeled; unmatched releases, source multiplicity, and allocation failure are not reproduced fully.

`0x400dc18a` calls that helper at `0x400dc1ac`. A nonzero result branches past the normal emitted note-off path. Thus a deferred physical key release does not immediately remove its arp note.

Pedal-off flushers call `0x400dc18a` directly for their queued entries and free the queue nodes. The flush does not move those entries from one pedal queue into the other. In the traced overlapping-pedal case, releasing CC66 can therefore emit the deferred release even while CC64 remains on. This is included as a static-rule scenario, not a measured hardware claim.

The emitted release later reaches `0x4009e2c2..0x4009e2cc`, which removes the input note from the arp list through `0x4009743e`. Once the last arp note is removed, the active list becomes empty. Stored priority/settings/identity fields can remain populated; V1 must check active state before using context.

## Selected-track channel changes while a pedal is held

Controller handler branches using the special selected-track routing flag retain a pedal-down owner:

- CC64 owner: `0x401feb0c`, stored at `0x400dedc6`;
- CC66 owner: `0x401feb08`, stored at `0x400dee16`.

On pedal-up, the handler replaces the currently supplied track with the stored owner before calling the flusher (`0x400dedce` / `0x400dee1e`). A repeat of the same boolean pedal state on a different selected track is ignored by the preceding state/owner checks.

Therefore changing the selected track while sustaining does not make pedal-up blindly release the new selection. The model includes this owner latch. Exact Auto Channel UI labeling and the owner globals' initial values are not established here; an initial pedal-up with no modeled owner is explicitly unsupported.

This owner latch is separate from the V1 root/scale snapshot. A pedal operation neither selects a new arp identity nor provides a reason to replace its retained scale context.

## What the model reproduces versus proposes

Observed rules modeled:

- held setup priority 2 versus sequencer priority 1;
- rejection of lower-priority input while an arp is active;
- note-list reset on different settings or higher priority;
- additive notes retaining the current identity;
- a newly populated empty list creating a new identity;
- CC64/66 thresholds, deferred release, and selected-track owner behavior;
- original input keys being retained for release;
- active-list and stale-identity checks.

Proposed V1 rules modeled:

- snapshot the generating track's root/scale only for an accepted new arp identity;
- retain that context for additive notes and existing sustained notes;
- capture new context after the prior arp ends or accepts a replacement setup;
- carry a queued event's source pattern even if the global current pattern has changed;
- snap the coarse arp note **after transpose**, to the nearest permitted MIDI note;
- use the lower note for an equal-distance tie;
- preserve negative arp sentinel values;
- suppress out-of-range transposed notes instead of wrapping or clamping them;
- leave unrestricted scale notes unchanged.

These snapping and context policies are design assumptions for review, not claims about stock firmware. The model uses explicit musical pitch classes for major/minor and unrestricted mode; it does not assume firmware UI scale indices match membership-table indices. That translation still needs a separate audit.

Pattern changes in the model are abstract events: they change the available pattern without automatically resetting an arp. The tests then supply specific additive, rejected, or replacement setup events. This tests the proposed lifetime policy without claiming every stock switch mode emits exactly those events.

## Validation coverage

| Scenario | Result |
|---|---|
| Sustain, pattern change, additive held note, lower-priority rejection, release and retrigger | Passed |
| Changed settings replace context; old identity cannot generate a valid tick | Passed |
| Held input preempts sequencer even with the same settings | Passed |
| Queued event from the previous pattern retains its source context | Passed |
| Sostenuto holds notes present when marked, not newly added notes | Passed |
| Repressing a sustained key removes its stale deferred release | Passed |
| Sostenuto flush uses the traced direct-release path with both pedals down | Passed |
| Track isolation, -1/-2 sentinels, MIDI bounds and after-transpose snapping | Passed |
| Mode-off setup alone does not imply an active-note-list reset | Passed |
| Special-channel pedal-up targets the remembered pedal-down track | Passed |

The scale checks cover legal output, unchanged legal notes, unrestricted pass-through, and idempotence for every tested note/root/scale. They do not prove oscillator pitch stays in scale after fractional tuning, pitch bend, glide, or other later modulation.

## Files and use

- `digitone_behavior_model.py`: standalone Python 3 model and checks; standard library only. It has no device I/O and reads/writes no firmware.
- `Digitone-behavior-model-results.json`: the successful run's scenario traces and counts.

Run the Python file to print the JSON results. Import its `Model`, `Context`, and `snap` classes/functions to explore other explicit event sequences.

## Limits and next step

The static sustain trace is complete through CC dispatch, deferral, flush, and arp-note removal for the mapped paths. The model does not cover duplicate keys from multiple sources, memory-pool exhaustion, every latch/voice mode, controller reset/all-notes-off semantics, MIDI-track output, transport scheduling, or every pattern-switch callback. No hardware has been contacted.

The next step is to audit the V1 integration points: how source root/scale candidates can be carried into the accepted arp identity, where they can be stored safely, how reset/release paths invalidate them, and which scale-index conversion applies. Then locate a coarse pitch insertion point that preserves input-note identities and later transpose. A firmware patch is still premature until those storage and control-flow checks are established.
