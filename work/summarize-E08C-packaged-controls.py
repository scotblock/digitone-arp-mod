from pathlib import Path
import json

folder=Path('outputs')
r=json.loads((folder/'Digitone-E08C-packaged-controls-results.json').read_text())
assert r['passed']
p=r['playback']
text=f'''# E08 controls integrated into the PC startup package

The tested M1 MODE/RATE/GATE controls and project conversion helpers are now
part of the internal E08 PC package. They are loaded by the stock loader,
copied by startup and initialized before normal application playback. The
tests do not load replacement helper bytes, install the firmware hooks from
Python, call the M1 initializer from the host, or write the arp settings into
RAM. ColdFire instruction adapters and modeled peripherals remain in use.

This experiment uses E08C filenames to keep the earlier E08 package and test
evidence intact. E08C is an internal controls-integration label, not a released
firmware version. E07 is unchanged. No hardware installation build is released.

## Startup and preservation

- Independent unpacking reproduces the intended MAIN image exactly, and the
  unmodified stock container writer round-trip remains byte-exact.
- The stock bootstrap/loader reaches MAIN at 0x400004e8 with matching image
  bytes after {r['loader_instructions']:,} modeled instructions and no flash writes.
- The copied payload is {r['copied_payload_bytes']:,} bytes, including
  {r['controls_added_copy_bytes']:,} additional bytes for this integration.
  Helpers, strings, rate table and displaced stock codec trampolines all travel
  in that payload. No additional heap allocation is introduced.
- The existing 336-byte M1 state contains the pending tagged settings and
  binding cookies. An isolated test poisons its final 24 bytes immediately
  before the native initializer; the initializer clears them. The wrong-caller
  control still excludes M1 initialization.
- Actual native startup reaches LIVE, clears the logo and reaches the UI with
  M1 OFF / 1/16 / 50%, empty event storage, no strict custom-instruction failures
  and no host completion-semaphore satisfactions.
- Resident helper code, tables and installed hooks remain intact after playback.
  The original appended MAIN copier source is zeroed by the time playback
  begins; it is a startup-only area. This does not make warm copier replay safe.

The loader handoff, cold checkpoint and UI checkpoint preserve modeled state.
This establishes a PC execution chain across those checkpoints, not physical
cache or DDR behavior.

## Panel controls, playback and project persistence

On M1, FUNC + SYN2 opens the native page. A changes MODE OFF/UP, B changes
RATE, C changes GATE, and NO closes it. The playback run selects UP / 1/32 /
80% from this page, then later selects UP / 1/16 / 50% from the page again.
There are no host arp-configuration requests in this run.

The observed output contains **{p['note_on_count']} note-ons and
{p['matching_note_off_count']} matching note-offs**, with no hanging notes.
OFF passes the C–E–G chord through; UP produces ascending C–E–G repeats.
Both note-release cases leave the held set and descriptor arena empty. Stop
is checked after release; this is not coverage of every held/sustained Stop case.

| Observed phase | Mean step | Predicted from native clock | Mean gate |
|---|---:|---:|---:|
'''
for row in p['cadence']:
    text+=f"| {row['phase']} | {row['mean_step_ms']:.2f} ms | {row['predicted_step_ms']:.2f} ms | {row['mean_gate_ms']:.2f} ms |\n"
text+='''
The LEVEL encoder's bulk tempo input changes the measured native musical
clock rate; the arp interval follows it. Changing 1/32 to 1/16 at the same
slower clock doubles the observed step interval. These are emulator timings,
not physical latency measurements or proof of audio DMA deadlines.

A separate fresh packaged-startup session repeats native project saving:
set UP / 1/32 / 80%, save through the project menus and emulated storage,
change MODE to OFF, and reload the saved project. The saved word and native
arp consumer both return to UP / 1/32 / 80% without another encoder edit.
Synth T4 data and existing M1 fields remain unchanged during the edits, and
the synth-settings getter is not called during the tested M1 control phases.
Legacy records still default to OFF / 1/16 / 50%.

The MIDI input-gate check retains the earlier disclosed emulator fixture.
In this playback run its before/after values are both 3, so reception was
already enabled and the write did not change its value.

## Remaining limits

This is M1 only. M2–M4 are not enabled. Native project persistence has been
observed for this sequence, but actual pattern-handoff isolation, preset
copying, warm reset, retained-view destruction and wider storage lifetimes
still need coverage. The proposed MIDI-record extension has no complete
exclusive-ownership certification. Physical RAM ownership, cache coherence
and real-time audio timing remain unverified. No hardware trial is approved
by these results.

The next bounded test is two patterns with different M1 arp settings, switched
through the real pattern transition while notes are queued or held, followed
by the relevant copy/reset cases. This extends the existing packaged tests
without changing the physical Digitone.

Evidence: `Digitone-E08C-packaged-controls-results.json`,
`Digitone-E08C-packed-loader.json`,
`Digitone-E08C-PC-startup-comparison.json`,
`Digitone-E08C-PC-copier-initialization.json`,
`Digitone-E08C-packaged-panel-playback.json`,
`Digitone-E08C-packaged-playback-verification.json`, and
`Digitone-E08C-packaged-project-controls.json`.

The observed MIDI output is saved as
`Digitone-E08C-packaged-M1-observed-PC.mid` for independent inspection.
'''
text+=f"\nInternal PC container SHA-256: `{r['candidate_sha256']}`.\n"
text+=f"\nUnchanged E07 SHA-256: `{r['E07_unchanged_sha256']}`.\n"
(folder/'Digitone-E08C-packaged-controls-review.md').write_text(text,encoding='utf-8')
older=folder/'Digitone-E08-M1-controls-and-saving.md'
previous=older.read_text(encoding='utf-8')
if 'Later packaged integration:' not in previous:
    first,body=previous.split('\n',1)
    previous=(first+'\n\nLater packaged integration: see '
              '[E08 packaged controls review](Digitone-E08C-packaged-controls-review.md). '
              'The overlay-only limitation below describes this earlier experiment.\n\n'+body.lstrip('\n'))
    older.write_text(previous,encoding='utf-8')
print('Wrote E08 packaged controls and playback review.')
