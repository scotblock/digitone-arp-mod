# E08 M1 device controls and project saving — PC prototype

Later packaged integration: see [E08 packaged controls review](Digitone-E08C-packaged-controls-review.md). The overlay-only limitation below describes this earlier experiment.

M1 has a native controls page with MODE OFF/UP, eight clock-linked RATE
divisions, and GATE 1–99%. Open it with FUNC + SYN2 while M1 is selected.
Encoders A, B and C change those three settings; NO closes the page.
M2–M4 remain unimplemented.

The page uses the MIDI-specific settings handle, rather than the synth sound
getter that clamps M1 to synth T4. The isolated native accessor checks exercise
all 1,584 valid settings combinations, reject invalid inputs before mutation,
and default legacy/unmarked settings to OFF / 1/16 / 50%.

The PC overlay carries a tagged settings word from runtime MIDI preset offset
0x9e to serialized offset 0xa6 and back. Stock conversion alone clears or
ignores that word. The conversion bridge preserves the existing serialized
record length and passes the tested stock fields unchanged. This establishes
a working extension in the tested paths, not exclusive ownership of those
bytes under every firmware operation.

## Continuous native save/reload check

The test opens the page through panel events, sets UP / 1/32 / 80%, and
processes the firmware's normal dirty-notification and project save work.
It then changes MODE to OFF and reloads the saved project through the native
project menus and emulated storage. The runtime word returns to UP / 1/32 /
80%, and the native MIDI consumer applies those values without another
encoder edit. This is a project file save/load test, not a RAM snapshot
standing in for project persistence.

The completed-run verifier checks these concrete observations:

- Panel A/B/C select UP, 1/32 and 80%; D through H leave settings unchanged.
- The captured synth T4 data and existing M1 fields remain byte-identical during edits.
- No synth-settings getter executes during the M1 page, edits, close or initial input test.
- Native project save followed by OFF edit and native project reload restores UP/1/32/80% to the actual consumer without another encoder edit.
- The accessor, codec, consumer, retained-view and binding contract checks pass.
- The published E07 container remains unchanged.
- A separate completed-frame capture repeats the panel settings and consumer readback; its UP/1/32/80% OLED image was visually inspected.

The initialized UI-root observer notices current M1 data rebinding or changed
settings and publishes a complete request. It reads the existing root pointer;
it does not invoke its lazy constructor. The native consumer applies settings
inside its protected frame. Context descriptors also read the receiving
KitActive's M1 settings. Separate isolated fixtures test legacy data, changed
bindings, invalid class/null pointers, and COLD admission. They do not replace
a continuous real pattern-handoff test.

The custom MIDI view retains an identity tag. Its timer callback preserves
that tag; synth arp copy/clear/paste shortcuts are refused for it. Release
events do not close the newly opened page, and late encoder events after an
M2 selection refuse mutation. Actual reset, destruction and retained-reference
lifetimes still need wider continuous coverage.

## Packaging and limits

The new accessor, codec and controls code is a host-loaded PC overlay on the
older E08 startup snapshot. The older packaged loader/startup/playback result
does **not** establish loader continuity for these new helpers. No new
installable E08 has been produced from this work. E07 remains unchanged.

The next integration step is to include these helpers, their hooks and data in
one PC-only payload; copy and initialize them through startup; then repeat the
save/load and chord-playback checks using that packaged path. Actual pattern
switch isolation, MIDI preset copying and reset lifetimes remain separate
coverage gaps. Physical cache behavior, timing and RAM ownership are not
certified. This is not a hardware-trial approval.

Evidence: `Digitone-E08-native-M1-controls.json`,
`Digitone-E08-M1-controls-verification.json`,
`Digitone-E08-settings-accessor-tests.json`,
`Digitone-E08-settings-codec-bridge-tests.json`,
`Digitone-E08-settings-consumer-tests.json`,
`Digitone-E08-M1-view-guard-tests.json`, and
`Digitone-E08-current-settings-binding-tests.json`.

E07 SHA-256: a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd
