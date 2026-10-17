# Arp settings and step-storage trace

Continued read-only inspection. No modified or flashable firmware was generated.

## Settings identified

The arp edit dispatcher at `0x4004eb34` contains a nine-entry signed-word jump table at `0x4004eb94`. Decoding each target separately avoids interpreting table data as instructions.

| Returned-storage offset | Getter | Setter | Observed behaviour / interpretation |
|---|---|---|---|
| +0x10f | 0x4002ecea | 0x4002ed1a | Mode candidate; setter clamps to 0..4, preserves previous byte at +0x126; separate toggle restores a previous nonzero mode |
| +0x110 | 0x4002ee82 | 0x4002eeb2 | Arp speed; setter clamps to 0..17; UI display table contains 18 divisions from 1/1 through 1/96 |
| +0x111 | 0x4002ef20 | 0x4002ef50 | Octave range; setter clamps to 0..7; edit code displays value +1 through `OCTAVE RANGE: %d` |
| +0x116..+0x125 | 0x4002eab2 | 0x4002eafa | Sixteen signed step-value bytes; strong offset-array candidate |

Offsets refer to the storage returned by a separate object's virtual method at table byte offset +0x28, not to the UI object itself. Several setters construct the same apparent change-notification object and call virtual slot +0x10 after writing storage. The notification object's exact type is not yet proven.

The mode display tables copied into the view include `OFF`, `TRUE`, `UP`, `DOWN`, `CYCL/CYCLE`, `SHUF/SHUFFLE`, `RAND/RANDOM`, `CHRD/CHORD`. Since the inspected mode setter only accepts 0..4, the additional names must not be assumed to be selectable modes on this version. They may be shared or unused display data.

## Sixteen-step array: concrete evidence

Edit-dispatch case 5 at **0x4004edda**:

1. obtains an edit delta;
2. reads the selected step index from UI field +0x2bc;
3. calls getter `0x4002eab2` with that index;
4. adds an adjusted edit delta to the returned value;
5. calls setter `0x4002eafa` with storage object, step index, and updated value.

The getter clamps the index to 0..15 and returns a **sign-extended byte** from `storage + 0x116 + index`. The setter clamps the index to 0..15 and the input value to **-64..63**, then writes that byte and issues a change notification. This establishes the array layout and signed representation. It does not yet prove the musical unit or whether an endpoint value has special semantics (such as a rest/sentinel).

Adjacent code reads a bit from a word at storage +0x114, indexed by the same 0..15 range. This is a candidate per-step flag mask; its exact meaning remains unproven.

Edit case 9 at `0x4004eeaa` updates and clamps UI selection +0x2bc to 0..15. Thus +0x2bc is strongly supported as the currently selected arp step, rather than a playback index.

## Shared caller reclassified

The code around **0x40091500** calls many settings getters, writes their outputs into a stack record, and loops over sixteen step values. Subsequent code copies other groups of parameters. This is consistent with serialization, conversion, or settings snapshotting. It is **not sufficient evidence of the live arpeggiator engine**. The earlier suggestion to use this caller as a path into operating behaviour needs that qualification.

## Where this leaves V1

We now have a concrete arp storage lead: mode, speed, octave range, sixteen signed step values, and a candidate step-flag word. The next useful trace is from this storage into the playback engine, looking for reads of the step array that feed pitch arithmetic and note emission. The edit getter/setter could also help locate the storage class and its change notifications.

No validated final pitch calculation, musical-scale quantizer, or safe patch location has been identified. These findings justify continuing offline code analysis, not altering the storage values or firmware.
