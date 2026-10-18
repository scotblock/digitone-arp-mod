# E10 packaged edit/save/restart/recall — 18 October 2026

The scoped PC workflow passes on the unchanged internal E10 package. No new
firmware code, hardware release or device update was made. The package SHA-256 is
`bec5b8bbb71a17a96a5acd30962166e6d38b57e0f4c72c7a81ccf7d8e082b4c7`.

## Native edit and save

A03 and A04 are created with native Digitone panel/encoder input, starting from
the verified packaged loader-derived UI state. A03 has 15 steps, C Ionian context
and first-step offset +1. A04 has 16 steps, C-sharp Ionian context and first-step
offset -1; its second step is explicitly made a rest (enabled mask 0xfffd).
The two programs have independent checksummed 32-byte pattern records.

Native Save Project As overwrites private-card slot 002 NEW PROJECT, including
both the overwrite confirmation and name confirmation. A subsequent unsaved
A03 offset change is discarded by native project reload. A03/A04 recall the
saved fields, offsets, lengths and rest mask rather than the unsaved change.
No E10 program, bank, executable helper or hook is host-inserted.

## Cold restart and saved-project recall

A separate private card and fresh native application cold startup begin from
the previously verified exact package-loader handoff. The native copier,
initializer, logo and normal UI execute again. This reuses the verified loader
handoff bytes; it does not rerun the loader bootstrap itself.

The saved named project is then selected through the native menu. All 128
serialized records match the observed saved bank; the persistence generation
advances and the complete active bank matches too. Native A03/A04 selection
and step-page input subsequently show their exact saved fields, including
A04's rest. The initial working-cache bank need not equal the named file before
that explicit load. These are serialized engine stages, not one uninterrupted
physical boot or an abrupt power-loss experiment.

## Running handoff

A held three-note chord runs on A03, then a native pattern request selects A04.
The test requires a changed playback backing pointer, the actual consumer's
receiving owner and the corresponding step owner/fields. A queued panel request
alone is not accepted. The actual step helper observes +1 in A03, -1 in A04,
the respective 15/16 lengths and disabled second step in A04. Native rest and
emission counters confirm that the receiving program runs and skips its rest.
Release and Stop leave no active/held/arena notes, and the full bank is preserved.
The inherited MIDI input-gate fixture remains explicit.

## Copy, clear and reset

On a separate private copy of the packaged saved session, populated A01/A02
exercise native full-pattern copy, paste, undo-paste and re-paste. Native ordinary
settings and E10 records move together. Clear and undo-clear retain arp settings
while clearing/restoring trigs, following the stock MIDI-setting semantics.
Editor updates and all 128 bank records match the retained RAM mirror; the stock
header checksum validates. This scenario precedes the additional A04 rest edit;
it tests the same unchanged code with a different populated bank.

Ten direct guarded reset-entry controls cover diagnostic admission values,
warm setup, pool wrapper/initializer, test exit and cold initialization in LIVE.
They return without writes to the watched storage. These are admission fixtures,
not concurrent physical reset/input tests and not a claim that the unit resets
and clears every arp setting.

## Test-driver corrections

The restored card already contained project slot 002, so the save driver needed
an extra overwrite confirmation. The first A04 setup changed root rather than
rest; the final run explicitly uses the step cursor and rest encoder and checks
0xfffd before saving. A chosen legacy UI checkpoint was not visited after the
cold named load despite the exact restored bank and generation change. Final
completion is established by those data checks and responsive native pattern
controls. An unrelated attempt to require a low-interrupt snapshot boundary was
removed: no subsequent test needs that extra snapshot. Firmware bytes were not
changed to accommodate any of these driver corrections.

## Scope

M1 only. PC execution retains the previously disclosed ColdFire adapters,
clock/memory/DSP/peripheral models, flash-read shortcut, scheduling fixtures and
serialized state handoffs. No physical timing/cache or full update-receiver
claim is added. Stock power handling remains the accepted inherited assumption;
no guaranteed abrupt-loss recovery or power-system redesign is claimed.

The consolidated checks are in
[the verification report](Digitone-E10-PC-package-workflow-verification.json).
The working E09A image and E10 lifecycle MAIN/payload remain unchanged. No full
firmware, project card, snapshot or loader-handoff bytes are exported here.
